import io
import os
import struct

from .message import InGameMessage
from .abstract import Serializable


class InGameMessageTable(Serializable):
    def __init__(
        self,
        number: int,
        offset: int,
        size: int,
        parent: "InGameMessageTable | None" = None,
        tables: "list[InGameMessageTable] | None" = None,
        messages: "list[InGameMessage] | None" = None,
    ):
        self.number = number
        self.offset = offset
        self.size = size
        self._parent = parent
        self.tables = tables if tables is not None else list()
        self.messages = messages if messages is not None else list()

    def add_table(self, table: "InGameMessageTable"):
        if self.messages:
            raise RuntimeError("cannot add table while messages exist")

        self.tables.append(table)

    def add_message(self, message: "InGameMessage"):
        if self.tables:
            raise RuntimeError("cannot add message while tables exists")

        self.messages.append(message)

    def __str__(self):
        if self.tables:
            return f'{len(self.tables)} Table{"s" if len(self.tables) != 1 else ""}'
        else:
            return f'{len(self.messages)} Message{"s" if len(self.messages) != 1 else ""}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def __getitem__(self, item):
        if self.tables:
            return self.tables[item]

        return self.messages[item]

    def has_overlap(self, other):
        r1 = range(self.offset, self.offset + self.size)
        r2 = range(other.offset, other.offset + other.size)
        return len(list(set(r1) & set(r2))) != 0

    def encode(self, offset=0):
        table = self.tables if self.tables else self.messages

        encoded = io.BytesIO()
        offsets = list()

        encoded.write(bytearray(len(table * 4)))
        offset += len(table) * 4

        for entry in table:
            offsets.append(offset)
            enc = entry.encode(offset)
            encoded.write(enc)
            offset += len(enc)

        encoded.seek(0, os.SEEK_SET)

        table_bin = struct.pack(f"<{len(offsets)}I", *offsets)
        encoded.write(table_bin)

        encoded.seek(0, os.SEEK_SET)

        return encoded.read()
