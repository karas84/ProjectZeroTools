import argparse

from zerotools.imgbd.extract import extract_iso


def argument_parser():
    parser = argparse.ArgumentParser(description="Extract IMG_BD files from ISO.")
    parser.add_argument("iso_path", type=str, help="ISO path")
    parser.add_argument("out_folder", type=str, help="output folder")

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    extract_iso(args.iso_path, args.out_folder)


if __name__ == "__main__":
    main()
