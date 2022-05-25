import logging
from typing import MutableMapping, Union

from ospx.component import Component
from ospx.connection import Connection, Endpoint
from ospx.connector import Connector
from ospx.fmi.fmu import FMU
from ospx.fmi.unit import Unit
from ospx.fmi.variable import ScalarVariable


logger = logging.getLogger(__name__)


class SystemStructure():

    def __init__(self, properties: MutableMapping):
        self._components: dict[str, Component] = {}
        self._connections: dict[str, Connection] = {}
        self._read_components(properties)
        self._read_connections(properties)

    @property
    def fmus(self) -> dict[str, FMU]:
        return {
            component.fmu.file.name: component.fmu
            for component in self.components.values()
            if component.fmu
        }

    @property
    def components(self) -> dict[str, Component]:
        return self._components

    @property
    def connections(self) -> dict[str, Connection]:
        return self._connections

    @property
    def units(self) -> dict[str, Unit]:
        units: dict[str, Unit] = {}
        for component in self.components.values():
            if component.units:
                units |= component.units
        return units

    @property
    def connectors(self) -> dict[str, Connector]:
        connectors: dict[str, Connector] = {}
        for component in self.components.values():
            if component.connectors:
                connectors |= component.connectors
        return connectors

    @property
    def variables(self) -> dict[str, ScalarVariable]:
        variables: dict[str, ScalarVariable] = {}
        for component in self.components.values():
            if component.variables:
                variables |= component.variables
        return variables

    def _read_components(self, properties: MutableMapping):
        """Reads components from (case dict) properties
        """
        logger.info('read components from case dict')
        self._components.clear()
        if 'components' not in properties:
            return
        for component_name, component_properties in properties['components'].items():
            component = Component(component_name, component_properties)
            self._components[component.name] = component

    def _read_connections(self, properties: MutableMapping):
        """Reads connections from (case dict) properties
        """
        logger.info('read connections from case dict')
        self._connections.clear()
        if 'connections' not in properties:
            return
        for connection_name, connection_properties in properties['connections'].items():
            connection = Connection(name=connection_name)
            if 'source' in connection_properties:
                connection.source = self._read_endpoint(connection_properties['source'])
            if 'target' in connection_properties:
                connection.target = self._read_endpoint(connection_properties['target'])
            if connection.source and connection.target:
                self._connections[connection_name] = connection
            else:
                logger.error(
                    f'connection {connection_name}: connection could not be resolved. Please recheck connection properties in case dict.'
                )
        return

    def _read_endpoint(self, properties: MutableMapping) -> Union[Endpoint, None]:
        endpoint: Endpoint = Endpoint()
        component: Union[Component, None] = None
        connector: Union[Connector, None] = None
        variable: Union[ScalarVariable, None] = None
        if 'component' in properties:
            component_name = properties['component']
            if component_name in self.components:
                component = self.components[component_name]
                endpoint.component = component_name
        if 'connector' in properties:
            connector_name = properties['connector']
            if component and connector_name in component.connectors:
                connector = component.connectors[connector_name]
                endpoint.connector = connector_name
            else:
                for component_name, c in self.components.items():
                    if connector_name in c.connectors:
                        component = c
                        connector = c.connectors[connector_name]
                        endpoint.component = component_name
                        endpoint.connector = connector_name
                        break
            if component and connector:
                if variable_name := connector.variable:
                    if variable_name in component.variables:
                        variable = component.variables[variable_name]
                        endpoint.variable = variable_name
        if 'variable' in properties:
            variable_name = properties['variable']
            if component and variable_name in component.variables:
                variable = component.variables[variable_name]
                endpoint.variable = variable_name

        return endpoint if component and variable else None
