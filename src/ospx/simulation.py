import logging
from dataclasses import dataclass

__ALL__ = ["Simulation"]

logger = logging.getLogger(__name__)


@dataclass()
class Simulation:
    """Data class holding the attributes of the 'simulation' element inside OspSystemStructure.xml."""

    name: str | None = None
    start_time: float | None = None
    stop_time: float | None = None
    base_step_size: float | None = None
    _algorithm: str | None = None

    @property
    def algorithm(self) -> str | None:
        """Return the simulation algorithm."""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str) -> None:
        """Set the simulation algorithm."""
        valid_values: list[str] = [
            "fixedStep",
        ]
        if value not in valid_values:
            logger.error(f"variable {self.name}: algorithm value '{value}' is invalid.")
            return
        self._algorithm = value
        return
