from dataclasses import dataclass
import logging
from typing import Union


logger = logging.getLogger(__name__)


def get_fmi_data_type(arg):
    """Returns the fmi data type of the passed in argument (best guess)
    """
    if isinstance(arg, int):
        return 'Integer'
    elif isinstance(arg, float):
        return 'Real'
    elif isinstance(arg, bool):
        return 'Bool'
    else:
        return 'String'


@dataclass()
class Variable():
    name: str
    value_reference: int = 0
    description: Union[str, None] = None
    _causality: str = 'local'
    _variability: Union[str, None] = None
    quantity: Union[str, None] = None
    unit: Union[str, None] = None
    display_unit: Union[str, None] = None
    _initial_value: Union[int, float, bool, str, None] = None
    fmi_data_type: Union[str, None] = None

    @property
    def causality(self) -> str:
        return self._causality

    @causality.setter
    def causality(self, value: str):
        permissable_values: list[str] = [
            'parameter',
            'calculatedParameter',
            'input',
            'output',
            'local',
            'independent',
            'structuralParameter',
        ]
        if value not in permissable_values:
            logger.error(f"variable {self.name}: value for causality '{value}' is invalid.")
            return
        self._causality = value
        return

    @property
    def variability(self) -> Union[str, None]:
        return self._variability

    @variability.setter
    def variability(self, value: str):
        permissable_values: list[str] = [
            'constant',
            'fixed',
            'tunable',
            'discrete',
            'continuous',
        ]
        if value not in permissable_values:
            logger.error(f"variable {self.name}: value for variability '{value}' is invalid.")
            return
        self._variability = value
        return

    @property
    def initial_value(self) -> Union[int, float, bool, str, None]:
        return self._initial_value

    @initial_value.setter
    def initial_value(self, value: Union[int, float, bool, str, None]):
        self._initial_value = value
        if not self.fmi_data_type and self.initial_value:
            self.fmi_data_type = get_fmi_data_type(self.initial_value)
