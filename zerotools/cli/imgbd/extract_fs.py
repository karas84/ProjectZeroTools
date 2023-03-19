import argparse

from zerotools.imgbd.extract import extract_fs


def argument_parser():
    parser = argparse.ArgumentParser(description="Extract IMG_BD files from files.")
    parser.add_argument("img_bd_folder", type=str, help="folder path containing IMG_BD.BIN and IMG_HD.BIN")
    parser.add_argument("file_list_path", type=str, help="ordered list of file names to extract")
    parser.add_argument("out_folder", type=str, help="output folder")

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    extract_fs(args.img_bd_folder, args.file_list_path, args.out_folder)


if __name__ == "__main__":
    main()
