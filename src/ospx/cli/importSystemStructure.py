#!/usr/bin/env python
"""importSystemStructure command line interface."""

import argparse
import logging
import pprint
from importlib import metadata
from pathlib import Path

from ospx.importer import OspSystemStructureImporter
from ospx.utils.logging import configure_logging

logger = logging.getLogger(__name__)


def _get_version() -> str:
    """Return the installed package version, or a safe fallback if unavailable."""
    try:
        return metadata.version("ospx")
    except metadata.PackageNotFoundError:
        # Fallback when package metadata is not available (e.g. running from source)
        return "ospx (version unknown)"


def _argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="importSystemStructure",
        usage="%(prog)s system_structure_file [options [args]]",
        epilog="_________________importSystemStructure___________________",
        prefix_chars="-",
        add_help=True,
        description=("Imports an existing OspSystemStructure.xml and translates it into a case dict file."),
    )

    _ = parser.add_argument(
        "system_structure_file",
        metavar="system_structure_file",
        type=str,
        help="name of the system structure file",
        default="OspSystemStructure.xml",
    )

    console_verbosity = parser.add_mutually_exclusive_group(required=False)

    _ = console_verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help=("console output will be quiet."),
        default=False,
    )

    _ = console_verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=("console output will be verbose."),
        default=False,
    )

    _ = parser.add_argument(
        "--log",
        action="store",
        type=str,
        help="name of log file. If specified, this will activate logging to file.",
        default=None,
        required=False,
    )

    _ = parser.add_argument(
        "--log-level",
        action="store",
        type=str,
        help="log level applied to logging to file.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        required=False,
    )

    _ = parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_get_version(),
    )

    return parser


def main() -> None:
    """Entry point for console script as configured in pyproject.toml.

    Runs the command line interface and parses arguments and options entered on the console.
    """
    parser = _argparser()
    args = parser.parse_args()

    # Configure Logging
    # ..to console
    log_level_console: str = "WARNING"
    if any([args.quiet, args.verbose]):
        log_level_console = "ERROR" if args.quiet else log_level_console
        log_level_console = "INFO" if args.verbose else log_level_console
    # ..to file
    log_file: Path | None = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    system_structure_file: Path = Path(args.system_structure_file)

    # Check whether system structure file exists
    if not system_structure_file.is_file():
        logger.error(f"importSystemStructure.py: File {system_structure_file} not found.")
        return

    # Print the parsed commandline arguments for documentation and debugging purposes.
    # The arguments will be split into one argument per line, if possible.
    # If extracting a mapping from `args` fails, fall back to its string representation.
    _indent: str = " " * 13
    try:
        _arg_mapping = vars(args)
    except TypeError:
        _arg_mapping = {"args": str(args)}
    _formatted_args = pprint.pformat(_arg_mapping, sort_dicts=True)
    _indented_args = "\n".join(f"{_indent}{line}" for line in _formatted_args.splitlines())
    logger.info(
        "Start importSystemStructure.py with following arguments:\n%s\n",
        _indented_args,
    )

    # Invoke API
    OspSystemStructureImporter.import_system_structure(system_structure_file)

    return


if __name__ == "__main__":
    main()
