import logging
from dataclasses import dataclass
from typing import Union


__ALL__ = ['Endpoint', 'Connection']

logger = logging.getLogger(__name__)


@dataclass()
class Endpoint():
    component: Union[str, None] = None
    connector: Union[str, None] = None
    variable: Union[str, None] = None


@dataclass()
class Connection():
    name: str
    source: Union[Endpoint, None] = None
    target: Union[Endpoint, None] = None
