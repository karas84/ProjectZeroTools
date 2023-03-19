import os
import math
import struct
import itertools

from typing import List, BinaryIO

from zerotools.elf.utils import read_file_list_from_file
from zerotools.utils.iso import iso_context, ISO_SECTOR_SIZE, check_path, check_elf_path
from zerotools.zero.names import IMG_HD, IMG_BD
from zerotools.elf.tables.filename import get_file_names_from_elf
from zerotools.zero.reader.pjzreader import PJZReader


ALIGN_VALUES = 16, 8, 4, 2, 1
ALIGN_DEFAULT = ALIGN_VALUES[0]

READ_BLOCK_SIZE = 16 * 1024


def copy_file_h(src_h: BinaryIO, dst_h: BinaryIO):
    data = 1
    while data:
        data = src_h.read(READ_BLOCK_SIZE)
        dst_h.write(data)


def zero_pad_file_h(file_h: BinaryIO, padding: int = 0):
    while padding > 0:
        padding_to_write = min(READ_BLOCK_SIZE, padding)
        file_h.write(bytearray(padding_to_write))
        padding -= padding_to_write


def check_img_bd_folder_files(img_bd_folder: str, file_list: List[str]):
    files_in_folder = next(os.walk(img_bd_folder))[-1]
    return set(file_list).issubset(files_in_folder)


def recalculate_img_bin_offsets(all_sizes, align=16):
    offsets = [0]
    for size in all_sizes:
        current_offset = offsets[-1]
        next_offset = current_offset + int(math.ceil(size / align / ISO_SECTOR_SIZE)) * align
        offsets.append(next_offset)

    offset, img_bd_size = offsets[:-1], offsets[-1] * ISO_SECTOR_SIZE

    return offset, img_bd_size


def rebuild_img_bd_iso(img_bd_folder: str, iso_path: str):
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

        if not check_img_bd_folder_files(img_bd_folder, file_list):
            raise RuntimeError("cannot find all necessary files in img_bd folder")

        new_file_list = [os.path.join(img_bd_folder, f) for f in file_list]

        file_size_list = [os.stat(f).st_size for f in new_file_list]

        max_img_bd_size = iso.get_record(iso_path=img_bd_path).get_data_length()

        found = False
        offsets = [-1]
        img_bd_size = -1
        align_values = list(ALIGN_VALUES)
        align_value = align_values[0]
        while not found and align_value > 0:
            align_value = align_values.pop(0)
            offsets, img_bd_size = recalculate_img_bin_offsets(file_size_list, align=align_value)
            found = img_bd_size <= max_img_bd_size

        if not found:
            raise RuntimeError("cannot find align value to rebuild img_bd")

        img_hd_iso_offset = iso.get_record(iso_path=img_hd_path).fp_offset
        img_bd_iso_offset = iso.get_record(iso_path=img_bd_path).fp_offset

    # generate and write the new IMG_HD.BIN into ISO
    with open(iso_path, "rb+") as iso_fh:
        img_hd_bin = struct.pack(f"<{len(offsets) * 2}I", *list(itertools.chain(*zip(offsets, file_size_list))))

        iso_fh.seek(img_hd_iso_offset, os.SEEK_SET)
        iso_fh.write(img_hd_bin)

    # generate and write the new IMG_BD.BIN into ISO
    with open(iso_path, "rb+") as iso_fh:
        for n, (file_name, offset, size) in enumerate(zip(new_file_list, offsets, file_size_list)):
            # compute offset for current entry and padding value to zero out up to the next entry
            current_offset = offset * ISO_SECTOR_SIZE
            next_offset = offsets[n + 1] * ISO_SECTOR_SIZE if len(offsets) > n + 1 else img_bd_size
            zero_padding = next_offset - (current_offset + size)

            # write current entry
            iso_fh.seek(img_bd_iso_offset + current_offset, os.SEEK_SET)
            with open(file_name, "rb") as file_h:
                copy_file_h(file_h, iso_fh)

            # fill with zeros up to the next entry
            zero_pad_file_h(iso_fh, zero_padding)


def rebuild_img_bd_fs(img_bd_folder: str, file_list_path: str, out_folder: str, align: int = ALIGN_DEFAULT):
    if align not in ALIGN_VALUES:
        raise ValueError

    file_list = read_file_list_from_file(file_list_path)

    if not check_img_bd_folder_files(img_bd_folder, file_list):
        raise RuntimeError("cannot find all necessary files in img_bd folder")

    new_file_list = [os.path.join(img_bd_folder, f) for f in file_list]

    file_size_list = [os.stat(f).st_size for f in new_file_list]

    offsets, img_bd_size = recalculate_img_bin_offsets(file_size_list, align=align)

    os.makedirs(out_folder, exist_ok=True)

    # generate and write the new IMG_HD.BIN into ISO
    img_hd_bin_out = os.path.join(out_folder, IMG_HD)
    with open(img_hd_bin_out, "wb") as img_hd_fh:
        img_hd_bin = struct.pack(f"<{len(offsets) * 2}I", *list(itertools.chain(*zip(offsets, file_size_list))))
        img_hd_fh.write(img_hd_bin)

    # generate and write the new IMG_BD.BIN into ISO
    img_bd_bin_out = os.path.join(out_folder, IMG_BD)
    with open(img_bd_bin_out, "wb") as img_bd_fh:
        for n, (file_name, offset, size) in enumerate(zip(new_file_list, offsets, file_size_list)):
            # compute offset for current entry and padding value to zero out up to the next entry
            current_offset = offset * ISO_SECTOR_SIZE
            next_offset = offsets[n + 1] * ISO_SECTOR_SIZE if len(offsets) > n + 1 else img_bd_size
            zero_padding = next_offset - (current_offset + size)

            # write current entry
            with open(file_name, "rb") as file_h:
                copy_file_h(file_h, img_bd_fh)

            # fill with zeros up to the next entry
            zero_pad_file_h(img_bd_fh, zero_padding)


def rebuild_img_bd_iso_inplace(iso_path: str, replace_entries: dict[str, BinaryIO]):
    if not replace_entries:
        raise RuntimeError("no entry to replace")

    reader = PJZReader(iso_path)

    for entry_name in replace_entries:
        if not reader.find_entry(entry_name):
            raise RuntimeError(f"{entry_name} does not exist in {IMG_BD}")

    with iso_context(iso_path) as iso:
        elf_path = check_elf_path(iso)
        img_hd_path = check_path(iso, f"/{IMG_HD};1")
        img_bd_path = check_path(iso, f"/{IMG_BD};1")

        if not elf_path or not img_hd_path or not img_bd_path:
            raise RuntimeError("cannot find elf, img_hd or img_bd in iso")

        with iso.open_file_from_iso(iso_path=elf_path) as elf_fh:
            file_list = get_file_names_from_elf(elf_fh)

        if file_list is None:
            raise RuntimeError("cannot read file list from elf")

        file_size_list = list()
        for file_name in file_list:
            if file_name not in replace_entries:
                entry = reader.find_entry(file_name)
                if entry is None:
                    raise RuntimeError(f"cannot find entry {file_name}")
                size = entry.size
            else:
                file_h = replace_entries[file_name]
                size = file_h.seek(0, os.SEEK_END)
                file_h.seek(0, os.SEEK_SET)

            file_size_list.append(size)

        max_img_bd_size = iso.get_record(iso_path=img_bd_path).get_data_length()

        found = False
        offsets = [-1]
        img_bd_size = -1
        align_values = list(ALIGN_VALUES)
        align_value = align_values[0]
        while not found and align_value > 0:
            align_value = align_values.pop(0)
            offsets, img_bd_size = recalculate_img_bin_offsets(file_size_list, align=align_value)
            found = img_bd_size <= max_img_bd_size

        if not found:
            raise RuntimeError("cannot find align value to rebuild img_bd")

        img_hd_iso_offset = iso.get_record(iso_path=img_hd_path).fp_offset
        img_bd_iso_offset = iso.get_record(iso_path=img_bd_path).fp_offset

    # generate and write the new IMG_HD.BIN into ISO
    with open(iso_path, "rb+") as iso_fh:
        img_hd_bin = struct.pack(f"<{len(offsets) * 2}I", *list(itertools.chain(*zip(offsets, file_size_list))))

        iso_fh.seek(img_hd_iso_offset, os.SEEK_SET)
        iso_fh.write(img_hd_bin)

    # generate and write the new IMG_BD.BIN into ISO
    with open(iso_path, "rb+") as iso_fh:
        for n, (file_name, offset, size) in enumerate(zip(file_list, offsets, file_size_list)):
            # compute offset for current entry and padding value to zero out up to the next entry
            current_offset = offset * ISO_SECTOR_SIZE
            next_offset = offsets[n + 1] * ISO_SECTOR_SIZE if len(offsets) > n + 1 else img_bd_size
            zero_padding = next_offset - (current_offset + size)

            # write current entry
            iso_fh.seek(img_bd_iso_offset + current_offset, os.SEEK_SET)
            with reader.open(file_name) as file_h:
                if file_name in replace_entries:
                    file_h = replace_entries[file_name]
                copy_file_h(file_h, iso_fh)

            # fill with zeros up to the next entry
            zero_pad_file_h(iso_fh, zero_padding)
