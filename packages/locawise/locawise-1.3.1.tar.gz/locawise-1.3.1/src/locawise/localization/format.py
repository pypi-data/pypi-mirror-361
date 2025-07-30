from enum import Enum

from locawise.errors import LocalizationFormatError


class LocalizationFormat(Enum):
    PROPERTIES = "properties"
    JSON = 'json'
    XML = 'xml'


def detect_format(file_path: str) -> LocalizationFormat:
    suffix: str = find_extension(file_path)
    if not suffix:
        raise LocalizationFormatError(f"Format of the file could not be detected. file_path={file_path}")

    for format_type in LocalizationFormat:
        if format_type.value.lower() == suffix.lower():
            return format_type

    raise LocalizationFormatError(f"Unsupported localization format: {suffix}")


def find_extension(file_path: str) -> str:
    if '.' not in file_path:
        return ""

    parts = file_path.split(".")
    if not parts:
        return ""

    return parts[-1]
