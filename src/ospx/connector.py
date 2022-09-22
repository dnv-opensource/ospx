import logging
from typing import Union


__ALL__ = ['Connector']

logger = logging.getLogger(__name__)


class Connector():

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
        return self._variable

    @variable.setter
    def variable(self, variable: str):
        if self._variable_group:
            msg = (
                f'Inconsistency: Connector {self.name} defines both variable and variableGroup.\n'
                f'variable: {variable}\nvariableGroup: {self._variable_group}\n'
                'variable is used. variableGroup is omitted.'
            )
            logger.warning(msg)
            self._variable_group = None
        self._variable = variable

    @property
    def variable_group(self) -> Union[str, None]:
        return self._variable_group

    @variable_group.setter
    def variable_group(self, variable_group: str):
        if self._variable:
            msg = (
                f'Inconsistency: Connector {self.name} defines both variable and variableGroup.\n'
                f'variable: {self._variable}\nvariableGroup: {variable_group}\n'
                'variable is omitted. variableGroup is used.'
            )
            logger.warning(msg)
            self._variable = None
        self._variable_group = variable_group

    @property
    def type(self) -> Union[str, None]:
        return self._type

    @type.setter
    def type(self, type: str):
        valid_types: list[str] = [
            'input',
            'output',
        ]
        if type not in valid_types:
            logger.error(f"connector {self.name}: type '{type}' is invalid.")
            return
        self._type = type
        return

    @property
    def is_single_connector(self) -> bool:
        return bool(self._variable)

    @property
    def is_group_connector(self) -> bool:
        return bool(self._variable_group)

    @property
    def variable_name(self) -> str:
        if self._variable:
            return self._variable
        elif self._variable_group:
            return self._variable_group
        else:
            return 'UNKNOWN'
