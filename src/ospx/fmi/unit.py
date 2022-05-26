import logging
from dataclasses import dataclass
from typing import Union


__ALL__ = ['Unit', 'BaseUnit', 'DisplayUnit']

logger = logging.getLogger(__name__)


@dataclass()
class BaseUnit():
    """fmi 2.0 BaseUnit

    Unit definition with reference to SI base units \n
    base unit value = factor * unit value + offset \n
    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2Unit.xsd
    """
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
    """fmi 2.0 DisplayUnit

    display unit value = factor * unit value + offset \n
    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2Unit.xsd
    """
    # Name of DisplayUnit element, e.g. <Unit name="rad"/>, <DisplayUnit name="deg" factor="57.29..."/>.
    # Name must be unique with respect to all other DisplayUnits defined inside a Unit element
    # (in contrast, multiple Unit elements may have DisplayUnits with the same name).
    name: str = '-'
    # display_unit value = factor * unit value + offset
    factor: float = 1.
    offset: float = 0.


@dataclass()
class Unit():
    """fmi 2.0 Unit Definition

    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2Unit.xsd
    """
    # Name of unit, e.g. "N.m", "Nm",  "%/s".
    # "name" must be unique with respect to all other unit elements inside the UnitDefinitions section.
    name: str = '-'
    base_unit: Union[BaseUnit, None] = None
    display_unit: DisplayUnit = DisplayUnit()
