import functools
import logging
import os
import platform
import re
import subprocess
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path
from shutil import copyfile
from typing import MutableMapping, Sequence, Union
from zipfile import ZipFile

import graphviz as gv
from dictIO.cppDict import CppDict
from dictIO.dictReader import DictReader
from dictIO.dictWriter import DictWriter
from dictIO.formatter import XmlFormatter
from dictIO.parser import XmlParser
from dictIO.utils.counter import BorgCounter

from ospx.utils.zip import (
    add_file_content_to_zip,
    read_file_content_from_zip,
    remove_files_from_zip,
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
        case.get_simulation_properties()

        # get models, get simulators
        case.get_components()

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
        self.baseStepSize: str = self.case_dict['run']['simulation']['baseStepSize']

        self.work_dir: Path = Path.cwd()
        for key in self.case_dict['_environment'].keys():
            if re.match('root', key, re.I):
                self.work_dir: Path = Path.cwd() / self.case_dict['_environment'][key]

        if not self.work_dir.exists():
            logger.error(f'work dir {self.work_dir} does not exist')

        self.lib_source: Path = Path(self.case_dict['_environment']['libSource'])

        self.unit_definitions: dict = {}    # all unique unit definitions
        self.variables: dict = {}           # all ScalarVariables from all fmu's
        self.attributes: dict = {}          # all original attributes from all fmu's
        self.connectors: dict = {}          # all connectors from all fmu's

        self.simulation: dict = {}                          # to be filled with general simulation properties
        self.models: dict = {}                              # to be filled with model data as they appear in simulators
        self.connections: dict = {}                         # to be filled with connection data
        logger.info(f'initalizing simulation {self.name}')  # 0

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

        logger.info('remove all existing case files')

        for file_type in file_types:
            files = list(Path('.').rglob(file_type))

            for file in files:
                if Path(file).is_file():
                    os.remove(file)
                else:
                    from shutil import rmtree
                    rmtree(file)

    def get_simulation_properties(self):
        """Reads simulation base properties.
        """
        logger.info('reading simulation properties')    # 0

        # self.simulation_dict = dict({k:str(v) for k, v in self.config['simulation'].items() if re.match('(StartTime|BaseStepSize|Algorithm)', k)})
        self.simulation = dict(self.case_dict['run']['simulation'].items())

    def get_components(self):
        """Reads components from case_dict into a dict of models
        """
        logger.info('read model information from case dict')    # 0

        components = self.case_dict['systemStructure']['components']
        for model_index, (model_name, model_properties) in enumerate(components.items()):

            generate_proxy = False
            remote_access: Union[MutableMapping, None] = None

            simulator_id = f'{model_index:06d}_Simulator'

            # Attributes
            self.models[simulator_id] = {
                '_attributes': {
                    'name': model_name,
                    'source': f'{model_name}.fmu',
                    'fmu': model_properties['fmu'],
                    'stepSize': self.baseStepSize
                }
            }

            # Initial Values
            if 'initialize' in model_properties.keys():
                initial_values = {}
                for variable_index, (variable_name, variable_properties) in enumerate(
                    model_properties['initialize'].items()
                ):
                    variable_id = f'{variable_index:06d}_InitialValue'
                    fmi_data_type = self._get_fmi_data_type(variable_properties['start'])
                    initial_values[variable_id] = {
                        fmi_data_type: {
                            '_attributes': {
                                'value': variable_properties['start']
                            }
                        },
                        '_attributes': {
                            'variable': variable_name
                        }
                    }
                self.models[simulator_id]['InitialValues'] = initial_values

            if 'generateProxy' in model_properties:
                # generate fmu-proxy (NTNU-IHB/fmu-proxify)
                remote_access = model_properties['remoteAccess'
                                                 ] if 'remoteAccess' in model_properties else None
                generate_proxy = True

            self._prepare_model(
                model_index,
                model_name,
                model_properties,
                fmu_file_name=model_properties['fmu'],
                write_osp_model_description=True,
                generate_proxy=generate_proxy,
                remote_access=remote_access
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
                k2: {k3: v3
                     for k3, v3 in self.models[k1][k2].items()
                     if not re.match('fmu', k3)}
                for k2 in self.models[k1].keys()
            }
            for k1 in self.models.keys()
        }
        osp_ss['Simulators'] = models
        osp_ss['Connections'] = self.connections
        osp_ss['_xmlOpts'] = {
            '_nameSpaces': {
                'osp': 'https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd'
            },
            '_rootTag': 'OspSystemStructure',
        }

        # '_nameSpaces':{'osp':'https://opensimulationplatform.com/xsd/OspSystemStructure'},
        # '_nameSpaces':{'osp':'file:///C:/Software/OSP/xsd/OspSystemStructure-0.1.xsd'},
        # '_nameSpaces':{'osp':'file:///C:/Software/OSP/xsd/OspSystemStructure'},

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
        for key, item in self.models.items():

            connectors = dict({})

            for key1, item1 in self.connectors.items():
                i = self.counter()

                if self.connectors[key1]['component'] == self.models[key]['_attributes']['name']:
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
                    'name': self.models[key]['_attributes']['name'],
                    'source': self.models[key]['_attributes']['source'],
                },
                'Connectors': connectors,                                   # 'ParameterBindings': parameter_bindings,
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

        for key in self.models.keys():

            label_key, label = self._set_node_label(self.models[key]['_attributes']['name'], self.models[key])
            # var_keys = self._find_numbered_key_by_string(self.models[key]['InitialValues'], 'InitialValue')
            # variables = {}
            label = self._create_table(
                label_key,
                {
                    'source:': self.models[key]['_attributes']['source'],
                    'variables:': '',                                       # 'stepsize:':self.models[key]['_attributes']['stepSize'],
                }
            )

            if re.search(input_names, self.models[key]['_attributes']['name']):
                shape = 'diamond'
                style = 'filled,rounded'
                fillcolor = '#FFFFFF'
            elif re.search(basic_op_names, self.models[key]['_attributes']['name'], re.I):
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
        for m_key, m_item in self.models.items():
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

    def _update_model_description(self, model_dict, name):
        """updating modelDescripion.xml
        used whithin proxification (may be obsolete in future)
        """
        # update root attributes
        root_attributes = dict({})
        # take existing
        for key, item in model_dict['_xmlOpts']['_rootAttributes'].items():
            root_attributes[key] = item
        # new guid
        # root_attributes.update({'guid':'{%s}' % str(uuid4()).upper()})
        # new date
        root_attributes['generationDateAndTime'] = str(datetime.now())
        # author
        if platform.system() == 'Linux':
            root_attributes['author'] = os.environ['USER']
        else:
            root_attributes['author'] = os.environ['USERNAME']

        root_attributes['modelName'] = name

        # also find and replace model_dict['CoSimulation']['_attributes']['modelIdentifier']
        # this is now required if someone want to proxify the fmu
        # it changes also the modelIdentifier in CoSimulation xml tag,
        # what is used by fmu-proxify to estimate the output name
        # related to limitation of the -d option

        # this function is only to be used with fmu-proxify, temporary disabled
        # because it requires also a rename of dll's
        cosim_string = self._find_numbered_key_by_string(model_dict, 'CoSimulation')[0]
        model_dict[cosim_string]['_attributes'].update({'modelIdentifier': name})

        model_dict.update(
            {
                '_xmlOpts': {
                    '_rootTag': 'fmiModelDescription',
                    '_rootAttributes': root_attributes,
                }
            }
        )

        return model_dict

    def _prepare_model(
        self,
        model_index: int,
        model_name: str,
        model_properties: MutableMapping,
        fmu_file_name: str,
        write_osp_model_description: bool = False,
        generate_proxy: bool = False,
        remote_access: Union[MutableMapping, None] = None,
    ):
        """Copies an FMU from the source library into the working directory (i.e. case folder) and initializes it.

        Copies the FMU from the source library into the working directory (i.e. case folder),
        writes its OspModelDescription.xml and sets / initializes its parameters to their case specific values.
        """
        source_fmu_file = Path(self.lib_source) / Path(fmu_file_name)
        target_fmu_file = self.work_dir / Path(f'{model_name}.fmu')
        target_xml_file = self.work_dir / Path(f'{model_name}_OspModelDescription.xml')

        if not source_fmu_file.exists():
            logger.error(f'FMU source file does not exist: {source_fmu_file}')

        logger.info(f'copy {source_fmu_file} --> {target_fmu_file}')    # 2
        copyfile(source_fmu_file, target_fmu_file)

        # xml_parser = XmlParser(
        #     {
        #         '_nameSpaces': {
        #             'xs': 'file:///C:/Software/OSP/xsd/fmi3ModelDescription.xsd'
        #         },
        #     }
        # )
        # @TODO: Is the namspace important already during PARSING of XML?
        #        If so, we might need to make namespaces an attribute of XmlParser.
        #        CLAROS, 2021-08-23
        xml_parser = XmlParser()

        model_dict = CppDict(Path('modelDescription.xml'))

        if file_content := read_file_content_from_zip(target_fmu_file, 'modelDescription.xml'):
            model_dict = xml_parser.parse_string(file_content, model_dict)

        self.attributes.update({model_name: model_dict['_xmlOpts']['_rootAttributes']})

        model_variables_key = self._find_numbered_key_by_string(model_dict, 'ModelVariables$')[0]

        fmu_name = model_dict['_xmlOpts']['_rootAttributes']['modelName']

        # if not in "inspect mode"
        # also change modelDescription.xml (in zip file) for completeness
        if not self.inspect_mode:
            # if component has "initialize"
            if 'initialize' in model_properties.keys():
                logger.info(
                    f'{model_name} initialize: updating variables in modelDescription.xml'
                )                                                                           # 2

                # foreach key in list
                for list_key, list_item in model_properties['initialize'].items():

                    # fail, items not dictionaries but lists of k,v pais
                    for key, item in model_dict[model_variables_key].items():
                        if model_dict[model_variables_key][key]['_attributes']['name'] == list_key:

                            base_key = self._get_key_name(model_dict[model_variables_key][key])
                            numbered_key = self._find_numbered_key_by_string(
                                model_dict[model_variables_key][key], f'{base_key}$'
                            )[0]

                            # if there is to do a translation from e.g. Real to Integer, it has to be done here
                            # substituting numbered_key with an other one, deleting the orginal
                            # a key hat to be made therefor in generator dict

                            logger.info(
                                f"{model_name} modify: {model_dict[model_variables_key][key]['_attributes']['name']} {base_key} in {model_name} to {dict(list_item.items())}"
                            )

                            model_dict[model_variables_key][key][numbered_key]['_attributes'][
                                'start'] = list_item['start']
                            model_dict[model_variables_key][key]['_attributes'][
                                'variability'] = list_item['variability']
                            model_dict[model_variables_key][key]['_attributes'][
                                'causality'] = list_item['causality']

            # take ownerhsip of attributes in modelDescription.xml on copy
            # STC requires consistency between <fmiModelDescription><modelName> and <CoSimulation modelIdentifier>
            logger.info(
                f'{model_name}: updating fmiModelDescription:description in modelDescription.xml'
            )                                                                                       # 2

            old_author = model_dict['_xmlOpts']['_rootAttributes']['author']
            if platform.system() == 'Linux':
                new_author = os.environ['USER']
            else:
                new_author = os.environ['USERNAME']
            old_date = model_dict['_xmlOpts']['_rootAttributes']['generationDateAndTime']
            new_date = str(datetime.now())
            add_description_string = '\nmodified %s:\n' % date.today()
            add_description_string += '\tmodelName %s to %s\n' % (fmu_name, model_name)
            add_description_string += '\tauthor %s to %s\n' % (old_author, new_author)
            add_description_string += '\tgenerationDateAndTime %s to %s\n' % (old_date, new_date)
            model_dict['_xmlOpts']['_rootAttributes']['description'] += add_description_string

            model_dict = self._update_model_description(model_dict, model_name)

        # substitute new model_dict as modelDescription.xml in FMU
        # and make always a copy for reference
        # formatter = XmlFormatter(
        #     {
        #         '_nameSpaces': {
        #             'xs': 'file:///C:/Software/OSP/xsd/fmi3ModelDescription.xsd'
        #         },
        #     }
        # )
        # @TODO: Current approach with namespaces is that they are saved with the dict (in ['_xmlOpts']).
        #        However, if preferred / needed we could also make namespaces an attribute of XmlFormatter.
        #        To be considered / discussed.
        #        CLAROS, 2021-08-23
        model_dict['_xmlOpts']['_nameSpaces'] = {
            'xs': 'file:///C:/Software/OSP/xsd/fmi3ModelDescription.xsd'
        }
        formatter = XmlFormatter()
        formatted_xml = formatter.to_string(model_dict)

        with open(f'{model_name}_ModelDescription.xml', 'w') as f:
            f.write(formatted_xml)

        if not self.inspect_mode:
            # if 'initialize' in properties.keys() or generate_proxy is True:
            # do always, does not cost so much if original name remains the same but removes confusion here
            logger.info(
                f'{model_name} initialize: substituting modelDescription.xml in {model_name}.fmu'
            )

            remove_files_from_zip(target_fmu_file, 'modelDescription.xml')
            add_file_content_to_zip(target_fmu_file, 'modelDescription.xml', formatted_xml)

            # do a dll rename for all copyied fmu
            # required by STC
            # reason: ask me (frl)
            self._generate_copy(
                target_fmu_file, fmu_name, model_name, remote_access, generate_proxy
            )

        # avoid units with "-" as they do not have to declared (signal only)
        # give add. index for distinguishing betwee modelDescription.xml's containing one single ScalaVariable, otherwise it will be overwritten here
        unit_definitions_key = self._find_numbered_key_by_string(model_dict, 'UnitDefinitions$')[0]
        if unit_definitions_key == 'ELEMENTNOTFOUND':
            # self.unit_d.update({'%06i_UnitDefinitions'% self.counter():{'name':'ELEMENTNOTFOUND'}})
            pass
        else:
            self.unit_definitions.update(dict(model_dict[unit_definitions_key].items()))

        # make always unique units list and keep xml files clean
        self.unit_definitions = _shrink_dict(
            self.unit_definitions, make_unique=['_attributes', 'name']
        )

        # avoid solver internal variables, e..g "_iti_..."
        for key in model_dict[model_variables_key].keys():
            model_dict[model_variables_key][key]['_origin'] = model_name

        # proprietary: removing here "_" and also "settings" from iti namespace
        self.variables.update(
            {
                '%06i_%s' % (self.counter(), re.sub(r'^\d{6}_', '', k)): v
                for k,
                v in model_dict[model_variables_key].items()
                if not re.match('^(_|settings)', v['_attributes']['name'])
            }
        )

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

    def _get_key_name(self, dd):
        """return the key name of the list
        {Unknown|Real|Integer|String|Boolean}
        """
        key_list = ['Unknown', 'Real', 'Integer', 'String', 'Boolean']
        return_key = []
        for key in dd.keys():
            key = re.sub(r'^\d{6}_', '', key)

            if key in key_list:
                return_key.append(key)

        return return_key[0] if len(return_key) == 1 else 'ELEMENTNOTFOUND'

    def _find_numbered_key_by_string(self, dd, search_string):
        """find the element name for an (anyways unique) element
        after it was preceeded by a number to keep the sequence of xml elements
        as this is not the "nature" of dicts
        """
        try:
            return [k for k in dd.keys() if re.search(search_string, k)]
        except Exception:
            return ['ELEMENTNOTFOUND']

    def _get_fmi_data_type(self, arg):
        """estimate the data type, if available
        """
        if isinstance(arg, int):
            return 'Integer'
        elif isinstance(arg, float):
            return 'Real'
        elif isinstance(arg, bool):
            return 'Bool'
        else:
            return 'String'

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
        for _, model_properties in self.models.items():

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
