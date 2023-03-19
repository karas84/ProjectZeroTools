import os
import struct

from typing import BinaryIO
from pycdlib.pycdlibio import PyCdlibIO

from zerotools.elf.utils import read_file_list_from_file
from zerotools.utils.iso import iso_context, ISO_SECTOR_SIZE, check_path, check_elf_path
from zerotools.zero.names import IMG_BD, IMG_HD
from zerotools.utils.fileio import read_file, copy_file_fh
from zerotools.utils.subfile import SubFile
from zerotools.elf.tables.filename import get_file_names_from_elf


def make_file_entry_list(img_hd_fh: "BinaryIO | PyCdlibIO") -> "list[tuple[int, int]] | None":
    img_hd_bin = read_file(img_hd_fh)

    if len(img_hd_bin) % 8 != 0:
        return None

    num_int32 = len(img_hd_bin) // 4
    file_data = struct.unpack(f"<{num_int32}I", img_hd_bin)

    file_entry_list = [(file_data[i] * ISO_SECTOR_SIZE, file_data[i + 1]) for i in range(0, len(file_data), 2)]

    return file_entry_list


def extract_img_bd(
    img_bd_fh: "BinaryIO | PyCdlibIO", file_list: list[str], file_entry_list: list[tuple[int, int]], out_folder: str
):
    pos = img_bd_fh.tell()
    img_bd_fh.seek(0, os.SEEK_SET)

    for name, (offset, bytes_to_read) in zip(file_list, file_entry_list):
        src_fh = SubFile(img_bd_fh, offset=offset, size=bytes_to_read)

        out_file = os.path.join(out_folder, name)

        with open(out_file, "wb") as out_fh:
            copy_file_fh(src_fh, out_fh)

    img_bd_fh.seek(pos, os.SEEK_SET)


def extract_iso(iso_path: str, out_folder: str):
    with iso_context(iso_path) as iso:
        elf_path = check_elf_path(iso)
        img_hd_path = check_path(iso, f"/{IMG_HD};1")
        img_bd_path = check_path(iso, f"/{IMG_BD};1")

        if not elf_path or not img_hd_path or not img_bd_path:
            raise RuntimeError("cannot find elf, img_hd or img_bd in iso")

        with iso.open_file_from_iso(iso_path=elf_path) as elf_fh:
            file_list = get_file_names_from_elf(elf_fh)

            if file_list is None:
                raise RuntimeError("cannot get file names from elf")

        with iso.open_file_from_iso(iso_path=img_hd_path) as img_hd_fh:
            file_entry_list = make_file_entry_list(img_hd_fh)

            if file_entry_list is None:
                raise RuntimeError("cannot find file entry list")

        if len(file_list) != len(file_entry_list):
            raise RuntimeError("invalid file entry list")

        with iso.open_file_from_iso(iso_path=img_bd_path) as img_bd_fh:
            os.makedirs(out_folder, exist_ok=True)
            extract_img_bd(img_bd_fh, file_list, file_entry_list, out_folder)


def extract_fs(img_bd_folder: str, file_list_path: str, out_folder: str):
    img_bd_path = os.path.join(img_bd_folder, IMG_BD)
    img_hd_path = os.path.join(img_bd_folder, IMG_HD)

    if not os.path.isfile(img_bd_path) or not os.path.isfile(img_hd_path):
        raise RuntimeError("cannot find img_bd or img_hd in filesystem")

    file_list = read_file_list_from_file(file_list_path)

    with open(img_hd_path, "rb") as img_hd_fh:
        file_entry_list = make_file_entry_list(img_hd_fh)

        if file_entry_list is None:
            raise RuntimeError("cannot find file entry list")

    if len(file_list) != len(file_entry_list):
        raise RuntimeError("invalid file entry list")

    with open(img_bd_path, "rb") as img_bd_fh:
        os.makedirs(out_folder, exist_ok=True)
        extract_img_bd(img_bd_fh, file_list, file_entry_list, out_folder)
