import logging
from collections.abc import Iterable
from typing import Any, List, Sequence, Union

from dictIO import Formatter, Parser

__ALL__ = ["ScalarVariable", "get_fmi_data_type"]

logger = logging.getLogger(__name__)


class ScalarVariable:
    """fmi 2.0 ScalarVariable.

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
        self._causality: str = "local"
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
        """Returns the FMI data type of the scalar Variable."""
        return self._data_type

    @data_type.setter
    def data_type(self, type: str):
        """Set the FMI data type of the scalar Variable.

        Valid values are:
            "Real"
            "Integer"
            "Boolean"
            "String"
            "Enumeration"
        """
        valid_types: list[str] = [
            "Real",
            "Integer",
            "Boolean",
            "String",
            "Enumeration",
        ]
        if type not in valid_types:
            logger.error(f"variable {self.name}: value for data_type '{type}' is invalid.")
            return
        self._data_type = type
        return

    @property
    def causality(self) -> str:
        """Returns the causality of the scalar Variable."""
        return self._causality

    @causality.setter
    def causality(self, value: str):
        """Set the causality of the scalar Variable.

        Valid values are:
            "parameter"
            "calculatedParameter"
            "input"
            "output"
            "local"
            "independent"
            "structuralParameter"
        """
        valid_values: list[str] = [
            "parameter",
            "calculatedParameter",
            "input",
            "output",
            "local",
            "independent",
            "structuralParameter",
        ]
        if value not in valid_values:
            logger.error(f"variable {self.name}: causality value '{value}' is invalid.")
            return
        self._causality = value
        return

    @property
    def variability(self) -> Union[str, None]:
        """Returns the variability of the scalar Variable."""
        return self._variability

    @variability.setter
    def variability(self, value: str):
        """Set the variability of the scalar Variable.

        Valid values are:
            "constant"
            "fixed"
            "tunable"
            "discrete"
            "continuous"
        """
        valid_values: list[str] = [
            "constant",
            "fixed",
            "tunable",
            "discrete",
            "continuous",
        ]
        if value not in valid_values:
            logger.error(f"variable {self.name}: value for variability '{value}' is invalid.")
            return
        self._variability = value
        return

    @property
    def start(self) -> Union[int, float, bool, str, None]:
        """Returns the start value (initial value) of the scalar Variable."""
        return self._start

    @start.setter
    def start(self, value: Union[int, float, bool, str, None]):
        """Set the start value (initial value) of the scalar Variable."""
        if value is None:
            logger.error(f"variable {self.name}: start value shall be set to 'None', but 'None' is invalid for start.")
            return
        if self.data_type:
            # make sure the data type of the new value does either match or gets casted to the data_type defined for the variable
            new_value_data_type = get_fmi_data_type(value)
            if new_value_data_type == self.data_type:
                self._start = value
            else:
                casted_value = _cast_to_fmi_data_type(value, self.data_type)
                if casted_value is not None and not isinstance(casted_value, Sequence):
                    self._start = casted_value
                elif casted_value is None:
                    logger.error(
                        f"variable {self.name}: start shall be set to 'None', but 'None' is invalid for start."
                    )
                    return
                else:
                    logger.error(
                        f"variable {self.name}: start shall be set to {casted_value}, but fmi data type 'Enumeration' is invalid for start."
                    )
                    return
        else:
            self._start = value
            self.data_type = get_fmi_data_type(self.start)


def get_fmi_data_type(arg: Any) -> str:
    r"""Return the fmi 2.0 data type corresponding to Python type of the passed in argument.

    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2Type.xsd

    Parameters
    ----------
    arg : Any
        The argument for which the fmi 2.0 data type shall be determined

    Returns
    -------
    str
        The fmi 2.0 data type, returned as string literal.\n
        valid fmi 2.0 data types are 'Integer', 'Real', 'Boolean', 'String' and 'Enumeration'
    """

    if isinstance(arg, int):
        return "Integer"
    elif isinstance(arg, float):
        return "Real"
    elif isinstance(arg, bool):
        return "Boolean"
    # not regarding the content, sequence is always returned if not int or float, e.g. string.
    # requires a solution, if xs:enumeration is required.
    # elif isinstance(arg, Sequence):
    #    return 'Enumeration'
    else:
        return "String"


def _cast_to_fmi_data_type(
    arg: Union[int, float, bool, str, Sequence[Any]], fmi_data_type: str
) -> Union[int, float, bool, str, List[Any], None]:
    r"""Casts the passed in argument to a Python data type that matches the requested fmi data type.

    Parameters
    ----------
    arg : Union[int, float, bool, str, Sequence[Any]]
        The argument to be casted
    fmi_data_type : str
        The fmi data type the argument shall be casted to.\n
        valid fmi 2.0 data types are 'Integer', 'Real', 'Boolean', 'String' and 'Enumeration'

    Returns
    -------
    Union[int, float, bool, str, List[Any], None]
        The casted value (in a Python data type that matches the requested fmi data type)
    """
    if fmi_data_type in {"Integer", "Real", "Boolean"}:
        if isinstance(arg, Sequence):
            logger.warning(
                f"_cast_to_fmi_data_type(): argument {arg} of type List/Tuple/Sequence cannot be casted to fmi data type {fmi_data_type}"
            )
            return None
        # parse if arg is string
        parsed_value: Union[int, float, bool]
        parsed_value = Parser().parse_type(arg) if isinstance(arg, str) else arg
        # cast to int / float / bool
        if fmi_data_type == "Integer":
            return int(parsed_value)
        elif fmi_data_type == "Real":
            return float(parsed_value)
        else:
            return bool(parsed_value)
    elif fmi_data_type == "String":
        # format as string
        return Formatter().format_dict(arg) if isinstance(arg, Sequence) else Formatter().format_type(arg)
    elif fmi_data_type == "Enumeration":
        # cast to list
        return list(arg) if isinstance(arg, Iterable) else [arg]
    else:
        return None
