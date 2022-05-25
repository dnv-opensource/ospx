import logging
from dataclasses import dataclass
from typing import Union


logger = logging.getLogger(__name__)


@dataclass()
class Connector():
    name: str
    variable: Union[str, None] = None
    _type: Union[str, None] = None

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
