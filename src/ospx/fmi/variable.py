from dataclasses import dataclass
import logging
from typing import Sequence, Union


logger = logging.getLogger(__name__)


def get_fmi_data_type(arg):
    """Returns the fmi 2.0 data type of the passed in argument
    """
    if isinstance(arg, int):
        return 'Integer'
    elif isinstance(arg, float):
        return 'Real'
    elif isinstance(arg, bool):
        return 'Boolean'
    elif isinstance(arg, Sequence):
        return 'Enumeration'
    else:
        return 'String'


@dataclass()
class ScalarVariable():
    name: str
    value_reference: int = 0
    description: Union[str, None] = None
    _causality: str = 'local'
    _variability: Union[str, None] = None
    quantity: Union[str, None] = None
    unit: Union[str, None] = None
    display_unit: Union[str, None] = None
    _initial_value: Union[int, float, bool, str, None] = None
    _data_type: Union[str, None] = None

    @property
    def causality(self) -> str:
        return self._causality

    @causality.setter
    def causality(self, value: str):
        valid_values: list[str] = [
            'parameter',
            'calculatedParameter',
            'input',
            'output',
            'local',
            'independent',
            'structuralParameter',
        ]
        if value not in valid_values:
            logger.error(f"variable {self.name}: causality value '{value}' is invalid.")
            return
        self._causality = value
        return

    @property
    def variability(self) -> Union[str, None]:
        return self._variability

    @variability.setter
    def variability(self, value: str):
        valid_values: list[str] = [
            'constant',
            'fixed',
            'tunable',
            'discrete',
            'continuous',
        ]
        if value not in valid_values:
            logger.error(f"variable {self.name}: value for variability '{value}' is invalid.")
            return
        self._variability = value
        return

    @property
    def data_type(self) -> Union[str, None]:
        return self._data_type

    @data_type.setter
    def data_type(self, type: str):
        valid_types: list[str] = [
            'Real',
            'Integer',
            'Boolean',
            'String',
            'Enumeration',
        ]
        if type not in valid_types:
            logger.error(f"variable {self.name}: value for data_type '{type}' is invalid.")
            return
        self._data_type = type
        return

    @property
    def initial_value(self) -> Union[int, float, bool, str, None]:
        return self._initial_value

    @initial_value.setter
    def initial_value(self, value: Union[int, float, bool, str, None]):
        self._initial_value = value
        if not self.data_type and self.initial_value:
            self.data_type = get_fmi_data_type(self.initial_value)
