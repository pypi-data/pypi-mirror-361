import argparse

import jbussdieker


def _get_parser():
    parser = argparse.ArgumentParser(description="CLI for jbussdieker")
    parser.add_argument("--version", action="store_true", help="Show the version")
    return parser


def main():
    parser = _get_parser()
    args = parser.parse_args()

    if args.version:
        print(f"jbussdieker v{jbussdieker.__version__}")
    else:
        print("No arguments provided. Use --help for available options.")


if __name__ == "__main__":
    main()
