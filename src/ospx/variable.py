from dataclasses import dataclass
import logging
from typing import MutableMapping, Union


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
    initial_value: Union[int, float, bool, str, None] = None
    fmi_data_type: Union[str, None] = None
