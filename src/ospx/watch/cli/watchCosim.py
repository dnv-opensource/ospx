#!/usr/bin/env python
# coding: utf-8

import logging
import os
import re
from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from typing import Union

from ospx.utils.logging import configure_logging
from ospx.watch.watchCosim import CosimWatcher

logger = logging.getLogger(__name__)


def cli():

    parser = ArgumentParser(
        prog='watchCosim',
        usage='%(prog)s [options [args]]',
        epilog='_________________watchCosim___________________',
        prefix_chars='-',
        add_help=True,
        description=
        'Continuously watches the progress of cosim, and finally saves results as a pandas dataframe.'
    )

    parser.add_argument(
        'watchDict',
        metavar='WATCHDICT',
        type=str,
        help='name of the dict file containing the watch configuration.',
    )

    parser.add_argument(
        '-p',
        '--plot',
        action='store_true',
        help='execute plot during runtime and afterwards',
        default=False,
        required=False
    )

    parser.add_argument(
        '-d',
        '--dump',
        action='store_true',
        help='dump a pickle file afterwards',
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

    watch_dict_file: Path = Path(args.watchDict)
    plot: bool = args.plot
    dump: bool = args.dump

    main(
        watch_dict_file=watch_dict_file,
        plot=plot,
        dump=dump,
    )


def main(
    watch_dict_file: Path,
    plot: bool = False,
    dump: bool = False,
):

    if not watch_dict_file.is_file():
        logger.error(f"file {watch_dict_file} not found.")
        return

    while True:
        csv_files = list(Path('.').rglob('*.csv'))
        csv_file_names = (sorted(file.name for file in csv_files))
        if len(csv_file_names) == 0:
            logger.info('waiting for csv files being written')  # 1
            sleep(5)
        else:
                                                                # not too fast
            sleep(1)
            break

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

    watcher = CosimWatcher(latest_csv_file_names)

    watcher.read_config_dict(watch_dict_file)

    Path(watcher.results_dir).mkdir(parents=True, exist_ok=True)

    if plot:
        # watcher.determine_optimum_screen_size()

        watcher.define_data_source_properties_for_plotting()

        watcher.initialize_plot()

        watcher.plot()

    if dump:

        watcher.define_data_source_properties_for_plotting()

        watcher.dump()


if __name__ == '__main__':
    cli()
