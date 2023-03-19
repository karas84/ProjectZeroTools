from typing import BinaryIO, cast
from pycdlib.pycdlibio import PyCdlibIO

from zerotools.utils.iso import iso_context, check_elf_path
from zerotools.text.message.locale import Locale


def get_ingame_message_table_names_from_elf(elf_fh: "BinaryIO | PyCdlibIO") -> "list[str] | None":
    elf_bin = elf_fh.read()

    try:
        ig_msg_anchor = elf_bin.index(b",IGMSG_SND_TST:52,")
        ig_msg_start = elf_bin.rfind(b"=eIGMSG_GET_FILE0:0,", 0, ig_msg_anchor) + 2
        ig_msg_end = elf_bin.index(b",;", ig_msg_anchor)

        ig_msg_names = elf_bin[ig_msg_start:ig_msg_end]

        ig_msg_names = ig_msg_names.replace(b"\x2C\x5C\x00", b"\x2C").decode("ascii")
        ig_msg_names = ig_msg_names.rstrip(",").split(",")
        ig_msg_names = [name.rsplit(":", 1) for name in ig_msg_names]
        ig_msg_names = sorted([(int(num), name) for name, num in ig_msg_names], key=lambda x: x[0])
    except ValueError:
        return None

    ig_msg_nums, ig_msg_names_str = zip(*ig_msg_names)

    ig_msg_nums = cast(list[int], ig_msg_nums)
    ig_msg_names_str = cast(list[str], ig_msg_names_str)

    if ig_msg_nums != tuple(range(len(ig_msg_names_str))):
        return None

    return list(ig_msg_names_str)


def get_ingame_message_table_names_from_iso(iso_path: str):
    with iso_context(iso_path) as iso:
        elf_path = check_elf_path(iso)

        if not elf_path:
            raise RuntimeError

        locale, elf_name = Locale.from_elf_path(elf_path)

        with iso.open_file_from_iso(iso_path=elf_path) as elf_fh:
            table_names = get_ingame_message_table_names_from_elf(elf_fh)

        return table_names, locale, elf_name


def get_ingame_message_table_names_from_txt(txt_path: str) -> list[str]:
    with open(txt_path, mode="r", encoding="utf-8") as file_h:
        return file_h.read().strip().split("\n")
