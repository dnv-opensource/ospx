import functools
import logging
# from msilib.schema import Component
import os
import re
from pathlib import Path
from shutil import copyfile
from typing import Sequence, Union

import graphviz as gv
from dictIO.cppDict import CppDict
from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.formatter import XmlFormatter
from dictIO.utils.counter import BorgCounter

from ospx.component import Component
from ospx.fmu import FMU
from ospx.utils.dict import shrink_dict, find_key


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
        case = OspSimulationCase(case_dict, inspect)

        case.clean()

        # general properties
        case.read_simulation_properties()

        # register and copy to local case folder all FMUs referenced by components in the case dict
        case.copy_fmus_from_library()

        # get models, get simulators
        case.read_components()

        if inspect:
            # inspect and stop
            case.inspect()
            return

        # this dict is to put into every NAME_OspModelDescription.xml
        case.unit_definitions = shrink_dict(
            case.unit_definitions, unique_keys=['_attributes', 'name']
        )

        case.variables = shrink_dict(case.variables, unique_keys=['_attributes', 'name'])

        case.get_connectors()   # useful to sort connections later

        case.get_connections()  # taken from manual config in parsed dict

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
        inspect: bool = False,
    ):

        self.counter = BorgCounter()
        self.case_dict: CppDict = case_dict
        self.inspect_mode: bool = inspect

        self.name: str = self.case_dict['run']['simulation']['name']
        logger.info(f'initalizing simulation case {self.name}')     # 0

        self.baseStepSize: float = self.case_dict['run']['simulation']['baseStepSize']

        self.case_folder: Path = Path.cwd()
        for key in self.case_dict['_environment'].keys():
            if re.match('root', key, re.I):
                self.case_folder: Path = Path.cwd() / self.case_dict['_environment'][key]

        if not self.case_folder.exists():
            logger.error(f'case folder {self.case_folder} does not exist')
            return

        self.lib_source: Path = Path(self.case_dict['_environment']['libSource'])

        self.unit_definitions: dict = {}            # all unique unit definitions
        self.variables: dict = {}                   # all ScalarVariables from all fmu's
        self.attributes: dict = {}                  # all original attributes from all fmu's
        self.connectors: dict = {}                  # all connectors from all fmu's
        self.simulation: dict = {}                  # general properties of the simulation case
        self.components: dict[str, Component] = {
        }                                           # component = instance of a model. OSP calls this 'simulator'.
        self.fmus: dict[str, FMU] = {}              # register of FMUs referenced by the components
        self.connections: dict = {}                 # to be filled with connection data

    def clean(self):
        """Removes all formerly generated case output files, retaining initial case configuration.
        """

        # specify all files to be deleted (or comment-in / comment-out as needed)
        file_types = [
            '*.csv',
            '*.out',
            '*.xml',
            '*.fmu',
            '*callGraph',
            '*.pdf',
            '*.png',
            'watchDict',
            'statisticsDict',   # 'results',
            'zip',
        ]

        logger.info(f'clean case folder: {self.case_folder}')

        for file_type in file_types:
            files = list(Path('.').rglob(file_type))

            for file in files:
                if Path(file).is_file():
                    os.remove(file)
                else:
                    from shutil import rmtree
                    rmtree(file)

    def read_simulation_properties(self):
        """Reads general simulation properties from case dict.
        """
        logger.info('reading simulation properties')    # 0

        # self.simulation_dict = dict({k:str(v) for k, v in self.config['simulation'].items() if re.match('(StartTime|BaseStepSize|Algorithm)', k)})
        self.simulation = dict(self.case_dict['run']['simulation'].items())

    def copy_fmus_from_library(self):
        """Copies all referenced FMUs from the library into the case folder.

        Important: In case multiple components reference the same FMU, these are registered and copied only once.
        """
        logger.info('Copy referenced FMUs from library into case folder')   # 0

        components = self.case_dict['systemStructure']['components']

        self.fmus.clear()
        for component_name, component_properties in components.items():
            if 'fmu' not in component_properties:
                logger.error(f"element 'fmu' missing in component {component_name}")
                return
            fmu_file_name_in_case_dict: str = component_properties['fmu']
            fmu_file_name = Path(fmu_file_name_in_case_dict).name
            fmu_file_in_library = self.lib_source / fmu_file_name_in_case_dict
            fmu_file_in_case_folder = self.case_folder / fmu_file_name
            if fmu_file_name not in self.fmus:
                if not fmu_file_in_library.exists():
                    logger.error(
                        f'FMU file {fmu_file_name} referenced by component {component_name} does not exist in library {self.lib_source.absolute()}'
                    )
                    raise FileNotFoundError(f'file not found: {fmu_file_in_library.absolute()}')

                logger.info(f'copy {fmu_file_in_library} --> {fmu_file_in_case_folder}')    # 2
                copyfile(fmu_file_in_library, fmu_file_in_case_folder)
                self.fmus[fmu_file_name] = FMU(fmu_file_in_case_folder)

    def read_components(self):
        """Read the components from case dict
        """
        logger.info('read components from case dict')   # 0

        components = self.case_dict['systemStructure']['components']

        self.components.clear()
        for component_name, component_properties in components.items():
            component = Component(component_name, component_properties)     # type: ignore
            component.step_size = self.baseStepSize
            self.components[component_name] = component

            if not self.inspect_mode:
                component.fmu.set_start_values(component.initial_values)
                component.write_osp_model_description()
                # self.attributes.update(
                #     {component.name: model_description['_xmlOpts']['_rootAttributes']}
                # )

            if self.inspect_mode:
                # clean up
                logger.info(f'inspect mode: delete {component.fmu.file.name}')
                component.fmu.file.unlink()

        return

    def get_connectors(self):
        """Reads connectors from case_dict into a dict of connectors
        """
        components = self.case_dict['systemStructure']['components']
        for component_name, component in components.items():
            if 'connectors' in component:
                for connector_name, connector in component['connectors'].items():
                    if 'generateProxy' in component:                        # if NTNU-IHB fmu-proxy code is used
                        connector['component'] = f'{component_name}-proxy'  # use "proxy"-reference
                    else:
                        connector['component'] = component_name
                    self.connectors[connector_name] = connector             # save connector

    def get_connections(self):
        """Reads connections from case_dict into a dict of connections
        """
        connections = self.case_dict['systemStructure']['connections']
        for _, connection in connections.items():

            # Read 'component' and 'reference' properties of source connector
            source_connector_name = connection['source']
            source_connector = self.connectors[source_connector_name]
            source_component = source_connector['component']
            source_reference = source_connector['reference']
            # Read 'component' and 'reference' properties of target connector
            target_connector_name = connection['target']
            target_connector = self.connectors[target_connector_name]
            target_component = target_connector['component']
            target_reference = target_connector['reference']

            # Save connection
            # (note: the order 000000, 000001 is essential here!)
            connection_name = f'{self.counter():06d}_VariableConnection'
            self.connections[connection_name] = {
                '000000_Variable': {
                    '_attributes': {
                        'simulator': source_component, 'name': source_reference
                    }
                },
                '000001_Variable': {
                    '_attributes': {
                        'simulator': target_component, 'name': target_reference
                    }
                }
            }

        return

    def inspect(self):
        """Inspects all FMUs for the public variable names and units they declare (as documented in their modelDescription.xml's)
        """
        delim = '\t' * 3
        logger.info("Main attributes collected from modelDescription.xml's")    # 0
        logger.info(f'name{delim}attributes{delim}\n')                          # 1

        uuid_set = set([])
        suspect_names = set([])
        for old_len, (key, item) in enumerate(self.attributes.items(), start=1):
            substring = '\n'.join(f'{delim}{k}{delim}{v}' for k, v in item.items())

            logger.info(key)        # 1
            logger.info(substring)  # 1
            uuid_set.add(item['guid'])
            if old_len != len(uuid_set):
                suspect_names.add(key)

        logger.info("Unit definitions collected from modelDescription.xml's")   # 0
        logger.info(f'unit{delim}factor{delim}offset\n')                        # 1

        for key, item in self.unit_definitions.items():
            real_key = find_key(item, 'DisplayUnit$')[0]
            logger.info(
                f"{item['_attributes']['name']}{delim}{item[real_key]['_attributes']['factor']}{delim}{item[real_key]['_attributes']['offset']}"
            )

        logger.info("Exposed variables (connectors) collected from modelDescription.xml's")     # 0
        logger.info(f'origin\t{delim}connector{delim}unit\n')                                   # 1

        for key, item in self.variables.items():
            try:
                real_key = find_key(item, 'Real$')[0]
                string = f"{item['_origin']}{delim}{item['_attributes']['name']}{delim}{item[real_key]['_attributes']['unit']}"

            except Exception:
                string = f"{item['_origin']}{delim}{item['_attributes']['name']}"
            logger.info(string)     # 1
        logger.info('')

        if len(uuid_set) != len(self.attributes):
            logger.warning(
                f"there are fmu's with the same guid, apply generate_proxy=True -- at least to {(', '.join(suspect_names))} -- to avoid related errors"
            )

        logger.info(
            f'inspect mode: Stopped after 1 case. You can now detail out the connector and connection elements in {self.case_dict.name} and then continue without --inspect'
        )

    def write_osp_system_structure_xml(self):
        """Writes OspSystemStructure.xml
        """

        # osp_ss meta data
        osp_system_structure: dict = {
            k: v
            for k,
            v in self.simulation.items()
            if re.match('(StartTime|BaseStepSize|Algorithm)', k)
        }

        # models (simulators)
        # ('simulators' is OSP terminology. Any instance of a model is referred to as a 'simulator' in OSP.)
        simulators: dict = {}
        for index, (_, component) in enumerate(self.components.items()):
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
                    initial_value_key = f'{index:06d}_InitialValue'
                    initial_value_properties: dict = {
                        '_attributes': {
                            'variable': variable.name
                        },
                        variable.fmi_data_type: {
                            '_attributes': {
                                'value': variable.initial_value
                            },
                        },
                    }

                    simulator_properties['InitialValues'][initial_value_key
                                                          ] = initial_value_properties
            simulators[simulator_key] = simulator_properties

        osp_system_structure['Simulators'] = simulators
        osp_system_structure['Connections'] = self.connections
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
                                'baseStepSize': str(self.simulation['baseStepSize']),
                                'startTime': str(self.simulation['startTime']),
                                'stopTime': str(self.simulation['stopTime'])
                            }
                        }
                    }
                }
            }
        }

        # elements
        # (an 'element' in ssd equals what is a 'simulator' in osp_ss: An instance of a model.)
        elements = {}
        for component_key, component in self.components.items():
            connectors = {
                f'{self.counter():06d}_Connector': {
                    '_attributes': {
                        'name': self.connectors[connector_key]['reference'],
                        'kind': self.connectors[connector_key]['type']
                    },
                    'Real': {},
                }
                for connector_key in self.connectors
                if self.connectors[connector_key]['component'] == component.name
            }

            elements[f'{self.counter():06d}_Component'] = {
                '_attributes': {
                    'name': component.name,
                    'source': component.fmu.file.name,
                },
                'Connectors': connectors,
            }

        # connections
        connections = {
            f'{self.counter():06d}_Connection': {
                '_attributes': {
                    'startElement': connection['000000_Variable']['_attributes']['simulator'],
                    'startConnector': connection['000000_Variable']['_attributes']['name'],
                    'endElement': connection['000001_Variable']['_attributes']['simulator'],
                    'endConnector': connection['000001_Variable']['_attributes']['name'],
                }
            }
            for _,
            connection in self.connections.items()
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
        if 'plots' in self.case_dict['postproc'].keys():
            for key, item in self.case_dict['postproc']['plots'].items():
                variables = [
                    dict(
                        {
                            'simulator': self.connectors[key1]['inModel'],
                            'variable': self.connectors[key1]['reference'],
                        }
                    ) for key1,
                    item1 in self.connectors.items() if key1 in item['ySignals']
                ]

                temp_dict['plots'].append(
                    {
                        'label': item['title'],
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

        statistics_dict['simulation'] = {'name': self.case_dict['run']['simulation']['name']}

        statistics_dict['components'] = {
            'count': len(self.case_dict['systemStructure']['components'].keys()),
            'names': list(self.case_dict['systemStructure']['components'].keys()),
        }

        statistics_dict['connections'] = {
            'count': len(self.case_dict['systemStructure']['connections'].keys()),
            'names': list(self.case_dict['systemStructure']['connections'].keys()),
        }

        statistics_dict['connectors'] = {
            'count': len(self.connectors.keys()),
            'names': list(self.connectors.keys()),
        }

        unit_list = []
        display_unit_list = []
        factors_list = []
        offsets_list = []
        for _, item in self.unit_definitions.items():
            display_unit_key = find_key(item, 'DisplayUnit$')[0]
            unit_list.append(item['_attributes']['name'])
            display_unit_list.append(item[display_unit_key]['_attributes']['name'])
            factors_list.append(item[display_unit_key]['_attributes']['factor'])
            offsets_list.append(item[display_unit_key]['_attributes']['offset'])

        statistics_dict['units'] = {
            'count': len(self.unit_definitions.keys()),
            'unitNames': unit_list,
            'displayUnitNames': display_unit_list,
            'factors': factors_list,
            'offsets': offsets_list,
        }

        variables_list = [item['_attributes']['name'] for key, item in self.variables.items()]

        statistics_dict['variables'] = {
            'count': len(self.variables.keys()),
            'variableNames': variables_list,
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
                'label': f"{self.simulation['name']}",
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

        basic_op_names = '(power|dot|sum|diff|prod|div|quotient)'
        input_names = '^(INP|inp)'

        digraph = functools.partial(gv.Digraph, format='png')

        cg = digraph()

        cg = self._apply_styles(cg, styles)

        for _, component in self.components.items():

            label_key, label = self._set_node_label(component.name, component)
            # var_keys = find_key(self.models[key]['InitialValues'], 'InitialValue')
            # variables = {}
            label = self._create_table(
                label_key,
                {
                    'source:': component.fmu,
                    'variables:': '',           # 'stepsize:':self.models[key]['_attributes']['stepSize'],
                }
            )

            if re.search(input_names, component.name):
                shape = 'diamond'
                style = 'filled,rounded'
                fillcolor = '#FFFFFF'
            elif re.search(basic_op_names, component.name, re.I):
                # label = self._create_table(label_key, {'source:':self.models_dict[key]['_attributes']['source'], 'stepsize:':self.models_dict[key]['_attributes']['stepSize']})
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

        for connection_key, connection in self.connections.items():

            from_key = connection['000000_Variable']['_attributes']['simulator']
            to_key = connection['000001_Variable']['_attributes']['simulator']
            label = self._set_edge_label(connection_key, connection)

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
                penwidth = '%i' % int(round((len(connection))**1.5, 0)),
                weight = '%i' % int(round((len(connection))**1.5, 0)),

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

        cg.render(f"{self.simulation['name']}_callGraph", format='pdf')

    def write_watch_dict(self):
        """writing at most possible watchDict

        used by watchCosim for
            - convergence control
            - convergence plotting
            - extracting the results
        """
        watch_dict = {
            'datasources': {},
            'delimiter': ',',                       # 'objects': {},
            'simulation': {
                'name': self.simulation['name']
            }
        }

        # append model
        for _, component in self.components.items():
            last_index = sum(
                c_item['component'] == component.name for _, c_item in self.connectors.items()
            )

            # Time, StepCount, conn0, conn1, etc from modelDescription.xml ModelVariables
            # should match connectors in caseDict for respective model
            # improvement needed
            # columns = [0, 1]+[x+2 for x in range(last_index)]
            columns = [0, 1] + [x + 2 for x in range(last_index)]   # f*** StepCount

            watch_dict['datasources'].update({component.name: {'columns': columns}})

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

    def _set_node_label(self, key, sub_dict):
        label = f"{sub_dict['_attributes']['name']}\n___________\n\nfmu\n"
        label += re.sub(r'(^.*/|^.*\\|\.fmu.*$)', '', sub_dict['_attributes']['fmu'])

        label_key = sub_dict['_attributes']['name']
        return label_key, label

    def _set_edge_label(self, key, sub_dict):
        return (
            f"{sub_dict['000000_Variable']['_attributes']['simulator']}"
            '-->'
            f"{sub_dict['000001_Variable']['_attributes']['simulator']}"
        )

    def _create_table(self, name, child=None):

        child = child or {' ': ' '}
        n_child = len(child)
        string = (
            f'<\n<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">\n<TR>\n<TD COLSPAN="{2 * n_child:d}">{name}</TD>\n</TR>\n'
        )
        for key, item in child.items():
            string += f'<TR><TD>{key}</TD><TD>{item}</TD></TR>\n'
        string += '</TABLE>\n>'

        return string
