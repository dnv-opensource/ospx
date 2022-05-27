#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.utils.counter import BorgCounter
from ospx.utils.dict import find_key, find_type_identifier_in_keys
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

    # Dispatch to _main(), which takes care of processing the arguments and invoking the API.
    _main(system_structure_file=system_structure_file)


def _main(system_structure_file: Path):
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

    source_dict = DictReader.read(system_structure_file, comments=False)

    # Main subdicts contained in systemStructure
    connections: dict[str, dict] = {}
    components: dict[str, dict] = {}

    # Connections
    # iterate over the connections first as they contain the variable and component names
    temp_connectors = {}
    if connections_key := find_key(source_dict, 'Connections$'):
        for connection_properties in source_dict[connections_key].values():
            connection: dict[str, dict] = {}
            connection_name: str = ''
            # this loop has the range {0,1}
            for index, (endpoint_type,
                        endpoint_properties) in enumerate(connection_properties.items()):
                component_name = endpoint_properties['_attributes']['simulator']
                variable_name = endpoint_properties['_attributes']['name']
                # alternator for source <--> target (because there are always 2 entries in VariableConnection in always the same sequence)
                endpoint_type: str = 'source' if index % 2 == 0 else 'target'
                connection[endpoint_type] = {
                    'component': component_name,
                    'variable': variable_name,
                }
                # Save connector in temp_connectors dict.
                # (The variable and component information stored in these connectors
                #  is later used to complete the component properties)
                connector_name = f'{component_name}_{variable_name}'
                connector_type = 'output' if endpoint_type == 'source' else 'input'
                temp_connectors[f'{counter():06d}_{component_name}'] = {
                    connector_name: {
                        'variable': variable_name,
                        'type': connector_type,
                    }
                }
                if not connection_name:
                    connection_name = component_name
                else:
                    connection_name += f'_to_{component_name}'

            connections[connection_name] = connection

    # Simulators (=Components)
    if simulators_key := find_key(source_dict, 'Simulators$'):
        for simulator_properties in source_dict[simulators_key].values():
            # Component
            component: dict[str, dict] = {}
            component_name = simulator_properties['_attributes']['name']
            # Connectors
            component_connectors: dict[str, dict] = {}
            for temp_connector_key, connector in temp_connectors.items():
                if component_name in temp_connector_key:
                    component_connectors |= connector
            component['connectors'] = component_connectors
            # FMU
            fmu_name = simulator_properties['_attributes']['source']
            component['fmu'] = fmu_name
            # Initial values
            if initial_values_key := find_key(simulator_properties, 'InitialValues$'):
                initial_values = simulator_properties[initial_values_key]
                if initial_value_key := find_key(initial_values, 'InitialValue$'):
                    initial_value = initial_values[initial_value_key]
                    if data_type := find_type_identifier_in_keys(initial_value):
                        type_key = find_key(initial_value, f'{data_type}$')
                        variable_name = initial_value['_attributes']['variable']
                        value = initial_value[type_key]['_attributes']['value']
                        component['initialize'] = {
                            variable_name: {
                                'causality': 'parameter',
                                'variability': 'fixed',
                                'start': value,
                            }
                        }
            # Save in components dict
            components[component_name] = component

    system_structure: dict[str, dict] = {
        'connections': connections,
        'components': components,
    }

    # General simulation attributes
    # 1: Defaults
    simulation: dict = {
        'name': system_structure_file.stem,
        'startTime': 0.,
        'baseStepSize': 0.01,
        'algorithm': 'fixedStep',
    }
    # 2: Overwrite defaults with values from source dict, where existing
    if '_attributes' in source_dict:
        attributes = source_dict['_attributes']
        if 'StartTime' in attributes:
            simulation['startTime'] = attributes['StartTime']
        if 'BaseStepSize' in attributes:
            simulation['baseStepSize'] = attributes['BaseStepSize']
        if 'Algorithm' in attributes:
            simulation['algorithm'] = attributes['Algorithm']

    # Assemble case dict
    case_dict = {
        '_environment': {
            'libSource': '.',
            'root': Path.cwd(),
        },
        'systemStructure': system_structure,
        'run': {
            'simulation': simulation,
        },
    }

    source_file_name = source_dict.name.replace('.', '_')
    target_file = Path.cwd() / f'caseDict_imported_from_{source_file_name}'

    DictWriter.write(case_dict, target_file, mode='w')

    return


if __name__ == '__main__':

    main()
