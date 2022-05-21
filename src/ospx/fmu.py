import logging
import os
import platform
import re
from datetime import date, datetime
from pathlib import Path
from shutil import copyfile
from typing import MutableMapping, Union
from zipfile import ZipFile

from dictIO.cppDict import CppDict
from dictIO.formatter import XmlFormatter
from dictIO.parser import XmlParser
from dictIO.utils.counter import BorgCounter

from ospx.utils.dict import find_key, find_type_identifier_in_keys, shrink_dict
from ospx.utils.zip import (
    add_file_content_to_zip,
    read_file_content_from_zip,
    remove_files_from_zip,
    rename_file_in_zip,
)
from ospx.variable import Variable


logger = logging.getLogger(__name__)


class FMU():

    def __init__(self, file: Union[str, os.PathLike[str]]):
        # Make sure fmu_file argument is of type Path. If not, cast it to Path type.
        file = file if isinstance(file, Path) else Path(file)
        if not file.exists():
            logger.error(f"DictParser: File {file} not found.")
            raise FileNotFoundError(file)

        self.file: Path = file
        self.counter = BorgCounter()

    @property
    def unit_definitions(self) -> dict:
        # give add. index for distinguishing between modelDescription.xml's containing one single ScalarVariable, otherwise it will be overwritten here
        unit_definitions: dict = {}
        model_description: CppDict = self.read_model_description()
        unit_definitions_key: str = find_key(model_description, 'UnitDefinitions$')
        if unit_definitions_key != 'ELEMENTNOTFOUND':
            unit_definitions = dict(model_description[unit_definitions_key].items())
            # make always unique units list and keep xml files clean
            unit_definitions = shrink_dict(unit_definitions, unique_keys=['_attributes', 'name'])
        return unit_definitions

    def read_model_description(self) -> CppDict:
        model_description = CppDict(Path('modelDescription.xml'))
        xml_parser = XmlParser()

        logger.info(f'{self.file.name}: read modelDescription.xml')

        if file_content := read_file_content_from_zip(self.file, 'modelDescription.xml'):
            model_description = xml_parser.parse_string(file_content, model_description)

        return model_description

    def write_model_description(self, model_description: CppDict):
        """Save updated model_description both inside FMU as well as separate file in the FMUs directory
        """
        model_description['_xmlOpts']['_nameSpaces'] = {
            'xs': 'file:///C:/Software/OSP/xsd/fmi3ModelDescription.xsd'
        }

        formatter = XmlFormatter()
        formatted_xml = formatter.to_string(model_description)

        logger.info(f'{self.file.name}: write modelDescription.xml')

        remove_files_from_zip(self.file, 'modelDescription.xml')
        add_file_content_to_zip(self.file, 'modelDescription.xml', formatted_xml)

        external_file = self.file.parent.absolute() / f'{self.file.stem}_ModelDescription.xml'
        with open(external_file, 'w') as f:
            f.write(formatted_xml)

        return

    def clean_solver_internal_variables(self):
        """Clean solver internal variables, such as '_iti_...'
        """
        model_description: CppDict = self.read_model_description()
        model_variables: dict = model_description[find_key(model_description, 'ModelVariables$')]
        model_name = model_description['_xmlOpts']['_rootAttributes']['modelName']
        for model_variable_key in model_variables:
            if '_origin' in model_variables[model_variable_key]:
                model_variables[model_variable_key]['_origin'] = model_name
        self.write_model_description(model_description)

    @property
    def variables(self) -> dict:
        # note: "_" and "settings" are proprietary variables from iti and get removed
        model_description: CppDict = self.read_model_description()
        model_variables: dict = model_description[find_key(model_description, 'ModelVariables$')]
        return {
            f"{self.counter():06d}_" + re.sub(r'^\d{6}_', '', k): v
            for k,
            v in model_variables.items()
            if not re.match('^(_|settings)', v['_attributes']['name'])
        }

    def set_start_values(self, variables_with_start_values: Union[dict[str, Variable], None]):
        """sets the start values of variables in the FMUs modelDescription.xml
        """

        variables_with_start_values = variables_with_start_values or {}

        logger.info(
            f'{self.file.name}: update start values of variables in modelDescription.xml'
        )                                                                                   # 2

        model_description: CppDict = self.read_model_description()
        model_variables: dict = model_description[find_key(model_description, 'ModelVariables$')]

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
                    f'\tstart:\t\t{variable_with_start_values.initial_value}\n'
                    f'\tvariability:\t{variable_with_start_values.variability}\n'
                    f'\tcausality:\t {variable_with_start_values.causality}'
                )

                model_variables[model_variable_key][type_key]['_attributes'][
                    'start'] = variable_with_start_values.initial_value
                model_variables[model_variable_key]['_attributes'][
                    'variability'] = variable_with_start_values.variability
                model_variables[model_variable_key]['_attributes'][
                    'causality'] = variable_with_start_values.causality

        self._log_update_in_model_description(model_description)
        self.write_model_description(model_description)

    def copy(self, new_name: str):
        """Creates a copy of the FMU with a new name
        """
        # Prepare
        new_name = Path(new_name).stem
        existing_name = self.file.stem
        if new_name == existing_name:
            logger.error(
                f'{self.file.name} copy: new name {new_name} is identical with existing name. copy() aborted.'
            )
        model_description: CppDict = self.read_model_description()
        new_file = self.file.parent.absolute() / f'{new_name}.fmu'

        # Copy FMU
        copyfile(self.file, new_file)

        # Rename *.dll files in FMU to match new fmu name
        with ZipFile(new_file, 'r') as document:
            dll_file_names = [
                file.filename
                for file in document.infolist()
                if re.search(r'.*\.dll$', file.filename) and existing_name in file.filename
            ]
        new_dll_file_names = [
            re.sub(existing_name, new_name, dll_file_name) for dll_file_name in dll_file_names
        ]
        for dll_file_name, new_dll_file_name in zip(dll_file_names, new_dll_file_names):
            logger.info(
                f'{self.file.name} copy: renaming dll {dll_file_name} to {new_dll_file_name}'
            )
            rename_file_in_zip(new_file, dll_file_name, new_dll_file_name)

        # Rename <fmiModelDescription modelName> in modelDescription.xml
        model_description['_xmlOpts']['_rootAttributes']['modelName'] = new_name

        # Rename <CoSimulation modelIdentifier> in modelDescription.xml
        # (STC requires consistency between <fmiModelDescription modelName> and <CoSimulation modelIdentifier>)
        co_simulation: dict = model_description[find_key(model_description, 'CoSimulation$')]
        co_simulation['_attributes']['modelIdentifier'] = new_name

        # Log the update in modelDescription.xml
        self._log_update_in_model_description(model_description)

        # Write updated modelDescription.xml into new FMU
        new_fmu = FMU(new_file)
        new_fmu.write_model_description(model_description)

        return new_fmu

    def proxify(self, host: str, port: int):
        """Creates a proxy version of the FMU

        For details see NTNU-IHB/fmu-proxify
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

    def _log_update_in_model_description(self, model_description: MutableMapping):
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
