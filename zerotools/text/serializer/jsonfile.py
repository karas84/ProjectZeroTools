import os
import json

from collections import OrderedDict


from zerotools.text.message.parser import InGameMessageParser
from zerotools.text.message.table import InGameMessageTable
from zerotools.text.serializer import TABLE_NAME_MIN_DIGIT


def _serialize_table_json(ig_msg_table: InGameMessageTable):
    json_tables = OrderedDict()

    if ig_msg_table.tables:
        num_table_digits = max(TABLE_NAME_MIN_DIGIT, len(str(len(ig_msg_table.tables))))
        for i, table in enumerate(ig_msg_table.tables):
            name = f"{i:0{num_table_digits}d}"
            json_table = _serialize_table_json(table)
            json_tables[name] = {"order": i, "messages": json_table}

    else:
        num_message_digits = max(TABLE_NAME_MIN_DIGIT, len(str(len(ig_msg_table.messages))))
        for i, message in enumerate(ig_msg_table.messages):
            name = f"{i:0{num_message_digits}d}"
            json_tables[name] = {
                "order": i,
                "message": message.message,
                "suffix": message.suffix.hex(),
            }

    return json_tables


def serialize_json(ig_msg_parser: InGameMessageParser, out_file: str):
    if not ig_msg_parser.table_names:
        raise RuntimeError("invalid ig_msg_parser (no table names)")

    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    json_data = OrderedDict()
    with open(out_file, mode="w", encoding="utf-8") as json_fh:
        for i, (name, table) in enumerate(zip(ig_msg_parser.table_names, ig_msg_parser.msg_tables.tables)):
            json_table = _serialize_table_json(table)
            json_data[name] = {"order": i, "messages": json_table}

        json.dump(json_data, json_fh, indent=2, ensure_ascii=False)
