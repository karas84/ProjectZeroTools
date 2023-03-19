import os
import re

from xml.dom import minidom
from xml.etree import ElementTree

from zerotools.text.serializer import TABLE_NAME_MIN_DIGIT
from zerotools.text.message.table import InGameMessageTable
from zerotools.text.message.parser import InGameMessageParser


def _serialize_table_xml(ig_msg_table: InGameMessageTable, xml_messages):
    if ig_msg_table.tables:
        num_table_digits = max(TABLE_NAME_MIN_DIGIT, len(str(len(ig_msg_table.tables))))
        for i, table in enumerate(ig_msg_table.tables):
            xml_submessages = ElementTree.SubElement(xml_messages, "messages")
            name = f"{i:0{num_table_digits}d}"
            xml_submessages.set("order", f"{i}")
            xml_submessages.set("name", name)
            _serialize_table_xml(table, xml_submessages)

    else:
        num_message_digits = max(TABLE_NAME_MIN_DIGIT, len(str(len(ig_msg_table.messages))))
        for i, message in enumerate(ig_msg_table.messages):
            xml_message = ElementTree.SubElement(xml_messages, "message")
            name = f"{i:0{num_message_digits}d}"
            xml_message.set("order", f"{i}")
            xml_message.set("name", name)
            xml_message.set("suffix", message.suffix.hex())
            xml_message.text = message.message.replace("\n", "\\n")


def serialize_xml(ig_msg_parser: InGameMessageParser, xml_file: str):
    if not ig_msg_parser.table_names:
        raise RuntimeError("invalid ig_msg_parser (no table names)")

    os.makedirs(os.path.dirname(xml_file), exist_ok=True)

    xml_root = ElementTree.Element("localization")
    with open(xml_file, mode="w", encoding="utf-8") as xml_fh:
        for i, (name, table) in enumerate(zip(ig_msg_parser.table_names, ig_msg_parser.msg_tables.tables)):
            xml_messages = ElementTree.SubElement(xml_root, "messages")
            xml_messages.set("order", f"{i}")
            xml_messages.set("name", name)
            _serialize_table_xml(table, xml_messages)

        xml_str = minidom.parseString(
            ElementTree.tostring(xml_root, method="xml", short_empty_elements=False)
        ).toprettyxml(indent="  ")
        # fix short_empty_elements=False not always working properly ...
        xml_str = re.sub(r"^(\s*)<message ([^/]*)/>(\s*)$", r"\1<message \2></message>\3", xml_str, flags=re.MULTILINE)
        xml_fh.write(xml_str)
