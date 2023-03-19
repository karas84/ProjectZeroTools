from enum import Enum
from typing import Tuple

from ...zero.names import IG_MSG, IG_MSG_E, IG_MSG_F, IG_MSG_G, IG_MSG_S, IG_MSG_I
from ...zero.names import M_EVENTS, M_EVENTS_E, M_EVENTS_F, M_EVENTS_G, M_EVENTS_S, M_EVENTS_I
from ...elf.version import ELF_EU, ELF_JP, ELF_US


class Locale(Enum):
    US = "US"
    JP = "JP"
    EN = "EN"
    FR = "FR"
    GE = "GE"
    SP = "SP"
    IT = "IT"

    @classmethod
    def from_string(cls, lang_str: str) -> "Locale":
        try:
            return next(locale for locale in cls if locale.name == lang_str.upper())
        except StopIteration:
            raise ValueError(f"{lang_str} is not a valid locale")

    @classmethod
    def from_elf_path(cls, elf_path: str) -> Tuple["Locale", str]:
        elf_name = elf_path[: elf_path.rindex(";", 1)].lstrip("/")

        if elf_name == ELF_EU:
            return Locale.EN, ELF_EU

        elif elf_name == ELF_JP:
            return Locale.JP, ELF_JP

        elif elf_name == ELF_US:
            return Locale.US, ELF_US

        else:
            raise ValueError(f"{elf_path} is not a valid ELF")

    @property
    def event_file_names(self):
        if self in (Locale.US, Locale.JP):
            return M_EVENTS

        elif self == Locale.EN:
            return M_EVENTS_E

        elif self == Locale.FR:
            return M_EVENTS_F

        elif self == Locale.GE:
            return M_EVENTS_G

        elif self == Locale.SP:
            return M_EVENTS_S

        elif self == Locale.IT:
            return M_EVENTS_I

        else:
            raise RuntimeError("cannot convert to file name")

    @property
    def ig_msg_file_name(self):
        if self in (Locale.US, Locale.JP):
            return IG_MSG

        elif self == Locale.EN:
            return IG_MSG_E

        elif self == Locale.FR:
            return IG_MSG_F

        elif self == Locale.GE:
            return IG_MSG_G

        elif self == Locale.SP:
            return IG_MSG_S

        elif self == Locale.IT:
            return IG_MSG_I

        else:
            raise RuntimeError("cannot convert to file name")


LOCALES = [locale.name for locale in Locale]

EU_LOCALES = Locale.EN, Locale.FR, Locale.GE, Locale.SP, Locale.IT
