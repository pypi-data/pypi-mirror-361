import logging
import re
from collections import namedtuple, OrderedDict

from lxml import etree

from locawise.errors import MalformedAndroidStringsXMLError

_RESOURCES_TAG: str = 'resources'
_STRING_TAG: str = 'string'
_STRING_ARRAY_TAG: str = 'string-array'
_PLURALS_TAG: str = 'plurals'
_ITEM_TAG: str = 'item'

_STRING_ARRAY_ITEM_SEPARATOR = '_/_'
_PLURALS_ITEM_SEPARATOR = '___'

_TranslationPair = namedtuple('TranslationPair', ['key', 'value'])


def parse_xml_string(file_content: str) -> dict[str, str]:
    file_content = file_content.encode("UTF-8")
    parser = etree.XMLParser(encoding='UTF-8', remove_comments=True, strip_cdata=False)
    content = etree.fromstring(file_content, parser=parser)
    tree = etree.ElementTree(content)
    return _parse_xml_tree(tree)


def _parse_xml_tree(tree: etree.ElementTree) -> dict[str, str]:
    result: dict[str, str] = OrderedDict()

    root = tree.getroot()

    if root.tag.lower() != _RESOURCES_TAG:
        raise MalformedAndroidStringsXMLError("Expecting root tag to be <resources> tag.")

    for node in root:
        tag = node.tag.lower()

        if tag == _STRING_TAG:
            pairs = _parse_string_node(node)
        elif tag == _PLURALS_TAG:
            pairs = _parse_plurals_tree(node)
        elif tag == _STRING_ARRAY_TAG:
            pairs = _parse_string_array_tree(node)
        else:
            logging.warning(f"Unrecognized XML item {node}")
            continue

        for pair in pairs:
            result[pair.key] = pair.value

    return result


def _parse_string_node(node) -> list[_TranslationPair]:
    tag = node.tag.lower()
    if tag != _STRING_TAG:
        raise ValueError(f"Expected tag: {_STRING_TAG} actual tag: {tag}")

    key = node.attrib['name']
    value = _extract_inner_content(node)
    if key is None:
        raise MalformedAndroidStringsXMLError("Expecting <string> tag to contain a name attribute.")

    pair = _TranslationPair(key=key, value=value)

    return [pair]


def _parse_string_array_tree(node) -> list[_TranslationPair]:
    tag = node.tag.lower()
    if tag != _STRING_ARRAY_TAG:
        raise ValueError(f"Expected tag: {_STRING_ARRAY_TAG} actual tag: {tag}")

    array_name = node.attrib['name']
    translation_pairs = []
    for index, child in enumerate(node):
        child_tag = child.tag.lower()
        if child_tag == _ITEM_TAG:
            key = array_name + _STRING_ARRAY_ITEM_SEPARATOR + str(index)
            value = _extract_inner_content(child)
            pair = _TranslationPair(key=key, value=value)
            translation_pairs.append(pair)
        else:
            logging.warning(f"Unknown child element index={index} child={child} parent={node}")

    return translation_pairs


def _parse_plurals_tree(node) -> list[_TranslationPair]:
    tag = node.tag.lower()
    if tag != _PLURALS_TAG:
        raise ValueError(f"Expected tag: {_PLURALS_TAG} actual tag: {tag}")

    plurals_name = node.attrib['name']
    translation_pairs = []
    for child in node:
        child_tag = child.tag.lower()
        if child_tag == _ITEM_TAG:
            value = _extract_inner_content(child)
            quantity = child.attrib.get('quantity')
            if quantity is None:
                raise MalformedAndroidStringsXMLError(
                    "Expecting <item> tag to contain a quantity to indicate pluralism.")

            key = plurals_name + _PLURALS_ITEM_SEPARATOR + quantity
            pair = _TranslationPair(key=key, value=value)
            translation_pairs.append(pair)
        else:
            logging.warning(f"Unknown child element child={child} parent={node}")

    return translation_pairs


def _extract_inner_content(node) -> str:
    # Convert the entire element to string
    xml_content = etree.tostring(node, encoding='unicode')
    if '/>' in xml_content and '</' not in xml_content:
        return ''
    # Single regex with a capture group to extract the content
    pattern = r'^<(?:string|item)[^>]*>(.*)</(?:string|item)>'

    # Extract the content using the capture group
    match = re.search(pattern, xml_content, re.DOTALL)
    if match:
        return match.group(1)
    else:
        raise MalformedAndroidStringsXMLError("Malformed XML content. Expected content inside <string> tags.")


# Building XML #
def serialize_to_xml(pairs: dict[str, str]) -> str:
    tree = _build_xml_tree(pairs)
    etree.indent(tree, space='    ')
    _bytes = etree.tostring(tree, encoding='utf-8', xml_declaration=True)
    return _bytes.decode('utf-8')


def _build_xml_tree(pairs: dict[str, str]):
    root = etree.Element('resources')
    plurals_and_string_arrays = {}

    for key, value in pairs.items():
        if _PLURALS_ITEM_SEPARATOR in key:
            split = key.split(_PLURALS_ITEM_SEPARATOR)
            plurals_name = split[0]
            quantity = split[1]

            plurals_element = plurals_and_string_arrays.get(plurals_name)
            if plurals_element is None:
                plurals_element = etree.Element('plurals', {'name': plurals_name})
                root.append(plurals_element)
                plurals_and_string_arrays[plurals_name] = plurals_element

            item = etree.Element('item', attrib={'quantity': quantity})
            item.text = value

            plurals_element.append(item)
        elif _STRING_ARRAY_ITEM_SEPARATOR in key:
            split = key.split(_STRING_ARRAY_ITEM_SEPARATOR)
            array_name = split[0]

            array_element = plurals_and_string_arrays.get(array_name)
            if array_element is None:
                array_element = etree.Element('string-array', attrib={'name': array_name})
                root.append(array_element)
                plurals_and_string_arrays[array_name] = array_element

            item = etree.Element('item')
            item.text = value

            array_element.append(item)
        else:
            element = _create_string_element(key, value)
            root.append(element)

    return root


def _create_string_element(key: str, value: str):
    element = etree.Element('string', attrib={'name': key})
    if _is_cdata_section(value.strip()):
        # If the value is a CDATA section, we need to handle it differently
        cdata_value = value.strip()[9:-3]  # Remove <![CDATA[ and ]]>
        element.text = etree.CDATA(cdata_value)
    else:
        element.text = value
    return element


def _is_cdata_section(text: str) -> bool:
    """
    Check if the text is a CDATA section.
    """
    return text.startswith('<![CDATA[') and text.endswith(']]>')
