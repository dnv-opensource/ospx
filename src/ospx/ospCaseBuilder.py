import functools
import logging
# from msilib.schema import Component
import os
import re
import subprocess
from collections import OrderedDict
from pathlib import Path
from shutil import copyfile
from typing import MutableMapping, Sequence, Union
from zipfile import ZipFile

import graphviz as gv
from dictIO.cppDict import CppDict
from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.formatter import XmlFormatter
from dictIO.utils.counter import BorgCounter

from ospx.fmu import FMU
from ospx.component import Component

from ospx.utils.zip import (
    rename_file_in_zip,
)


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
        case.register_fmus()

        # get models, get simulators
        case.read_components()

        if inspect:
            # inspect and stop
            case.inspect()
            return

        # this dict is to put into every NAME_OspModelDescription.xml
        case.unit_definitions = _shrink_dict(
            case.unit_definitions, make_unique=['_attributes', 'name']
        )

        case.variables = _shrink_dict(case.variables, make_unique=['_attributes', 'name'])

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

        self.baseStepSize: str = self.case_dict['run']['simulation']['baseStepSize']

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

    def register_fmus(self):
        """Register all FMUs referenced by components in the case dict, and copy them into the case folder.

        Important: In case multiple components reference the same FMU, these are registered and copied only once.
        """
        logger.info('register FMUs referenced in case dict')    # 0

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
                                                                            # Have each component point to the correct FMU instance it references
            fmu_file_name_in_case_dict: str = component_properties['fmu']
            fmu_file_name = Path(fmu_file_name_in_case_dict).name
            component.fmu = self.fmus[fmu_file_name]
            self.components[component_name] = component

            self._prepare_component(
                component,
                write_osp_model_description=True,
            )

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
            real_key = self._find_numbered_key_by_string(item, 'DisplayUnit$')[0]
            logger.info(
                f"{item['_attributes']['name']}{delim}{item[real_key]['_attributes']['factor']}{delim}{item[real_key]['_attributes']['offset']}"
            )

        logger.info("Exposed variables (connectors) collected from modelDescription.xml's")     # 0
        logger.info(f'origin\t{delim}connector{delim}unit\n')                                   # 1

        for key, item in self.variables.items():
            try:
                real_key = self._find_numbered_key_by_string(item, 'Real$')[0]
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
        osp_ss: dict = {
            k: v
            for k,
            v in self.simulation.items()
            if re.match('(StartTime|BaseStepSize|Algorithm)', k)
        }

        # models (simulators)
        # ('simulators' is OSP terminology. Any instance of a model is referred to as a 'simulator' in OSP.)
        models: dict = {
            k1: {
                k2:
                {k3: v3
                 for k3, v3 in self.components[k1][k2].items()
                 if not re.match('fmu', k3)}
                for k2 in self.components[k1].keys()
            }
            for k1 in self.components.keys()
        }
        osp_ss['Simulators'] = models
        osp_ss['Connections'] = self.connections
        osp_ss['_xmlOpts'] = {
            '_nameSpaces': {
                'osp': 'https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd'
            },
            '_rootTag': 'OspSystemStructure',
        }

        # Write OspSystemStructure.xml
        target_file_path = Path.cwd() / 'OspSystemStructure.xml'
        formatter = XmlFormatter()
        DictWriter.write(osp_ss, target_file_path, formatter=formatter)

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

        # models (elements)
        # (an 'element' in ssd equals what is a 'simulator' in osp_ss: An instance of a model.)
        models = {}
        for key, item in self.components.items():

            connectors = dict({})

            for key1, item1 in self.connectors.items():
                i = self.counter()

                if self.connectors[key1]['component'] == self.components[key]['_attributes']['name'
                                                                                             ]:
                    connectors['%06i_Connector' % i] = {
                        '_attributes': {
                            'name': self.connectors[key1]['reference'],
                            'kind': self.connectors[key1]['type']
                        },
                        'Real': {},
                    }
            # parameter_bindings = {}

            j = self.counter()
            models['%06i_Component' % j] = {
                '_attributes': {
                    'name': self.components[key]['_attributes']['name'],
                    'source': self.components[key]['_attributes']['source'],
                },
                'Connectors': connectors,                                       # 'ParameterBindings': parameter_bindings,
            }

        # connections
        connections = {}
        for key, item in self.connections.items():
            i = self.counter()

            connections['%06i_Connection' % i] = {
                '_attributes': {
                    'startElement':
                    self.connections[key]['000000_Variable']['_attributes']['simulator'],
                    'startConnector':
                    self.connections[key]['000000_Variable']['_attributes']['name'],
                    'endElement':
                    self.connections[key]['000001_Variable']['_attributes']['simulator'],
                    'endConnector':
                    self.connections[key]['000001_Variable']['_attributes']['name'],
                }
            }

        ssd = {
            'DefaultExperiment': settings,
            'System': {
                '_attributes': {
                    'name': self.name,
                    'description': self.name,
                },
                'Elements': models,
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
            display_unit_key = self._find_numbered_key_by_string(item, 'DisplayUnit$')[0]
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

        for key in self.components.keys():

            label_key, label = self._set_node_label(self.components[key]['_attributes']['name'], self.components[key])
            # var_keys = self._find_numbered_key_by_string(self.models[key]['InitialValues'], 'InitialValue')
            # variables = {}
            label = self._create_table(
                label_key,
                {
                    'source:': self.components[key]['_attributes']['source'],
                    'variables:': '',                                           # 'stepsize:':self.models[key]['_attributes']['stepSize'],
                }
            )

            if re.search(input_names, self.components[key]['_attributes']['name']):
                shape = 'diamond'
                style = 'filled,rounded'
                fillcolor = '#FFFFFF'
            elif re.search(basic_op_names, self.components[key]['_attributes']['name'], re.I):
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

        for key in self.connections:

            from_key = self.connections[key]['000000_Variable']['_attributes']['simulator']
            to_key = self.connections[key]['000001_Variable']['_attributes']['simulator']
            label = self._set_edge_label(key, self.connections[key])

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
                penwidth = '%i' % int(round((len(self.connections[key]))**1.5, 0)),
                weight = '%i' % int(round((len(self.connections[key]))**1.5, 0)),

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
        for m_key, m_item in self.components.items():
            last_index = sum(
                c_item['component'] == m_item['_attributes']['name'] for _,
                c_item in self.connectors.items()
            )

            # Time, StepCount, conn0, conn1, etc from modelDescription.xml ModelVariables
            # should match connectors in caseDict for respective model
            # improvement needed
            # columns = [0, 1]+[x+2 for x in range(last_index)]
            columns = [0, 1] + [x + 2 for x in range(last_index)]   # f*** StepCount

            watch_dict['datasources'].update({m_item['_attributes']['name']: {'columns': columns}})

        target_file_path = Path.cwd() / 'watchDict'
        DictWriter.write(watch_dict, target_file_path, mode='a')

    def _prepare_component(
        self,
        component: Component,
        write_osp_model_description: bool = False,
    ):
        """Writes OspModelDescription.xml and sets / initializes its parameters to their case specific values.
        """
        source_fmu_file = Path(self.lib_source) / Path(fmu_file_name)
        target_fmu_file = self.case_folder / Path(f'{component}.fmu')
        target_xml_file = self.case_folder / Path(f'{component}_OspModelDescription.xml')

        # if not in "inspect mode"
        # also change modelDescription.xml (in zip file) for completeness
        if not self.inspect_mode:
            component.fmu.set_start_values(component.variables_with_initial_values)
            self.attributes.update(
                {component.name: model_description['_xmlOpts']['_rootAttributes']}
            )

        if not self.inspect_mode:

            # Copy FMU and rename all dll's therein.
            # required by STC
            # @TODO: @Frank: Why is this necessary?
            # Copying and altering the FMU should only be necessary in case of remote access (-> proxification).
            # But as long as proxification isn't required, there should be no need to copy and alter the FMU?
            # CLAROS, 2022-05-17
            self._generate_copy(
                target_fmu_file, fmu_name, component, remote_access, generate_proxy
            )
            # proxify_fmu()

        if write_osp_model_description is True and not self.inspect_mode:
            self._write_osp_model_description(target_xml_file)

        if self.inspect_mode is True:
            # final clean if --inspect
            logger.info(f'rm {target_fmu_file}')
            os.remove(target_fmu_file)

        return

    def _write_osp_model_description(self, target_xml_file: Path):
        """writing OspModelDescription.xml
        """
        osp_md = dict({'UnitDefinitions': self.unit_definitions})

        osp_md['VariableGroups'] = {}

        temp_dict = dict({})

        for key, item in self.variables.items():

            real_key = ''
            try:
                real_key = self._find_numbered_key_by_string(item, 'Real$')[0]
                if 'quantity' in item[real_key]['_attributes'].keys():
                    quantity_name = item[real_key]['_attributes']['quantity']
                    quantity_unit = item[real_key]['_attributes']['unit']
                else:
                    quantity_name = 'UNKNOWN'
                    quantity_unit = 'UNKNOWN'

            except Exception:
                logger.warning(f'no quantity or unit given for {key}')
                quantity_name = 'UNKNOWN'
                quantity_unit = 'UNKNOWN'

            i = self.counter()
            temp_dict['%06i_Generic' % i] = {
                '_attributes': {
                    'name': quantity_name
                },
                quantity_name: {
                    '_attributes': {
                        'name': quantity_name
                    },
                    'Variable': {
                        '_attributes': {
                            'ref': item['_attributes']['name'],
                            'unit': quantity_unit,
                        }
                    },
                },
            }

        # this is the content of OspModelDescription
        osp_md['VariableGroups'] = temp_dict

        # _xmlOpts
        osp_md['_xmlOpts'] = {
            '_nameSpaces': {
                'osp': 'https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd'
            },
            '_rootTag': 'ospModelDescription',
        }

        DictWriter.write(osp_md, target_xml_file)

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

    def _find_numbered_key_by_string(self, dd, search_string):
        """find the element name for an (anyways unique) element
        after it was preceeded by a number to keep the sequence of xml elements
        as this is not the "nature" of dicts
        """
        try:
            return [k for k in dd.keys() if re.search(search_string, k)]
        except Exception:
            return ['ELEMENTNOTFOUND']

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

    def _generate_copy(
        self,
        target_fmu_file: Path,
        fmu_name: str,
        model_name: str,
        remote_access: Union[MutableMapping, None],
        generate_proxy: bool
    ):
        '''generate_proxy and remote_access are relatives:
        there is no remote acess without generating proxy.
        but nowadays, all fmu uploaded to STC needs special "generate_proxy" treatment, now called generate copy
        the problem is, that I could not find so far a way to host one fmu in model library (STC) and using it several times in the same simulation
        This might be solved in the future
        '''
        # read file names of all *.dll files contained in target_fmu_file
        with ZipFile(target_fmu_file, 'r') as document:
            files_to_modify = [
                file.filename
                for file in document.infolist()
                if re.search(r'.*\.dll$', file.filename)
            ]

        # rename first from ['_attributes']['fmu'] to ['_attributes']['source']
        destination_file_names = [re.sub(fmu_name, model_name, file) for file in files_to_modify]

        for file_name, new_file_name in zip(files_to_modify, destination_file_names):
            logger.info(
                f'{model_name} generate_proxy or modify: renaming {file_name} to {new_file_name}'
            )
            rename_file_in_zip(target_fmu_file, file_name, new_file_name)

        new_name = f'{model_name}-proxy' if generate_proxy else model_name  # change the name only in case fmu is to be proxified

        # update models_dict
        for _, model_properties in self.components.items():

            if model_properties['_attributes']['name'] == model_name:
                logger.info(
                    f'{model_name} generate_proxy: renaming {model_name} to {new_name} / {new_name}.fmu'
                )

                model_properties['_attributes']['name'] = new_name
                model_properties['_attributes']['source'] = f'{new_name}.fmu'

        if remote_access:
            # Proxify the FMU
            remote_string = f"--remote={remote_access['host']}:{remote_access['port']}"
            command = (f'fmu-proxify {model_name}.fmu {remote_string}')
            try:
                subprocess.run(command, timeout=60)
            except subprocess.TimeoutExpired:
                logger.exception(f'Timeout occured when calling {command}.')


def proxify_fmu(fmu: FMU, host: str, port: int):
    """Proxifies an FMU

    Generates fmu-proxy (NTNU-IHB/fmu-proxify)
    """
    remote_string = f"--remote={host}:{port}"
    command = (f'fmu-proxify {fmu.file.name} {remote_string}')
    try:
        subprocess.run(command, timeout=60)
    except subprocess.TimeoutExpired:
        logger.exception(f'Timeout occured when calling {command}.')


def _shrink_dict(dictionary, make_unique=None):
    """function removes doubled entries in dicts
    """
    make_unique = make_unique or ['']
    make_unique = "['" + "']['".join(make_unique) + "']"
    # sort an ordered dict for attribute (child) where the dict is to make unique for
    eval_string = f'sorted(dictionary.items(), key=lambda x: x[1]{make_unique})'

    # list doubles and remember for deleting
    seen = set([])
    remove_key = []

    for key, value in OrderedDict(eval(eval_string)).items():
        proove_value = eval(f'value{make_unique}')
        if proove_value in seen:
            remove_key.append(key)
        else:
            seen.add(eval(f'value{make_unique}'))

    out_dict = dict({})

    for key in dictionary.keys():
        if key not in remove_key:
            out_dict[key] = dictionary[key]

    return out_dict
