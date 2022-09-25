import logging
import os
from pathlib import Path
import re
from typing import Union

from dictIO import DictReader, DictWriter
from dictIO.utils.counter import BorgCounter

from ospx.utils.dict import find_key, find_keys, find_type_identifier_in_keys


__ALL__ = ['OspSystemStructureImporter']

logger = logging.getLogger(__name__)


class OspSystemStructureImporter():

    @staticmethod
    def import_system_structure(system_structure_file: Union[str, os.PathLike[str]], ):

        # Make sure source_file argument is of type Path. If not, cast it to Path type.
        system_structure_file = system_structure_file if isinstance(
            system_structure_file, Path
        ) else Path(system_structure_file)

        # Check whether system structure file exists
        if not system_structure_file.exists():
            logger.error(f"OspSystemStructureImporter: File {system_structure_file} not found.")
            raise FileNotFoundError(system_structure_file)

        if system_structure_file.suffix != '.xml':
            logger.error(
                f"OspSystemStructureImporter: File type {system_structure_file} not implemented yet."
            )
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
            for connection_type, connection_properties in source_dict[connections_key].items():
                connection_type: str = re.sub(r'(^\d{1,6}_)', '', connection_type)

                if connection_type not in {'VariableConnection', 'VariableGroupConnection'}:
                    if connection_type in {'SignalConnection', 'SignalGroupConnection'}:
                        msg: str = (
                            f"Import failed: {system_structure_file.name} contains a connection with OSP-IS connection type '{connection_type}'\n"
                            f"The support for connection type '{connection_type}' is not yet implemented in ospx."
                        )
                    else:
                        msg: str = (
                            f"Import failed: {system_structure_file.name} contains a connection with unknown connection type '{connection_type}'\n"
                        )
                    logger.error(msg)
                    raise TypeError(msg)

                connection: dict[str, dict] = {}
                connection_name: str = ''
                # following loop has range {0,1}
                for index, (endpoint_type,
                            endpoint_properties) in enumerate(connection_properties.items()):
                    endpoint_type: str = re.sub(r'(^\d{1,6}_)', '', endpoint_type)

                    if endpoint_type not in {'Variable', 'VariableGroup'}:
                        if endpoint_type in {'Signal', 'SignalGroup'}:
                            msg: str = (
                                f"Import failed: {system_structure_file.name} contains a connection with OSP-IS endpoint type '{endpoint_type}'\n"
                                f"The support for endpoint type '{endpoint_type}' is not yet implemented in ospx."
                            )
                        else:
                            msg: str = (
                                f"Import failed: {system_structure_file.name} contains a connection with unknown endpoint type '{endpoint_type}'\n"
                            )
                        logger.error(msg)
                        raise TypeError(msg)

                    component_name: str = endpoint_properties['_attributes']['simulator']
                    referenced_name: str = endpoint_properties['_attributes']['name']
                    # alternator for source <--> target (because there are always 2 entries in VariableConnection in always the same sequence)
                    endpoint_name: str = 'source' if index % 2 == 0 else 'target'
                    endpoint: dict[str, str] = {}
                    _connector_type: str = 'output' if endpoint_name == 'source' else 'input'
                    _connector: dict[str, str] = {}
                    _connector_name: str = f'{component_name}_{referenced_name}'
                    if endpoint_type == 'Variable':
                        endpoint = {
                            'component': component_name,
                            'variable': referenced_name,
                        }
                        _connector = {
                            'variable': referenced_name,
                            'type': _connector_type,
                        }
                    elif endpoint_type == 'VariableGroup':
                        endpoint = {
                            'component': component_name,
                            'connector': _connector_name,
                        }
                        _connector = {
                            'variableGroup': referenced_name,
                            'type': _connector_type,
                        }
                    connection[endpoint_name] = endpoint
                    if not connection_name:
                        connection_name = component_name
                    else:
                        connection_name += f'_to_{component_name}'

                    # Save _connector in temp_connectors dict.
                    # (The variable and component information stored in these connectors
                    #  is later used to complete component properties)
                    temp_connectors[f'{counter():06d}_{component_name}'] = {
                        _connector_name: _connector
                    }
                # Save in connections dict
                connections[connection_name] = connection

        # Simulators (=Components)
        if simulators_key := find_key(source_dict, 'Simulators$'):
            for simulator_properties in source_dict[simulators_key].values():
                # Component
                component_name = simulator_properties['_attributes']['name']
                # Connectors
                component_connectors: dict[str, dict] = {}
                for temp_connector_key, connector in temp_connectors.items():
                    if component_name in temp_connector_key:
                        component_connectors |= connector
                # FMU
                fmu_name: str = simulator_properties['_attributes']['source']
                # Step Size
                step_size: Union[float, None] = None
                if 'stepSize' in simulator_properties['_attributes']:
                    step_size = float(simulator_properties['_attributes']['stepSize'])
                # Initial values
                component_initial_values: dict[str, dict] = {}
                if initial_values_key := find_key(simulator_properties, 'InitialValues$'):
                    initial_values = simulator_properties[initial_values_key]
                    if initial_value_keys := find_keys(initial_values, 'InitialValue$'):
                        for initial_value_key in initial_value_keys:
                            initial_value = initial_values[initial_value_key]
                            if data_type := find_type_identifier_in_keys(initial_value):
                                type_key = find_key(initial_value, f'{data_type}$')
                                referenced_name = initial_value['_attributes']['variable']
                                value = initial_value[type_key]['_attributes']['value']
                                component_initial_values |= {referenced_name: {'start': value}}
                # Assemble component
                component: dict[str, Union[dict, str, float]] = {
                    'connectors': component_connectors,
                    'fmu': fmu_name,
                }
                if step_size:
                    component['stepSize'] = step_size
                if component_initial_values:
                    component['initialize'] = component_initial_values
                # Save in components dict
                components[component_name] = component

        # System Structure
        system_structure: dict[str, dict] = {
            'connections': connections,
            'components': components,
        }

        # Global Settings
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
