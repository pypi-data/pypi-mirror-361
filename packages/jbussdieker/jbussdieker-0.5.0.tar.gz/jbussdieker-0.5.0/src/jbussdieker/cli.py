import argparse
import json

import jbussdieker

from jbussdieker.config import Config


def _get_parser():
    parser = argparse.ArgumentParser(description="CLI for jbussdieker")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")
    subparsers.add_parser("version", help="Show the version")
    parser_config = subparsers.add_parser("config", help="Show or set config")
    parser_config.add_argument("--set", metavar="KEY=VALUE", help="Set a config value")
    return parser


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"jbussdieker v{jbussdieker.__version__}")
    elif args.command == "config":
        cfg = Config.load()
        if args.set:
            key, sep, value = args.set.partition("=")
            if not sep:
                print("Invalid format. Use KEY=VALUE.")
                return
            if hasattr(cfg, key):
                attr = getattr(cfg, key)
                if isinstance(attr, bool):
                    value = value.lower() in ("1", "true", "yes")
                setattr(cfg, key, value)
                cfg.save()
                print(f"Set {key} = {value}")
            else:
                cfg.custom_settings[key] = value
                cfg.save()
                print(f"Set custom setting {key} = {value}")
        else:
            print("Current config:")
            print(json.dumps(cfg.asdict(), indent=2))
    else:
        parser.print_help()
