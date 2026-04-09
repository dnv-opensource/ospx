#!/usr/bin/env python
"""ospCaseBuilder command line interface."""

import argparse
import logging
import pprint
from importlib import metadata
from pathlib import Path

from ospx.ospCaseBuilder import OspCaseBuilder
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
        prog="ospCaseBuilder",
        usage="%(prog)s case_dict_file [options [args]]",
        epilog="_________________ospCaseBuilder___________________",
        prefix_chars="-",
        add_help=True,
        description="Builds the OSP-specific configuration files needed to run an OSP (co-)simulation case.",
    )

    _ = parser.add_argument(
        "case_dict_file",
        metavar="case_dict_file",
        type=str,
        help="name of the dict file containing the OSP simulation case configuration.",
    )

    _ = parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "cleans up working directory and deletes any existing ospx files, e.g. modelDescription.xml .fmu .csv etc."
        ),
        default=False,
        required=False,
    )

    _ = parser.add_argument(
        "-i",
        "--inspect",
        action="store_true",
        help=("inspect mode: reads all properties from the FMUs but does not actually create the OSP case files."),
        default=False,
        required=False,
    )

    _ = parser.add_argument(
        "-g",
        "--graph",
        action="store_true",
        help="creates a dependency graph image using graphviz",
        default=False,
        required=False,
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

    inspect: bool = args.inspect
    graph: bool = args.graph
    clean: bool = args.clean

    case_dict_file: Path = Path(args.case_dict_file)

    # Check whether case dict file exists
    if not case_dict_file.is_file():
        logger.error(f"ospCaseBuilder.py: File {case_dict_file} not found.")
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
        "Start ospCaseBuilder.py with following arguments:\n%s\n",
        _indented_args,
    )

    # Invoke API
    OspCaseBuilder.build(
        case_dict_file=case_dict_file,
        inspect=inspect,
        graph=graph,
        clean=clean,
    )


if __name__ == "__main__":
    main()
