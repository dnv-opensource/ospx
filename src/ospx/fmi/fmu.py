import logging
import os
import platform
import re
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from shutil import copyfile
from typing import MutableMapping, Union
from zipfile import ZipFile

from dictIO import CppDict, XmlFormatter, XmlParser
from dictIO.utils.counter import BorgCounter
from ospx.fmi import BaseUnit, DisplayUnit, Experiment, ScalarVariable, Unit
from ospx.utils.dict import find_key, find_type_identifier_in_keys, shrink_dict
from ospx.utils.zip import (
    add_file_content_to_zip, read_file_content_from_zip, remove_files_from_zip, rename_file_in_zip
)


__ALL__ = ['FMU']

logger = logging.getLogger(__name__)


class FMU():
    """Class to read and interact with an fmi 2.0 Functional Mockup Unit (FMU)

    See also https://github.com/modelica/fmi-standard/blob/v2.0.x/schema/fmi2ModelDescription.xsd
    """

    def __init__(self, file: Union[str, os.PathLike[str]]):
        # Make sure fmu_file argument is of type Path. If not, cast it to Path type.
        file = file if isinstance(file, Path) else Path(file)
        if not file.exists():
            logger.error(f"DictParser: File {file} not found.")
            raise FileNotFoundError(file)

        self.file: Path = file
        self.model_description: CppDict = self._read_model_description()
        self.counter = BorgCounter()

    def _read_model_description(self) -> CppDict:
        model_description = CppDict(Path('modelDescription.xml'))
        xml_parser = XmlParser()

        logger.info(f'{self.file.name}: read modelDescription.xml')

        if file_content := read_file_content_from_zip(self.file, 'modelDescription.xml'):
            model_description = xml_parser.parse_string(file_content, model_description)

        self._clean_solver_internal_variables(model_description)

        self.model_description = model_description

        return model_description

    def _write_model_description(
        self, model_description: Union[CppDict, None] = None, write_inside_fmu: bool = False
    ):
        """Save updated model_description both inside FMU as well as separate file in the FMUs directory
        """
        if model_description:
            self.model_description = model_description

        self.model_description['_xmlOpts']['_nameSpaces'] = {
            'xs': 'file:///C:/Software/OSP/xsd/fmi3ModelDescription.xsd'
        }

        formatter = XmlFormatter()
        formatted_xml = formatter.to_string(self.model_description)

        logger.info(f'{self.file.name}: write modelDescription.xml')

        # Write internal modelDescription.xml (inside FMU)
        if write_inside_fmu:
            remove_files_from_zip(self.file, 'modelDescription.xml')
            add_file_content_to_zip(self.file, 'modelDescription.xml', formatted_xml)

        # Write external modelDescription.xml (separate file, beside FMU)
        external_file = self.file.parent.absolute() / f'{self.file.stem}_ModelDescription.xml'
        with open(external_file, 'w') as f:
            f.write(formatted_xml)

        return

    @property
    def units(self) -> dict[str, Unit]:
        model_unit_definitions: dict = {}
        if unit_definitions_key := find_key(self.model_description, 'UnitDefinitions$'):
            model_unit_definitions = self.model_description[unit_definitions_key]
            # make sure unit definitions are unique (e.g. to keep XML files clean)
            model_unit_definitions = shrink_dict(
                model_unit_definitions, unique_key=['_attributes', 'name']
            )
        unit_definitions: dict[str, Unit] = {}
        for u in model_unit_definitions.values():
            unit = Unit()
            unit.name = u['_attributes']['name']
            # BaseUnit
            if base_unit_key := find_key(u, 'BaseUnit$'):
                unit.base_unit = BaseUnit()
                if 'kg' in u[base_unit_key]['_attributes']:
                    unit.base_unit.kg = u[base_unit_key]['_attributes']['kg']
                if 'm' in u[base_unit_key]['_attributes']:
                    unit.base_unit.m = u[base_unit_key]['_attributes']['m']
                if 's' in u[base_unit_key]['_attributes']:
                    unit.base_unit.s = u[base_unit_key]['_attributes']['s']
                if 'A' in u[base_unit_key]['_attributes']:
                    unit.base_unit.A = u[base_unit_key]['_attributes']['A']
                if 'K' in u[base_unit_key]['_attributes']:
                    unit.base_unit.K = u[base_unit_key]['_attributes']['K']
                if 'mol' in u[base_unit_key]['_attributes']:
                    unit.base_unit.mol = u[base_unit_key]['_attributes']['mol']
                if 'cd' in u[base_unit_key]['_attributes']:
                    unit.base_unit.cd = u[base_unit_key]['_attributes']['cd']
                if 'rad' in u[base_unit_key]['_attributes']:
                    unit.base_unit.rad = u[base_unit_key]['_attributes']['rad']
                if 'factor' in u[base_unit_key]['_attributes']:
                    unit.base_unit.factor = u[base_unit_key]['_attributes']['factor']
                if 'offset' in u[base_unit_key]['_attributes']:
                    unit.base_unit.offset = u[base_unit_key]['_attributes']['offset']
            # DisplayUnit
            if display_unit_key := find_key(u, 'DisplayUnit$'):
                unit.display_unit = DisplayUnit()
                if 'name' in u[display_unit_key]['_attributes']:
                    unit.display_unit.name = u[display_unit_key]['_attributes']['name']
                if 'factor' in u[display_unit_key]['_attributes']:
                    unit.display_unit.factor = u[display_unit_key]['_attributes']['factor']
                if 'offset' in u[display_unit_key]['_attributes']:
                    unit.display_unit.offset = u[display_unit_key]['_attributes']['offset']
            unit_definitions[unit.name] = unit
        return unit_definitions

    @property
    def variables(self) -> dict[str, ScalarVariable]:
        model_variables_key = find_key(self.model_description, 'ModelVariables$')
        if not model_variables_key:
            return {}
        # Read model variables from model description
        # (without "_" and "settings" as these are proprietary variables from iti)
        model_variables = {
            k: v
            for k,
            v in self.model_description[model_variables_key].items()
            if not re.match('^(_|settings)', v['_attributes']['name'])
        }
        # Translate variable attributes from model description into Variable objects
        variables: dict[str, ScalarVariable] = {}
        for k, v in model_variables.items():
            variable_type: str = re.sub(r'^\d{6}_', '', k)
            if variable_type == 'ScalarVariable':
                variable = ScalarVariable(name=v['_attributes']['name'])
                if 'valueReference' in v['_attributes']:
                    variable.value_reference = v['_attributes']['valueReference']
                if 'description' in v['_attributes']:
                    variable.description = v['_attributes']['description']
                if 'causality' in v['_attributes']:
                    variable.causality = v['_attributes']['causality']
                if 'variability' in v['_attributes']:
                    variable.variability = v['_attributes']['variability']
                if type_identifier := find_type_identifier_in_keys(v):
                    variable.data_type = type_identifier
                    type_key = find_key(v, f'{type_identifier}$')
                    if v[type_key] and '_attributes' in v[type_key]:
                        if 'quantity' in v[type_key]['_attributes']:
                            variable.quantity = v[type_key]['_attributes']['quantity']
                        if 'unit' in v[type_key]['_attributes']:
                            variable.unit = v[type_key]['_attributes']['unit']
                        if 'display_unit' in v[type_key]['_attributes']:
                            variable.display_unit = v[type_key]['_attributes']['display_unit']
                        if 'initial_value' in v[type_key]['_attributes']:
                            variable.start = v[type_key]['_attributes']['initial_value']
                variables[variable.name] = variable

        return variables

    @property
    def default_experiment(self) -> Union[Experiment, None]:
        default_experiment_key = find_key(self.model_description, 'DefaultExperiment$')
        if not default_experiment_key:
            return None
        default_experiment = Experiment()
        default_experiment_properties = self.model_description[default_experiment_key]
        if '_attributes' in default_experiment_properties:
            default_experiment_attributes = default_experiment_properties['_attributes']
            if 'startTime' in default_experiment_attributes:
                default_experiment.start_time = default_experiment_attributes['startTime']
            if 'stopTime' in default_experiment_attributes:
                default_experiment.stop_time = default_experiment_attributes['stopTime']
            if 'tolerance' in default_experiment_attributes:
                default_experiment.tolerance = default_experiment_attributes['tolerance']
            if 'stepSize' in default_experiment_attributes:
                default_experiment.step_size = default_experiment_attributes['stepSize']
        return default_experiment

    def copy(self, new_name: str):
        """Saves a copy of the FMU with a new name

        Parameters
        ----------
        new_name : str
            Intended name of the copy. The new name must be different from the existing name.

        Returns
        -------
        FMU
            The new FMU
        """
        # Prepare
        new_name = Path(new_name).stem
        existing_file_name = self.file.stem
        if new_name == existing_file_name:
            logger.error(
                f'{self.file.name} copy: new name {new_name} is identical with existing name. copy() aborted.'
            )
        new_model_description: CppDict = deepcopy(self.model_description)
        new_file = self.file.parent.absolute() / f'{new_name}.fmu'

        # Copy FMU
        copyfile(self.file, new_file)

        # Rename *.dll files in FMU to match new fmu name
        with ZipFile(new_file, 'r') as document:
            dll_file_names = [
                file.filename
                for file in document.infolist()
                if re.search(r'.*\.dll$', file.filename) and existing_file_name in file.filename
            ]
        new_dll_file_names = [
            re.sub(existing_file_name, new_name, dll_file_name) for dll_file_name in dll_file_names
        ]
        for dll_file_name, new_dll_file_name in zip(dll_file_names, new_dll_file_names):
            logger.info(
                f'{self.file.name} copy: renaming dll {dll_file_name} to {new_dll_file_name}'
            )
            rename_file_in_zip(new_file, dll_file_name, new_dll_file_name)

        # Rename <fmiModelDescription modelName> in modelDescription.xml
        new_model_description['_xmlOpts']['_rootAttributes']['modelName'] = new_name

        # Rename <CoSimulation modelIdentifier> in modelDescription.xml
        # (STC requires consistency between <fmiModelDescription modelName> and <CoSimulation modelIdentifier>)
        co_simulation: dict = new_model_description[
            find_key(new_model_description, 'CoSimulation$')]
        co_simulation['_attributes']['modelIdentifier'] = new_name

        # Log the update in modelDescription.xml
        self._log_update_in_model_description(new_model_description)

        # Write updated modelDescription.xml into new FMU
        new_fmu = FMU(new_file)
        new_fmu._write_model_description(new_model_description)

        return new_fmu

    def proxify(self, host: str, port: int):
        """Creates a proxy version of the FMU

        For details see https://github.com/NTNU-IHB/FMU-proxy

        Parameters
        ----------
        host : str
            Remote host
        port : int
            Remote port

        Returns
        -------
        FMU
            The created proxy version of the FMU
        """

        import subprocess
        remote_string = f"--remote={host}:{port}"
        command = (f'fmu-proxify {self.file.name} {remote_string}')
        try:
            subprocess.run(command, timeout=60)
        except subprocess.TimeoutExpired:
            logger.exception(f'Timeout occured when calling {command}.')
            return self
        proxy_fmu_file = self.file.parent.absolute() / f'{self.file.stem}-proxy.fmu'
        return FMU(proxy_fmu_file)

    def _modify_start_values(self, variables_with_start_values: dict[str, ScalarVariable]):
        """Modifies the start values of variables inside the FMUs modelDescription.xml
        """

        logger.info(
            f'{self.file.name}: update start values of variables in modelDescription.xml'
        )                                                                                   # 2

        model_variables: dict = self.model_description[
            find_key(self.model_description, 'ModelVariables$')]

        names_of_variables_with_start_values: list[str] = [
            variable.name for _, variable in variables_with_start_values.items()
        ]

        for model_variable_key, model_variable_properties in model_variables.items():

            model_variable_name: str = model_variable_properties['_attributes']['name']

            if model_variable_name in names_of_variables_with_start_values:
                variable_with_start_values = variables_with_start_values[model_variable_name]
                type_identifier = find_type_identifier_in_keys(model_variable_properties)
                type_key = find_key(model_variable_properties, f'{type_identifier}$')

                logger.info(
                    f'{self.file.name}: update start values for variable {model_variable_name}:\n'
                    f'\tstart:\t\t{variable_with_start_values.start}\n'
                    f'\tcausality:\t {variable_with_start_values.causality}\n'
                    f'\tvariability:\t{variable_with_start_values.variability}'
                )

                model_variables[model_variable_key][type_key]['_attributes'][
                    'start'] = variable_with_start_values.start
                model_variables[model_variable_key]['_attributes'][
                    'causality'] = variable_with_start_values.causality
                model_variables[model_variable_key]['_attributes'][
                    'variability'] = variable_with_start_values.variability

        self._log_update_in_model_description()

    def _log_update_in_model_description(self, model_description: Union[CppDict, None] = None):

        model_description = model_description or self.model_description

        logger.info(f'{self.file.name}: update <fmiModelDescription description>')  # 2
                                                                                    # Author
        old_author = model_description['_xmlOpts']['_rootAttributes']['author']
        if platform.system() == 'Linux':
            new_author = os.environ['USER']
        else:
            new_author = os.environ['USERNAME']
        model_description['_xmlOpts']['_rootAttributes']['author'] = new_author
                                                                                    # DateAndTime
        old_date = model_description['_xmlOpts']['_rootAttributes']['generationDateAndTime']
        new_date = str(datetime.now())
        model_description['_xmlOpts']['_rootAttributes']['generationDateAndTime'] = new_date
                                                                                    # Log modifications in <fmiModelDescription description> attribute
        add_description_string = (
            f'\nmodified {date.today()}:\n'
            f'\tauthor {old_author} to {new_author}\n'
            f'\tgenerationDateAndTime {old_date} to {new_date}\n'
        )
        model_description['_xmlOpts']['_rootAttributes']['description'] += add_description_string

    # @TODO: Check when and where this method needs to be called. And why..
    #        CLAROS, 2022-05-24
    def _clean_solver_internal_variables(self, model_description: MutableMapping):
        """Clean solver internal variables, such as '_iti_...'
        """
        model_variables: dict = model_description[find_key(model_description, 'ModelVariables$')]
        model_name = model_description['_xmlOpts']['_rootAttributes']['modelName']
        for model_variable_key in model_variables:
            if '_origin' in model_variables[model_variable_key]:
                model_variables[model_variable_key]['_origin'] = model_name
