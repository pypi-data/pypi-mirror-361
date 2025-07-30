import json
import logging
from collections import OrderedDict

import jproperties

from locawise.androidutils import parse_xml_string
from locawise.dictutils import flatten_dict
from locawise.errors import ParseError
from locawise.fileutils import read_file
from locawise.localization.format import detect_format, LocalizationFormat


async def parse(file_path: str) -> dict[str, str]:
    """
    :param file_path:
    :return:
    :raises LocalizationFormatError:
    :raises ParseError:
    :raises ValueError:
    """
    if not file_path:
        return {}
    localization_format: LocalizationFormat = detect_format(file_path)
    try:
        file_content = await read_file(file_path)
    except FileNotFoundError as e:
        logging.info(f'File not found {file_path}')
        raise e
    except Exception as e:
        raise ParseError(f"Unknown exception while reading {file_path}") from e

    match localization_format:
        case LocalizationFormat.PROPERTIES:
            return await parse_java_properties_file(file_content)
        case LocalizationFormat.JSON:
            return await parse_json_file(file_content)
        case LocalizationFormat.XML:
            return parse_xml_string(file_content)
        case _:
            raise ValueError(f"Parsing is not implemented for format={localization_format}")


async def parse_java_properties_file(file_content: str) -> dict[str, str]:
    try:
        p = jproperties.Properties()
        p.load(file_content, encoding='UTF-8')
        ordered_dict = OrderedDict()
        for k, v in p.items():
            value, _ = v
            ordered_dict[k] = value
        return ordered_dict
    except Exception as e:
        raise ParseError("Java properties file could not be parsed") from e


async def parse_json_file(file_content: str) -> dict[str, str]:
    try:
        _dict = json.loads(file_content)
        _dict = flatten_dict(_dict)
        return _dict
    except Exception as e:
        raise ParseError('JSON file could not be parsed') from e
