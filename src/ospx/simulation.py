import logging
from dataclasses import dataclass
from typing import Union


logger = logging.getLogger(__name__)


@dataclass()
class Simulation():
    name: Union[str, None] = None
    start_time: Union[float, None] = None
    stop_time: Union[float, None] = None
    base_step_size: Union[float, None] = None
