import logging
import os
from pathlib import Path
from typing import Union

from dictIO import DictReader, DictWriter
from dictIO.utils.counter import BorgCounter

from ospx.utils.dict import find_key, find_type_identifier_in_keys


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
