import pycdlib


from typing import Generator
from pycdlib import pycdlibexception
from contextlib import contextmanager

from zerotools.elf.version import ELF_EU, ELF_JP, ELF_US

ISO_SECTOR_SIZE = 0x800


@contextmanager
def iso_context(iso_path: str, /, *, mode="rb") -> Generator[pycdlib.PyCdlib, None, None]:
    iso = pycdlib.PyCdlib()
    iso.open(iso_path, mode=mode)

    try:
        yield iso
    finally:
        iso.close()


def check_path(iso: pycdlib.PyCdlib, iso_path: str) -> "str | None":
    try:
        iso.get_record(iso_path=iso_path)
        return iso_path
    except pycdlibexception.PyCdlibInvalidInput:
        return None


def check_elf_path(iso: pycdlib.PyCdlib):
    return check_path(iso, f"/{ELF_JP};1") or check_path(iso, f"/{ELF_EU};1") or check_path(iso, f"/{ELF_US};1")
