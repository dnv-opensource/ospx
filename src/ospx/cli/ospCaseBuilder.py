#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
from pathlib import Path
from typing import Union

from ospx.ospCaseBuilder import OspCaseBuilder
from ospx.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def cli():

    parser = argparse.ArgumentParser(
        prog='ospCaseBuilder',
        usage='%(prog)s [options [args]]',
        epilog='_________________ospCaseBuilder___________________',
        prefix_chars='-',
        add_help=True,
        description='Builds an OSP (Co-)simulation case.'
    )

    parser.add_argument(
        'caseDict',
        metavar='CASEDICT',
        type=str,
        help='name of the dict file containing the OSP simulation case configuration.',
    )

    parser.add_argument(
        '-i',
        '--inspect',
        action='store_true',
        help=(
            'inspect mode: check all modelDescription.xml refs\n'
            'but do not actually write connectors and connections.'
        ),
        default=False,
        required=False,
    )

    parser.add_argument(
        '-g',
        '--graph',
        action='store_true',
        help='creates a dependency graph using graphviz',
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

    args = parser.parse_args()

    # Configure Logging
    # ..to console
    log_level_console: str = 'WARNING'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console
    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    case_dict_file: Path = Path(args.caseDict)
    inspect: bool = args.inspect
    generate_graph: bool = args.graph

    main(
        case_dict_file=case_dict_file,
        inspect=inspect,
        generate_graph=generate_graph,
    )


def main(
    case_dict_file: Path,
    inspect: bool = False,
    generate_graph: bool = True,
):

    # Check whether case dict file exists
    if not case_dict_file.is_file():
        logger.error(f"BuildOspCase.py: File {case_dict_file} not found.")
        return

    case_builder: OspCaseBuilder = OspCaseBuilder(
        case_dict_file=case_dict_file,
        inspect=inspect,
        generate_graph=generate_graph,
    )
    case_builder.build()

    return


if __name__ == '__main__':
    cli()
