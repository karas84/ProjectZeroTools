import argparse

from zerotools.cli.parser import ArgEnum
from zerotools.text.extract import extract_iso
from zerotools.text.serializer import LocalizationSerializerFormat
from zerotools.text.message.locale import Locale


def argument_parser():
    argenum_locale = ArgEnum(Locale)
    argenum_format = ArgEnum(LocalizationSerializerFormat)

    parser = argparse.ArgumentParser(description="Extract and parse in-game text files from ISO.")
    parser.add_argument("iso_path", type=str, help="ISO path")
    parser.add_argument("out_folder", type=str, help="output folder")
    parser.add_argument(
        "-f", "--format", type=argenum_format, required=True, help=f"format (one of: {argenum_format.option_str})"
    )
    parser.add_argument(
        "-l", "--locale", type=argenum_locale, default=None, help=f"locale (one of: {argenum_locale.option_str})"
    )

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    extract_iso(args.iso_path, args.out_folder, serializer_format=args.format, locale=args.locale)


if __name__ == "__main__":
    main()
