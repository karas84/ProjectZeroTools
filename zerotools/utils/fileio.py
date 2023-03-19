import os

from typing import BinaryIO

from pycdlib.pycdlibio import PyCdlibIO


def read_file(file_h: "BinaryIO | PyCdlibIO"):
    pos = file_h.tell()
    file_h.seek(0, os.SEEK_SET)
    file_bin = file_h.read()
    file_h.seek(pos, os.SEEK_SET)
    return file_bin


def copy_file_fh(src_fh: BinaryIO, dst_fh: BinaryIO, /, *, block_size: int = 2**20):
    src_fh.seek(0, os.SEEK_SET)
    data = True
    while data:
        data = src_fh.read(block_size)
        dst_fh.write(data)
