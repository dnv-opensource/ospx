#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
from pathlib import Path
from typing import Union

from ospx import OspCaseBuilder
from ospx.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def _argparser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog='ospCaseBuilder',
        usage='%(prog)s caseDict [options [args]]',
        epilog='_________________ospCaseBuilder___________________',
        prefix_chars='-',
        add_help=True,
        description=
        'Builds the OSP-specific configuration files needed to run an OSP (co-)simulation case.'
    )

    parser.add_argument(
        'caseDict',
        metavar='caseDict',
        type=str,
        nargs='?',
        help='name of the dict file containing the OSP simulation case configuration.',
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help=(
            'cleans up working directory and deletes any existing ospx files, e.g. modelDescription.xml .fmu .csv etc.'
        ),
        default=False,
        required=False,
    )

    parser.add_argument(
        '-i',
        '--inspect',
        action='store_true',
        help=(
            'inspect mode: reads all properties from the FMUs but does not actually create the OSP case files.'
        ),
        default=False,
        required=False,
    )

    parser.add_argument(
        '-g',
        '--graph',
        action='store_true',
        help='creates a dependency graph image using graphviz',
        default=False,
        required=False,
    )

    console_verbosity = parser.add_mutually_exclusive_group(required=False)

    console_verbosity.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help=('console output will be quiet.'),
        default=False,
    )

    console_verbosity.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help=('console output will be verbose.'),
        default=False,
    )

    parser.add_argument(
        '--log',
        action='store',
        type=str,
        help='name of log file. If specified, this will activate logging to file.',
        default=None,
        required=False,
    )

    parser.add_argument(
        '--log-level',
        action='store',
        type=str,
        help='log level applied to logging to file.',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        required=False,
    )

    return parser


def main():
    """Entry point for console script as configured in setup.cfg

    Runs the command line interface and parses arguments and options entered on the console.
    """
    parser = _argparser()
    args = parser.parse_args()

    # Configure Logging
    # ..to console
    log_level_console: str = 'INFO'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console

    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    inspect: bool = args.inspect
    graph: bool = args.graph
    clean: bool = args.clean

    case_dict_file: Path = Path(args.caseDict)

    # Check whether case dict file exists
    if not case_dict_file.exists():
        logger.error(f"ospCaseBuilder.py: File {case_dict_file} not found.")
        return

    logger.info(
        f"Start ospCaseBuilder.py with following arguments:\n"
        f"\t case_dict_file: \t\t{case_dict_file}\n"
        f"\t inspect: \t\t\t\t{inspect}\n"
        f"\t graph: \t\t\t{graph}\n"
        f"\t clean: \t\t\t{clean}\n"
    )

    # Invoke API
    OspCaseBuilder.build(
        case_dict_file=case_dict_file,
        inspect=inspect,
        graph=graph,
        clean=clean,
    )


if __name__ == '__main__':
    main()
