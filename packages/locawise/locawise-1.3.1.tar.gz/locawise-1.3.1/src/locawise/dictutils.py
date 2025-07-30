import itertools
from collections import OrderedDict
from itertools import batched
from typing import Any

from locawise.errors import UnsupportedLocalizationKeyError


def chunk_dict(data, size: int):
    chunks = []
    for item in (dict(batch) for batch in batched(data.items(), size)):
        chunks.append(item)
    return chunks


def simple_union(*dicts):
    return dict(itertools.chain.from_iterable(dct.items() for dct in dicts))


def unsafe_subdict(original_dict: dict, sub_keys: set):
    "unsafe in the sense that if a key is not in the dict it will raise an error"
    return dict((k, original_dict[k]) for k in sub_keys)


def flatten_dict(_dict: dict[str, Any], level_separator: str = '_/') -> dict[str, str]:
    def flatten_dict_recursive(prefix: str, _dict: dict[str, Any]) -> dict[str, str]:
        result = {}
        for k, v in _dict.items():
            if level_separator in k:
                raise UnsupportedLocalizationKeyError(f'{level_separator} is not allowed in keys. Please change it.')

            if isinstance(v, dict):
                sub_result = flatten_dict_recursive(prefix + k + level_separator, v)
                result.update(sub_result)
            else:
                result[prefix + k] = v

        return result

    return flatten_dict_recursive('', _dict)


def unflatten_dict(_dict: dict[str, str], level_separator: str = '_/') -> dict[str, Any]:
    result = OrderedDict()
    for k, v in _dict.items():
        nodes = k.split(level_separator)

        # dict to add the key-value pair
        leaf_dict = result
        for index, node in enumerate(nodes):
            if index == len(nodes) - 1:
                leaf_dict[node] = v
            else:
                temp = leaf_dict.get(node)
                if temp is None:
                    leaf_dict[node] = OrderedDict()

                leaf_dict = leaf_dict[node]

    return result
