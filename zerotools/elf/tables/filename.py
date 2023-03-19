from typing import BinaryIO

from pycdlib.pycdlibio import PyCdlibIO

from zerotools.utils.fileio import read_file


def get_file_names_from_elf(elf_fh: "BinaryIO | PyCdlibIO") -> "list[str] | None":
    elf_bin = read_file(elf_fh)

    try:
        cd_file_dat_start = elf_bin.index(b"CD_FILE_DAT:T")
        cd_file_dat_end = elf_bin.index(b",;", cd_file_dat_start)
        cd_file_dat = elf_bin[cd_file_dat_start:cd_file_dat_end]
    except ValueError:
        return None

    cd_file_dat = cd_file_dat.replace(b"\x2C\x5C\x00", b"\x2C").decode("ascii")
    section_name, file_list = cd_file_dat.split("=e", 1)

    file_list = [file.rsplit(":", 1) for file in file_list.rstrip(",").split(",")]
    file_list = [".".join(name.rsplit("_", 1)) for name, _ in sorted(file_list, key=lambda x: int(x[-1]))]

    return file_list
