import logging
from typing import Any, Sequence, Union


__ALL__ = ['ScalarVariable', 'get_fmi_data_type']

logger = logging.getLogger(__name__)


class ScalarVariable():
    """fmi 2.0 ScalarVariable

    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2ScalarVariable.xsd
    """

    def __init__(
        self,
        name: str,
        data_type: Union[str, None] = None,
        causality: Union[str, None] = None,
        variability: Union[str, None] = None,
        start: Union[int, float, bool, str, None] = None,
        value_reference: int = 0,
        description: Union[str, None] = None,
        quantity: Union[str, None] = None,
        unit: Union[str, None] = None,
        display_unit: Union[str, None] = None,
    ):
        # Attributes
        self.name: str
        self._data_type: Union[str, None] = None
        self._causality: str = 'local'
        self._variability: Union[str, None] = None
        self._start: Union[int, float, bool, str, None] = None
        self.value_reference: int = 0
        self.description: Union[str, None] = None
        self.quantity: Union[str, None] = None
        self.unit: Union[str, None] = None
        self.display_unit: Union[str, None] = None
        # Initialization
        self.name = name
        if data_type:
            self.data_type = data_type
        if causality:
            self.causality = causality
        if variability:
            self.variability = variability
        if start:
            self.start = start
        self.value_reference = value_reference
        self.description = description
        self.quantity = quantity
        self.unit = unit
        self.display_unit = display_unit

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
    def start(self) -> Union[int, float, bool, str, None]:
        return self._start

    @start.setter
    def start(self, value: Union[int, float, bool, str, None]):
        self._start = value
        if not self.data_type and self.start:
            self.data_type = get_fmi_data_type(self.start)


def get_fmi_data_type(arg: Any) -> str:
    """Returns the fmi 2.0 data type of the passed in argument

    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2Type.xsd

    Parameters
    ----------
    arg : Any
        The argument for which the fmi 2.0 data type shall be determined

    Returns
    -------
    str
        The data type, returned as string literal.\n
        valid fmi 2.0 data types are 'Integer', 'Real', 'Boolean', 'String' and 'Enumeration'
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
