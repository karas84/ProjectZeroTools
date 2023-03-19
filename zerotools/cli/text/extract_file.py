import argparse

from zerotools.cli.parser import ArgEnum
from zerotools.text.extract import extract_file
from zerotools.text.serializer import LocalizationSerializerFormat
from zerotools.text.message.locale import Locale


def argument_parser():
    argenum_locale = ArgEnum(Locale)
    argenum_format = ArgEnum(LocalizationSerializerFormat)

    parser = argparse.ArgumentParser(description="Extract and parse in-game text files from OBJ.")
    parser.add_argument("lang_file", type=str, help="BIN language file path")
    parser.add_argument("out_file", type=str, help="decoded output file")
    parser.add_argument("name_list_src", type=str, help="source from where to get file list")
    parser.add_argument(
        "-f", "--format", type=argenum_format, required=True, help=f"format (one of: {argenum_format.option_str})"
    )
    parser.add_argument(
        "-l", "--locale", type=argenum_locale, required=True, help=f"locale (one of: {argenum_locale.option_str})"
    )

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    extract_file(
        args.lang_file,
        args.out_file,
        name_list_src=args.name_list_src,
        locale=args.locale,
        serializer_format=args.format,
    )


if __name__ == "__main__":
    main()
