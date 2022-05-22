#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.utils.counter import BorgCounter
from ospx.utils.logging import configure_logging
from ospx.utils.dict import find_key


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

    # Dispatch to _main(), which takes care of processing the arguments and invoking the API.
    _main(system_structure_file=system_structure_file, )


def _main(system_structure_file: Path, ):
    """Entry point for unit tests.

    Processes the arguments parsed by main() on the console and invokes the API.
    """

    # Check whether system structure file exists
    if not system_structure_file.exists():
        logger.error(f"importSystemStructure.py: File {system_structure_file} not found.")
        return

    logger.info(
        f"Start importSystemStructure.py with following arguments:\n"
        f"\t system_structure_file: \t{system_structure_file}\n"
    )

    if system_structure_file.suffix != '.xml':
        logger.error(f"file {system_structure_file} not implemented yet.")
        return

    counter = BorgCounter()

    # gather the source xml
    # this is provided from a side path, not the actual folder, otherwise it will be overwritten!
    source_dict = DictReader.read(system_structure_file, comments=False)

    # the to main subdicts contained by systemStructure dict
    components_dict = {}
    connectors_dict = {}
    connections_dict = {}

    # iterate over the connections first,
    # because they contain the var names and the component name
    # collecting and naming the ports
    numbered_connections_dict_key = find_key(source_dict, 'Connections')
    for key, item in source_dict[numbered_connections_dict_key].items():

        connection_name = []
        temp_connections_dict = {}
        # this loop has the range {0,1}
        for index, (s_key,
                    s_item) in enumerate(source_dict[numbered_connections_dict_key][key].items()):

            connector_name = 'PORT_' + s_item['_attributes']['simulator'] + '_VAR_' + s_item[
                '_attributes']['name']

            # alternator for source <--> target (because there are always 2 entries in VariableConnection in always the same sequence)
            if index % 2 == 0:
                temp_connections_dict['source'] = connector_name
                type = 'output'
            else:
                temp_connections_dict['target'] = connector_name
                type = 'input'

            connectors_dict['%06i_%s' % (counter(), s_item['_attributes']['simulator'])] = {
                connector_name: {
                    'reference': s_item['_attributes']['name'],
                    'type': type,
                }
            }

            connection_name.append(s_item['_attributes']['simulator'])

        connection_name = '_TO_'.join(connection_name)

        connections_dict[connection_name] = temp_connections_dict

    # iterate over "Simulators"
    numbered_components_dict_key = find_key(source_dict, 'Simulator')
    for key, item in source_dict[numbered_components_dict_key].items():

        named_key = item['_attributes']['name']
        source_fmu_name = item['_attributes']['source']
        temp_connectors_dict = {}

        for c_key, c_item in connectors_dict.items():

            if named_key in c_key:
                temp_connectors_dict.update(c_item)

        components_dict[named_key] = {'connectors': temp_connectors_dict, 'fmu': source_fmu_name}

        # if there is a InitialValues in numberedComponentDictKey
        numbered_initial_values_key = find_key(item, 'InitialValues')
        if 'InitialValues' in numbered_initial_values_key:

            # find numbered key names
            numbered_initial_value_key = find_key(
                item[numbered_initial_values_key], 'InitialValue'
            )
            numbered_real_key = find_key(
                item[numbered_initial_values_key][numbered_initial_value_key], 'Real'
            )

            # extract var name, value
            var_name = item[numbered_initial_values_key][numbered_initial_value_key]['_attributes'
                                                                                     ]['variable']
            value = item[numbered_initial_values_key][numbered_initial_value_key][
                numbered_real_key]['_attributes']['value']

            # sub dict
            initialize_dict = {
                'initialize': {
                    var_name: {
                        'causality': 'parameter', 'variability': 'fixed', 'start': value
                    }
                }
            }

            # update
            components_dict[named_key].update(initialize_dict)

    system_structure_dict = {'components': components_dict, 'connections': connections_dict}

    # finally assemble all
    case_dict = {
        '_environment': {
            'libSource': '.', 'root': Path.cwd()
        },
        'systemStructure': system_structure_dict,
        'run': {
            'simulation': {
                'name': 'demoCase', 'startTime': 0., 'stopTime': None, 'baseStepSize': 0.01
            }
        },
    }

    source_file_name = source_dict.name.replace('.', '_')
    target_file = Path.cwd() / f'caseDict_imported_from_{source_file_name}'

    DictWriter.write(case_dict, target_file, mode='w')

    return


if __name__ == '__main__':

    main()
