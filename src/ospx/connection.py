import logging
from typing import Union

from ospx.component import Component
from ospx.connector import Connector
from ospx.fmi.variable import ScalarVariable

__ALL__ = ["Endpoint", "Connection"]

logger = logging.getLogger(__name__)


class Endpoint:
    """Endpoints relate each side of a connection to distinct variables or connectors.

    An endpoint is for a connection what a connector is for a component.
    A connection has two endpoints, one for each side.
    Connection endpoints are hence the 'counterparts' to component's connectors.
    """

    def __init__(
        self,
        component: Component,
        connector: Union[Connector, None] = None,
        variable: Union[ScalarVariable, None] = None,
    ):
        self.component: Component = component
        self._connector: Union[Connector, None] = None
        self._variable: Union[ScalarVariable, None] = None
        if connector:
            self.connector = connector
        if variable:
            self.variable = variable

    @property
    def connector(self) -> Union[Connector, None]:
        """Returns the connector this endpoint refers to, if defined.

        Returns
        -------
        Union[Connector, None]
            the connector, if defined. Otherwise None.
        """
        return self._connector

    @connector.setter
    def connector(self, connector: Connector):
        """Set the connector this endpoint shall refer to.

        Parameters
        ----------
        connector : Connector
            the connector
        """
        if self._variable:
            msg = (
                f"Inconsistency: Connection endpoint defines both connector and variable.\n"
                f"connector: {connector.name}\nvariable: {self._variable.name}\n"
                "connector is used. variable is omitted."
            )
            logger.warning(msg)
            self._variable = None
        self._connector = connector

    @property
    def variable(self) -> Union[ScalarVariable, None]:
        """Returns the scalar variable this endpoint refers to, if defined.

        Returns
        -------
        Union[ScalarVariable, None]
            the scalar variable, if defined. Otherwise None.
        """
        return self._variable

    @variable.setter
    def variable(self, variable: ScalarVariable):
        """Set the scalar variable this endpoint shall refer to.

        Parameters
        ----------
        variable : ScalarVariable
            the scalar variable
        """
        if self._connector:
            msg = (
                f"Inconsistency: Connection endpoint defines both connector and variable.\n"
                f"connector: {self._connector.name}\nvariable: {variable.name}\n"
                "connector is omitted. variable is used."
            )
            logger.warning(msg)
            self._connector = None
        self._variable = variable

    @property
    def variable_name(self) -> str:
        """Returns the name of the scalar variable this endpoint refers to.

        Returns
        -------
        str
            the name of the scalar variable.
        """
        if self._connector:
            return self._connector.variable_name
        elif self._variable:
            return self._variable.name
        else:
            return "UNKNOWN"

    @property
    def is_valid(self) -> bool:
        """Consistency check. Returns True if endpoint is defined and valid.

        Returns
        -------
        bool
            True if valid. Otherwise False.
        """
        return bool(self.component and (self.connector or self.variable))


class Connection:
    """A connection is the primary artefact to connect outputs and inputs of componoents in a system.

    A connection connects an output connector of one component with an input connector of another component.
    """

    def __init__(
        self,
        name: str,
        source_endpoint: Endpoint,
        target_endpoint: Endpoint,
    ):
        self.name: str = name
        self.source_endpoint: Endpoint = source_endpoint
        self.target_endpoint: Endpoint = target_endpoint

    @property
    def is_variable_connection(self) -> bool:
        """Returns True if connection is a single variable connection.

        Returns
        -------
        bool
            True if single variable connection. Otherwise False.
        """
        if not self.source_endpoint:
            return False
        if self.source_endpoint.variable:
            return True
        if self.source_endpoint.connector:
            return self.source_endpoint.connector.is_single_connector
        return False

    @property
    def is_variable_group_connection(self) -> bool:
        """Returns True if connection is a variable group connection.

        Returns
        -------
        bool
            True if variable group connection. Otherwise False.
        """
        if not self.source_endpoint:
            return False
        if self.source_endpoint.variable:
            return False
        if self.source_endpoint.connector:
            return self.source_endpoint.connector.is_group_connector
        return False

    @property
    def is_valid(self) -> bool:
        """Consistency check. Returns True if connection is found fully defined and valid.

        Returns
        -------
        bool
            True if valid. Otherwise False.
        """
        if not (self.source_endpoint.is_valid and self.target_endpoint.is_valid):
            return False
        if self.source_endpoint.variable and self.target_endpoint.variable:
            return True
        if self.source_endpoint.connector and self.target_endpoint.connector:
            _both_are_single: bool = (
                self.source_endpoint.connector.is_single_connector
                and self.target_endpoint.connector.is_single_connector
            )
            _both_are_group: bool = (
                self.source_endpoint.connector.is_group_connector and self.target_endpoint.connector.is_group_connector
            )
            return _both_are_single or _both_are_group
        elif self.source_endpoint.connector:
            return self.source_endpoint.connector.is_single_connector
        elif self.target_endpoint.connector:
            return self.target_endpoint.connector.is_single_connector
        return False
