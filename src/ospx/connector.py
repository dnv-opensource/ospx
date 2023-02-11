import logging
from typing import Union

__ALL__ = ["Connector"]

logger = logging.getLogger(__name__)


class Connector:
    """Connectors allow to explicitely make public a components scalar variable or variable group
    at the component's outer interface.

    An connector is for a component what an endpoint is for a connection.
    Connectors are hence the 'counterparts' to connection's endpoints.
    """

    def __init__(
        self,
        name: str,
        variable: Union[str, None] = None,
        variable_group: Union[str, None] = None,
        type: Union[str, None] = None,
    ):
        self.name: str = name
        self._variable: Union[str, None] = None
        self._variable_group: Union[str, None] = None
        self._type: Union[str, None] = None
        if variable:
            self.variable = variable
        if variable_group:
            self.variable_group = variable_group
        if type:
            self.type = type

    @property
    def variable(self) -> Union[str, None]:
        """Returns the scalar variable this connector is defined for.

        Returns
        -------
        Union[str, None]
            the scalar variable, if connector is a group connector. Otherwise None.
        """
        return self._variable

    @variable.setter
    def variable(self, variable: str):
        """Set the scalar variable this connector shall be defined for.

        Parameters
        ----------
        variable : str
            the scalar variable
        """
        if self._variable_group:
            msg = (
                f"Inconsistency: Connector {self.name} defines both variable and variableGroup.\n"
                f"variable: {variable}\nvariableGroup: {self._variable_group}\n"
                "variable is used. variableGroup is omitted."
            )
            logger.warning(msg)
            self._variable_group = None
        self._variable = variable

    @property
    def variable_group(self) -> Union[str, None]:
        """Returns the variable group this connector is defined for.

        Returns
        -------
        Union[str, None]
            the variable group, if connector is a group connector. Otherwise None.
        """
        return self._variable_group

    @variable_group.setter
    def variable_group(self, variable_group: str):
        """Set the variable group this connector shall be defined for.

        Parameters
        ----------
        variable_group : str
            the variable group
        """
        if self._variable:
            msg = (
                f"Inconsistency: Connector {self.name} defines both variable and variableGroup.\n"
                f"variable: {self._variable}\nvariableGroup: {variable_group}\n"
                "variable is omitted. variableGroup is used."
            )
            logger.warning(msg)
            self._variable = None
        self._variable_group = variable_group

    @property
    def type(self) -> Union[str, None]:
        """Returns the type of the connector."""
        return self._type

    @type.setter
    def type(self, type: str):
        """Set the type of the connector.

        Valid values are:
            "input"
            "output"
        """
        valid_types: list[str] = [
            "input",
            "output",
        ]
        if type not in valid_types:
            logger.error(f"connector {self.name}: type '{type}' is invalid.")
            return
        self._type = type
        return

    @property
    def is_single_connector(self) -> bool:
        """Returns True if connector is a single variable connector.

        Returns
        -------
        bool
            True if single variable connector. Otherwise False.
        """
        return bool(self._variable)

    @property
    def is_group_connector(self) -> bool:
        """Returns True if connector is a variable group connector.

        Returns
        -------
        bool
            True if variable group connector. Otherwise False.
        """
        return bool(self._variable_group)

    @property
    def variable_name(self) -> str:
        """Returns the name of the variable or variable group this connector is defined for.

        Returns
        -------
        str
            name of the variable or variable group
        """
        if self._variable:
            return self._variable
        elif self._variable_group:
            return self._variable_group
        else:
            return "UNKNOWN"
