#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from ospx import OspSystemStructureImporter
from ospx.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def _argparser() -> argparse.ArgumentParser:

    parser = ArgumentParser(
        prog='importSystemStructure',
        usage='%(prog)s systemStructureFile [options [args]]',
        epilog='_________________importSystemStructure___________________',
        prefix_chars='-',
        add_help=True,
        description=(
            'Imports an existing OspSystemStructure.xml and translates it into a caseDict.'
        )
    )

    parser.add_argument(
        'systemStructureFile',
        metavar='systemStructureFile',
        type=str,
        help='name of the system structure file',
        default='OspSystemStructure.xml'
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
    log_level_console: str = 'WARNING'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console
    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    system_structure_file: Path = Path(args.systemStructureFile)

    # Check whether system structure file exists
    if not system_structure_file.is_file():
        logger.error(f"importSystemStructure: File {system_structure_file} not found.")
        return

    logger.info(
        f"Start importSystemStructure.py with following arguments:\n"
        f"\t system_structure_file: \t{system_structure_file}"
    )

    # Invoke API
    OspSystemStructureImporter.import_system_structure(system_structure_file)

    return


if __name__ == '__main__':

    main()
