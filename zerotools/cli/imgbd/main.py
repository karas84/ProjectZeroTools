from zerotools.cli.parser import AutoParser, ParserCommand
from . import extract_fs
from . import rebuild_fs
from . import extract_iso
from . import rebuild_iso


class IMGBDArgParser(AutoParser):
    description = "Extract and Rebuild IMG_BD file"

    commands = {
        "extract-iso": ParserCommand(extract_iso.argument_parser(), extract_iso.main),
        "extract-fs": ParserCommand(extract_fs.argument_parser(), extract_fs.main),
        "rebuild-iso": ParserCommand(rebuild_iso.argument_parser(), rebuild_iso.main),
        "rebuild-fs": ParserCommand(rebuild_fs.argument_parser(), rebuild_fs.main),
    }


def main():
    parser = IMGBDArgParser()
    parser()


if __name__ == "__main__":
    main()
