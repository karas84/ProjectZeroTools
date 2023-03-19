import json

from zerotools.text.message.table import InGameMessageTable
from zerotools.text.message.locale import Locale
from zerotools.text.message.parser import InGameMessageParser
from zerotools.text.message.message import InGameMessage


def _sort_tables(tables):
    return sorted(tables.values(), key=lambda v: v["order"])


def _is_subtable(table):
    return "messages" in table


def _is_message(table):
    return "message" in table and "suffix" in table


def _parse_json_table(json_table, parent: InGameMessageTable, locale: Locale):
    for table in _sort_tables(json_table["messages"]):
        if _is_subtable(table):
            igm_table = InGameMessageTable(number=table["order"], offset=-1, size=0)
            parent.tables.append(igm_table)
            _parse_json_table(table, igm_table, locale)
        elif _is_message(table):
            message = _parse_json_message(table, parent, locale)
            parent.messages.append(message)
        else:
            raise RuntimeError


def _parse_json_message(table, parent: InGameMessageTable, locale: Locale):
    number = table["order"]
    suffix = bytes.fromhex(table["suffix"])
    message = table["message"]
    return InGameMessage.from_message(number, parent, message, locale, suffix=suffix)


def rebuild_language_json(json_path: str, locale: Locale):
    ig_msg_parser = InGameMessageParser(file=None, locale=locale)

    with open(json_path, "rb") as file_h:
        json_tables: dict = json.load(file_h)

    for table in _sort_tables(json_tables):
        if not _is_subtable(table):
            raise RuntimeError

        igm_table = InGameMessageTable(number=table["order"], offset=-1, size=0)
        ig_msg_parser.msg_tables.tables.append(igm_table)

        _parse_json_table(table, igm_table, locale)

    return ig_msg_parser
