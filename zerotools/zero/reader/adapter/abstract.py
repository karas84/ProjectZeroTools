from io import BytesIO
from abc import ABC, abstractmethod
from contextlib import contextmanager

from zerotools.elf.version import ELF_EU, ELF_JP, ELF_US
from zerotools.zero.names import IMG_HD, IMG_BD


class AbstractAdapter(ABC):
    @abstractmethod
    def test_file(self, file_path: str) -> bool:
        ...

    @abstractmethod
    def read_file(self, file_name: str, size=-1, offset=0) -> bytes:
        ...

    @abstractmethod
    def get_img_bd_size(self) -> int:
        ...

    @abstractmethod
    def find_file(self, file_name: str) -> str:
        ...

    @contextmanager
    @abstractmethod
    def open(self, file_name: str) -> BytesIO:
        ...

    def __init__(self, load_path: str):
        self._init_called = True

        self.load_path = load_path

        self.elf_path = None
        self.img_hd_path = None
        self.img_bd_path = None

    def setup(self):
        if not getattr(self, "_init_called", False):
            raise RuntimeError("must call __init__ of super class")

        self.elf_path = self.find_file(ELF_EU) or self.find_file(ELF_JP) or self.find_file(ELF_US)
        self.img_hd_path = self.find_file(IMG_HD)
        self.img_bd_path = self.find_file(IMG_BD)

        if not self.elf_path or not self.img_hd_path or not self.img_bd_path:
            raise RuntimeError('path does not point to valid "Zero / Project Zero / Fatal Frame" data')
