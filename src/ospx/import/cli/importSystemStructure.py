#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import re
from argparse import ArgumentParser
from pathlib import Path

from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.utils.counter import BorgCounter

from ospx.utils.logging import configure_logging

logger = logging.getLogger(__name__)


def _argparser() -> argparse.ArgumentParser:

    parser = ArgumentParser(
        prog='importSystemStructure',
        usage='%(prog)s [options [args]]',
        epilog='_________________importSystemStructure___________________',
        prefix_chars='-',
        add_help=True,
        description=
        'Import OspSystemStructure.xml or SystemStructure.ssd'
    )

    parser.add_argument(
        'xmlFilePath',
        metavar='xmlFilePath',
        type=str,
        help = 'relative system structure file path',
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


def _find_numbered_key_by_string(dd, search_string):
    """find the element name for an (anyways unique) element
    after it was preceeded by a number to keep the sequence of xml elements
    as this is not the "nature" of dicts
    """
    try:
        return [k for k in dd.keys() if re.search(search_string, k)][0]
    except Exception:
        return 'ELEMENTNOTFOUND'


def main():
    """Entry point for console script as configured in setup.cfg

    Runs the command line interface and parses arguments and options entered on the console.
    """

    parser = _argparser()
    args = parser.parse_args()

    counter = BorgCounter()

    # Configure Logging
    log_level_console: str = 'WARNING'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console
    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    xmlFilePath: str = args.xmlFilePath

    xmlFilePath = Path(xmlFilePath)

    if not xmlFilePath.is_file():
        logger.error(f"file {xmlFilePath} not found.")
        return

    if xmlFilePath.suffix != '.xml':
        logger.error(f"file {xmlFilePath} not implemented yet.")
        return

    sourceDict = DictReader.read(xmlFilePath, comments=False)

    connectionsDict = {}; connectorsDict = {}
    numberedConnectionsDictName = _find_numbered_key_by_string(sourceDict, 'Connections')
    for key, item in sourceDict[numberedConnectionsDictName].items():

        connectionName = []; tempConnectionDict = {}
        #this loop has the range {0,1}
        for index, (sKey, sItem) in enumerate(sourceDict[numberedConnectionsDictName][key].items()):

            connectorName = 'PORT_' + sItem['_attributes']['simulator'] + '_VAR_' + sItem['_attributes']['name']

            if index % 2 == 0:
                tempConnectionDict.update({'source':connectorName})
                type = 'output'
            else:
                tempConnectionDict.update({'target':connectorName})
                type = 'input'

            connectorsDict.update({'%06i_%s' %(counter(), sItem['_attributes']['simulator']):{connectorName:{'reference':sItem['_attributes']['name'], 'type':type}}})
            connectionName.append(sItem['_attributes']['simulator'])

        connectionName = '_TO_'. join(connectionName)

        connectionsDict.update({connectionName:tempConnectionDict})

    componentsDict = {}
    numberedComponentsDictName = _find_numbered_key_by_string(sourceDict, 'Simulator')
    for key, item in sourceDict[numberedComponentsDictName].items():
        namedKey = item['_attributes']['name']
        sourceFmuName = item['_attributes']['source']

        tempConnectorsDict = {}
        for cKey, cItem in connectorsDict.items():

            if namedKey in cKey:
                tempConnectorsDict.update(cItem)

        componentsDict.update({namedKey:{'connectors':tempConnectorsDict, 'fmu':{sourceFmuName}}})

    systemStructureDict = {'Components':componentsDict, 'Connections':connectionsDict}

    caseDict = {
        '_environment':{'libSource':'', 'root':Path.cwd()},
        'systemStructure':systemStructureDict,
        'run':{'simulation':{'name':'demoCase', 'startTime':0., 'stopTime':None, 'baseStepSize':0.01}},
        }
    tempDictPath = '-'.join([sourceDict.name, 'Dict'])

    tempDictPath = Path.cwd() / tempDictPath
    DictWriter.write(caseDict, tempDictPath, mode='w')

    exit(0)


if __name__ == '__main__':

    main()
