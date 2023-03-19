import os

from io import BytesIO
from typing import BinaryIO, cast

from .names import MessageNames
from .serializer import LocalizationSerializerFormat
from ..utils.iso import iso_context
from ..zero.names import IMG_BD
from .message.locale import Locale
from .message.parser import InGameMessageParser
from ..imgbd.rebuild import rebuild_img_bd_iso_inplace
from .deserializer.xmlfile import rebuild_language_xml
from .deserializer.jsonfile import rebuild_language_json
from ..zero.reader.pjzreader import PJZReader
from .deserializer.filesystem import rebuild_language_fs


def _rebuild_file(
    lang_path: str, locale: Locale, serializer_format: LocalizationSerializerFormat
) -> InGameMessageParser:
    if serializer_format == LocalizationSerializerFormat.FS:
        return rebuild_language_fs(lang_path, locale)

    elif serializer_format == LocalizationSerializerFormat.JSON:
        return rebuild_language_json(lang_path, locale)

    elif serializer_format == LocalizationSerializerFormat.XML:
        return rebuild_language_xml(lang_path, locale)

    else:
        raise ValueError("wrong serializer format")


def rebuild_iso(
    lang_path: str,
    iso_path: str,
    /,
    *,
    locale: Locale,
    serializer_format: LocalizationSerializerFormat,
    event_type: MessageNames,
):
    ig_msg_parser = _rebuild_file(lang_path, locale, serializer_format)

    new_lang_bytes = ig_msg_parser.encode()
    new_lang_size = len(new_lang_bytes)

    file_name = event_type.to_locale_file_name(locale)

    reader = PJZReader(iso_path)
    entry = reader.find_entry(file_name)

    if entry is None:
        raise RuntimeError(f"cannot find entry {file_name}")

    if new_lang_size <= entry.max_size:
        with iso_context(iso_path) as iso:
            img_bd_offset = iso.get_record(iso_path=f"/{IMG_BD};1").fp_offset

        zero_padding = entry.max_size - new_lang_size

        with open(iso_path, "rb+") as iso_fh:
            iso_fh.seek(img_bd_offset + entry.offset, os.SEEK_SET)
            iso_fh.write(new_lang_bytes)
            iso_fh.write(bytearray(zero_padding))
    else:
        replace_entries = {
            file_name: cast(BinaryIO, BytesIO(new_lang_bytes)),
        }

        rebuild_img_bd_iso_inplace(iso_path, replace_entries)


def rebuild_file(
    lang_path: str, out_language_path: str, /, *, locale: Locale, serializer_format: LocalizationSerializerFormat
):
    ig_msg_parser = _rebuild_file(lang_path, locale, serializer_format)

    os.makedirs(os.path.dirname(out_language_path), exist_ok=True)

    with open(out_language_path, "wb") as file_h:
        file_h.write(ig_msg_parser.encode())
