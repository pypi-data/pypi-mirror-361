import logging

import pycountry


def is_valid_two_letter_lang_code(lang_code: str) -> bool:
    lang = pycountry.languages.get(alpha_2=lang_code)
    return lang is not None


def retrieve_lang_full_name(lang_code: str) -> str:
    lang = pycountry.languages.get(alpha_2=lang_code)
    if not lang:
        logging.error('Invalid language code. This indicates a programming error.')
        raise ValueError('Invalid language code')

    return lang.name
