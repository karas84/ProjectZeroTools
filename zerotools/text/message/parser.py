import io
import os
import struct

from typing import BinaryIO

from .table import InGameMessageTable
from .locale import Locale
from .message import InGameMessage


class InGameMessageParser:
    def __init__(self, file: "str | bytes | BinaryIO | None", table_names: "list[str] | None" = None, locale=Locale.EN):
        if isinstance(file, str):
            with open(file, "rb") as fh:
                self.file_h = io.BytesIO(fh.read())
        elif isinstance(file, bytes):
            self.file_h = io.BytesIO(file)
        elif isinstance(file, io.IOBase):
            pos = file.tell()
            file.seek(0, os.SEEK_SET)
            self.file_h = io.BytesIO(file.read())
            file.seek(pos, os.SEEK_SET)
        elif file is None:
            self.file_h = None
        else:
            raise ValueError("input must be filename or open file handle")

        self.table_names: "list[str] | None"

        self.file_size = self.file_h.getbuffer().nbytes if self.file_h else 0
        self.locale = locale

        self._boundaries: list[int] = []
        self._byte_address_read = []

        self.msg_tables = self._parse_obj(locale=locale) if self.file_h else InGameMessageTable(0, -1, 0)

        if self.msg_tables is None:
            raise RuntimeError("cannot find message tables")

        if self.file_h is None or (isinstance(table_names, list) and len(table_names) == len(self.msg_tables.tables)):
            self.table_names = table_names
        else:
            num_tables = len(self.msg_tables.tables)
            num_table_digits = len(str(num_tables))
            self.table_names = [f"{i:0{num_table_digits}d}" for i in range(num_tables)]

    def __getitem__(self, item):
        if not self.msg_tables or not self.table_names:
            raise RuntimeError("invalid message parser")

        if isinstance(item, int):
            return self.msg_tables.tables[item]

        table_idx = self.table_names.index(item)
        return self.msg_tables.tables[table_idx]

    @staticmethod
    def _read_dword(f):
        return struct.unpack("<I", f.read(4))[0], f.tell()

    def next_boundary(self, offset):
        return next(b for b in self._boundaries if b > offset)

    def _parse_obj_rec(self, msg_table: InGameMessageTable):
        file_has_table = len(msg_table.tables) > 0

        if file_has_table:
            for sub_table in msg_table.tables:
                self._parse_obj_rec(sub_table)
            return

        if self.file_h is None:
            raise RuntimeError("missing data handle")

        for message in msg_table.messages:
            size = self.next_boundary(message.offset) - message.offset
            addresses = [x for x in range(message.offset, message.offset + message.size)]
            self._byte_address_read.extend(addresses)
            message.parse_text(self.file_h, size)
            message.encode()

    def _find_table_size(self, offset):
        max_offset = self.file_size
        position = -1
        maybe_table = []
        address_read = []

        if not self.file_h:
            raise RuntimeError("missing data handle")

        while max_offset > position:
            address_read.extend([x for x in range(self.file_h.tell(), self.file_h.tell() + 4)])
            if self.file_h.tell() + 4 >= self.file_size:
                return False, 0
            address, position = self._read_dword(self.file_h)
            max_offset = min(address, max_offset)
            if address > self.file_size or max_offset < offset:
                return False, 0
            maybe_table.append(address)
        self._byte_address_read.extend(address_read)
        return maybe_table, max_offset - offset

    def _parse_obj_tables(self, number, offset=0, msg_table: "InGameMessageTable | None" = None, locale=Locale.EN):
        if not self.file_h:
            raise RuntimeError("missing data handle")

        self.file_h.seek(offset, os.SEEK_SET)

        table, tbl_size = self._find_table_size(offset)

        if table is False:
            return

        cur_msg_table = InGameMessageTable(number, offset, tbl_size, msg_table)
        self._boundaries.append(offset)

        if msg_table is not None:
            msg_table.add_table(cur_msg_table)

        for n, offset_start in enumerate(table):
            has_subtable = self._parse_obj_tables(n, offset_start, cur_msg_table, locale) is not None
            if not has_subtable:
                cur_msg_table.add_message(InGameMessage(n, offset_start, cur_msg_table, locale))
                self._boundaries.append(offset_start)

        return cur_msg_table

    def _parse_obj(self, locale=Locale.EN):
        msg_tables = self._parse_obj_tables(number=0, locale=locale)

        if msg_tables is None:
            raise RuntimeError("cannot find message tables")

        self._boundaries.append(self.file_size)
        self._boundaries = list(set(self._boundaries))
        self._boundaries.sort()

        for n, table in enumerate(msg_tables.tables):
            self._parse_obj_rec(table)

        return msg_tables

    def _find_message_containing(self, text: str, msg_table: InGameMessageTable, results: list[InGameMessage]):
        for table in msg_table.tables:
            self._find_message_containing(text, table, results)

        for message in msg_table.messages:
            if text in message.message.lower():
                results.append(message)

    def find_message_containing(self, text: str):
        results: list[InGameMessage] = []
        self._find_message_containing(text.lower(), self.msg_tables, results)
        return results

    def encode(self):
        return self.msg_tables.encode()
