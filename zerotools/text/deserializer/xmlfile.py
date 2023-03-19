import xml.etree.ElementTree as ElementTree

from typing import cast

from zerotools.text.message.table import InGameMessageTable
from zerotools.text.message.locale import Locale
from zerotools.text.message.parser import InGameMessageParser
from zerotools.text.message.message import InGameMessage


def _is_valid_suffix(text: str):
    if not isinstance(text, str):
        return False

    if text == "":
        return True

    try:
        int(text, 16)
        return True
    except ValueError:
        return False


def _is_subtable(element: ElementTree.Element):
    return (
        element.tag == "messages"
        and "order" in element.attrib
        and element.get("order", "").isnumeric()
        and "name" in element.attrib
        and cast(str, element.get("name"))
    )


def _sort_tables(children: list[ElementTree.Element]):
    return sorted(children, key=lambda c: int(c.get("order", "")))


def _is_message(element: ElementTree.Element):
    return (
        element.tag == "message"
        and "order" in element.attrib
        and element.get("order", "").isnumeric()
        and "name" in element.attrib
        and cast(str, element.get("name"))
        and "suffix" in element.attrib
        and _is_valid_suffix(element.get("suffix", ""))
    )


def _parse_xml_table(xml_table: ElementTree.Element, parent: InGameMessageTable, locale: Locale):
    children = list(xml_table)

    if not all(_is_subtable(e) or _is_message(e) for e in children):
        raise RuntimeError

    children = _sort_tables(children)

    for table in children:
        if _is_subtable(table):
            order = int(cast(str, xml_table.get("order")))
            igm_table = InGameMessageTable(number=order, offset=-1, size=0)
            parent.tables.append(igm_table)
            _parse_xml_table(table, igm_table, locale)
        elif _is_message(table):
            message = _parse_xml_message(table, parent, locale)
            parent.messages.append(message)
        else:
            raise RuntimeError


def _parse_xml_message(message: ElementTree.Element, parent: InGameMessageTable, locale: Locale) -> InGameMessage:
    number = int(cast(str, message.get("order")))
    suffix = bytes.fromhex(cast(str, message.get("suffix")))
    message_text = (message.text or "").replace("\\n", "\n")
    return InGameMessage.from_message(number, parent, message_text, locale, suffix=suffix)


def rebuild_language_xml(xml_path: str, locale: Locale) -> InGameMessageParser:
    ig_msg_parser = InGameMessageParser(file=None, locale=locale)

    tree = ElementTree.parse(xml_path)
    xml_root = tree.getroot()

    if xml_root.tag != "localization":
        raise RuntimeError

    children = list(xml_root)

    if not all(_is_subtable(e) for e in children):
        raise RuntimeError

    children = _sort_tables(children)
    ig_msg_parser.table_names = [child.get("name", "") for child in children]

    for table in children:
        if table.tag != "messages":
            raise RuntimeError

        order = int(table.get("order", ""))
        igm_table = InGameMessageTable(number=order, offset=-1, size=0)
        ig_msg_parser.msg_tables.tables.append(igm_table)

        _parse_xml_table(table, igm_table, locale)

    return ig_msg_parser
