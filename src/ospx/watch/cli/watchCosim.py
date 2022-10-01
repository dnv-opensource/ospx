#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import os
import re
import shutil
from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from typing import List, Union

from ospx.utils.logging import configure_logging
from ospx.watch.watchCosim import CosimWatcher


logger = logging.getLogger(__name__)


def _argparser() -> argparse.ArgumentParser:

    parser = ArgumentParser(
        prog='watchCosim',
        usage='%(prog)s watchDict [options [args]]',
        epilog='_________________watchCosim___________________',
        prefix_chars='-',
        add_help=True,
        description=
        'Continuously watches the progress of cosim, and finally saves results as a pandas dataframe.'
    )

    parser.add_argument(
        'watchDict',
        metavar='watchDict',
        type=str,
        help=
        'name of the dict file containing the watch configuration (will also be part of the result file names).',
    )

    parser.add_argument(
        '-c',
        '--converge',
        action='store_true',
        help=
        'watch convergence progress, finally --dump (reading watchDict and .csv, plotting convergence until no changes happen for 5s to any .csv)',
        default=False,
        required=False
    )

    parser.add_argument(
        '-p',
        '--plot',
        action='store_true',
        help=
        'plot data including --dump (reading watchDict and .csv, creating results/SIMULATIONNAME.png)',
        default=False,
        required=False
    )

    parser.add_argument(
        '-d',
        '--dump',
        action='store_true',
        help=
        'dump data (reading watchDict and .csv, creating results/{dataFrameDump, resultsDict})',
        default=False,
        required=False
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
        '--latest',
        action='store',
        type=int,
        help='specify the interval of latest n timesteps to be taken into account',
        default=0,
        required=False,
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

    parser.add_argument(
        '--skip',
        action='store',
        type=int,
        help='skip the first n timesteps',
        default=0,
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
    log_level_console: str = 'WARNING'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console
    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    watch_dict_file_name: str = args.watchDict
    converge: bool = args.converge
    plot: bool = args.plot
    dump: bool = args.dump
    skip: int = args.skip
    latest: int = args.latest
    if not converge and not plot and not dump:
        logger.error('give at least one option what to do: --converge, --plot or --dump')
        parser.print_help()
        exit(0)

    # Dispatch to _main(), which takes care of processing the arguments and invoking the API.
    _main(
        watch_dict_file_name=watch_dict_file_name,
        converge=converge,
        plot=plot,
        dump=dump,
        skip_values=skip,
        latest_values=latest,
    )


def _main(
    watch_dict_file_name: str,
    converge: bool = False,
    plot: bool = False,
    dump: bool = False,
    skip_values: int = 0,
    latest_values: int = 0,
):
    """Entry point for unit tests.

    Processes the arguments parsed by main() on the console and invokes the API.
    """

    watch_dict_file = Path(watch_dict_file_name)

    if not watch_dict_file.is_file():
        logger.error(f"file {watch_dict_file} not found.")
        return

    csv_files: List[Path] = []
    wait_counter: int = 0
    while wait_counter < 5:
        csv_files = list(Path('.').glob('*.csv'))
        if csv_files:
            break
        if wait_counter == 0:
            logger.warning('waiting for csv files..')
        else:
            logger.info('waiting for csv files.')
        wait_counter += 1
        sleep(1)

    if not csv_files:
        logger.error('no csv files found.')
        return

    csv_file_names: List[str] = (sorted(file.name for file in csv_files))

    # From the csv file names, identify all data sources for which csv files have been written,
    # and save them as set.
    data_source_names = {re.sub(r'_\d{8}_\d{6}_\d{6}.*$', '', n) for n in csv_file_names}

    # For each identified component name:
    # 1. Find all csv files that match the component name
    # 2. From these, collect only the latest (newest) version
    latest_csv_file_names = [
        sorted(
            [file_name for file_name in csv_file_names if re.match(data_source_name, file_name)],
            key=os.path.getmtime,
        )[-1] for data_source_name in data_source_names
    ]

    watcher = CosimWatcher(latest_csv_file_names, skip_values, latest_values)
    watcher.read_watch_dict(watch_dict_file_name)

    Path(watcher.results_dir).mkdir(parents=True, exist_ok=True)

    if converge:
        watcher.plot(converge=True)

    elif plot:
        watcher.plot()

    if dump:
        watcher.dump()

        # finally: move annoying csv files to results
        # after simplifying watchCosim or splitting off, it can be considered to move csv files in advance
        # (not suitable for -c option!)
        for file in csv_files:
            shutil.move(file, "results")


if __name__ == '__main__':
    main()
