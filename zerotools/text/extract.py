import os

from typing import BinaryIO

from .serializer import LocalizationSerializerFormat
from ..elf.version import ELF_EU, ELF_JP, ELF_US
from .message.locale import Locale, EU_LOCALES
from .message.parser import InGameMessageParser
from .serializer.xmlfile import serialize_xml
from .serializer.jsonfile import serialize_json
from .serializer.filesystem import serialize_fs
from ..elf.tables.igmessage import get_ingame_message_table_names_from_elf
from ..elf.tables.igmessage import get_ingame_message_table_names_from_iso
from ..elf.tables.igmessage import get_ingame_message_table_names_from_txt
from ..zero.reader.pjzreader import PJZReader


def _validate_locale_with_elf(locale, iso_locale, elf_name):
    if not locale and elf_name != ELF_EU:
        return iso_locale
    elif not locale or not (
        (elf_name == ELF_US and locale == Locale.US)
        or (elf_name == ELF_JP and locale == Locale.JP)
        or (elf_name == ELF_EU and locale in EU_LOCALES)
    ):
        raise ValueError("incorrect locale or missing locale for ISO version")
    else:
        return locale


def _extract_fh(
    file_h: BinaryIO,
    out_file_name: str,
    table_names: "list[str] | None",
    locale: Locale,
    serializer_format: LocalizationSerializerFormat,
):
    out_file_name = os.path.splitext(out_file_name)[0]

    ig_msg_parser = InGameMessageParser(file_h, table_names=table_names, locale=locale)

    # serialize into chosen format
    if serializer_format == LocalizationSerializerFormat.FS:
        serialize_fs(ig_msg_parser, out_file_name)

    elif serializer_format == LocalizationSerializerFormat.JSON:
        serialize_json(ig_msg_parser, out_file_name + ".json")

    elif serializer_format == LocalizationSerializerFormat.XML:
        serialize_xml(ig_msg_parser, out_file_name + ".xml")


def extract_iso(iso_path: str, out_folder: str, /, *, serializer_format: LocalizationSerializerFormat, locale: Locale):
    table_names, iso_locale, elf_name = get_ingame_message_table_names_from_iso(iso_path)

    if table_names is None:
        raise RuntimeError("cannot parse ELF file for in-game messages")

    locale = _validate_locale_with_elf(locale, iso_locale, elf_name)

    reader = PJZReader(iso_path)

    # extract in-game text
    in_game_text_file = locale.ig_msg_file_name
    out_file = os.path.join(out_folder, in_game_text_file)
    with reader.open(in_game_text_file) as file_h:
        _extract_fh(file_h, out_file, table_names, locale, serializer_format)

    # extract event text
    for m_event_file in locale.event_file_names:
        with reader.open(m_event_file) as file_h:
            out_file = os.path.join(out_folder, m_event_file)
            _extract_fh(file_h, out_file, table_names, locale, serializer_format)


def extract_file(
    lang_file: str,
    out_file: str,
    /,
    *,
    name_list_src: str,
    locale: Locale,
    serializer_format: LocalizationSerializerFormat,
):
    name_list_src_ext = os.path.splitext(name_list_src)[1].upper()

    if os.path.basename(name_list_src) in (ELF_EU, ELF_JP, ELF_US):
        with open(name_list_src, "rb") as file_h:
            table_names = get_ingame_message_table_names_from_elf(file_h)

        if table_names is None:
            raise RuntimeError("error getting file list from ELF file")

    elif name_list_src_ext == ".ISO":
        table_names, iso_locale, elf_name = get_ingame_message_table_names_from_iso(name_list_src)

        if table_names is None:
            raise RuntimeError("error getting file list from ISO")

        locale = _validate_locale_with_elf(locale, iso_locale, elf_name)

    elif name_list_src_ext == ".TXT":
        table_names = get_ingame_message_table_names_from_txt(name_list_src)

    else:
        table_names = None
        # raise ValueError('wrong file list source')

    with open(lang_file, "rb") as file_h:
        _extract_fh(file_h, out_file, table_names, locale, serializer_format)
