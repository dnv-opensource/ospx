import logging
from dataclasses import dataclass

__ALL__ = ["Experiment"]

logger = logging.getLogger(__name__)


@dataclass()
class Experiment:
    """Data class for the DefaultExperiment element inside fmi 2.0 ModelDescription.

    See https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2ModelDescription.xsd
    """

    start_time: float | None = None
    stop_time: float | None = None
    tolerance: float | None = None
    step_size: float | None = None
