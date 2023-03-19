import os
import re
import struct

from typing import BinaryIO, Generator, cast
from contextlib import contextmanager

from .entry import TOCEntry, FileEntry
from .adapter import FilesystemAdapter, ISOAdapter
from ...utils.iso import ISO_SECTOR_SIZE
from zerotools.utils.subfile import SubFile


def is_iso_file(file_path):
    return os.path.isfile(file_path) and os.path.splitext(file_path)[1].upper() == ".ISO"


class PJZReader:
    re_dat_entry = re.compile(r"([A-Z0-9_]+)_([A-Z0-9]+):([0-9]+)")

    def __init__(self, load_path):
        self.load_path = load_path

        if is_iso_file(load_path):
            self.adapter = ISOAdapter(self.load_path)
        elif os.path.isdir(load_path):
            self.adapter = FilesystemAdapter(self.load_path)
        else:
            raise ValueError("load_path must be iso or filesystem path")

        self.adapter.setup()

        toc_entry_list = self.prepare_toc_and_entries()

        if toc_entry_list is None:
            raise RuntimeError("cannot prepare toc and entries")

        self.toc_entry_list = toc_entry_list

        self.file_name_index = self.make_file_name_index()

    def parse_cd_file_dat(self, elf_path):
        elf_bin = self.adapter.read_file(elf_path)

        if not elf_bin:
            raise RuntimeError("cannot read elf file, file not found")

        try:
            cd_file_dat_start = elf_bin.index(b"CD_FILE_DAT:T")
            cd_file_dat_end = elf_bin.index(b",;", cd_file_dat_start)
            cd_file_dat = elf_bin[cd_file_dat_start:cd_file_dat_end]
        except ValueError:
            return None

        cd_file_dat = cd_file_dat.replace(b"\x2C\x5C\x00", b"\x2C").decode("ascii")
        section_name, file_list = cd_file_dat.split("=e", 1)

        file_list = file_list.rstrip(",").split(",")

        entry_matches = [self.re_dat_entry.match(entry) for entry in file_list]

        if not all(entry_matches):
            return None

        entry_matches = cast(list[re.Match[str]], entry_matches)

        toc_entry_list = [
            TOCEntry(f"{entry.group(1)}.{entry.group(2)}", int(entry.group(3))) for entry in entry_matches
        ]

        return toc_entry_list

    def parse_img_hd(self, img_hd_path):
        img_hd_bin = self.adapter.read_file(img_hd_path)

        if img_hd_bin is None or len(img_hd_bin) % 8 != 0:
            return None

        num_int32 = len(img_hd_bin) // 4
        file_data = struct.unpack(f"<{num_int32}I", img_hd_bin)

        file_entry_list = [
            FileEntry(file_data[i] * ISO_SECTOR_SIZE, file_data[i + 1]) for i in range(0, len(file_data), 2)
        ]

        return file_entry_list

    @staticmethod
    def validate_toc(toc_entry_list, file_entry_list):
        return (
            toc_entry_list is not None and file_entry_list is not None and len(toc_entry_list) == len(file_entry_list)
        )

    def validate_image_bd_size(self, file_entry_list):
        max_file_entry_position = max([fe.offset + fe.size for fe in file_entry_list])
        image_bd_size = self.adapter.get_img_bd_size()
        return image_bd_size >= max_file_entry_position

    def print_files(self):
        for toc_entry in self.toc_entry_list:
            print(f"{toc_entry.name} {toc_entry.size}")

    def list_files(self) -> list[str]:
        return [toc_entry.name for toc_entry in self.toc_entry_list]

    def num_files(self):
        return len(self.toc_entry_list)

    def file_exist(self, file_name):
        return file_name in ("", ".") or file_name in self.file_name_index

    def find_entry(self, file_name) -> "TOCEntry | None":
        if file_name not in self.file_name_index:
            return None

        toc_entry = self.file_name_index[file_name]

        return toc_entry

    def read_file(self, file_name, size=-1, offset=0):
        if not self.adapter.img_bd_path:
            raise RuntimeError("adapter uninitialized")

        toc_entry = self.find_entry(file_name)

        if toc_entry is None:
            return RuntimeError("file not found")

        bytes_left = max(0, toc_entry.size - offset)
        if size == -1 or size > bytes_left:
            size = bytes_left

        return self.adapter.read_file(self.adapter.img_bd_path, size, toc_entry.offset + offset)

    @contextmanager
    def open(self, file_name) -> Generator[BinaryIO, None, None]:
        if not self.adapter.img_bd_path:
            raise RuntimeError("adapter uninitialized")

        toc_entry = self.find_entry(file_name)

        if toc_entry is None:
            raise RuntimeError(f"file not found ({file_name})")

        with self.adapter.open(self.adapter.img_bd_path) as file_h:
            yield SubFile(file_h, offset=toc_entry.offset, size=toc_entry.size)

    def prepare_toc_and_entries(self):
        if not self.adapter.elf_path or not self.adapter.img_hd_path or not self.adapter.img_bd_path:
            raise RuntimeError("adapter uninitialized")

        if not all(
            map(self.adapter.test_file, (self.adapter.elf_path, self.adapter.img_hd_path, self.adapter.img_bd_path))
        ):
            raise RuntimeError("wrong root folder")

        toc_entry_list = self.parse_cd_file_dat(self.adapter.elf_path)

        if not toc_entry_list:
            raise RuntimeError("cannot find toc entry list")

        file_entry_list = self.parse_img_hd(self.adapter.img_hd_path)

        if not file_entry_list:
            raise RuntimeError("cannot find file entry list")

        if not self.validate_toc(toc_entry_list, file_entry_list) or not self.validate_image_bd_size(file_entry_list):
            raise RuntimeError("wrong format")

        img_bd_size = self.adapter.get_img_bd_size()

        if img_bd_size is None:
            raise RuntimeError("cannot get IMG_BD.BIN file size")

        next_offsets = [file_entry.offset for file_entry in file_entry_list[1:]] + [img_bd_size]

        for toc_entry, file_entry, next_offset in zip(toc_entry_list, file_entry_list, next_offsets):
            toc_entry.offset = file_entry.offset
            toc_entry.size = file_entry.size
            toc_entry.max_size = next_offset - file_entry.offset

        return toc_entry_list

    def make_file_name_index(self) -> dict[str, TOCEntry]:
        return {entry.name: entry for entry in self.toc_entry_list}

    def __repr__(self):
        return (
            f"{self.__class__.__name__}[{self.adapter.__class__.__name__}="
            f"{os.path.basename(self.adapter.load_path)}]"
        )
