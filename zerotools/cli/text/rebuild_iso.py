import argparse

from zerotools.cli.parser import ArgEnum
from zerotools.text.names import MessageNames
from zerotools.text.rebuild import rebuild_iso
from zerotools.text.serializer import LocalizationSerializerFormat
from zerotools.text.message.locale import Locale


def argument_parser():
    argenum_locale = ArgEnum(Locale)
    argenum_format = ArgEnum(LocalizationSerializerFormat)
    argenum_names = ArgEnum(MessageNames)

    parser = argparse.ArgumentParser(description="Rebuild in-game text and inject it back into ISO.")
    parser.add_argument("lang_path", type=str, help="lang path")
    parser.add_argument("iso_path", type=str, help="ISO path")
    parser.add_argument(
        "-f", "--format", type=argenum_format, required=True, help=f"format (one of: {argenum_format.option_str})"
    )
    parser.add_argument(
        "-l", "--locale", type=argenum_locale, required=True, help=f"locale (one of: {argenum_locale.option_str})"
    )
    parser.add_argument(
        "-t", "--type", type=argenum_names, required=True, help=f"text type (one of: {argenum_names.option_str})"
    )

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    rebuild_iso(args.lang_path, args.iso_path, locale=args.locale, serializer_format=args.format, event_type=args.type)


if __name__ == "__main__":
    main()
