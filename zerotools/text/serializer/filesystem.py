import os

from zerotools.text.serializer import TABLE_NAME_MIN_DIGIT
from zerotools.text.message.table import InGameMessageTable
from zerotools.text.message.parser import InGameMessageParser


def _serialize_table_fs(ig_msg_table: InGameMessageTable, out_folder: str):
    if ig_msg_table.tables:
        num_table_digits = max(TABLE_NAME_MIN_DIGIT, len(str(len(ig_msg_table.tables))))
        hidden_info_file = os.path.join(out_folder, ".info")
        os.makedirs(out_folder, exist_ok=True)
        with open(hidden_info_file, mode="w", encoding="utf-8") as info_h:
            for i, table in enumerate(ig_msg_table.tables):
                name = f"{i:0{num_table_digits}d}"
                table_folder = os.path.join(out_folder, name)
                _serialize_table_fs(table, table_folder)
                info_h.write(f"{i},{name}\n")

    else:
        os.makedirs(out_folder, exist_ok=True)
        hidden_info_file = os.path.join(out_folder, ".info")
        os.makedirs(out_folder, exist_ok=True)
        with open(hidden_info_file, mode="w", encoding="utf-8") as info_h:
            num_message_digits = max(TABLE_NAME_MIN_DIGIT, len(str(len(ig_msg_table.messages))))
            for i, message in enumerate(ig_msg_table.messages):
                name = f"{i:0{num_message_digits}d}"
                message_file = os.path.join(out_folder, f"{name}.TXT")
                with open(message_file, mode="w", encoding="utf-8") as file_h:
                    file_h.write(message.message)
                info_h.write(f"{name},{message.suffix.hex()}\n")


def serialize_fs(ig_msg_parser: InGameMessageParser, out_folder: str):
    if not ig_msg_parser.table_names:
        raise RuntimeError("invalid ig_msg_parser (no table names)")

    os.makedirs(out_folder, exist_ok=True)
    hidden_info_file = os.path.join(out_folder, ".info")
    with open(hidden_info_file, mode="w", encoding="utf-8") as info_h:
        for i, (name, table) in enumerate(zip(ig_msg_parser.table_names, ig_msg_parser.msg_tables.tables)):
            table_folder = os.path.join(out_folder, name)
            _serialize_table_fs(table, table_folder)
            info_h.write(f"{i},{name}\n")
