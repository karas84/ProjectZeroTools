import os
import argparse

from zerotools.elf.extract import extract_file_names_iso, extract_ingame_message_names_iso


def argument_parser():
    parser = argparse.ArgumentParser(description="Extract various file names from ISO.")
    parser.add_argument("iso_path", type=str, help="ISO path")
    parser.add_argument("out_folder", type=str, help="output folder")

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)

    # if not os.path.isdir(args.out_folder):
    #     print(f'ERROR: "{args.out_folder}" does not exists!', file=sys.stderr)
    #     sys.exit(1)
    os.makedirs(args.out_folder, exist_ok=True)

    extract_file_names_iso(args.iso_path, os.path.join(args.out_folder, "IMG_BD_FILES.TXT"))
    extract_ingame_message_names_iso(args.iso_path, os.path.join(args.out_folder, "IG_MSG_NAMES.TXT"))


if __name__ == "__main__":
    main()
