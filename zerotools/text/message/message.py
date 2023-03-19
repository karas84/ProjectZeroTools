import io
import os
import re

from typing import BinaryIO, TYPE_CHECKING, cast

from .locale import Locale, EU_LOCALES
from ..tables import table_jp, table_eu, COLOR, NEWLINE, LASTCH
from .abstract import Serializable
from ..tables.american import table_us


if TYPE_CHECKING:
    from .table import InGameMessageTable


class InGameMessage(Serializable):
    def __init__(self, number: int, offset: int, parent: "InGameMessageTable | None" = None, locale=Locale.EN):
        self.number: int = number
        self.offset: int = offset
        self._parent: "InGameMessageTable | None" = parent
        self.size: int = 0
        self.message: str = ""
        self.suffix: bytes = b""
        self.data: bytes = b""
        self.locale = locale

    @classmethod
    def from_message(
        cls,
        number: int,
        parent: "InGameMessageTable",
        message: str,
        locale: Locale,
        offset=-1,
        suffix=b"\xff",
        encode=False,
    ):
        msg = cls(number, offset, parent, locale)
        msg.message = message
        msg.suffix = suffix
        if encode:
            msg.encode()
        return msg

    @classmethod
    def from_data(cls, number, parent, data: bytes, locale: Locale, offset=-1):
        msg = cls(number, offset, parent, locale)
        msg._parse_data(data)
        return msg

    @staticmethod
    def _separate_suffix(data: bytes) -> tuple[bytes, bytes]:
        match = re.match(b"^(.*?)(\xFA?\xFF*)$", data, re.DOTALL)
        assert match is not None
        data, suffix = match.groups()
        return data, suffix

    def parse_text(self, file_h: BinaryIO, size: int):
        file_h.seek(self.offset)
        data = file_h.read(size)
        return self._parse_data(data)

    def _parse_data(self, data: bytes):
        self.size = len(data)
        # data_hex_str = " ".join(f"{x:02X}" for x in data)
        self.data, self.suffix = self._separate_suffix(data)

        text_bin = self.data

        font_table = table_eu
        if self.locale == Locale.JP:
            font_table = table_jp
        elif self.locale == Locale.US:
            font_table = table_us

        idx = 0
        while idx < len(text_bin):
            x = text_bin[idx]

            if x == COLOR:
                idx_left = len(text_bin) - 1 - idx
                if idx_left >= 3:
                    self.message += "{Color#%02X%02X%02X}" % (text_bin[idx + 1], text_bin[idx + 2], text_bin[idx + 3])
                    idx += 3
                else:
                    self.message += "{Color}"

            elif x == NEWLINE:
                self.message += "\n"

            elif self.locale not in EU_LOCALES and x in font_table:
                table = font_table[x]
                idx += 1
                self.message += table[text_bin[idx]]

            elif x <= LASTCH:
                self.message += font_table["default"][x]

            else:
                self.message += f"{{0x{x:02X}}}"

            idx += 1

    @staticmethod
    def _encode_color(color_str):
        return re.sub(
            r"{Color#([A-F0-9]{2})([A-F0-9]{2})([A-F0-9]{2})}",
            f"{{0x{COLOR:02X}}}{{0x\\1}}{{0x\\2}}{{0x\\3}}",
            color_str,
        )

    def encode(self, offset=0):
        message = (
            self._encode_color(self.message)
            .replace("{Color}", f"{{0x{COLOR:02X}}}")
            .replace("\n", f"{{0x{NEWLINE:02X}}}")
        )

        encoded = io.BytesIO()

        char_table = table_eu
        if self.locale == Locale.JP:
            char_table = table_jp
        elif self.locale == Locale.US:
            char_table = table_us

        characters = re.findall(r"({0x[A-F0-9]{2}}|{.*?}|.)", message)
        for ch in characters:
            enc = None
            if len(ch) != 6:
                for name, table in char_table.items():
                    if ch in table:
                        enc = table.index(ch).to_bytes(1, "little")
                    if enc is not None and name != "default":
                        name = cast(int, name)
                        enc = name.to_bytes(1, "little") + enc
                    if enc is not None:
                        break
            else:
                enc = bytes.fromhex(ch[3:5])

            if enc is None:
                raise RuntimeError(f"unable to find encoding in language table for character {ch}")

            encoded.write(enc)

        encoded.seek(0, os.SEEK_SET)
        self.data = encoded.read()
        self.size = len(self.data) + len(self.suffix)

        return self.data + self.suffix

    def __str__(self):
        suffix_hex = "".join(f"{x:02X}" for x in self.suffix)
        return f'"{self.message}" ({suffix_hex})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, InGameMessage):
            return self.offset == other.offset and self.size == other.size
        else:
            return id(self) == id(other)

    def has_overlap(self, other):
        r1 = range(self.offset, self.offset + self.size)
        r2 = range(other.offset, other.offset + other.size)
        return len(list(set(r1) & set(r2))) != 0
