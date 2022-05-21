import logging
from typing import MutableMapping, Union


logger = logging.getLogger(__name__)


class Variable():

    def __init__(self, name: str, properties: MutableMapping):
        self.name: str = name
        self.fmi_data_type: str = ''
        self.causality: str = ''
        self.variability: str = ''
        self.initial_value: Union[int, float, bool, str] = 0.0

        if 'start' in properties:
            self.initial_value = properties['start']
            self.fmi_data_type = self._get_fmi_data_type(properties['start'])
        if 'causality' in properties:
            self.causality = properties['causality']
        if 'variability' in properties:
            self.variability = properties['variability']

    def _get_fmi_data_type(self, arg):
        """Returns the fmi data type of the passed in argument (best guess)
        """
        if isinstance(arg, int):
            return 'Integer'
        elif isinstance(arg, float):
            return 'Real'
        elif isinstance(arg, bool):
            return 'Bool'
        else:
            return 'String'
