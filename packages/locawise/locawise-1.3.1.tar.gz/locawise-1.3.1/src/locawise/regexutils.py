import re


def remove_all_whitespace(text):
    # \s matches any whitespace character (spaces, tabs, newlines)
    return re.sub(r'\s+', '', text)
