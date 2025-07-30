import io
import json
import logging

import jproperties

from locawise.androidutils import serialize_to_xml
from locawise.dictutils import unflatten_dict
from locawise.errors import FileSaveError, SerializationError
from locawise.fileutils import write_to_file
from locawise.localization.format import LocalizationFormat, detect_format


async def serialize_and_save(key_value_pairs: dict[str, str], target_path: str):
    """
    :raises LocalizationFormatError
    :raises FileSaveError
    :raises ValueError
    """
    logging.info(f"Serializing and saving to target_path={target_path}")
    if not target_path.strip():
        raise ValueError(f"Target path cannot be empty")

    localization_format = detect_format(target_path)
    content = serialize(key_value_pairs, localization_format=localization_format)

    try:
        await write_to_file(file_path=target_path, content=content)
    except Exception as e:
        raise FileSaveError(f"Could not write content to target_path={target_path}") from e


def serialize(key_value_map: dict[str, str], localization_format: LocalizationFormat) -> str:
    match localization_format:
        case LocalizationFormat.PROPERTIES:
            return serialize_to_properties_format(key_value_map)
        case LocalizationFormat.JSON:
            return serialize_to_json(key_value_map)
        case LocalizationFormat.XML:
            return serialize_to_xml(key_value_map)
        case _:
            raise ValueError(f"Serialization for {localization_format} is not implemented")


def serialize_to_properties_format(key_value_map: dict[str, str]) -> str:
    try:
        with io.BytesIO() as output_stream:
            # Call your function with the memory stream
            encoding = 'utf-8'
            properties = jproperties.Properties()
            properties.properties = key_value_map
            for k, _ in key_value_map.items():
                properties._key_order.append(k)
            properties.store(output_stream, encoding=encoding, strict=True, strip_meta=True, timestamp=False)
            binary_content: bytes = output_stream.getvalue()

            # Convert to string using the same encoding that was used for writing
            return binary_content.decode(encoding=encoding)
    except Exception as e:
        raise SerializationError("Could not serialize to properties format") from e


def serialize_to_json(key_value_map: dict[str, str]) -> str:
    try:
        _dict = unflatten_dict(key_value_map)
        return json.dumps(_dict, ensure_ascii=False, indent=2)
    except Exception as e:
        raise SerializationError from e
