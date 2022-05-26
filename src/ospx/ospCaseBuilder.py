import functools
import logging
import os
import re
from pathlib import Path
from shutil import copyfile
from typing import Sequence, Union
from shutil import rmtree

import graphviz as gv
from dictIO.cppDict import CppDict
from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.formatter import XmlFormatter
from dictIO.utils.counter import BorgCounter

from ospx import Component, Connection, Simulation, SystemStructure


__ALL__ = ['OspCaseBuilder', 'OspSimulationCase']

logger = logging.getLogger(__name__)


class OspCaseBuilder():
    """Builder for OSP-specific configuration files needed to run an OSP (co-)simulation case.
    """

    def __init__(self):
        return

    @staticmethod
    def build(
        case_dict_file: Union[str, os.PathLike[str]],
        inspect: bool = False,
        graph: bool = False,
    ):
        """Builds the OSP-specific configuration files needed to run an OSP (co-)simulation case.

        Builds following files:
            - OspSystemStructure.xml
            - SystemStructure.ssd
            - Plot.json
            - statisticsDict
            - watchDict

        Parameters
        ----------
        case_dict_file : Union[str, os.PathLike[str]]
            caseDict file. Contains all case-specific information OspCaseBuilder needs to generate the OSP files.
        inspect : bool, optional
            inspect mode. If True, build() checks all references in modelDescription.xml but does not actually create connectors and connections, by default False
        graph : bool, optional
            if True, creates a dependency graph image using graphviz, by default False

        Raises
        ------
        FileNotFoundError
            if case_dict_file does not exist
        """

        # Make sure source_file argument is of type Path. If not, cast it to Path type.
        case_dict_file = case_dict_file if isinstance(case_dict_file,
                                                      Path) else Path(case_dict_file)
        if not case_dict_file.exists():
            logger.error(f"OspCaseBuilder: File {case_dict_file} not found.")
            raise FileNotFoundError(case_dict_file)

        logger.info(f'reading {case_dict_file}')    # 0

        case_dict = DictReader.read(case_dict_file, comments=False)

        # first leave empty, may read defaults later
        case = OspSimulationCase(case_dict)
        case.initialize()

        if inspect:
            # inspect and stop
            case.inspect()
            # clean up
            # logger.info(f'inspect mode: delete {component.fmu.file.name}')
            # component.fmu.file.unlink()
            return

        case.write_osp_model_descriptions()
        case.write_osp_system_structure_xml()
        case.write_system_structure_ssd()

        if 'postProcessing' in case_dict.keys():
            case.write_plot_config()

        case.write_statistics()

        if graph:
            case.generate_dependency_graph()

        # comment out in favour of manual writing
        case.write_watch_dict()

        # run cosim run OspSystemStructure.xml -b 0 -e 10 -v

        return


class OspSimulationCase():
    """class OspSimulationCase
    """

    def __init__(
        self,
        case_dict: CppDict,
    ):

        self.counter = BorgCounter()
        self.case_dict: CppDict = case_dict

        self.name: str = self.case_dict['run']['simulation']['name']
        logger.info(f'initalizing simulation case {self.name}')     # 0

        self.lib_source: Path = Path(self.case_dict['_environment']['libSource'])
        self.simulation: Simulation     # general properties of the simulation case
        self.system_structure: SystemStructure

        self.case_folder: Path = Path.cwd()
        for key in self.case_dict['_environment'].keys():
            if re.match('root', key, re.I):
                self.case_folder: Path = Path.cwd() / self.case_dict['_environment'][key]

        if not self.case_folder.exists():
            logger.error(f'case folder {self.case_folder} does not exist')
            return

    def clear(self):
        """Removes all formerly generated case output files, retaining initial case configuration.
        """

        # specify all files to be deleted (or comment-in / comment-out as needed)
        case_builder_result_files = [
            '*.csv',
            '*.out',
            '*.xml',
            '*.fmu',
            '*callGraph',
            '*.pdf',
            '*.png',
            'watchDict',
            'statisticsDict',           # 'results',
            'zip',
        ]

        logger.info(f'clean case folder: {self.case_folder}')

        for pattern in case_builder_result_files:
            files = list(Path('.').rglob(pattern))
            for file in files:
                if file.is_file():
                    if not file.name.startswith('test_'):
                        file.unlink(missing_ok=True)
                else:
                    rmtree(file)

    def initialize(self):

        self.clear()

        # general properties
        self.read_simulation()

        # register and copy to local case folder all FMUs referenced by components in the case dict
        self.copy_fmus_from_library()

        self.system_structure = SystemStructure(self.case_dict['systemStructure'])

        # set master algorithm step size
        if self.simulation and self.simulation.base_step_size:
            self.set_step_size(self.simulation.base_step_size)

    def read_simulation(self):
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

    def copy_fmus_from_library(self):
        """Copies all referenced FMUs from the library into the case folder.

        Important: In case multiple components reference the same FMU, these are registered and copied only once.
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

                logger.info(f'copy {fmu_file_in_library} --> {fmu_file_in_case_folder}')    # 2
                copyfile(fmu_file_in_library, fmu_file_in_case_folder)
                file_names_copied.append(fmu_file_name)

    def set_step_size(self, step_size: float):
        if not self.system_structure or not self.system_structure.components:
            return
        for component in self.system_structure.components.values():
            component.step_size = step_size
        return

    def inspect(self):
        """Inspects all components and all FMUs for the public variable names and units they declare, as documented in their modelDescription.xml's
        """
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

    def write_osp_model_descriptions(self):
        if not self.system_structure or not self.system_structure.components:
            return
        for component in self.system_structure.components.values():
            # component.fmu.set_start_values(component.initial_values)
            component.write_osp_model_description()
        return

    def write_osp_system_structure_xml(self):
        """Writes OspSystemStructure.xml
        """

        # osp_ss meta data
        osp_system_structure: dict = {}

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

        osp_system_structure['_xmlOpts'] = {
            '_nameSpaces': {
                'osp': 'https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd'
            },
            '_rootTag': 'OspSystemStructure',
        }

        # Write OspSystemStructure.xml
        target_file = self.case_folder / 'OspSystemStructure.xml'
        formatter = XmlFormatter()
        DictWriter.write(osp_system_structure, target_file, formatter=formatter)

        self._xml_sub_wrong_namespace(
            'OspSystemStructure.xml',
            subst=(
                '<OspSystemStructure.*>?',
                '''<OspSystemStructure xmlns="http://opensimulationplatform.com/MSMI/OSPSystemStructure" version="0.1">'''
            )
        )

    def write_system_structure_ssd(self):
        """Collocates and writes SystemStructure.ssd
        """

        # global settings
        settings = {
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

        # Elements
        # (an 'element' in ssd equals what is a 'simulator' in osp, or a 'component' in ospx: An instance of a model.)
        elements = {}
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
            elements[element_key] = {
                '_attributes': {
                    'name': component_name,
                    'source': component.fmu.file.name,
                },
                'Connectors': connectors,
            }

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

        ssd = {
            'DefaultExperiment': settings,
            'System': {
                '_attributes': {
                    'name': self.name,
                    'description': self.name,
                },
                'Elements': elements,
                'Connections': connections,
            },
            '_xmlOpts': {
                '_nameSpaces': {
                    'ssd': 'file:///C:/Software/OSP/xsd/SystemStructureDescription',
                    'ssv': 'file:///C:/Software/OSP/xsd/SystemStructureParameterValues',
                    'ssc': 'file:///C:/Software/OSP/xsd/SystemStructureCommon',
                },
                '_rootTag': 'SystemStructureDescription',
            },
        }

        # Write SystemStructure.ssd

        target_file_path = Path.cwd() / 'SystemStructure.ssd'
        formatter = XmlFormatter(omit_prefix=False)
        DictWriter.write(ssd, target_file_path, formatter=formatter)

        return

    def write_plot_config(self):
        """writing postprocessing information
        e.g. PlotConfig.json
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

    def write_statistics(self):
        """collecting all measures
        and writing to dict for other non-specific purposes
        """
        # sourcery skip: merge-dict-assign, simplify-dictionary-update

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

    def generate_dependency_graph(self):
        """generating a dependency graph for documentation
        proper installation of graphviz is required
        """
        # default styles
        text_size = '11'
        styles = {
            'graph': {
                'label': f"{self.simulation.name}",
                'fontname': 'Verdana',
                'fontsize': text_size,
                'fontcolor': 'black',
                'bgcolor': 'white',
                'rankdir': 'TD',
                'overlap': 'compress',
                'sep': '10,100',
                'remincross': 'true',
                'ratio': 'fill',
                'margin': '0',
                'size': '10, 10!'
            },
            'nodes': {
                'fontname': 'Verdana',
                'fontsize': text_size,
                'fontcolor': 'white',
                'shape': 'square',
                'color': 'magenta',
                'style': 'filled',
                'fillcolor': 'magenta'
            },
            'edges': {
                'style': 'dashed',
                'color': 'magenta',
                'penwidth': '3',
                'arrowhead': 'open',
                'fontname': 'Verdana',
                'fontsize': text_size,
                'fontcolor': 'magenta'
            }
        }

        basic_op_names: str = '(power|dot|sum|diff|prod|div|quotient)'
        input_names: str = '^(INP|inp)'

        digraph = functools.partial(gv.Digraph, format='png')

        cg = digraph()

        cg = self._apply_styles(cg, styles)

        for component in self.system_structure.components.values():

            label_key, label = self._set_node_label(component)
            # var_keys = find_key(self.models[key]['InitialValues'], 'InitialValue')
            # variables = {}
            label = self._create_table(
                label_key,
                {
                    'source:': component.fmu.file.name,
                    'variables:': '',                       # 'stepsize:':self.models[key]['_attributes']['stepSize'],
                }
            )

            if re.search(input_names, component.name):
                shape = 'diamond'
                style = 'filled,rounded'
                fillcolor = '#FFFFFF'
            elif re.search(basic_op_names, component.name, re.I):
                # label = self._create_table(label_key, {'source:':component.fmu.file.name, 'stepsize:':component.step_size})
                label = label
                shape = 'square'
                style = 'filled, rounded'
                fillcolor = '#EEBBDD'
            else:
                shape = 'square'
                style = 'filled'
                fillcolor = '#DDDDEE'

            cg.node(
                label_key,
                label=label,
                fontname='Verdana',
                fontsize=text_size,
                fontcolor='black',
                shape=shape,
                color='black',
                style=style,
                fillcolor=fillcolor
            )

        for connection in self.system_structure.connections.values():
            if not (connection.source and connection.target):
                return
            if not (connection.source.component and connection.target.component):
                return
            from_key: str = connection.source.component
            to_key: str = connection.target.component
            label = self._set_edge_label(connection)

            if re.search(input_names, from_key, re.I):
                label = 'input\n%s' % label
                style = 'dashed'
                color = '#003399'
                fontcolor = '#003399'
                penwidth = '%i' % 1,
                weight = '%i' % 1

            elif re.search(basic_op_names, from_key, re.I):

                style = 'filled'
                color = '#995566'
                fontcolor = '#663344'
                penwidth = '%i' % 3,
                weight = '%.2f' % 0.66,

            else:

                style = 'bold'
                color = 'black'
                fontcolor = 'black'
                penwidth = '%i' % int(round((2)**1.5, 0)),
                weight = '%i' % int(round((2)**1.5, 0)),

            cg.edge(
                from_key,
                to_key,
                style=style,
                color=color,
                arrowhead='open',
                fontname='Verdana',
                fontsize=text_size,
                fontcolor=fontcolor,
                penwidth=str(penwidth),
                weight=str(weight),
                label=label,
                overlap='false',
                splines='true'
            )

        cg.render(f"{self.simulation.name}_callGraph", format='pdf')

    def write_watch_dict(self):
        """writing at most possible watchDict

        used by watchCosim for
            - convergence control
            - convergence plotting
            - extracting the results
        """
        watch_dict = {
            'datasources': {},
            'delimiter': ',',                   # 'objects': {},
            'simulation': {
                'name': self.simulation.name
            }
        }

        # append model
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

    def _xml_sub_wrong_namespace(self, file_name, subst: Sequence[str]):
        """Substitute namespace
        (may be obsolete in future)
        """
        buffer = ''
        with open(file_name, 'r') as f:
            buffer = re.sub(subst[0], subst[1], f.read())

        with open(file_name, 'w') as f:
            f.write(buffer)

        return

    def _apply_styles(self, digraph, styles):
        digraph.graph_attr.update(('graph' in styles and styles['graph']) or {})
        digraph.node_attr.update(('nodes' in styles and styles['nodes']) or {})
        digraph.edge_attr.update(('edges' in styles and styles['edges']) or {})
        return digraph

    def _set_node_label(self, component: Component):
        label = f"{component.name}\n___________\n\nfmu\n"
        label += re.sub(r'(^.*/|^.*\\|\.fmu.*$)', '', component.fmu.file.name)

        label_key = component.name
        return label_key, label

    def _set_edge_label(self, connection: Connection) -> str:
        if not (connection.source and connection.target):
            return ''
        return (f"{connection.source.component}"
                '-->'
                f"{connection.target.component}")

    def _create_table(self, name, child=None) -> str:

        child = child or {' ': ' '}
        n_child = len(child)
        string: str = (
            f'<\n<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">\n<TR>\n<TD COLSPAN="{2 * n_child:d}">{name}</TD>\n</TR>\n'
        )
        for key, item in child.items():
            string += f'<TR><TD>{key}</TD><TD>{item}</TD></TR>\n'
        string += '</TABLE>\n>'

        return string
