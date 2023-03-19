import argparse

from zerotools.cli.parser import ArgEnum
from zerotools.text.rebuild import rebuild_file
from zerotools.text.serializer import LocalizationSerializerFormat
from zerotools.text.message.locale import Locale


def argument_parser():
    argenum_locale = ArgEnum(Locale)
    argenum_format = ArgEnum(LocalizationSerializerFormat)

    parser = argparse.ArgumentParser(description="Rebuild in-game text and save it as OBJ file.")
    parser.add_argument("lang_path", type=str, help="lang path")
    parser.add_argument("out_language_path", type=str, help="output file path")
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
    rebuild_file(args.lang_path, args.out_language_path, locale=args.locale, serializer_format=args.format)


if __name__ == "__main__":
    main()
