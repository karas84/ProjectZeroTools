import argparse

from zerotools.imgbd.rebuild import rebuild_img_bd_iso


def argument_parser():
    parser = argparse.ArgumentParser(description="Rebuild IMG_BD from files and inject it back into ISO.")
    parser.add_argument("img_bd_folder", type=str, help="IMG_BD folder")
    parser.add_argument("iso_path", type=str, help="ISO path")

    return parser


def main(args=None):
    parser = argument_parser()
    args = parser.parse_args(args)
    rebuild_img_bd_iso(args.img_bd_folder, args.iso_path)


if __name__ == "__main__":
    main()
