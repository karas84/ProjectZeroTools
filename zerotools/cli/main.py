from .parser import AutoParser
from .elf.main import ELFArgParser
from .text.main import LanguageArgParser
from .imgbd.main import IMGBDArgParser


class MainParser(AutoParser):
    description = "Project Zero ISO Tools"

    commands = {
        "imgbd": IMGBDArgParser(),
        "text": LanguageArgParser(),
        "elf": ELFArgParser(),
    }


def main():
    parser = MainParser()
    parser()


if __name__ == "__main__":
    main()
