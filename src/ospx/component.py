from dataclasses import dataclass
import logging
from typing import MutableMapping, Union
from ospx.variable import Variable
from ospx.fmu import FMU


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
        self.variables_with_initial_values: dict[str, Variable] = {}
        self.generate_proxy: bool = False
        self.remote_access: Union[RemoteAccess, None] = None

        if 'initialize' in properties:
            self.variables_with_initial_values.update(
                {
                    name: Variable(name, properties)
                    for name,
                    properties in properties['initialize'].items()
                }
            )

        if 'generate_proxy' in properties:
            self.generate_proxy = properties['generate_proxy']

        if 'remoteAccess' in properties:                        # sourcery skip: merge-nested-ifs
            if 'host' in properties['remoteAccess'] and 'port' in properties['remoteAccess']:
                self.remote_access = RemoteAccess(
                    host=properties['remoteAccess']['host'],
                    port=properties['remoteAccess']['port'],
                )

        if self.generate_proxy and not self.remote_access:
            logger.error(
                f"component {self.name}: 'generate_proxy' set to True, but the 'remoteAccess' element is not correctly defined."
            )


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