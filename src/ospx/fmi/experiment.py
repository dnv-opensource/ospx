import logging
from dataclasses import dataclass
from typing import Union


logger = logging.getLogger(__name__)


@dataclass()
class Experiment():
    start_time: Union[float, None] = None
    stop_time: Union[float, None] = None
    tolerance: Union[float, None] = None
    step_size: Union[float, None] = None
