import os


def retrieve_openai_api_key():
    return os.environ.get('OPENAI_API_KEY')


def generate_localization_file_name(lang_code: str, file_name_pattern: str) -> str:
    return file_name_pattern.replace('{language}', lang_code)
