from dataclasses import dataclass
import logging
from typing import MutableMapping, Union

from ospx.utils.fmi import get_fmi_data_type


logger = logging.getLogger(__name__)


@dataclass()
class Variable():
    name: str
    value_reference: Union[int, None] = None
    description: Union[str, None] = None
    causality: Union[str, None] = None
    variability: Union[str, None] = None
    quantity: Union[str, None] = None
    unit: Union[str, None] = None
    display_unit: Union[str, None] = None
    _initial_value: Union[int, float, bool, str, None] = None
    fmi_data_type: Union[str, None] = None

    @property
    def initial_value(self) -> Union[int, float, bool, str, None]:
        return self._initial_value

    @initial_value.setter
    def initial_value(self, value: Union[int, float, bool, str, None]):
        self._initial_value = value
        if not self.fmi_data_type and self.initial_value:
            self.fmi_data_type = get_fmi_data_type(self.initial_value)


@dataclass()
class BaseUnit():
    kg: int = 0
    m: int = 0
    s: int = 0
    A: int = 0
    K: int = 0
    mol: int = 0
    cd: int = 0
    rad: int = 0
    factor: float = 1.
    offset: float = 0.


@dataclass()
class DisplayUnit():
    name: str = '-'
    factor: float = 1.
    offset: float = 0.
    inverse: Union[bool, None] = None


@dataclass()
class Unit():
    _name: str = '-'
    base_unit: Union[BaseUnit, None] = None
    display_unit: DisplayUnit = DisplayUnit()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        self.display_unit.name = name
