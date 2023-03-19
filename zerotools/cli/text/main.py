from . import extract_iso, rebuild_iso, extract_file, rebuild_file
from ...cli.parser import AutoParser, ParserCommand


class LanguageArgParser(AutoParser):
    description = "Extract (and Rebuild) language files"

    commands = {
        "extract-iso": ParserCommand(extract_iso.argument_parser(), extract_iso.main),
        "rebuild-iso": ParserCommand(rebuild_iso.argument_parser(), rebuild_iso.main),
        "extract-file": ParserCommand(extract_file.argument_parser(), extract_file.main),
        "rebuild-file": ParserCommand(rebuild_file.argument_parser(), rebuild_file.main),
    }


def main():
    parser = LanguageArgParser()
    parser()


if __name__ == "__main__":
    main()
