import os

from zerotools.text.message.table import InGameMessageTable
from zerotools.text.message.locale import Locale
from zerotools.text.message.parser import InGameMessageParser
from zerotools.text.message.message import InGameMessage


def _parse_table_info(info_path: str):
    with open(info_path, mode="r", encoding="utf-8") as file_h:
        lines = file_h.read().strip().split("\n")
        lines = [line.split(",") for line in lines]

    if not all(len(line) == 2 and line[0].isnumeric() for line in lines):
        raise RuntimeError

    if sorted(int(order) for order, _ in lines) != list(range(len(lines))):
        raise RuntimeError

    return sorted(lines, key=lambda x: int(x[0]))


def _is_subtable(folder_path: str):
    files = _list_files(folder_path)
    folders = _list_folders(folder_path)

    if ".info" not in files:
        raise RuntimeError

    info_file = os.path.join(folder_path, ".info")
    if len(files) != 1 or len(folders) == 0:
        return False

    info = _parse_table_info(info_file)
    orders, folders = zip(*info)

    if list(map(int, orders)) != list(range(len(orders))):
        return

    return all(os.path.isdir(os.path.join(folder_path, folder)) for folder in folders)


def _sort_tables(children: list[str]):
    return sorted(children, key=lambda x: int(x))


def _is_message_list(folder_path: str):
    files = _list_files(folder_path)
    folders = _list_folders(folder_path)

    if ".info" not in files:
        raise RuntimeError

    files.remove(".info")

    info_file = os.path.join(folder_path, ".info")

    info = _parse_table_info(info_file)
    file_names, suffixes = zip(*info)
    file_names = [f"{name}.TXT" for name in file_names]

    if (
        len(folders) != 0
        or len(files) != len(file_names)
        or not all(os.path.isfile(os.path.join(folder_path, f)) for f in file_names)
    ):
        return False

    return True


def _parse_fs_table(folder_path: str, parent: InGameMessageTable, locale: Locale):
    info_file = os.path.join(folder_path, ".info")
    info = _parse_table_info(info_file)

    if _is_subtable(folder_path):
        for order, table in info:
            table = os.path.join(folder_path, table)
            igm_table = InGameMessageTable(number=int(order), offset=-1, size=0)
            parent.tables.append(igm_table)
            _parse_fs_table(table, igm_table, locale)
    elif _is_message_list(folder_path):
        for file_name, suffix in info:
            order = int(os.path.splitext(file_name)[0])
            file_name = os.path.join(folder_path, f"{file_name}.TXT")
            message = _parse_fs_message(file_name, order, suffix, parent, locale)
            parent.messages.append(message)
    else:
        raise RuntimeError


def _parse_fs_message(file_name: str, number: int, suffix: str, parent: InGameMessageTable, locale: Locale):
    with open(file_name, mode="r", encoding="utf-8") as file_h:
        suffix_bytes = bytes.fromhex(suffix)
        message = file_h.read()
        return InGameMessage.from_message(number, parent, message, locale, suffix=suffix_bytes)


def _list_folders(folder_path: str):
    return next(os.walk(folder_path))[1]


def _list_files(folder_path: str):
    return next(os.walk(folder_path))[2]


def rebuild_language_fs(folder_path: str, locale: Locale):
    ig_msg_parser = InGameMessageParser(file=None, locale=locale)

    info_file = os.path.join(folder_path, ".info")
    if not os.path.isfile(info_file):
        raise RuntimeError

    if not _is_subtable(folder_path):
        raise RuntimeError

    info = _parse_table_info(info_file)
    orders, tables = zip(*info)

    ig_msg_parser.table_names = [table for table in tables]

    for order, table in zip(orders, tables):
        order = int(order)
        table = os.path.join(folder_path, table)
        igm_table = InGameMessageTable(number=order, offset=-1, size=0)
        ig_msg_parser.msg_tables.tables.append(igm_table)

        _parse_fs_table(table, igm_table, locale)

    return ig_msg_parser
