from dataclasses import dataclass
import logging
from typing import Union


logger = logging.getLogger(__name__)


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
