import logging
from typing import Any, MutableMapping, Union

from ospx import Component, Connection, Connector, Endpoint
from ospx.fmi import FMU, ScalarVariable, Unit

__ALL__ = ["System"]

logger = logging.getLogger(__name__)


class System:
    """The system structure describes the topology of the co-simulated system.

    A system structure can contain an arbitrary number of components.
    Components can be connected through connections.
    Connections relate a source endpoint with a target endpoint.
    Both component variables and component connectors can be used as endpoints in a connection.
    """

    def __init__(self, properties: MutableMapping[Any, Any]):
        self._components: dict[str, Component] = {}
        self._connections: dict[str, Connection] = {}
        self._read_components(properties)
        self._read_connections(properties)

    @property
    def fmus(self) -> dict[str, FMU]:
        """Returns a dict with all FMUs referenced by components contained in the system.

        Returns
        -------
        dict[str, FMU]
            dict with all FMUs
        """
        return {component.fmu.file.name: component.fmu for component in self.components.values() if component.fmu}

    @property
    def components(self) -> dict[str, Component]:
        """Returns a dict with all components contained in the system.

        Returns
        -------
        dict[str, Component]
            dict with all components
        """
        return self._components

    @property
    def connections(self) -> dict[str, Connection]:
        """Returns a dict with all connections defined in the system.

        Returns
        -------
        dict[str, Connection]
            dict with all connections
        """
        return self._connections

    @property
    def units(self) -> dict[str, Unit]:
        """Returns a combined dict with all units
        from all components contained in the system.

        Returns
        -------
        dict[str, Unit]
            dict with all units from all components
        """
        units: dict[str, Unit] = {}
        for component in self.components.values():
            if component.units:
                units |= component.units
        return units

    @property
    def connectors(self) -> dict[str, Connector]:
        """Returns a combined dict with all connectors
        from all components contained in the system.

        Returns
        -------
        dict[str, Connector]
            dict with all connectors from all components
        """
        connectors: dict[str, Connector] = {}
        for component in self.components.values():
            if component.connectors:
                connectors |= component.connectors
        return connectors

    @property
    def variables(self) -> dict[str, ScalarVariable]:
        """Returns a combined dict with all scalar variables
        from all components contained in the system.

        Returns
        -------
        dict[str, ScalarVariable]
            dict with all scalar variables from all components
        """
        variables: dict[str, ScalarVariable] = {}
        for component in self.components.values():
            if component.variables:
                variables |= component.variables
        return variables

    def _read_components(self, properties: MutableMapping[Any, Any]):
        """Read components from (case dict) properties."""
        logger.info("read components from case dict")
        self._components.clear()
        if "components" not in properties:
            return
        for component_name, component_properties in properties["components"].items():
            component = Component(component_name, component_properties)
            self._components[component.name] = component

    def _read_connections(self, properties: MutableMapping[Any, Any]):
        """Read connections from (case dict) properties."""
        logger.info("read connections from case dict")
        self._connections.clear()
        if "connections" not in properties:
            return
        for connection_name, connection_properties in properties["connections"].items():
            source_endpoint: Union[Endpoint, None] = None
            target_endpoint: Union[Endpoint, None] = None
            if "source" in connection_properties:
                source_endpoint = self._read_endpoint(connection_properties["source"])
            if "target" in connection_properties:
                target_endpoint = self._read_endpoint(connection_properties["target"])
            if source_endpoint and target_endpoint:
                connection = Connection(
                    name=connection_name,
                    source_endpoint=source_endpoint,
                    target_endpoint=target_endpoint,
                )
                self._connections[connection.name] = connection
            else:
                logger.error(
                    f"connection {connection_name}: connection could not be resolved. Please recheck connection properties in case dict."
                )
        return

    def _read_endpoint(self, properties: MutableMapping[Any, Any]) -> Union[Endpoint, None]:
        if "component" not in properties:
            return None
        component: Union[Component, None] = None
        connector: Union[Connector, None] = None
        variable: Union[ScalarVariable, None] = None

        component_name: str = properties["component"]
        if component_name in self.components:
            component = self.components[component_name]

        if "connector" in properties:
            connector_name = properties["connector"]
            if component and connector_name in component.connectors:
                connector = component.connectors[connector_name]
            else:
                for _, c in self.components.items():
                    if connector_name in c.connectors:
                        component = c
                        connector = c.connectors[connector_name]
                        break

        if "variable" in properties:
            variable_name = properties["variable"]
            if component and variable_name in component.variables:
                variable = component.variables[variable_name]

        if not component:
            return None

        if connector or variable:
            endpoint: Endpoint = Endpoint(
                component=component,
                connector=connector,
                variable=variable,
            )
            return endpoint if endpoint.is_valid else None

        return None
