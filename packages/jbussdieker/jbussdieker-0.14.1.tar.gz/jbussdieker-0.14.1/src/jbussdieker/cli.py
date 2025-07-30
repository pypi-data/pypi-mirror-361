import os
import logging
import argparse
import json

import jbussdieker

from jbussdieker.config import Config
from jbussdieker.logging import setup_logging
from jbussdieker.project import ProjectGenerator


def _get_parser():
    parser = argparse.ArgumentParser(description="CLI for jbussdieker")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")
    subparsers.add_parser("version", help="Show the version")
    parser_config = subparsers.add_parser("config", help="Show or set config")
    parser_config.add_argument("--set", metavar="KEY=VALUE", help="Set a config value")
    parser_create = subparsers.add_parser(
        "create", help="Create a new project directory"
    )
    parser_create.add_argument("name", metavar="NAME", help="Name of the new project")
    return parser


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)
    config = Config.load()
    log_level = logging.DEBUG if args.verbose else getattr(logging, config.log_level)
    setup_logging(level=log_level, format=config.log_format)
    logging.debug("Parsed args: %s", args)
    if args.command == "version":
        logging.info(f"jbussdieker v{jbussdieker.__version__}")
    elif args.command == "config":
        if args.set:
            key, sep, value = args.set.partition("=")
            if not sep:
                logging.error("Invalid format. Use KEY=VALUE.")
                return
            if hasattr(config, key):
                attr = getattr(config, key)
                if isinstance(attr, bool):
                    value = value.lower() in ("1", "true", "yes")
                setattr(config, key, value)
                config.save()
                logging.info(f"Set {key} = {value}")
            else:
                config.custom_settings[key] = value
                config.save()
                logging.info(f"Set custom setting {key} = {value}")
        else:
            logging.info("Current config:")
            logging.info(json.dumps(config.asdict(), indent=2))
    elif args.command == "create":
        generator = ProjectGenerator(args.name, config=config)
        generator.run()
    else:
        parser.print_help()
