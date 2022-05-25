import logging
from dataclasses import dataclass
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
    # base_unit value = factor * unit value + offset
    factor: float = 1.
    offset: float = 0.


@dataclass()
class DisplayUnit():
    # From https://github.com/modelica/fmi-standard/blob/support/v2.0.x/schema/fmi2Unit.xsd
    # Name of DisplayUnit element, e.g. <Unit name="rad"/>, <DisplayUnit name="deg" factor="57.29..."/>.
    # "name" must be unique with respect to all other "names" of the DisplayUnit definitions of the same Unit
    # (in contrast, different Unit elements may have the same DisplayUnit names).
    name: str = '-'
    # display_unit value = factor * unit value + offset
    factor: float = 1.
    offset: float = 0.
    inverse: Union[bool, None] = None   # added with FMI3


@dataclass()
class Unit():
    # From https://github.com/modelica/fmi-standard/blob/support/v2.0.x/schema/fmi2Unit.xsd
    # Unit definition (with respect to SI base units) and default display units.
    # Name of Unit element, e.g. "N.m", "Nm",  "%/s".
    # "name" must be unique with respect to all other elements of the UnitDefinitions list.
    # The variable values of fmi2SetXXX and fmi2GetXXX are with respect to this unit.
    name: str = '-'
    base_unit: Union[BaseUnit, None] = None
    display_unit: DisplayUnit = DisplayUnit()
