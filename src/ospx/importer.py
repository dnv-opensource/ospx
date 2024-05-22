import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Union

from dictIO import DictReader, DictWriter
from dictIO.utils.counter import BorgCounter
from dictIO.utils.path import highest_common_root_folder, relative_path

from ospx.utils.dict import find_key, find_keys, find_type_identifier_in_keys

__ALL__ = ["OspSystemStructureImporter"]

logger = logging.getLogger(__name__)


class OspSystemStructureImporter:
    """Class providing methods to convert an existing
    OspSystemStructure.xml file to an ospx caseDict file.
    """

    @staticmethod
    def import_system_structure(
        system_structure_file: Union[str, os.PathLike[str]],
        enter_lib_source_as_relative_path: bool = False,
    ):
        """Import an OspSystemStructure.xml file and save it as an ospx caseDict file.

        Parameters
        ----------
        system_structure_file : Union[str, os.PathLike[str]]
            the OspSystemStructure.xml file to be imported
        enter_lib_source_as_relative_path : bool, optional
            whether lib_source shall be entered as relative path in the caseDict, by default False

        Raises
        ------
        FileNotFoundError
            if system_structure_file does not exist

        NotImplementedError
            if the OspSystemStructure contains connections of OSP-IS type 'SignalConnection' or 'SignalGroupConnection'.
            These connection types are not implemented yet in ospx.

        NotImplementedError
            if the OspSystemStructure contains connections with OSP-IS endpoint type 'Signal' or 'SignalGroup'.
            These endpoint types are not implemented yet in ospx.

        TypeError
            if the OspSystemStructure contains connections of an unknown type.

        TypeError
            if the OspSystemStructure contains connections with an unknown endpoint type.
        """

        # Make sure source_file argument is of type Path. If not, cast it to Path type.
        system_structure_file = (
            system_structure_file if isinstance(system_structure_file, Path) else Path(system_structure_file)
        )

        # Check whether system structure file exists
        if not system_structure_file.exists():
            logger.error(f"OspSystemStructureImporter: File {system_structure_file} not found.")
            raise FileNotFoundError(system_structure_file)

        if system_structure_file.suffix != ".xml":
            logger.error(f"OspSystemStructureImporter: File type {system_structure_file} not implemented yet.")
            return

        counter = BorgCounter()

        source_dict = DictReader.read(system_structure_file, comments=False)
        source_folder: Path = system_structure_file.resolve().parent.absolute()
        lib_source_folder: Path = source_folder  # setting to source_folder acts as fallback / default
        target_folder: Path = Path.cwd().absolute()

        # Main subdicts contained in systemStructure
        connections: Dict[str, Dict[Any, Any]] = {}
        components: Dict[str, Dict[Any, Any]] = {}

        # Connections
        # iterate over the connections first as they contain the variable and component names
        temp_connectors = {}
        if connections_key := find_key(source_dict, "Connections$"):
            for connection_type, connection_properties in source_dict[connections_key].items():
                connection_type: str = re.sub(r"(^\d{1,6}_)", "", connection_type)

                if connection_type not in {
                    "VariableConnection",
                    "VariableGroupConnection",
                }:
                    if connection_type in {"SignalConnection", "SignalGroupConnection"}:
                        msg: str = (
                            f"Import failed: {system_structure_file.name} contains a connection with OSP-IS connection type '{connection_type}'\n"
                            f"The support for connection type '{connection_type}' is not yet implemented in ospx."
                        )
                        logger.error(msg)
                        raise NotImplementedError(msg)
                    else:
                        msg: str = f"Import failed: {system_structure_file.name} contains a connection with unknown connection type '{connection_type}'\n"
                        logger.error(msg)
                        raise TypeError(msg)

                connection: Dict[str, Dict[Any, Any]] = {}
                connection_name: str = ""
                # following loop has range {0,1}
                for index, (endpoint_type, endpoint_properties) in enumerate(connection_properties.items()):
                    endpoint_type: str = re.sub(r"(^\d{1,6}_)", "", endpoint_type)

                    if endpoint_type not in {"Variable", "VariableGroup"}:
                        if endpoint_type in {"Signal", "SignalGroup"}:
                            msg: str = (
                                f"Import failed: {system_structure_file.name} contains a connection with OSP-IS endpoint type '{endpoint_type}'\n"
                                f"The support for endpoint type '{endpoint_type}' is not yet implemented in ospx."
                            )
                            logger.error(msg)
                            raise NotImplementedError(msg)
                        else:
                            msg: str = f"Import failed: {system_structure_file.name} contains a connection with unknown endpoint type '{endpoint_type}'\n"
                            logger.error(msg)
                            raise TypeError(msg)

                    component_name: str = endpoint_properties["_attributes"]["simulator"]
                    referenced_name: str = endpoint_properties["_attributes"]["name"]
                    # alternator for source <--> target (because there are always 2 entries in VariableConnection in always the same sequence)
                    endpoint_name: str = "source" if index % 2 == 0 else "target"
                    endpoint: dict[str, str] = {}
                    _connector_type: str = "output" if endpoint_name == "source" else "input"
                    _connector: dict[str, str] = {}
                    _connector_name: str = f"{component_name}_{referenced_name}"
                    if endpoint_type == "Variable":
                        endpoint = {
                            "component": component_name,
                            "variable": referenced_name,
                        }
                        _connector = {
                            "variable": referenced_name,
                            "type": _connector_type,
                        }
                    elif endpoint_type == "VariableGroup":
                        endpoint = {
                            "component": component_name,
                            "connector": _connector_name,
                        }
                        _connector = {
                            "variableGroup": referenced_name,
                            "type": _connector_type,
                        }
                    connection[endpoint_name] = endpoint
                    if not connection_name:
                        connection_name = component_name
                    else:
                        connection_name += f"_to_{component_name}"

                    # Save _connector in temp_connectors dict.
                    # (The variable and component information stored in these connectors
                    #  is later used to complete component properties)
                    temp_connectors[f"{counter():06d}_{component_name}"] = {_connector_name: _connector}
                # Save in connections dict
                if connection_name in connections:
                    suffix_number: int = 2
                    _connection_name: str = f"{connection_name}_{suffix_number:02d}"
                    while _connection_name in connections:
                        suffix_number += 1
                        _connection_name = f"{connection_name}_{suffix_number:02d}"
                    connection_name = _connection_name
                connections[connection_name] = connection
        # Simulators (=Components)
        if simulators_key := find_key(source_dict, "Simulators$"):
            # Determine the highest common root folder among all FMU's.
            # This will be used as libSource folder.
            fmu_folders: List[Path] = []
            for simulator_properties in source_dict[simulators_key].values():
                fmu_name: str = simulator_properties["_attributes"]["source"]
                fmu_file: Path = Path(fmu_name)
                fmu_folder: Path
                if fmu_file.is_absolute():
                    fmu_folder = fmu_file.resolve().parent.absolute()
                else:
                    fmu_folder = (source_folder / fmu_file).resolve().parent.absolute()
                fmu_folders.append(fmu_folder)
            if fmu_folders:
                lib_source_folder = highest_common_root_folder(fmu_folders)

            for simulator_properties in source_dict[simulators_key].values():
                # Component
                component_name = simulator_properties["_attributes"]["name"]
                # Connectors
                component_connectors: Dict[str, Dict[Any, Any]] = {}
                for temp_connector_key, connector in temp_connectors.items():
                    if component_name in temp_connector_key:
                        component_connectors |= connector
                # FMU
                fmu_name: str = simulator_properties["_attributes"]["source"]
                fmu_file: Path = Path(fmu_name)
                if fmu_file.is_absolute():
                    fmu_file = fmu_file.resolve()
                else:
                    fmu_file = (source_folder / fmu_file).resolve()
                fmu_file_relative_to_lib_source: Path = relative_path(lib_source_folder, fmu_file)
                # Step Size
                step_size: Union[float, None] = None
                if "stepSize" in simulator_properties["_attributes"]:
                    step_size = float(simulator_properties["_attributes"]["stepSize"])
                    # Initial values
                component_initial_values: Dict[str, Dict[Any, Any]] = {}
                if initial_values_key := find_key(simulator_properties, "InitialValues$"):
                    initial_values = simulator_properties[initial_values_key]
                    if initial_value_keys := find_keys(initial_values, "InitialValue$"):
                        for initial_value_key in initial_value_keys:
                            initial_value = initial_values[initial_value_key]
                            if data_type := find_type_identifier_in_keys(initial_value):
                                type_key = find_key(initial_value, f"{data_type}$")
                                if not type_key:
                                    continue
                                _type: str = re.sub(r"(^\d{1,6}_)", "", type_key)
                                referenced_name = initial_value["_attributes"]["variable"]
                                value: Union[float, int, bool, str]
                                if _type == "Boolean":
                                    value = bool(initial_value[type_key]["_attributes"]["value"])
                                elif _type == "Integer":
                                    value = int(initial_value[type_key]["_attributes"]["value"])
                                elif _type == "Real":
                                    value = float(initial_value[type_key]["_attributes"]["value"])
                                else:
                                    value = initial_value[type_key]["_attributes"]["value"]
                                component_initial_values |= {referenced_name: {"start": value}}
                                # Assemble component
                component: Dict[str, Union[Dict[Any, Any], str, float, Path]] = {
                    "connectors": component_connectors,
                    "fmu": fmu_file_relative_to_lib_source,
                }
                if step_size:
                    component["stepSize"] = step_size
                if component_initial_values:
                    component["initialize"] = component_initial_values
                    # Save in components dict
                components[component_name] = component

        # System Structure
        system_structure: Dict[str, Dict[str, Any]] = {
            "connections": connections,
            "components": components,
        }

        # Global Settings
        # 1: Defaults
        simulation: Dict[str, Any] = {
            "name": system_structure_file.stem,
            "startTime": 0.0,
            "baseStepSize": 0.01,
            "algorithm": "fixedStep",
        }
        # 2: Overwrite defaults with values from source dict, where existing
        if "_attributes" in source_dict:
            attributes = source_dict["_attributes"]
            if "StartTime" in attributes:
                simulation["startTime"] = attributes["StartTime"]
            if "BaseStepSize" in attributes:
                simulation["baseStepSize"] = attributes["BaseStepSize"]
            if "Algorithm" in attributes:
                simulation["algorithm"] = attributes["Algorithm"]

        # Environment
        environment: dict[str, Path] = {}
        if enter_lib_source_as_relative_path:
            try:
                environment["libSource"] = relative_path(
                    from_path=target_folder,
                    to_path=lib_source_folder,
                )
            except ValueError:
                msg = (
                    "Resolving relative path from target folder to libSource folder failed.\n"
                    "Absolute path for libSource is used instead."
                )
                logger.warning(msg)
                environment["libSource"] = lib_source_folder
        else:
            environment["libSource"] = lib_source_folder

        # Assemble case dict
        case_dict = {
            "_environment": environment,
            "systemStructure": system_structure,
            "run": {
                "simulation": simulation,
            },
        }

        source_file_name = source_dict.name.replace(".", "_")
        target_file = Path.cwd() / f"caseDict_imported_from_{source_file_name}"

        DictWriter.write(case_dict, target_file, mode="w")

        return
