import logging
import re
from pathlib import Path
from shutil import rmtree, copy2

from dictIO import CppDict, DictWriter, XmlFormatter
from dictIO.utils.counter import BorgCounter

from ospx import Simulation, SystemStructure
from ospx.utils.dict import find_key


__ALL__ = ['OspSimulationCase']

logger = logging.getLogger(__name__)


class OspSimulationCase():
    """OSP Simulation Case
    """

    def __init__(
        self,
        case_dict: CppDict,
    ):

        self.counter = BorgCounter()
        self.case_dict: CppDict = case_dict
        self.case_folder: Path = Path.cwd()
        self.system_structure: SystemStructure

        # Global settings
        self.simulation: Simulation             # general properties of the simulation case
        self._read_simulation()
        self.name: str = self.case_dict.name    # initialize conservatively (with fallback path)
        if self.simulation and self.simulation.name:
            self.name = self.simulation.name

        # Library source path
        self.lib_source: Path = Path.cwd()                                                                                                                    # initialize conservatively (with fallback path)
        if '_environment' in self.case_dict:
            if 'libSource' in self.case_dict['_environment']:
                self.lib_source = Path(self.case_dict['_environment']['libSource'])
            else:
                logger.warning(
                    f"no 'libSource' element found in {self.case_dict.name}['_environment']. Path to libSource will be set to current working directory."
                )
        else:
            logger.warning(
                f"no '_environment' section found in {self.case_dict.name}. Path to libSource hence is unknown and will be set to current working directory."
            )
        self.lib_source: Path = Path(self.case_dict['_environment']['libSource'])

    def setup(self):
        """Sets up the OSP simulation case folder.

        This will also copy all referenced FMUs from the library into the case folder.
        """
        logger.info(f"Set up OSP simulation case '{self.name}' in case folder: {self.case_folder}")

        # Clean up case folder
        self.clean()

        # Register and copy to local case folder all FMUs referenced by components in the case dict
        self._copy_fmus_from_library()

        # Read system structure
        if 'systemStructure' not in self.case_dict:
            logger.error(
                f"no 'systemStructure' section found in {self.case_dict.name}. Cannot set up OSP simulation case."
            )
            return
        self.system_structure = SystemStructure(self.case_dict['systemStructure'])

        # Make sure all components have a step size defined
        self._check_components_step_size()

    def clean(self):
        """Cleans up the case folder and deletes any existing ospx files, e.g. modelDescription.xml .fmu .csv etc.
        """

        # specify all files to be deleted (or comment-in / comment-out as needed)
        case_builder_result_files = [
            '*.csv',
            '*.out',
            '*.xml',
            '*.fmu',
            '*callGraph',
            '*.pdf',
            #'*.png',                   # 'protect results/*.png'
            'watchDict',
            'statisticsDict',           # 'results',
            'zip',
        ]

        logger.info(f'Clean OSP simulation case folder: {self.case_folder}')

        for pattern in case_builder_result_files:
            files = list(Path('.').rglob(pattern))
            for file in files:
                if file.is_file():
                    if not file.name.startswith('test_'):
                        file.unlink(missing_ok=True)
                else:
                    rmtree(file)

    def write_osp_model_description_xmls(self):
        """Writes the <component.name>_OspModelDescription.xml files for all components defined in the system structure

        """
        logger.info(
            f"Write OspModelDescription.xml files for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )
        if not self.system_structure or not self.system_structure.components:
            return
        for component in self.system_structure.components.values():
            component.write_osp_model_description_xml()
        return

    def write_osp_system_structure_xml(self):
        """Writes the OspSystemStructure.xml file
        """
        # sourcery skip: merge-dict-assign
        logger.info(
            f"Write OspSystemStructure.xml file for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        osp_system_structure: dict = {}
        osp_system_structure['_xmlOpts'] = {
            '_nameSpaces': {
                'osp': 'https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd'
            },
            '_rootTag': 'OspSystemStructure',
        }

        # Global Settings
        if self.simulation:
            if self.simulation.start_time:
                osp_system_structure['StartTime'] = self.simulation.start_time
            if self.simulation.base_step_size:
                osp_system_structure['BaseStepSize'] = self.simulation.base_step_size
            if self.simulation.algorithm:
                osp_system_structure['Algorithm'] = self.simulation.algorithm

        # Simulators (=Components)
        simulators: dict = {}
        for index, (_, component) in enumerate(self.system_structure.components.items()):
            simulator_key = f'{index:06d}_Simulator'
            simulator_properties = {
                '_attributes': {
                    'name': component.name,
                    'source': component.fmu.file.name,
                    'stepSize': component.step_size
                }
            }
            if component.initial_values:
                simulator_properties['InitialValues'] = {}
                for index, (_, variable) in enumerate(component.initial_values.items()):
                    if variable.start is not None and variable.data_type is None:
                        logger.error(
                            f"component {component.name}: An initial value is defined for variable {variable.name}, but its data type is not defined.\n"
                            f"The initial value for variable {variable.name} will not be written into OspSystemStructure.xml.\n"
                            "OspSystemStructure.xml will be potentially wrong or incomplete."
                        )
                    else:
                        initial_value_key = f'{index:06d}_InitialValue'
                        initial_value_properties: dict = {
                            '_attributes': {
                                'variable': variable.name
                            },
                            variable.data_type: {
                                '_attributes': {
                                    'value': variable.start
                                },
                            },
                        }
                        simulator_properties['InitialValues'][initial_value_key
                                                              ] = initial_value_properties
            simulators[simulator_key] = simulator_properties

        osp_system_structure['Simulators'] = simulators

        # Connections
        connections: dict = {}
        for connection in self.system_structure.connections.values():
            if connection.source and connection.target:
                connection_key = f'{self.counter():06d}_VariableConnection'
                # (note: the order 000000, 000001 is essential here!)
                connections[connection_key] = {
                    '000000_Variable': {
                        '_attributes': {
                            'simulator': connection.source.component,
                            'name': connection.source.variable,
                        }
                    },
                    '000001_Variable': {
                        '_attributes': {
                            'simulator': connection.target.component,
                            'name': connection.target.variable,
                        }
                    }
                }
        osp_system_structure['Connections'] = connections

        # Write OspSystemStructure.xml
        target_file = self.case_folder / 'OspSystemStructure.xml'
        formatter = XmlFormatter()
        DictWriter.write(osp_system_structure, target_file, formatter=formatter)

        self._correct_wrong_xml_namespace(
            'OspSystemStructure.xml',
            '<OspSystemStructure.*>?',
            '''<OspSystemStructure xmlns="http://opensimulationplatform.com/MSMI/OSPSystemStructure" version="0.1">''',
        )

        return

    def write_system_structure_ssd(self):
        """Writes the SystemStructure.ssd file
        """
        # sourcery skip: merge-dict-assign
        logger.info(
            f"Write SystemStructure.ssd file for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        system_structure_ssd: dict = {}
        system_structure_ssd['_xmlOpts'] = {
            '_nameSpaces': {
                'ssd': 'file:///C:/Software/OSP/xsd/SystemStructureDescription',
                'ssv': 'file:///C:/Software/OSP/xsd/SystemStructureParameterValues',
                'ssc': 'file:///C:/Software/OSP/xsd/SystemStructureCommon',
            },
            '_rootTag': 'SystemStructureDescription',
        }
        system_structure_ssd['System'] = {
            '_attributes': {
                'name': self.name,
                'description': self.name,
            }
        }

        # Global settings
        default_experiment = {
            'Annotations': {
                'Annotation': {
                    '_attributes': {
                        'type': "com.opensimulationplatform"
                    },
                    'Algorithm': {
                        'FixedStepAlgorithm': {
                            '_attributes': {
                                'baseStepSize': str(self.simulation.base_step_size),
                                'startTime': str(self.simulation.start_time),
                                'stopTime': str(self.simulation.stop_time)
                            }
                        }
                    }
                }
            }
        }
        system_structure_ssd['DefaultExperiment'] = default_experiment

        # Components
        components = {}
        for component_name, component in self.system_structure.components.items():
            connectors: dict = {}
            for connector in component.connectors.values():
                if connector.variable and connector.type:
                    connector_key = f'{self.counter():06d}_Connector'
                    # (note: the order 000000, 000001 is essential here!)
                    connectors[connector_key] = {
                        '_attributes': {
                            'name': connector.variable,
                            'kind': connector.type,
                        },
                        'Real': {},
                    }
            element_key = f'{self.counter():06d}_Component'
            components[element_key] = {
                '_attributes': {
                    'name': component_name,
                    'source': component.fmu.file.name,
                },
                'Connectors': connectors,
            }
        system_structure_ssd['System']['Elements'] = components

        # Connections
        connections: dict = {}
        for connection in self.system_structure.connections.values():
            if connection.source and connection.target:
                connection_key = f'{self.counter():06d}_Connection'
                connections[connection_key] = {
                    '_attributes': {
                        'startElement': connection.source.component,
                        'startConnector': connection.source.variable,
                        'endElement': connection.target.component,
                        'endConnector': connection.target.variable,
                    }
                }
        system_structure_ssd['System']['Connections'] = connections

        # Write SystemStructure.ssd
        target_file_path = Path.cwd() / 'SystemStructure.ssd'
        formatter = XmlFormatter(omit_prefix=False)
        DictWriter.write(system_structure_ssd, target_file_path, formatter=formatter)

        return

    def write_statistics_dict(self):
        """Writes selected properties of the system structure into a statistics dict.

        I.e. for documentation or further statistical analysis.
        """
        # sourcery skip: merge-dict-assign, simplify-dictionary-update
        logger.info(
            f"Write statistics dict for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        statistics_dict = {}

        statistics_dict['simulation'] = {'name': self.simulation.name}

        statistics_dict['components'] = {
            'count': len(self.system_structure.components.keys()),
            'names': list(self.system_structure.components.keys()),
        }

        statistics_dict['connections'] = {
            'count': len(self.system_structure.connections.keys()),
            'names': list(self.system_structure.connections.keys()),
        }

        statistics_dict['connectors'] = {
            'count': len(self.system_structure.connectors.keys()),
            'names': list(self.system_structure.connectors.keys()),
        }

        unit_list = []
        display_unit_list = []
        factors_list = []
        offsets_list = []
        for unit in self.system_structure.units.values():
            unit_list.append(unit.name)
            display_unit_list.append(unit.display_unit.name)
            factors_list.append(unit.display_unit.factor)
            offsets_list.append(unit.display_unit.offset)

        statistics_dict['units'] = {
            'count': len(self.system_structure.units.keys()),
            'unitNames': unit_list,
            'displayUnitNames': display_unit_list,
            'factors': factors_list,
            'offsets': offsets_list,
        }

        statistics_dict['variables'] = {
            'count': len(self.system_structure.variables.keys()),
            'names': list(self.system_structure.variables.keys()),
        }

        target_file_path = Path.cwd() / 'statisticsDict'

        DictWriter.write(statistics_dict, target_file_path, mode='a')

    def write_watch_dict(self):
        """Writes a case-specific watch dict file

        The watch dict file can be used with watchCosim for
            - convergence control
            - convergence plotting
            - extracting the results
        """
        logger.info(
            f"Write watch dict for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        watch_dict = {
            'datasources': {},
            'delimiter': ',',                   # 'objects': {},
            'simulation': {
                'name': self.simulation.name
            }
        }

        # Components
        for component_name, component in self.system_structure.components.items():
            no_of_connectors = len(component.connectors.keys())

            # @TODO: Time, StepCount, conn0, conn1, etc from modelDescription.xml ModelVariables
            #        should match connectors in caseDict for respective model.Improvement needed.
            #        FRALUM, 2021-xx-xx
            # columns = [0, 1]+[x+2 for x in range(no_of_connectors)]
            columns = [0, 1] + [x + 2 for x in range(no_of_connectors)]     # f*** StepCount

            watch_dict['datasources'].update({component_name: {'columns': columns}})

        target_file_path = Path.cwd() / 'watchDict'
        DictWriter.write(watch_dict, target_file_path, mode='a')

        return

    def _read_simulation(self):
        """Reads general simulation properties from case dict.
        """
        logger.info('reading simulation properties')    # 0

        if 'run' not in self.case_dict:
            return
        if 'simulation' not in self.case_dict['run']:
            return
        simulation = Simulation()
        simulation_properties = self.case_dict['run']['simulation']
        if 'name' in simulation_properties:
            simulation.name = simulation_properties['name']
        if 'startTime' in simulation_properties:
            simulation.start_time = simulation_properties['startTime']
        if 'stopTime' in simulation_properties:
            simulation.stop_time = simulation_properties['stopTime']
        if 'baseStepSize' in simulation_properties:
            simulation.base_step_size = simulation_properties['baseStepSize']
        if 'algorithm' in simulation_properties:
            simulation.algorithm = simulation_properties['algorithm']
        self.simulation = simulation

    def _copy_fmus_from_library(self):
        """Copies all referenced FMUs from the library into the case folder.

        Note: In case multiple components reference the same FMU, these get copied only once.
        """
        logger.info('Copy referenced FMUs from library into case folder')   # 0
        file_names_copied: list[str] = []
        components = self.case_dict['systemStructure']['components']

        for component_name, component_properties in components.items():
            if 'fmu' not in component_properties:
                logger.error(f"element 'fmu' missing in component {component_name}")
                return
            fmu_file_name_in_case_dict: str = component_properties['fmu']
            fmu_file_name = Path(fmu_file_name_in_case_dict).name
            fmu_file_in_library = self.lib_source / fmu_file_name_in_case_dict
            fmu_file_in_case_folder = self.case_folder / fmu_file_name
            if fmu_file_name not in file_names_copied:
                if not fmu_file_in_library.exists():
                    logger.error(
                        f'FMU file {fmu_file_name} referenced by component {component_name} does not exist in library {self.lib_source.absolute()}'
                    )
                    raise FileNotFoundError(f'file not found: {fmu_file_in_library.absolute()}')

                logger.info(f'copy {fmu_file_in_library} --> {fmu_file_in_case_folder}')
                copy2(fmu_file_in_library, self.case_folder)
                file_names_copied.append(fmu_file_name)

    def _check_components_step_size(self):
        """Ensure that all components have a step size defined.

        If a components step size is undefined, it will be set to the base step size.
        """
        if not self.system_structure or not self.system_structure.components:
            return
        if not self.simulation or not self.simulation.base_step_size:
            return
        for component in self.system_structure.components.values():
            if not component.step_size:
                component.step_size = self.simulation.base_step_size
        return

    def _set_components_step_size(self, step_size: float):
        """Overwrites the step size of all components with the passed in value"""
        if not self.system_structure or not self.system_structure.components:
            return
        for component in self.system_structure.components.values():
            component.step_size = step_size
        return

    def _inspect(self):
        """Inspects all components and all FMUs for the public variable names and units they declare, as documented in their modelDescription.xml's

        Results get logged to the console.
        """
        logger.info(
            f"Inspect OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        delim = '\t' * 3

        log_string = (
            f"Components and related FMUs as defined in {self.case_dict.name}\n"
            f"\tcomponent{delim}fmu{delim}\n\n"
        )
        for component_name, component in self.system_structure.components.items():
            log_string += f'\t{component_name}{delim}{component.fmu.file.name}\n'
        logger.info(log_string + '\n')

        log_string = (
            f"FMU attributes defined in the fmu's modelDescription.xml\n"
            f"\tfmu{delim}attributes{delim}"
        )
        for fmu_name, fmu in self.system_structure.fmus.items():
            log_string += f'\n\n\t{fmu_name}\n'
            fmu_attributes = '\n'.join(
                f'\t{delim}{k}{delim}{v}' for k,
                v in fmu.model_description['_xmlOpts']['_rootAttributes'].items()
            )
            log_string += fmu_attributes
            if default_experiment_key := find_key(fmu.model_description, 'DefaultExperiment$'):
                fmu_default_experiment = '\n'.join(
                    f'\t{delim}{k}{delim}{v}' for k,
                    v in fmu.model_description[default_experiment_key]['_attributes'].items()
                )
                log_string += f'\n{fmu_default_experiment}'
        logger.info(log_string + '\n')

        log_string = (
            f"Unit definitions defined in the fmu's modelDescription.xml\n"
            f"\tfmu{delim}unit{delim}display unit{delim}factor{delim}offset"
        )
        for fmu_name, fmu in self.system_structure.fmus.items():
            log_string += f'\n\n\t{fmu_name}\n'
            unit_definitions = '\n'.join(
                f'\t{delim}{unit_name}{delim}{unit.display_unit.name}\t{delim}{unit.display_unit.factor}{delim}{unit.display_unit.offset}'
                for unit_name,
                unit in fmu.unit_definitions.items()
            )
            log_string += unit_definitions
        logger.info(log_string + '\n')

        log_string = (
            f"Variables defined in the fmu's modelDescription.xml\n"
            f"\tfmu{delim}variable{delim}type{delim}unit"
        )
        for fmu_name, fmu in self.system_structure.fmus.items():
            log_string += f'\n\n\t{fmu_name}\n'
            variable_definitions = '\n'.join(
                f'\t{delim}{variable_name}{delim}{variable.data_type}{delim}{variable.unit}'
                for variable_name,
                variable in fmu.variables.items()
            )
            log_string += variable_definitions
        logger.info(log_string + '\n')

        log_string = (
            f"Connectors defined in {self.case_dict.name}\n"
            f"\tComponent{delim}Connector{delim}Variable{delim}Type"
        )
        for component_name, component in self.system_structure.components.items():
            if component.connectors:
                log_string += f'\n\n\t{component_name}\n'
                connector_definitions = '\n'.join(
                    f'\t{delim}{connector_name}{delim}{connector.variable}{delim}{connector.type}'
                    for connector_name,
                    connector in component.connectors.items()
                )
                log_string += connector_definitions
        logger.info(log_string + '\n')

        logger.info(
            f'inspect mode: Stopped after 1 case. You can now detail out the connector and connection elements in {self.case_dict.name} and then continue without --inspect'
        )

    def _write_plot_config_json(self):
        """Writes the PlotConfig.json file, containing postprocessing information
        """
        temp_dict = {'plots': []}
        if 'plots' in self.case_dict['postProcessing'].keys():
            for plot in self.case_dict['postproc']['plots'].values():
                variables: list[dict] = []
                for component_name, component in self.system_structure.components.items():
                    variables.extend(
                        {
                            'simulator': component_name,
                            'variable': connector.variable,
                        }
                        for connector_name,
                        connector in component.connectors.items()
                        if connector_name in plot['ySignals']
                    )

                temp_dict['plots'].append(
                    {
                        'label': plot['title'],
                        'plotType': 'trend',
                        'variables': variables,
                    }
                )

            target_file_path = Path.cwd() / 'PlotConfig.json'
            DictWriter.write(temp_dict, target_file_path)

        return

    def _correct_wrong_xml_namespace(self, file_name, pattern: str, replace: str):
        """Substitutes namespace
        (may be obsolete in future)
        """
        buffer = ''
        with open(file_name, 'r') as f:
            buffer = re.sub(pattern, replace, f.read())

        with open(file_name, 'w') as f:
            f.write(buffer)

        return
