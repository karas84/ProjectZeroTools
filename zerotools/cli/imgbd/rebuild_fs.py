import argparse

from zerotools.imgbd.rebuild import rebuild_img_bd_fs, ALIGN_VALUES


def argument_parser():
    parser = argparse.ArgumentParser(description="Rebuild IMG_BD from files and save it into folder.")
    parser.add_argument("img_bd_folder", type=str, help="IMG_BD folder")
    parser.add_argument("file_list_path", type=str, help="Ordered list of files to rebuild")
    parser.add_argument("out_folder", type=str, help="Output path")
    parser.add_argument(
        "-a", "--align", type=int, choices=ALIGN_VALUES, default=ALIGN_VALUES[0], help="align offset multiple"
    )

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    rebuild_img_bd_fs(args.img_bd_folder, args.file_list_path, args.out_folder, args.align)


if __name__ == "__main__":
    main()
