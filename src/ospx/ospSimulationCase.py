import logging
import re
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List, Union

from dictIO import CppDict, DictWriter, XmlFormatter
from dictIO.utils.counter import BorgCounter
from dictIO.utils.path import relative_path

from ospx import Simulation, System
from ospx.utils.dict import find_key

__ALL__ = ["OspSimulationCase"]

logger = logging.getLogger(__name__)


class OspSimulationCase:
    """OSP Simulation Case."""

    def __init__(
        self,
        case_dict: CppDict,
    ):
        self.counter = BorgCounter()
        self.case_dict: CppDict = case_dict
        self.case_folder: Path = case_dict.source_file.resolve().parent if case_dict.source_file else Path.cwd()
        self.system_structure: System

        # Global settings
        self.simulation: Simulation  # general properties of the simulation case
        self._read_simulation()
        self.name: str = self.case_dict.name  # initialize conservatively (with fallback path)
        if self.simulation and self.simulation.name:
            self.name = self.simulation.name

        # Library source path
        self.lib_source: Path
        self._resolve_lib_source_folder()

    def setup(self):
        """Set up the OSP simulation case folder.

        Raises
        ------
        ValueError
            If an expected element in caseDict is missing
        FileNotFoundError
            If an FMU file referenced in caseDict does not exist
        """
        logger.info(f"Set up OSP simulation case '{self.name}' in case folder: {self.case_folder}")

        # Check whether all referenced FMUs actually exist
        self._check_all_fmus_exist()

        # Resolve all referenced FMUs and ensure they are accessible from the case folder via a relative path.
        # This is necessary because OspSystemStructure.xml allows only relative paths
        # as 'source' attribute in a <Simulator> element.
        # If an FMU is not accessible via a relative path, it will be copied into the case folder.
        self._resolve_all_fmus()

        # Read system structure
        if "systemStructure" not in self.case_dict:
            msg = f"no 'systemStructure' section found in {self.case_dict.name}. Cannot set up OSP simulation case."
            logger.exception(msg)
            raise ValueError(msg)
        self.system_structure = System(self.case_dict["systemStructure"])

        # Make sure all components have a step size defined
        self._check_components_step_size()

    def _write_osp_model_description_xmls(self):
        """Write the <component.name>_OspModelDescription.xml files for all components defined in the system structure."""
        logger.info(
            f"Write OspModelDescription.xml files for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )
        if not self.system_structure or not self.system_structure.components:
            return
        for component in self.system_structure.components.values():
            component.write_osp_model_description_xml()
        return

    def write_osp_system_structure_xml(self):
        """Write the OspSystemStructure.xml file."""
        # sourcery skip: class-extract-method, merge-dict-assign

        osp_system_structure_file = self.case_folder / "OspSystemStructure.xml"
        self._clean(osp_system_structure_file)

        logger.info(
            f"Write OspSystemStructure.xml file for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        osp_system_structure: Dict[str, Any] = {}
        osp_system_structure["_xmlOpts"] = {
            "_nameSpaces": {"osp": "https://opensimulationplatform.com/xsd/OspModelDescription-1.0.0.xsd"},
            "_rootTag": "OspSystemStructure",
        }

        # Global Settings
        if self.simulation:
            if self.simulation.start_time:
                osp_system_structure["StartTime"] = self.simulation.start_time
            if self.simulation.base_step_size:
                osp_system_structure["BaseStepSize"] = self.simulation.base_step_size
            if self.simulation.algorithm:
                osp_system_structure["Algorithm"] = self.simulation.algorithm

        # Simulators (=Components)
        simulators: Dict[str, Any] = {}
        for index, (_, component) in enumerate(self.system_structure.components.items()):
            simulator_key = f"{index:06d}_Simulator"
            simulator_properties: Dict[str, Dict[str, Union[str, float, Dict[str, Any], Path]]] = {
                "_attributes": {
                    "name": component.name,
                    "source": relative_path(self.case_folder, component.fmu.file),
                }
            }
            if component.step_size:
                write_step_size_to_osp_system_structure: bool = True
                if (
                    component.fmu.default_experiment
                    and component.fmu.default_experiment.step_size
                    and component.step_size == component.fmu.default_experiment.step_size
                ):
                    write_step_size_to_osp_system_structure = False
                if write_step_size_to_osp_system_structure:
                    simulator_properties["_attributes"]["stepSize"] = component.step_size

            if component.variables_with_start_values:
                simulator_properties["InitialValues"] = {}
                for index, (_, variable) in enumerate(component.variables_with_start_values.items()):
                    if variable.start is not None and variable.data_type is None:
                        logger.error(
                            f"component {component.name}: An initial value is defined for variable {variable.name}, but its data type is not defined.\n"
                            f"The initial value for variable {variable.name} will not be written into OspSystemStructure.xml.\n"
                            "OspSystemStructure.xml will be potentially wrong or incomplete."
                        )
                    else:
                        initial_value_key = f"{index:06d}_InitialValue"
                        initial_value_properties: Dict[str, Any] = {}
                        initial_value_properties["_attributes"] = {"variable": variable.name}
                        if variable.data_type:
                            initial_value_properties[variable.data_type] = {"_attributes": {"value": variable.start}}

                        simulator_properties["InitialValues"][initial_value_key] = initial_value_properties
            simulators[simulator_key] = simulator_properties

        osp_system_structure["Simulators"] = simulators

        # Connections
        connections: Dict[str, Dict[str, Any]] = {}
        for connection in self.system_structure.connections.values():
            if not connection.is_valid:
                continue
            if connection.is_variable_connection:
                connection_key = f"{self.counter():06d}_VariableConnection"
                # (note: the order 000000, 000001 is essential here!)
                connections[connection_key] = {
                    "000000_Variable": {
                        "_attributes": {
                            "simulator": connection.source_endpoint.component.name,
                            "name": connection.source_endpoint.variable_name,
                        }
                    },
                    "000001_Variable": {
                        "_attributes": {
                            "simulator": connection.target_endpoint.component.name,
                            "name": connection.target_endpoint.variable_name,
                        }
                    },
                }
            if connection.is_variable_group_connection:
                connection_key = f"{self.counter():06d}_VariableGroupConnection"
                # (note: the order 000000, 000001 is essential here!)
                connections[connection_key] = {
                    "000000_VariableGroup": {
                        "_attributes": {
                            "simulator": connection.source_endpoint.component.name,
                            "name": connection.source_endpoint.variable_name,
                        }
                    },
                    "000001_VariableGroup": {
                        "_attributes": {
                            "simulator": connection.target_endpoint.component.name,
                            "name": connection.target_endpoint.variable_name,
                        }
                    },
                }
        osp_system_structure["Connections"] = connections

        # Write OspSystemStructure.xml
        formatter = XmlFormatter()
        DictWriter.write(osp_system_structure, osp_system_structure_file, formatter=formatter)

        self._correct_wrong_xml_namespace(
            "OspSystemStructure.xml",
            "<OspSystemStructure.*>?",
            """<OspSystemStructure xmlns="http://opensimulationplatform.com/MSMI/OSPSystemStructure" version="0.1">""",
        )

        return

    def write_system_structure_ssd(self):
        """Write the SystemStructure.ssd file."""

        system_structure_ssd_file = self.case_folder / "SystemStructure.ssd"
        self._clean(system_structure_ssd_file)

        # sourcery skip: merge-dict-assign
        logger.info(
            f"Write SystemStructure.ssd file for OSP simulation case '{self.name}' in case folder: {self.case_folder}"
        )

        system_structure_ssd: Dict[str, Any] = {}
        system_structure_ssd["_xmlOpts"] = {
            "_nameSpaces": {
                "ssd": "file:///C:/Software/OSP/xsd/SystemStructureDescription",
                "ssv": "file:///C:/Software/OSP/xsd/SystemStructureParameterValues",
                "ssc": "file:///C:/Software/OSP/xsd/SystemStructureCommon",
            },
            "_rootTag": "SystemStructureDescription",
        }
        system_structure_ssd["System"] = {
            "_attributes": {
                "name": self.name,
                "description": self.name,
            }
        }

        # Global settings
        default_experiment = {
            "Annotations": {
                "Annotation": {
                    "_attributes": {"type": "com.opensimulationplatform"},
                    "Algorithm": {
                        "FixedStepAlgorithm": {
                            "_attributes": {
                                "baseStepSize": str(self.simulation.base_step_size),
                                "startTime": str(self.simulation.start_time),
                                "stopTime": str(self.simulation.stop_time),
                            }
                        }
                    },
                }
            }
        }
        system_structure_ssd["DefaultExperiment"] = default_experiment

        # Components
        components: Dict[str, Any] = {}
        for component_name, component in self.system_structure.components.items():
            connectors: Dict[str, Dict[str, Any]] = {}
            for connector in component.connectors.values():
                if connector.variable and connector.type:
                    connector_key = f"{self.counter():06d}_Connector"
                    # (note: the order 000000, 000001 is essential here!)
                    connectors[connector_key] = {
                        "_attributes": {
                            "name": connector.variable,
                            "kind": connector.type,
                        },
                        "Real": {},
                    }
            element_key = f"{self.counter():06d}_Component"
            components[element_key] = {
                "_attributes": {
                    "name": component_name,
                    "source": relative_path(self.case_folder, component.fmu.file),
                },
                "Connectors": connectors,
            }
        system_structure_ssd["System"]["Elements"] = components

        # Connections
        connections: Dict[str, Any] = {}
        for connection in self.system_structure.connections.values():
            if connection.source_endpoint and connection.target_endpoint:
                connection_key = f"{self.counter():06d}_Connection"
                connections[connection_key] = {
                    "_attributes": {
                        "startElement": connection.source_endpoint.component.name,
                        "startConnector": connection.source_endpoint.variable_name,
                        "endElement": connection.target_endpoint.component.name,
                        "endConnector": connection.target_endpoint.variable_name,
                    }
                }
        system_structure_ssd["System"]["Connections"] = connections

        # Write SystemStructure.ssd
        formatter = XmlFormatter(omit_prefix=False)
        DictWriter.write(system_structure_ssd, system_structure_ssd_file, formatter=formatter)

        return

    def write_statistics_dict(self):
        """Write selected properties of the system structure into a statistics dict.

        I.e. for documentation or further statistical analysis.
        """
        statistics_dict_file = self.case_folder / "statisticsDict"
        # self._clean(statistics_dict_file)

        # sourcery skip: merge-dict-assign, simplify-dictionary-update
        logger.info(f"Write statistics dict for OSP simulation case '{self.name}' in case folder: {self.case_folder}")

        statistics_dict = {}

        statistics_dict["simulation"] = {"name": self.simulation.name}

        statistics_dict["components"] = {
            "count": len(self.system_structure.components.keys()),
            "names": list(self.system_structure.components.keys()),
        }

        statistics_dict["connections"] = {
            "count": len(self.system_structure.connections.keys()),
            "names": list(self.system_structure.connections.keys()),
        }

        statistics_dict["connectors"] = {
            "count": len(self.system_structure.connectors.keys()),
            "names": list(self.system_structure.connectors.keys()),
        }

        unit_list: List[str] = []
        display_unit_list: List[str] = []
        factors_list: List[float] = []
        offsets_list: List[float] = []
        for unit in self.system_structure.units.values():
            unit_list.append(unit.name)
            display_unit_list.append(unit.display_unit.name)
            factors_list.append(unit.display_unit.factor)
            offsets_list.append(unit.display_unit.offset)

        statistics_dict["units"] = {
            "count": len(self.system_structure.units.keys()),
            "unitNames": unit_list,
            "displayUnitNames": display_unit_list,
            "factors": factors_list,
            "offsets": offsets_list,
        }

        statistics_dict["variables"] = {
            "count": len(self.system_structure.variables.keys()),
            "names": list(self.system_structure.variables.keys()),
        }

        DictWriter.write(statistics_dict, statistics_dict_file, mode="w")

    def write_watch_dict(self):
        """Write a case-specific watch dict file.

        The watch dict file can be used with watchCosim for
            - convergence control
            - convergence plotting
            - extracting the results
        """
        watch_dict_file = self.case_folder / "watchDict"
        # self._clean(watch_dict_file)

        logger.info(f"Write watch dict for OSP simulation case '{self.name}' in case folder: {self.case_folder}")

        watch_dict: Dict[str, Any] = {
            "datasources": {},
            "delimiter": ",",  # 'objects': {},
            "simulation": {"name": self.simulation.name},
        }

        # Components
        for component_name, component in self.system_structure.components.items():
            no_of_connectors = len(component.connectors.keys())

            # @TODO: Time, StepCount, conn0, conn1, etc from modelDescription.xml ModelVariables
            #        should match connectors in caseDict for respective model. Improvement needed.
            #        FRALUM, 2021-xx-xx
            columns = [0, 1] + [x + 2 for x in range(no_of_connectors)]  # f*** StepCount

            watch_dict["datasources"].update({component_name: {"columns": columns}})

        DictWriter.write(watch_dict, watch_dict_file, mode="w")

        return

    def _read_simulation(self):
        """Read general simulation properties from case dict."""
        logger.info("reading simulation properties")  # 0

        if "run" not in self.case_dict:
            return
        if "simulation" not in self.case_dict["run"]:
            return
        simulation = Simulation()
        simulation_properties = self.case_dict["run"]["simulation"]
        if "name" in simulation_properties:
            simulation.name = simulation_properties["name"]
        if "startTime" in simulation_properties:
            simulation.start_time = simulation_properties["startTime"]
        if "stopTime" in simulation_properties:
            simulation.stop_time = simulation_properties["stopTime"]
        if "baseStepSize" in simulation_properties:
            simulation.base_step_size = simulation_properties["baseStepSize"]
        if "algorithm" in simulation_properties:
            simulation.algorithm = simulation_properties["algorithm"]
        self.simulation = simulation

    def _resolve_lib_source_folder(self):
        """Resolve the library source folder."""
        self.lib_source = Path.cwd()  # initialize conservatively (with fallback path)
        if "_environment" in self.case_dict:
            if "libSource" in self.case_dict["_environment"]:
                self.lib_source = Path(self.case_dict["_environment"]["libSource"])
            else:
                logger.warning(
                    f"no 'libSource' element found in {self.case_dict.name}['_environment']. Path to libSource will be set to current working directory."
                )
        else:
            logger.warning(
                f"no '_environment' section found in {self.case_dict.name}. Path to libSource hence is unknown and will be set to current working directory."
            )
        self.lib_source = self.lib_source.resolve().absolute()

    def _resolve_fmu_file(self, fmu_name: str) -> Path:
        fmu_file: Path = Path(fmu_name)
        if fmu_file.is_absolute():
            fmu_file = fmu_file.resolve()
        else:
            fmu_file = (self.lib_source / fmu_file).resolve()
        return fmu_file

    def _check_all_fmus_exist(self):
        """Check whether all referenced FMUs actually exist."""
        logger.debug("Check whether all referenced FMUs exist.")
        components = self.case_dict["systemStructure"]["components"]

        for component_name, component_properties in components.items():
            if "fmu" not in component_properties:
                msg = f"component {component_name}: 'fmu' element missing in case dict."
                logger.exception(msg)
                raise ValueError(msg)
            fmu_file = self._resolve_fmu_file(component_properties["fmu"])
            if not fmu_file.exists():
                msg = f"component {component_name}: referenced FMU file {fmu_file} not found."
                logger.exception(msg)
                raise FileNotFoundError(fmu_file)

    def _resolve_all_fmus(self):
        """Resolve all referenced FMUs and ensures they are accessible from the case folder via a relative path.

        This is necessary because OspSystemStructure.xml allows only relative paths
        as 'source' attribute in a <Simulator> element.
        If an FMU is not accessible via a relative path, the FMU will be copied into the case folder.
        Note: If multiple components reference the same FMU, these get copied only once.
        """

        logger.debug("Ensure all referenced FMUs are accessible from the case folder via a relative path.")
        components = self.case_dict["systemStructure"]["components"]
        for _, component_properties in components.items():
            fmu_file = self._resolve_fmu_file(component_properties["fmu"])
            try:
                _ = relative_path(self.case_folder, fmu_file)
            except ValueError:
                fmu_file = self._copy_fmu_to_case_folder(fmu_file)
            component_properties["fmu"] = fmu_file

    def _copy_fmu_to_case_folder(self, fmu_file: Path) -> Path:
        """Copy the passed in FMU file into the case folder.

        If also an accompanying <fmu_name>_OspModelDescription.xml file exists in the same folder as the FMU file,
        then also that OspModelDescription.xml file will be copied into the case folder.

        Parameters
        ----------
        fmu_file : Path
            FMU file to be copied into the case folder.

        Returns
        -------
        Path
            FMU file copied into the case folder.
        """
        fmu_file_in_case_folder: Path = (self.case_folder / fmu_file.name).resolve().absolute()
        if not fmu_file_in_case_folder.exists():
            logger.info(f"Copy FMU {fmu_file} --> {fmu_file_in_case_folder}")
            copy2(fmu_file, self.case_folder)
            # Check whether also an <fmu_name>_OspModelDescription.xml file exists.
            # If so, copy also that one.
            osp_model_description_file = fmu_file.with_name(f"{fmu_file.stem}_OspModelDescription.xml")
            if osp_model_description_file.exists():
                logger.info(f"Copy OspModelDescription {osp_model_description_file} --> {fmu_file_in_case_folder}")
                copy2(osp_model_description_file, self.case_folder)
        return fmu_file_in_case_folder

    def _check_components_step_size(self):
        """Ensure that all components have a step size defined.

        If a components step size is undefined, it will be set to the base step size.
        """
        if not self.system_structure or not self.system_structure.components:
            return
        if not self.simulation or not self.simulation.base_step_size:
            return
        for component in self.system_structure.components.values():
            if not component.step_size:
                component.step_size = self.simulation.base_step_size
        return

    def _set_components_step_size(self, step_size: float):
        """Overwrite the step size of all components with the passed in value."""
        if not self.system_structure or not self.system_structure.components:
            return
        for component in self.system_structure.components.values():
            component.step_size = step_size
        return

    def _inspect(self):
        """Inspects all components and all FMUs for the public variable names and units they declare, as documented in their modelDescription.xml's.

        Results get logged to the console.
        """
        logger.info(f"Inspect OSP simulation case '{self.name}' in case folder: {self.case_folder}")

        delim = "\t" * 3

        log_string = (
            f"Components and related FMUs as defined in {self.case_dict.name}\n" f"\tcomponent{delim}fmu{delim}\n\n"
        )
        for component_name, component in self.system_structure.components.items():
            log_string += f"\t{component_name}{delim}{component.fmu.file.name}\n"
        logger.info(log_string + "\n")

        log_string = f"FMU attributes defined in the fmu's modelDescription.xml\n" f"\tfmu{delim}attributes{delim}"
        for fmu_name, fmu in self.system_structure.fmus.items():
            log_string += f"\n\n\t{fmu_name}\n"
            fmu_attributes = "\n".join(
                f"\t{delim}{k}{delim}{v}" for k, v in fmu.model_description["_xmlOpts"]["_rootAttributes"].items()
            )
            log_string += fmu_attributes
            if default_experiment_key := find_key(fmu.model_description, "DefaultExperiment$"):
                if "_attributes" in fmu.model_description[default_experiment_key]:
                    fmu_default_experiment = "\n".join(
                        f"\t{delim}{k}{delim}{v}"
                        for k, v in fmu.model_description[default_experiment_key]["_attributes"].items()
                    )
                    log_string += f"\n{fmu_default_experiment}"
        logger.info(log_string + "\n")

        log_string = (
            f"Unit definitions defined in the fmu's modelDescription.xml\n"
            f"\tfmu{delim}unit{delim}display unit{delim}factor{delim}offset"
        )
        for fmu_name, fmu in self.system_structure.fmus.items():
            log_string += f"\n\n\t{fmu_name}\n"
            unit_definitions = "\n".join(
                f"\t{delim}{unit_name}{delim}{unit.display_unit.name}\t{delim}{unit.display_unit.factor}{delim}{unit.display_unit.offset}"
                for unit_name, unit in fmu.units.items()
            )
            log_string += unit_definitions
        logger.info(log_string + "\n")

        log_string = (
            f"Variables defined in the fmu's modelDescription.xml\n" f"\tfmu{delim}variable{delim}type{delim}unit"
        )
        logger.info(log_string + "\n")
        for fmu_name, fmu in self.system_structure.fmus.items():
            log_string = f"\t{fmu_name}\n"
            variable_definitions = "\n".join(
                f"\n\n\t{delim}{variable_name}{delim}{variable.data_type}{delim}{variable.unit}"
                for variable_name, variable in fmu.variables.items()
            )
            log_string += variable_definitions
            logger.info(log_string + "\n")

        log_string = (
            f"Connectors defined in {self.case_dict.name}\n"
            f"\tComponent{delim}Connector{delim}Variable{delim}VariableGroup{delim}Type"
        )
        for component_name, component in self.system_structure.components.items():
            if component.connectors:
                log_string += f"\n\n\t{component_name}\n"
                connector_definitions = "\n".join(
                    f"\t{delim}{connector_name}{delim}{connector.variable}{delim}{connector.variable_group}{delim}{connector.type}"
                    for connector_name, connector in component.connectors.items()
                )
                log_string += connector_definitions
        logger.info(log_string + "\n")

        logger.info("Inspect mode: Finished.")

    def _write_plot_config_json(self):
        """Write the PlotConfig.json file, containing postprocessing information."""

        plot_config_file = self.case_folder / "PlotConfig.json"
        self._clean(plot_config_file)

        if "plots" in self.case_dict["postProcessing"].keys():
            temp_dict: Dict[str, List[Dict[str, Any]]] = {"plots": []}
            for plot in self.case_dict["postproc"]["plots"].values():
                variables: List[Dict[str, Any]] = []
                for (
                    component_name,
                    component,
                ) in self.system_structure.components.items():
                    variables.extend(
                        {
                            "simulator": component_name,
                            "variable": connector.variable,
                        }
                        for connector_name, connector in component.connectors.items()
                        if connector_name in plot["ySignals"]
                    )

                temp_dict["plots"].append(
                    {
                        "label": plot["title"],
                        "plotType": "trend",
                        "variables": variables,
                    }
                )

            DictWriter.write(temp_dict, plot_config_file)

        return

    def _correct_wrong_xml_namespace(self, file_name: str, pattern: str, replace: str):
        """Substitutes namespace
        (may be obsolete in future).
        """
        buffer = ""
        with open(file_name, "r") as f:
            buffer = re.sub(pattern, replace, f.read())

        with open(file_name, "w") as f:
            _ = f.write(buffer)

        return

    def _clean(self, file_to_remove: Union[str, Path]):
        """Clean up single file."""
        if isinstance(file_to_remove, str):
            file_to_remove = self.case_folder / file_to_remove
        file_to_remove.unlink(missing_ok=True)
