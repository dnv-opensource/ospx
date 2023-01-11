import logging
from dataclasses import dataclass
from typing import Union

__ALL__ = ["Simulation"]

logger = logging.getLogger(__name__)


@dataclass()
class Simulation:
    """Data class holding the attributes of the 'simulation' element inside OspSystemStructure.xml."""

    name: Union[str, None] = None
    start_time: Union[float, None] = None
    stop_time: Union[float, None] = None
    base_step_size: Union[float, None] = None
    _algorithm: Union[str, None] = None

    @property
    def algorithm(self) -> Union[str, None]:  # noqa: D102
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str):  # noqa: D102
        valid_values: list[str] = [
            "fixedStep",
        ]
        if value not in valid_values:
            logger.error(f"variable {self.name}: algorithm value '{value}' is invalid.")
            return
        self._algorithm = value
        return
