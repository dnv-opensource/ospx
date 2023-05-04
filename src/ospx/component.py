import logging
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, MutableMapping, Union

from dictIO import DictWriter
from dictIO.utils.counter import BorgCounter

from ospx import Connector
from ospx.fmi import FMU, ScalarVariable, Unit

__ALL__ = ["Component"]

logger = logging.getLogger(__name__)


class Component:
    r"""A component is an instance of a (component-) model.

    A component represents an instance of a (component-) model. Any system structure can contain an arbitrary number of components.
    Important here is, that multiple components in a system structure can be instances of one and the same model.
    In practical terms this means that multiple components can refer to the same physical FMU file. \n
    As components are instances of a model (FMU), they inherit the start values defined in the FMU's modelDescription file upon instantiation; \n
    howevere, being an instance, each component can alter and overwrite these start values.
    This is accomplished using the 'initialize' section inside a 'component' element in the ospx case dict. \n
    See https://dnv-opensource.github.io/ospx/fileFormat.caseDict.html

    Equivalent terms to 'component' are: \n
    \t 'Simulator' in OSP. See https://open-simulation-platform.github.io/libcosim/configuration#simulator \n
    \t 'Simulation model' in FMI for co-simulation. See https://github.com/modelica/fmi-standard/releases/download/v2.0.3/FMI-Specification-2.0.3.pdf \n
    \t 'Component' in SSP. See https://ssp-standard.org/publications/SSP10/SystemStructureAndParameterization10.pdf
    """

    def __init__(self, name: str, properties: MutableMapping[Any, Any]):
        self.name: str = name
        self.generate_proxy = False
        self.fmu: FMU
        self.step_size: Union[float, None] = None
        self._initial_values: dict[str, ScalarVariable] = {}
        self._connectors: dict[str, Connector] = {}
        self.generate_proxy: bool = False
        self.remote_access: Union[RemoteAccess, None] = None
        self.counter = BorgCounter()
        self._units: dict[str, Unit]
        self._variables: dict[str, ScalarVariable]

        self._read_fmu(properties)
        self._read_step_size(properties)

        self._read_generate_proxy(properties)
        self._read_remote_access(properties)
        if self.generate_proxy:
            self._generate_proxy()

        self._read_initialize(properties)
        self._init_units()
        self._init_variables()

        self._read_connectors(properties)

    def _read_fmu(self, properties: MutableMapping[Any, Any]):
        if "fmu" not in properties:
            msg = f"component {self.name}: 'fmu' element missing in case dict."
            logger.exception(msg)
            raise ValueError(msg)
        # Read name of fmu file from component properties.
        # Note: Relative paths (if existing) are omitted from the fmu name, as it is by convention expected
        # that the fmu has already been copied from the library into the current working directory (=case folder)
        fmu_file = Path(properties["fmu"])
        if not fmu_file.exists():
            logger.exception(f"component {self.name}: referenced FMU file {fmu_file} not found.")
            raise FileNotFoundError(fmu_file)
        self.fmu = FMU(fmu_file)
        if self.fmu.default_experiment and not self.step_size:
            self.step_size = self.fmu.default_experiment.step_size

    def _read_step_size(self, properties: MutableMapping[Any, Any]):
        if "stepSize" not in properties:
            return
        self.step_size = float(properties["stepSize"])

    def _read_initialize(self, properties: MutableMapping[Any, Any]):
        if "initialize" not in properties:
            return
        for variable_name, variable_properties in properties["initialize"].items():
            variable = ScalarVariable(name=variable_name)
            if "causality" in variable_properties:
                variable.causality = variable_properties["causality"]
            if "variability" in variable_properties:
                variable.variability = variable_properties["variability"]
            if "start" in variable_properties:
                variable.start = variable_properties["start"]
            self._initial_values[variable.name] = variable

    def _read_connectors(self, properties: MutableMapping[Any, Any]):
        if "connectors" not in properties:
            return
        for connector_name, connector_properties in properties["connectors"].items():
            connector = Connector(name=connector_name)
            if "variable" in connector_properties:
                connector.variable = connector_properties["variable"]
            if "variableGroup" in connector_properties:
                connector.variable_group = connector_properties["variableGroup"]
            if "type" in connector_properties:
                connector.type = connector_properties["type"]
            self._connectors[connector.name] = connector

    def _read_generate_proxy(self, properties: MutableMapping[Any, Any]):
        if "generate_proxy" not in properties:
            return
        self.generate_proxy = properties["generate_proxy"]

    def _read_remote_access(self, properties: MutableMapping[Any, Any]):
        if "remoteAccess" not in properties:
            return
        if "host" in properties["remoteAccess"] and "port" in properties["remoteAccess"]:
            self.remote_access = RemoteAccess(
                host=properties["remoteAccess"]["host"],
                port=properties["remoteAccess"]["port"],
            )

    def _generate_proxy(self):
        if not self.remote_access:
            logger.error(
                f"component {self.name}: 'generate_proxy' set to True, but the 'remoteAccess' element is not correctly defined."
            )
        elif not self.remote_access.host:
            logger.error(f"component {self.name}: 'remoteAccess' element is defined, but host is not specified.")
        elif not self.remote_access.port:
            logger.error(f"component {self.name}: 'remoteAccess' element is defined, but port is not specified.")
        else:
            self.fmu = self.fmu.proxify(self.remote_access.host, self.remote_access.port)
            # if NTNU-IHB fmu-proxy code is used, use '-proxy' reference
            self.name = f"{self.name}-proxy"
            # self.name = self.fmu.file.stem

    def _init_units(self):
        self._units = deepcopy(self.fmu.units)

    def _init_variables(self):
        self._variables = deepcopy(self.fmu.variables)

        for variable_name, variable in self._initial_values.items():
            if variable.causality:
                self._variables[variable_name].causality = variable.causality
            if variable.variability:
                self._variables[variable_name].variability = variable.variability
            if variable.start:
                self._variables[variable_name].start = variable.start

    @property
    def variables_with_start_values(self) -> dict[str, ScalarVariable]:
        """Returns a dict with all scalar variables for which start values (initial values)
        are defined in the component.

        Returns
        -------
        dict[str, ScalarVariable]
            dict with all scalar variables with start values defined.
        """
        return self._initial_values

    @property
    def units(self) -> dict[str, Unit]:
        """Returns a dict with all units defined in the component.

        Returns
        -------
        dict[str, Unit]
            dict with all units
        """
        return self._units

    @property
    def variables(self) -> dict[str, ScalarVariable]:
        """Returns a dict with all scalar variables defined in the component.

        Returns
        -------
        dict[str, ScalarVariable]
            dict with all scalar variables
        """
        return self._variables

    @property
    def connectors(self) -> dict[str, Connector]:
        """Returns a dict with all connectors defined by the component.

        Returns
        -------
        dict[str, Connector]
            dict with all connectors
        """
        return self._connectors

    def write_osp_model_description_xml(self):  # sourcery skip: merge-dict-assign
        """Write the <component.name>_OspModelDescription.xml file in the current working directory."""
        osp_model_description_file = self.fmu.file.parent.absolute() / f"{self.name}_OspModelDescription.xml"
        self._clean(osp_model_description_file)

        osp_model_description = {}

        # Unit Definitions
        unit_definitions = {}
        for unit in self.units.values():
            unit_definition = {"_attributes": {}}
            unit_definition["_attributes"]["name"] = unit.name
            if unit.base_unit:
                unit_definition["BaseUnit"] = {"_attributes": {}}
                if unit.base_unit.kg:
                    unit_definition["BaseUnit"]["_attributes"]["kg"] = unit.base_unit.kg
                if unit.base_unit.m:
                    unit_definition["BaseUnit"]["_attributes"]["m"] = unit.base_unit.m
                if unit.base_unit.s:
                    unit_definition["BaseUnit"]["_attributes"]["s"] = unit.base_unit.s
                if unit.base_unit.A:
                    unit_definition["BaseUnit"]["_attributes"]["A"] = unit.base_unit.A
                if unit.base_unit.K:
                    unit_definition["BaseUnit"]["_attributes"]["K"] = unit.base_unit.K
                if unit.base_unit.mol:
                    unit_definition["BaseUnit"]["_attributes"]["mol"] = unit.base_unit.mol
                if unit.base_unit.cd:
                    unit_definition["BaseUnit"]["_attributes"]["cd"] = unit.base_unit.cd
                if unit.base_unit.rad:
                    unit_definition["BaseUnit"]["_attributes"]["rad"] = unit.base_unit.rad
                if unit.base_unit.factor:
                    unit_definition["BaseUnit"]["_attributes"]["factor"] = unit.base_unit.factor
                if unit.base_unit.offset:
                    unit_definition["BaseUnit"]["_attributes"]["offset"] = unit.base_unit.offset
            if unit.display_unit:
                unit_definition["DisplayUnit"] = {"_attributes": {}}
                unit_definition["DisplayUnit"]["_attributes"]["name"] = unit.display_unit.name
                unit_definition["DisplayUnit"]["_attributes"]["factor"] = unit.display_unit.factor
                unit_definition["DisplayUnit"]["_attributes"]["offset"] = unit.display_unit.offset
            unit_definitions[f"{self.counter():06d}_Unit"] = unit_definition
        osp_model_description["UnitDefinitions"] = unit_definitions

        # Variable Groups
        variable_groups = {}
        for variable_name, variable in self.variables.items():
            if not variable.quantity:
                logger.warning(f"component {self.name}: no quantity defined for variable {variable_name}")
            if not variable.unit:
                logger.warning(f"component {self.name}: no unit defined for variable {variable_name}")
            quantity_name = variable.quantity or "UNKNOWN"
            quantity_unit = variable.unit or "UNKNOWN"
            variable_groups[f"{self.counter():06d}_Generic"] = {
                "_attributes": {"name": quantity_name},
                quantity_name: {
                    "_attributes": {"name": quantity_name},
                    "Variable": {
                        "_attributes": {
                            "ref": variable_name,
                            "unit": quantity_unit,
                        }
                    },
                },
            }
        osp_model_description["VariableGroups"] = variable_groups

        # _xmlOpts
        osp_model_description["_xmlOpts"] = {
            "_nameSpaces": {"osp": "https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd"},
            "_rootTag": "ospModelDescription",
        }

        DictWriter.write(osp_model_description, osp_model_description_file)

    def _clean(self, file_to_remove: Union[str, Path]):
        """Clean up single file."""
        if isinstance(file_to_remove, str):
            file_to_remove = Path.cwd() / file_to_remove
        file_to_remove.unlink(missing_ok=True)


@dataclass()
class RemoteAccess:
    """Data class holding the host and port information for a remote connection."""

    host: str = field(default_factory=lambda: "")
    port: int = 0
