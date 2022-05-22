from copy import deepcopy
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import MutableMapping, Union

from dictIO.dictWriter import DictWriter
from dictIO.utils.counter import BorgCounter

from ospx.fmu import FMU
from ospx.utils.dict import find_key, find_type_identifier_in_keys
from ospx.utils.fmi import get_fmi_data_type
from ospx.variable import Variable


logger = logging.getLogger(__name__)


@dataclass()
class RemoteAccess():
    host: str = ''
    port: int = 0


class Component():

    def __init__(self, name: str, properties: MutableMapping):

        self.name: str = name
        self.generate_proxy = False
        self.fmu: FMU
        self.step_size: float = 1.
        self._initial_values: dict[str, Variable] = {}
        self.generate_proxy: bool = False
        self.remote_access: Union[RemoteAccess, None] = None
        self.counter = BorgCounter()
        self._variables: dict[str, Variable]

        if 'fmu' in properties:
            fmu_file_name = properties['fmu']
            fmu_file = Path(fmu_file_name)
            if not fmu_file.exists():
                logger.exception(
                    f"component {self.name}: referenced FMU '{fmu_file_name}' not found."
                )
                raise FileNotFoundError(fmu_file)
            self.fmu = FMU(fmu_file)
        else:
            logger.error(f"component {self.name}: 'fmu' element missing in case dict.")
            return

        if 'initialize' in properties:
            for variable_name, variable_properties in properties['initialize'].items():
                variable = Variable(name=variable_name)
                if 'causality' in variable_properties:
                    variable.causality = variable_properties['causality']
                if 'variability' in variable_properties:
                    variable.variability = variable_properties['variability']
                if 'start' in variable_properties:
                    variable.initial_value = variable_properties['start']
                if not variable.fmi_data_type and variable.initial_value:
                    variable.fmi_data_type = get_fmi_data_type(variable.initial_value)
                self._initial_values[variable.name] = variable

        if 'generate_proxy' in properties:
            self.generate_proxy = properties['generate_proxy']

        if 'remoteAccess' in properties:                        # sourcery skip: merge-nested-ifs
            if 'host' in properties['remoteAccess'] and 'port' in properties['remoteAccess']:
                self.remote_access = RemoteAccess(
                    host=properties['remoteAccess']['host'],
                    port=properties['remoteAccess']['port'],
                )

        if self.generate_proxy:
            if not self.remote_access:
                logger.error(
                    f"component {self.name}: 'generate_proxy' set to True, but the 'remoteAccess' element is not correctly defined."
                )
            elif not self.remote_access.host:
                logger.error(
                    f"component {self.name}: 'remoteAccess' element is defined, but host is not specified."
                )
            elif not self.remote_access.port:
                logger.error(
                    f"component {self.name}: 'remoteAccess' element is defined, but port is not specified."
                )
            else:
                self.fmu = self.fmu.proxify(self.remote_access.host, self.remote_access.port)
                # self.name = self.fmu.file.stem

        self._init_variables()

    def _init_variables(self):
        self._variables = deepcopy(self.fmu.variables)
        for variable_name, variable in self._initial_values.items():
            if variable.causality:
                self._variables[variable_name].causality = variable.causality
            if variable.variability:
                self._variables[variable_name].variability = variable.variability
            if variable.initial_value:
                self._variables[variable_name].initial_value = variable.initial_value

    @property
    def initial_values(self) -> dict[str, Variable]:
        return self._initial_values

    @property
    def variables(self) -> dict[str, Variable]:
        return self._variables

    def write_osp_model_description(self):
        """writing OspModelDescription.xml
        """
        osp_model_description_file = self.fmu.file.parent.absolute(
        ) / f'{self.name}_OspModelDescription.xml'

        osp_model_description = {
            'UnitDefinitions': self.fmu.unit_definitions,
            'VariableGroups': {},
        }

        variable_groups = {}

        for variable_name, variable in self.variables.items():

            if not variable.quantity:
                logger.warning(
                    f'component {self.name}: no quantity defined for variable {variable_name}'
                )
            if not variable.unit:
                logger.warning(
                    f'component {self.name}: no unit defined for variable {variable_name}'
                )
            quantity_name = variable.quantity or 'UNKNOWN'
            quantity_unit = variable.unit or 'UNKNOWN'

            variable_groups[f'{self.counter():06d}_Generic'] = {
                '_attributes': {
                    'name': quantity_name
                },
                quantity_name: {
                    '_attributes': {
                        'name': quantity_name
                    },
                    'Variable': {
                        '_attributes': {
                            'ref': variable_name,
                            'unit': quantity_unit,
                        }
                    },
                },
            }

        # this is the content of OspModelDescription
        osp_model_description['VariableGroups'] = variable_groups

        # _xmlOpts
        osp_model_description['_xmlOpts'] = {
            '_nameSpaces': {
                'osp': 'https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd'
            },
            '_rootTag': 'ospModelDescription',
        }

        DictWriter.write(osp_model_description, osp_model_description_file)


'''
def temp_write_osp_system_structure_xml():

    # Attributes
    self.components[component_name] = {
        '_attributes': {
            'name': component_name,
            'source': component_properties['fmu'],
            'stepSize': self.baseStepSize
        }
    }

    if 'initialize' in properties:
        initial_values = {}
        for variable_index, (variable_name,
                             variable_properties) in enumerate(properties['initialize'].items()):
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
        self.components[component_id]['InitialValues'] = initial_values


'''
