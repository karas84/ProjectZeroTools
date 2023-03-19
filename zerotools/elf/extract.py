import pycdlib

from .tables import get_file_names_from_elf, get_ingame_message_table_names_from_elf
from ..utils.iso import iso_context, check_elf_path


def extract_file_names_iso(iso_path: str, out_file: str):
    with iso_context(iso_path) as iso:
        iso: pycdlib.PyCdlib

        elf_path = check_elf_path(iso)

        if not elf_path:
            raise RuntimeError("invalid elf path")

        with iso.open_file_from_iso(iso_path=elf_path) as elf_fh:
            file_list = get_file_names_from_elf(elf_fh)

        if file_list is None:
            raise RuntimeError("cannot get file list")

    with open(out_file, mode="w", encoding="utf-8") as file_h:
        for file_name in file_list:
            file_h.write(f"{file_name}\n")


def extract_ingame_message_names_iso(iso_path: str, out_file: str):
    with iso_context(iso_path) as iso:
        iso: pycdlib.PyCdlib

        elf_path = check_elf_path(iso)

        if not elf_path:
            raise RuntimeError

        with iso.open_file_from_iso(iso_path=elf_path) as elf_fh:
            ig_msg_names = get_ingame_message_table_names_from_elf(elf_fh)

        if ig_msg_names is None:
            raise RuntimeError("cannot get ingame message names")

    with open(out_file, mode="w", encoding="utf-8") as file_h:
        for message_name in ig_msg_names:
            file_h.write(f"{message_name}\n")


def extract_file_names_file(elf_path: str, out_file: str):
    with open(elf_path, "rb") as elf_fh:
        file_list = get_file_names_from_elf(elf_fh)

    if file_list is None:
        raise RuntimeError("cannot get file names from elf")

    with open(out_file, mode="w", encoding="utf-8") as file_h:
        for file_name in file_list:
            file_h.write(f"{file_name}\n")


def extract_ingame_message_names_file(elf_path: str, out_file: str):
    with open(elf_path, "rb") as elf_fh:
        ig_msg_names = get_ingame_message_table_names_from_elf(elf_fh)

    if ig_msg_names is None:
        raise RuntimeError("cannot get ingame message table names from elf")

    with open(out_file, mode="w", encoding="utf-8") as file_h:
        for message_name in ig_msg_names:
            file_h.write(f"{message_name}\n")
