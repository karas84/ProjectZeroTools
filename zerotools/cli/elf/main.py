from . import parse_iso
from . import parse_file
from zerotools.cli.parser import AutoParser, ParserCommand


class ELFArgParser(AutoParser):
    description = "Parse ELF file for entries"

    commands = {
        "parse-iso": ParserCommand(parse_iso.argument_parser(), parse_iso.main),
        "parse-file": ParserCommand(parse_file.argument_parser(), parse_file.main),
    }


def main():
    parser = ELFArgParser()
    parser()


if __name__ == "__main__":
    main()
