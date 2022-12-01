import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, List, Type, Union
from uuid import UUID


logger = logging.getLogger(__name__)

#
# Globals
#


def _cast(typ: Type, value):
    return value if typ is None or value is None else typ(value)


#
# Data representation classes.
#


class CausalityType(str, Enum):
    """CausalityType -- parameter: independent parameter
    calculatedParameter: calculated parameter
    input/output: can be used in connections
    local: variable calculated from other variables
    independent: independent variable (usually time)

    """

    PARAMETER = "parameter"
    CALCULATED_PARAMETER = "calculatedParameter"
    INPUT = "input"
    OUTPUT = "output"
    LOCAL = "local"
    INDEPENDENT = "independent"


class DependenciesKindType(str, Enum):
    """dependenciesKindType -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variablse)
    = "fixed"        : fixed factor, p*v (only for Real variables)
    = "tunable"    : tunable factor, p*v (only for Real variables)
    = "discrete"    : discrete factor, d*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    DEPENDENT = "dependent"
    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"


class InitialType(str, Enum):
    """InitialType -- exact: initialized with start value
    approx: iteration variable that starts with start value
    calculated: calculated from other variables.
    If not provided, initial is deduced from causality and variability (details see specification)

    """

    EXACT = "exact"
    APPROX = "approx"
    CALCULATED = "calculated"


class VariabilityType(str, Enum):
    """VariabilityType -- constant: value never changes
    fixed: value fixed after initialization
    tunable: value constant between external events
    discrete: value constant between internal events
    continuous: no restriction on value changes

    """

    CONSTANT = "constant"
    FIXED = "fixed"
    TUNABLE = "tunable"
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


class VariableNamingConventionType(str, Enum):
    FLAT = "flat"
    STRUCTURED = "structured"


class ModelExchangeType:
    """ModelExchangeType -- The FMU includes a model or the communication to a tool that provides a model. The environment provides the simulation engine for the model.
    List of capability flags that an FMI2 Model Exchange interface can provide
    modelIdentifier -- Short class name according to C-syntax, e.g. "A_B_C". Used as prefix for FMI2 functions if the functions are provided in C source code or in static libraries, but not if the functions are provided by a DLL/SharedObject. modelIdentifier is also used as name of the static library or DLL/SharedObject.
    needsExecutionTool -- If true, a tool is needed to execute the model and the FMU just contains the communication to this tool.
    SourceFiles -- List of source file names that are present in the "sources" directory of the FMU and need to be compiled in order to generate the binary of the FMU (only meaningful for source code FMUs).

    """

    def __init__(
        self,
        model_identifier: str,
        needs_execution_tool: bool = False,
        completed_integrator_step_not_needed: bool = False,
        can_be_instantiated_only_once_per_process: bool = False,
        can_not_use_memory_management_functions: bool = False,
        can_get_and_set_fmu_state: bool = False,
        can_serialize_fmu_state: bool = False,
        provides_directional_derivative=False,
        source_files: Union[List[Path], None] = None,
    ):
        self.model_identifier: str = model_identifier
        self.needs_execution_tool: bool = needs_execution_tool
        self.completed_integrator_step_not_needed: bool = (
            completed_integrator_step_not_needed
        )
        self.can_be_instantiated_only_once_per_process: bool = (
            can_be_instantiated_only_once_per_process
        )
        self.can_not_use_memory_management_functions: bool = (
            can_not_use_memory_management_functions
        )
        self.can_get_and_set_fmu_state: bool = can_get_and_set_fmu_state
        self.can_serialize_fmu_state: bool = can_serialize_fmu_state
        self.provides_directional_derivative: bool = provides_directional_derivative
        self.source_files: List[Path] = source_files or []

    def get_source_files(self) -> List[Path]:
        return self.source_files

    def set_source_files(self, source_files: List[Path]):
        self.source_files = source_files

    def get_model_identifier(self) -> str:
        return self.model_identifier

    def set_model_identifier(self, model_identifier: str):
        self.model_identifier = model_identifier

    def get_needs_execution_tool(self) -> bool:
        return self.needs_execution_tool

    def set_needs_execution_tool(self, needs_execution_tool: bool):
        self.needs_execution_tool = needs_execution_tool

    def get_completed_integrator_step_not_needed(self) -> bool:
        return self.completed_integrator_step_not_needed

    def set_completed_integrator_step_not_needed(
        self, completed_integrator_step_not_needed: bool
    ):
        self.completed_integrator_step_not_needed = completed_integrator_step_not_needed

    def get_can_be_instantiated_only_once_per_process(self) -> bool:
        return self.can_be_instantiated_only_once_per_process

    def set_can_be_instantiated_only_once_per_process(
        self, can_be_instantiated_only_once_per_process: bool
    ):
        self.can_be_instantiated_only_once_per_process = (
            can_be_instantiated_only_once_per_process
        )

    def get_can_not_use_memory_management_functions(self) -> bool:
        return self.can_not_use_memory_management_functions

    def set_can_not_use_memory_management_functions(
        self, can_not_use_memory_management_functions: bool
    ):
        self.can_not_use_memory_management_functions = (
            can_not_use_memory_management_functions
        )

    def get_can_get_and_set_fmu_state(self) -> bool:
        return self.can_get_and_set_fmu_state

    def set_can_get_and_set_fmu_state(self, can_get_and_set_fmu_state: bool):
        self.can_get_and_set_fmu_state = can_get_and_set_fmu_state

    def get_can_serialize_fmu_state(self) -> bool:
        return self.can_serialize_fmu_state

    def set_can_serialize_fmu_state(self, can_serialize_fmu_state: bool):
        self.can_serialize_fmu_state = can_serialize_fmu_state

    def get_provides_directional_derivative(self) -> bool:
        return self.provides_directional_derivative

    def set_provides_directional_derivative(
        self, provides_directional_derivative: bool
    ):
        self.provides_directional_derivative = provides_directional_derivative


class CoSimulationType:
    """CoSimulationType -- The FMU includes a model and the simulation engine, or the communication to a tool that provides this. The environment provides the master algorithm for the Co-Simulation coupling.
    modelIdentifier -- Short class name according to C-syntax, e.g. "A_B_C". Used as prefix for FMI2 functions if the functions are provided in C source code or in static libraries, but not if the functions are provided by a DLL/SharedObject. modelIdentifier is also used as name of the static library or DLL/SharedObject.
    needsExecutionTool -- If true, a tool is needed to execute the model and the FMU just contains the communication to this tool.
    providesDirectionalDerivative -- Directional derivatives at communication points
    SourceFiles -- List of source file names that are present in the "sources" directory of the FMU and need to be compiled in order to generate the binary of the FMU (only meaningful for source code FMUs).

    """

    def __init__(
        self,
        model_identifier: str,
        needs_execution_tool: bool = False,
        can_handle_variable_communication_step_size: bool = False,
        can_interpolate_inputs: bool = False,
        max_output_derivative_order: int = 0,
        can_run_asynchronuously: bool = False,
        can_be_instantiated_only_once_per_process: bool = False,
        can_not_use_memory_management_functions: bool = False,
        can_get_and_set_fmu_state: bool = False,
        can_serialize_fmu_state: bool = False,
        provides_directional_derivative: bool = False,
        source_files: Union[List[Path], None] = None,
    ):
        self.model_identifier: str = model_identifier
        self.needs_execution_tool: bool = needs_execution_tool
        self.can_handle_variable_communication_step_size: bool = (
            can_handle_variable_communication_step_size
        )
        self.can_interpolate_inputs: bool = can_interpolate_inputs
        self.max_output_derivative_order: int = max_output_derivative_order
        self.can_run_asynchronuously: bool = can_run_asynchronuously
        self.can_be_instantiated_only_once_per_process: bool = (
            can_be_instantiated_only_once_per_process
        )
        self.can_not_use_memory_management_functions: bool = (
            can_not_use_memory_management_functions
        )
        self.can_get_and_set_fmu_state: bool = can_get_and_set_fmu_state
        self.can_serialize_fmu_state: bool = can_serialize_fmu_state
        self.provides_directional_derivative: bool = provides_directional_derivative
        self.source_files: List[Path] = source_files or []

    def get_source_files(self) -> List[Path]:
        return self.source_files

    def set_source_files(self, source_files: List[Path]):
        self.source_files = source_files

    def get_model_identifier(self) -> str:
        return self.model_identifier

    def set_model_identifier(self, model_identifier: str):
        self.model_identifier = model_identifier

    def get_needs_execution_tool(self) -> bool:
        return self.needs_execution_tool

    def set_needs_execution_tool(self, needs_execution_tool: bool):
        self.needs_execution_tool = needs_execution_tool

    def get_can_handle_variable_communication_step_size(self) -> bool:
        return self.can_handle_variable_communication_step_size

    def set_can_handle_variable_communication_step_size(
        self, can_handle_variable_communication_step_size: bool
    ):
        self.can_handle_variable_communication_step_size = (
            can_handle_variable_communication_step_size
        )

    def get_can_interpolate_inputs(self) -> bool:
        return self.can_interpolate_inputs

    def set_can_interpolate_inputs(self, can_interpolate_inputs: bool):
        self.can_interpolate_inputs = can_interpolate_inputs

    def get_max_output_derivative_order(self) -> int:
        return self.max_output_derivative_order

    def set_max_output_derivative_order(self, max_output_derivative_order: int):
        self.max_output_derivative_order = max_output_derivative_order

    def get_can_run_asynchronuously(self) -> bool:
        return self.can_run_asynchronuously

    def set_can_run_asynchronuously(self, can_run_asynchronuously: bool):
        self.can_run_asynchronuously = can_run_asynchronuously

    def get_can_be_instantiated_only_once_per_process(self) -> bool:
        return self.can_be_instantiated_only_once_per_process

    def set_can_be_instantiated_only_once_per_process(
        self, can_be_instantiated_only_once_per_process: bool
    ):
        self.can_be_instantiated_only_once_per_process = (
            can_be_instantiated_only_once_per_process
        )

    def get_can_not_use_memory_management_functions(self) -> bool:
        return self.can_not_use_memory_management_functions

    def set_can_not_use_memory_management_functions(
        self, can_not_use_memory_management_functions: bool
    ):
        self.can_not_use_memory_management_functions = (
            can_not_use_memory_management_functions
        )

    def get_can_get_and_set_fmu_state(self) -> bool:
        return self.can_get_and_set_fmu_state

    def set_can_get_and_set_fmu_state(self, can_get_and_set_fmu_state: bool):
        self.can_get_and_set_fmu_state = can_get_and_set_fmu_state

    def get_can_serialize_fmu_state(self) -> bool:
        return self.can_serialize_fmu_state

    def set_can_serialize_fmu_state(self, can_serialize_fmu_state: bool):
        self.can_serialize_fmu_state = can_serialize_fmu_state

    def get_provides_directional_derivative(self) -> bool:
        return self.provides_directional_derivative

    def set_provides_directional_derivative(
        self, provides_directional_derivative: bool
    ):
        self.provides_directional_derivative = provides_directional_derivative


class FmiModelDescription:
    """fmiModelDescription -- At least one of the elements must be present
    fmi_version -- Version of FMI (Clarification for FMI 2.0.2: for FMI 2.0.x revisions fmi_version is defined as "2.0").
    model_name -- Class name of FMU, e.g. "A.B.C" (several FMU instances are possible)
    guid -- Fingerprint of xml-file content to verify that xml-file and C-functions are compatible to each other
    version -- Version of FMU, e.g., "1.4.1"
    copyright -- Information on intellectual property copyright for this FMU, such as
    “
    ©
    MyCompany 2011
    “
    license -- Information on intellectual property licensing for this FMU, such as
    “
    BSD license
    ”
    , "Proprietary", or "Public Domain"
    model_exchange -- The FMU includes a model or the communication to a tool that provides a model. The environment provides the simulation engine for the model.
    co_simulation -- The FMU includes a model and the simulation engine, or the communication to a tool that provides this. The environment provides the master algorithm for the Co-Simulation coupling.
    log_categories -- Log categories available in FMU
    vendor_annotations -- tool specific data (ignored by other tools)
    model_variables -- Ordered list of all variables (first definition has index = 1).
    model_structure -- Ordered lists of outputs, exposed state derivatives,
    and the initial unknowns. Optionally, the functional
    dependency of these variables can be defined.

    """

    def __init__(
        self,
        model_name: str,
        guid: Union[str, UUID],
        description: Union[str, None] = None,
        author: Union[str, None] = None,
        version: Union[str, None] = None,
        copyright: Union[str, None] = None,
        license: Union[str, None] = None,
        generation_tool: Union[str, None] = None,
        generation_date_and_time: Union[datetime, str, None] = None,
        variable_naming_convention: Union[
            VariableNamingConventionType, str, None
        ] = None,
        number_of_event_indicators: Union[int, None] = None,
        model_exchange: Union[ModelExchangeType, None] = None,
        co_simulation: Union[CoSimulationType, None] = None,
        unit_definitions=None,
        type_definitions=None,
        log_categories=None,
        default_experiment=None,
        vendor_annotations=None,
        model_variables=None,
        model_structure=None,
        **kwargs_
    ):
        self.fmi_version: str = "2.0"
        self.model_name: str = model_name
        self.guid: Union[str, UUID] = guid
        self.description: Union[str, None] = _cast(str, description)
        self.author: Union[str, None] = _cast(str, author)
        self.version: Union[str, None] = _cast(str, version)
        self.copyright: Union[str, None] = _cast(str, copyright)
        self.license: Union[str, None] = _cast(str, license)
        self.generation_tool: Union[str, None] = _cast(str, generation_tool)
        _date_and_time_init: Union[datetime, None]
        self.generation_date_and_time: Union[datetime, None]
        if isinstance(generation_date_and_time, datetime):
            self.generation_date_and_time = generation_date_and_time
        elif isinstance(generation_date_and_time, str):
            self.generation_date_and_time = datetime.strptime(
                generation_date_and_time, "%Y-%m-%dT%H:%M:%S"
            )
        else:
            self.generation_date_and_time = None
        self.variable_naming_convention: VariableNamingConventionType
        if isinstance(variable_naming_convention, VariableNamingConventionType):
            self.variable_naming_convention = variable_naming_convention
        elif isinstance(variable_naming_convention, str):
            self.variable_naming_convention = VariableNamingConventionType(
                variable_naming_convention
            )
        else:
            self.variable_naming_convention = VariableNamingConventionType.FLAT
        self.number_of_event_indicators: Union[int, None] = _cast(
            int, number_of_event_indicators
        )
        self.model_exchange: Union[ModelExchangeType, None] = model_exchange
        self.co_simulation: Union[CoSimulationType, None] = co_simulation
        self.unit_definitions = unit_definitions
        self.type_definitions = type_definitions
        self.log_categories = log_categories
        self.default_experiment = default_experiment
        self.vendor_annotations = vendor_annotations
        self.model_variables = model_variables
        self.model_structure = model_structure

    def get_model_exchange(self) -> Union[ModelExchangeType, None]:
        return self.model_exchange

    def set_model_exchange(self, model_exchange: Union[ModelExchangeType, None]):
        self.model_exchange = model_exchange

    def get_co_simulation(self) -> Union[CoSimulationType, None]:
        return self.co_simulation

    def set_co_simulation(self, co_simulation: Union[CoSimulationType, None]):
        self.co_simulation = co_simulation

    def get_unit_definitions(self):
        return self.unit_definitions

    def set_unit_definitions(self, unit_definitions):
        self.unit_definitions = unit_definitions

    def get_type_definitions(self):
        return self.type_definitions

    def set_type_definitions(self, type_definitions):
        self.type_definitions = type_definitions

    def get_log_categories(self):
        return self.log_categories

    def set_log_categories(self, log_categories):
        self.log_categories = log_categories

    def get_default_experiment(self):
        return self.default_experiment

    def set_default_experiment(self, default_experiment):
        self.default_experiment = default_experiment

    def get_vendor_annotations(self):
        return self.vendor_annotations

    def set_vendor_annotations(self, vendor_annotations):
        self.vendor_annotations = vendor_annotations

    def get_model_variables(self):
        return self.model_variables

    def set_model_variables(self, model_variables):
        self.model_variables = model_variables

    def get_model_structure(self):
        return self.model_structure

    def set_model_structure(self, model_structure):
        self.model_structure = model_structure

    def get_fmi_version(self) -> str:
        return self.fmi_version

    def set_fmi_version(self, fmi_version: str):
        self.fmi_version = fmi_version

    def get_model_name(self) -> str:
        return self.model_name

    def set_model_name(self, model_name: str):
        self.model_name = model_name

    def get_guid(self) -> Union[str, UUID]:
        return self.guid

    def set_guid(self, guid: Union[str, UUID]):
        self.guid = guid

    def get_description(self) -> Union[str, None]:
        return self.description

    def set_description(self, description: Union[str, None]):
        self.description = description

    def get_author(self) -> Union[str, None]:
        return self.author

    def set_author(self, author: Union[str, None]):
        self.author = author

    def get_version(self) -> Union[str, None]:
        return self.version

    def set_version(self, version: Union[str, None]):
        self.version = version

    def get_copyright(self) -> Union[str, None]:
        return self.copyright

    def set_copyright(self, copyright: Union[str, None]):
        self.copyright = copyright

    def get_license(self) -> Union[str, None]:
        return self.license

    def set_license(self, license: Union[str, None]):
        self.license = license

    def get_generation_tool(self) -> Union[str, None]:
        return self.generation_tool

    def set_generation_tool(self, generation_tool: Union[str, None]):
        self.generation_tool = generation_tool

    def get_generation_date_and_time(self) -> Union[datetime, None]:
        return self.generation_date_and_time

    def set_generation_date_and_time(
        self, generation_date_and_time: Union[datetime, None]
    ):
        self.generation_date_and_time = generation_date_and_time

    def get_variable_naming_convention(self) -> VariableNamingConventionType:
        return self.variable_naming_convention

    def set_variable_naming_convention(
        self, variable_naming_convention: VariableNamingConventionType
    ):
        self.variable_naming_convention = variable_naming_convention

    def get_number_of_event_indicators(self) -> Union[int, None]:
        return self.number_of_event_indicators

    def set_number_of_event_indicators(
        self, number_of_event_indicators: Union[int, None]
    ):
        self.number_of_event_indicators = number_of_event_indicators

    def validate_variable_naming_convention_type(self, value):
        # Validate type VariableNamingConventionType, a restriction on xs:normalizedString.
        if value is None:
            return True
        if not isinstance(value, str):

            logger.error(
                'Value "%(value)s"is not of the correct base simple type (str)'
                % {
                    "value": value,
                }
            )
            return False
        enumerations = ["flat", "structured"]
        if value not in enumerations:

            logger.error(
                'Value "%(value)s"does not match xsd enumeration restriction on variable_naming_conventionType'
                % {"value": value}
            )
            return False
        return True


class Fmi2ScalarVariable:
    """Fmi2ScalarVariable -- Properties of a scalar variable
    name -- Identifier of variable, e.g. "a.b.mod[3,4].'#123'.c". "name" must be unique with respect to all other elements of the model_variables list
    value_reference -- Identifier for variable value in FMI2 function calls (not necessarily unique with respect to all variables)
    causality -- parameter: independent parameter
    calculatedParameter: calculated parameter
    input/output: can be used in connections
    local: variable calculated from other variables
    independent: independent variable (usually time)
    variability -- constant: value never changes
    fixed: value fixed after initialization
    tunable: value constant between external events
    discrete: value constant between internal events
    continuous: no restriction on value changes
    initial -- exact: initialized with start value
    approx: iteration variable that starts with start value
    calculated: calculated from other variables.
    If not provided, initial is deduced from causality and variability (details see specification)
    can_handle_multiple_set_per_time_instant -- Only for model_exchange and only for variables with variability = "input":
    If present with value = false, then only one fmi2SetXXX call is allowed at one super dense time instant. In other words, this input is not allowed to appear in an algebraic loop.
    annotations -- Additional data of the scalar variable, e.g., for the dialog menu or the graphical layout

    """

    def __init__(
        self,
        name=None,
        value_reference=None,
        description=None,
        causality="local",
        variability="continuous",
        initial=None,
        can_handle_multiple_set_per_time_instant=None,
        real=None,
        integer=None,
        boolean=None,
        string=None,
        enumeration=None,
        annotations=None,
    ):
        self.name = _cast(None, name)
        self.value_reference = _cast(int, value_reference)
        self.description = _cast(None, description)
        self.causality = _cast(None, causality)
        self.variability = _cast(None, variability)
        self.initial = _cast(None, initial)
        self.can_handle_multiple_set_per_time_instant = _cast(
            bool, can_handle_multiple_set_per_time_instant
        )
        self.real = real
        self.integer = integer
        self.boolean = boolean
        self.string = string
        self.enumeration = enumeration
        self.annotations = annotations

    def get_real(self):
        return self.real

    def set_real(self, real):
        self.real = real

    def get_integer(self):
        return self.integer

    def set_integer(self, integer):
        self.integer = integer

    def get_boolean(self):
        return self.boolean

    def set_boolean(self, boolean):
        self.boolean = boolean

    def get_string(self):
        return self.string

    def set_string(self, string):
        self.string = string

    def get_enumeration(self):
        return self.enumeration

    def set_enumeration(self, enumeration):
        self.enumeration = enumeration

    def get_annotations(self):
        return self.annotations

    def set_annotations(self, annotations):
        self.annotations = annotations

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_value_reference(self):
        return self.value_reference

    def set_value_reference(self, value_reference):
        self.value_reference = value_reference

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_causality(self):
        return self.causality

    def set_causality(self, causality):
        self.causality = causality

    def get_variability(self):
        return self.variability

    def set_variability(self, variability):
        self.variability = variability

    def get_initial(self):
        return self.initial

    def set_initial(self, initial):
        self.initial = initial

    def get_can_handle_multiple_set_per_time_instant(self):
        return self.can_handle_multiple_set_per_time_instant

    def set_can_handle_multiple_set_per_time_instant(
        self, can_handle_multiple_set_per_time_instant
    ):
        self.can_handle_multiple_set_per_time_instant = (
            can_handle_multiple_set_per_time_instant
        )

    def validate_causality_type(self, value):
        # Validate type causalityType, a restriction on xs:normalizedString.
        if value is None:
            return True
        if not isinstance(value, str):

            logger.error(
                'Value "%(value)s"is not of the correct base simple type (str)'
                % {
                    "value": value,
                }
            )
            return False
        enumerations = [
            "parameter",
            "calculatedParameter",
            "input",
            "output",
            "local",
            "independent",
        ]
        if value not in enumerations:

            logger.error(
                'Value "%(value)s"does not match xsd enumeration restriction on causalityType'
                % {"value": value}
            )
            return False
        return True

    def validate_variability_type(self, value):
        # Validate type variabilityType, a restriction on xs:normalizedString.
        if value is None:
            return True
        if not isinstance(value, str):

            logger.error(
                'Value "%(value)s"is not of the correct base simple type (str)'
                % {
                    "value": value,
                }
            )
            return False
        enumerations = ["constant", "fixed", "tunable", "discrete", "continuous"]
        if value not in enumerations:

            logger.error(
                'Value "%(value)s"does not match xsd enumeration restriction on variabilityType'
                % {"value": value}
            )
            return False
        return True

    def validate_initial_type(self, value):
        # Validate type initialType, a restriction on xs:normalizedString.
        if value is None:
            return True
        if not isinstance(value, str):

            logger.error(
                'Value "%(value)s"is not of the correct base simple type (str)'
                % {
                    "value": value,
                }
            )
            return False
        enumerations = ["exact", "approx", "calculated"]
        if value not in enumerations:

            logger.error(
                'Value "%(value)s"does not match xsd enumeration restriction on initialType'
                % {"value": value}
            )
            return False
        return True


class Fmi2Annotation:
    """tool -- tool specific annotation (ignored by other tools)."""

    def __init__(
        self,
        tool=None,
    ):
        self.tool = [] if tool is None else tool

    def get_tool(self):
        return self.tool

    def set_tool(self, tool):
        self.tool = tool

    def add_tool(self, value):
        self.tool.append(value)

    def insert_tool_at(self, index, value):
        self.tool.insert(index, value)

    def replace_tool_at(self, index, value):
        self.tool[index] = value


class Fmi2VariableDependency:
    """Dependency of scalar Unknown from Knowns
    Unknown -- Dependency of scalar Unknown from Knowns
    in Continuous-Time and Event Mode (model_exchange),
    and at Communication Points (co_simulation):
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs", "continuous states" and
    "independent variable" (usually time)".

    """

    def __init__(
        self,
        unknown=None,
    ):
        self.unknown = [] if unknown is None else unknown

    def get_unknown(self):
        return self.unknown

    def set_unknown(self, unknown):
        self.unknown = unknown

    def add_unknown(self, value):
        self.unknown.append(value)

    def insert_unknown_at(self, index, value):
        self.unknown.insert(index, value)

    def replace_unknown_at(self, index, value):
        self.unknown[index] = value


class Fmi2Unit:
    """fmi2Unit -- Unit definition (with respect to SI base units) and default display units
    name -- Name of Unit element, e.g. "N.m", "Nm",  "%/s". "name" must be unique will respect to all other elements of the unit_definitions list. The variable values of fmi2SetXXX and fmi2GetXXX are with respect to this unit.
    BaseUnit -- BaseUnit_value = factor*Unit_value + offset
    DisplayUnit -- DisplayUnit_value = factor*Unit_value + offset

    """

    def __init__(
        self,
        name=None,
        base_unit=None,
        display_unit=None,
    ):
        self.name = _cast(None, name)
        self.base_unit = base_unit
        self.display_unit = [] if display_unit is None else display_unit

    def get_base_unit(self):
        return self.base_unit

    def set_base_unit(self, base_unit):
        self.base_unit = base_unit

    def get_display_unit(self):
        return self.display_unit

    def set_display_unit(self, display_unit):
        self.display_unit = display_unit

    def add_display_unit(self, value):
        self.display_unit.append(value)

    def insert_display_unit_at(self, index, value):
        self.display_unit.insert(index, value)

    def replace_display_unit_at(self, index, value):
        self.display_unit[index] = value

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name


class Fmi2SimpleType:
    """fmi2SimpleType -- Type attributes of a scalar variable
    name -- Name of SimpleType element. "name" must be unique with respect to all other elements of the type_definitions list. Furthermore,  "name" of a SimpleType must be different to all "name"s of ScalarVariable.
    description -- Description of the SimpleType

    """

    def __init__(
        self,
        name: str,
        description: Union[str, None] = None,
        real=None,
        integer=None,
        boolean=None,
        string=None,
        enumeration=None,
    ):
        self.name: str = name
        self.description: Union[str, None] = description
        self.real = real
        self.integer = integer
        self.boolean = boolean
        self.string = string
        self.enumeration = enumeration

    def get_real(self):
        return self.real

    def set_real(self, real):
        self.real = real

    def get_integer(self):
        return self.integer

    def set_integer(self, integer):
        self.integer = integer

    def get_boolean(self):
        return self.boolean

    def set_boolean(self, boolean):
        self.boolean = boolean

    def get_string(self):
        return self.string

    def set_string(self, string):
        self.string = string

    def get_enumeration(self):
        return self.enumeration

    def set_enumeration(self, enumeration):
        self.enumeration = enumeration

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_description(self) -> Union[str, None]:
        return self.description

    def set_description(self, description: Union[str, None]):
        self.description = description


class UnitDefinitionsType:
    def __init__(
        self,
        unit=None,
    ):
        self.unit = [] if unit is None else unit

    def get_unit(self):
        return self.unit

    def set_unit(self, unit):
        self.unit = unit

    def add_unit(self, value):
        self.unit.append(value)

    def insert_unit_at(self, index, value):
        self.unit.insert(index, value)

    def replace_unit_at(self, index, value):
        self.unit[index] = value


class TypeDefinitionsType:
    def __init__(
        self,
        simple_type=None,
    ):
        self.simple_type = [] if simple_type is None else simple_type

    def get_simple_type(self):
        return self.simple_type

    def set_simple_type(self, simple_type):
        self.simple_type = simple_type

    def add_simple_type(self, value):
        self.simple_type.append(value)

    def insert_simple_type_at(self, index, value):
        self.simple_type.insert(index, value)

    def replace_simple_type_at(self, index, value):
        self.simple_type[index] = value


class LogCategoriesType:
    """log_categoriesType -- Log categories available in FMU"""

    def __init__(
        self,
        category=None,
    ):
        self.category = [] if category is None else category

    def get_category(self):
        return self.category

    def set_category(self, category):
        self.category = category

    def add_category(self, value):
        self.category.append(value)

    def insert_category_at(self, index, value):
        self.category.insert(index, value)

    def replace_category_at(self, index, value):
        self.category[index] = value


class CategoryType:
    """name -- Name of Category element. "name" must be unique with respect to all other elements of the log_categories list. Standardized names: "logEvents", "logSingularLinearSystems", "logNonlinearSystems", "logDynamicStateSelection", "logStatusWarning", "logStatusDiscard", "logStatusError", "logStatusFatal", "logStatusPending", "logAll"
    description -- Description of the log category

    """

    def __init__(
        self,
        name=None,
        description=None,
    ):
        self.name = _cast(None, name)
        self.description = _cast(None, description)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description


class DefaultExperimentType:
    """startTime -- Default start time of simulation
    stopTime -- Default stop time of simulation
    tolerance -- Default relative integration tolerance
    stepSize -- model_exchange: Default step size for fixed step integrators. CoSimulation: Preferred communicationStepSize.
    """

    def __init__(
        self,
        start_time=None,
        stop_time=None,
        tolerance=None,
        step_size=None,
    ):
        self.start_time = _cast(float, start_time)
        self.stop_time = _cast(float, stop_time)
        self.tolerance = _cast(float, tolerance)
        self.step_size = _cast(float, step_size)

    def get_start_time(self):
        return self.start_time

    def set_start_time(self, start_time):
        self.start_time = start_time

    def get_stop_time(self):
        return self.stop_time

    def set_stop_time(self, stop_time):
        self.stop_time = stop_time

    def get_tolerance(self):
        return self.tolerance

    def set_tolerance(self, tolerance):
        self.tolerance = tolerance

    def get_step_size(self):
        return self.step_size

    def set_step_size(self, step_size):
        self.step_size = step_size


class ModelVariablesType:
    """ModelVariablesType -- Ordered list of all variables (first definition has index = 1)."""

    def __init__(
        self,
        scalar_variable=None,
    ):
        self.scalar_variable = [] if scalar_variable is None else scalar_variable

    def get_scalar_variable(self):
        return self.scalar_variable

    def set_scalar_variable(self, scalar_variable):
        self.scalar_variable = scalar_variable

    def add_scalar_variable(self, value):
        self.scalar_variable.append(value)

    def insert_scalar_variable_at(self, index, value):
        self.scalar_variable.insert(index, value)

    def replace_scalar_variable_at(self, index, value):
        self.scalar_variable[index] = value


class ModelStructureType:
    """ModelStructureType -- Ordered lists of outputs, exposed state derivatives,
    and the initial unknowns. Optionally, the functional
    dependency of these variables can be defined.
    Outputs -- Ordered list of all outputs. Exactly all variables with causality="output" must be in this list. The dependency definition holds for Continuous-Time and for Event Mode (model_exchange) and for Communication Points (co_simulation).
    Derivatives -- Ordered list of all exposed state derivatives (and therefore implicitely associated continuous-time states). Exactly all state derivatives of a model_exchange FMU must be in this list. A co_simulation FMU need not expose its state derivatives. If a model has dynamic state selection, introduce dummy state variables. The dependency definition holds for Continuous-Time and for Event Mode (model_exchange) and for Communication Points (co_simulation).
    InitialUnknowns -- Ordered list of all exposed Unknowns in Initialization Mode. This list consists of all variables with (1) causality = "output" and (initial="approx" or calculated"), (2) causality = "calculatedParameter", and (3) all continuous-time states and all state derivatives (defined with element Derivatives from model_structure)with initial=("approx" or "calculated"). The resulting list is not allowed to have duplicates (e.g. if a state is also an output, it is included only once in the list). The Unknowns in this list must be ordered according to their ScalarVariable index (e.g. if for two variables A and B the  ScalarVariable index of A is less than the index of B, then A must appear before B in InitialUnknowns).

    """

    def __init__(
        self,
        outputs=None,
        derivatives=None,
        initial_unknowns=None,
    ):
        self.outputs = outputs
        self.derivatives = derivatives
        self.initial_unknowns = initial_unknowns

    def get_outputs(self):
        return self.outputs

    def set_outputs(self, outputs):
        self.outputs = outputs

    def get_derivatives(self):
        return self.derivatives

    def set_derivatives(self, derivatives):
        self.derivatives = derivatives

    def get_initial_unknowns(self):
        return self.initial_unknowns

    def set_initial_unknowns(self, initial_unknowns):
        self.initial_unknowns = initial_unknowns


class InitialUnknownsType:
    """InitialUnknownsType -- Ordered list of all exposed Unknowns in Initialization Mode. This list consists of all variables with (1) causality = "output" and (initial="approx" or calculated"), (2) causality = "calculatedParameter", and (3) all continuous-time states and all state derivatives (defined with element Derivatives from model_structure)with initial=("approx" or "calculated"). The resulting list is not allowed to have duplicates (e.g. if a state is also an output, it is included only once in the list). The Unknowns in this list must be ordered according to their ScalarVariable index (e.g. if for two variables A and B the  ScalarVariable index of A is less than the index of B, then A must appear before B in InitialUnknowns).
    Unknown -- Dependency of scalar Unknown from Knowns:
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs",
    "variables with initial=exact", and
    "independent variable".

    """

    def __init__(
        self,
        unknown=None,
    ):
        self.unknown = [] if unknown is None else unknown

    def get_unknown(self):
        return self.unknown

    def set_unknown(self, unknown):
        self.unknown = unknown

    def add_unknown(self, value):
        self.unknown.append(value)

    def insert_unknown_at(self, index, value):
        self.unknown.insert(index, value)

    def replace_unknown_at(self, index, value):
        self.unknown[index] = value


class UnknownType:
    """UnknownType -- Dependency of scalar Unknown from Knowns:
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs",
    "variables with initial=exact", and
    "independent variable".
    index -- ScalarVariable index of Unknown
    dependencies -- Defines the dependency of the Unknown (directly or indirectly via auxiliary variables) on the Knowns in the Initialization Mode. If not present, it must be assumed that the Unknown depends on all Knowns. If present as empty list, the Unknown depends on none of the Knowns. Otherwise the Unknown depends on the Knowns defined by the given ScalarVariable indices. The indices are ordered according to size, starting with the smallest index.
    dependenciesKind -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    def __init__(
        self,
        index=None,
        dependencies=None,
        dependencies_kind=None,
    ):
        self.index = _cast(int, index)
        self.dependencies = dependencies
        self.dependencies_kind = dependencies_kind

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_dependencies(self):
        return self.dependencies

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies

    def get_dependencies_kind(self):
        return self.dependencies_kind

    def set_dependencies_kind(self, dependencies_kind):
        self.dependencies_kind = dependencies_kind

    def validate_dependencies_type(self, value):
        # Validate type dependenciesType, a restriction on xs:unsignedInt.
        pass

    def validate_dependencies_kind_type(self, value):
        # Validate type dependenciesKindType, a restriction on xs:normalizedString.
        pass


class UnknownType3:
    """UnknownType3 -- Dependency of scalar Unknown from Knowns
    in Continuous-Time and Event Mode (model_exchange),
    and at Communication Points (co_simulation):
    Unknown=f(Known_1, Known_2, ...).
    The Knowns are "inputs", "continuous states" and
    "independent variable" (usually time)".
    index -- ScalarVariable index of Unknown
    dependencies -- Defines the dependency of the Unknown (directly or indirectly via auxiliary variables) on the Knowns in Continuous-Time and Event Mode (model_exchange) and at Communication Points (co_simulation). If not present, it must be assumed that the Unknown depends on all Knowns. If present as empty list, the Unknown depends on none of the Knowns. Otherwise the Unknown depends on the Knowns defined by the given ScalarVariable indices. The indices are ordered according to size, starting with the smallest index.
    dependenciesKind -- If not present, it must be assumed that the Unknown depends on the Knowns without a particular structure. Otherwise, the corresponding Known v enters the equation as:
    = "dependent": no particular structure, f(v)
    = "constant"   : constant factor, c*v (only for Real variablse)
    = "fixed"        : fixed factor, p*v (only for Real variables)
    = "tunable"    : tunable factor, p*v (only for Real variables)
    = "discrete"    : discrete factor, d*v (only for Real variables)
    If "dependenciesKind" is present, "dependencies" must be present and must have the same number of list elements.

    """

    def __init__(
        self,
        index=None,
        dependencies=None,
        dependencies_kind=None,
    ):
        self.index = _cast(int, index)
        self.dependencies = dependencies
        self.dependencies_kind = dependencies_kind

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_dependencies(self):
        return self.dependencies

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies

    def get_dependencies_kind(self):
        return self.dependencies_kind

    def set_dependencies_kind(self, dependencies_kind):
        self.dependencies_kind = dependencies_kind

    def validate_dependencies_type(self, value):
        # Validate type dependenciesType, a restriction on xs:unsignedInt.
        pass

    def validate_dependencies_kind_type(self, value):
        # Validate type dependenciesKindType, a restriction on xs:normalizedString.
        pass


class RealType:
    """declaredType -- If present, name of type defined with type_definitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx.
    max
    >
    = start
    >
    = min required
    derivative -- If present, this variable is the derivative of variable with ScalarVariable index "derivative".
    reinit -- Only for model_exchange and if variable is a continuous-time state:
    If true, state can be reinitialized at an event by the FMU
    If false, state will never be reinitialized at an event by the FMU

    """

    def __init__(
        self,
        declared_type: Union[str, None] = None,
        start: Union[float, None] = None,
        derivative: Union[int, None] = None,
        reinit: bool = False,
        quantity: Union[str, None] = None,
        unit: Union[str, None] = None,
        display_unit: Union[str, None] = None,
        relative_quantity: bool = False,
        min: Union[float, None] = None,
        max: Union[float, None] = None,
        nominal: Union[float, None] = None,
        unbounded: bool = False,
    ):
        self.declared_type: Union[str, None] = _cast(str, declared_type)
        self.start: Union[float, None] = _cast(float, start)
        self.derivative: Union[int, None] = _cast(int, derivative)
        self.reinit: bool = reinit
        self.quantity: Union[str, None] = _cast(str, quantity)
        self.unit: Union[str, None] = _cast(None, unit)
        self.display_unit: Union[str, None] = _cast(None, display_unit)
        self.relative_quantity: bool = relative_quantity
        self.min: Union[float, None] = _cast(float, min)
        self.max: Union[float, None] = _cast(float, max)
        self.nominal: Union[float, None] = _cast(float, nominal)
        self.unbounded: bool = unbounded

    def get_declared_type(self) -> Union[str, None]:
        return self.declared_type

    def set_declared_type(self, declared_type: Union[str, None]):
        self.declared_type = declared_type

    def get_start(self) -> Union[float, None]:
        return self.start

    def set_start(self, start: Union[float, None]):
        self.start = start

    def get_derivative(self) -> Union[int, None]:
        return self.derivative

    def set_derivative(self, derivative: Union[int, None]):
        self.derivative = derivative

    def get_reinit(self) -> bool:
        return self.reinit

    def set_reinit(self, reinit: bool):
        self.reinit = reinit

    def get_quantity(self) -> Union[str, None]:
        return self.quantity

    def set_quantity(self, quantity: Union[str, None]):
        self.quantity = quantity

    def get_unit(self) -> Union[str, None]:
        return self.unit

    def set_unit(self, unit: Union[str, None]):
        self.unit = unit

    def get_display_unit(self) -> Union[str, None]:
        return self.display_unit

    def set_display_unit(self, display_unit: Union[str, None]):
        self.display_unit = display_unit

    def get_relative_quantity(self) -> bool:
        return self.relative_quantity

    def set_relative_quantity(self, relative_quantity: bool):
        self.relative_quantity = relative_quantity

    def get_min(self) -> Union[float, None]:
        return self.min

    def set_min(self, min: Union[float, None]):
        self.min = min

    def get_max(self) -> Union[float, None]:
        return self.max

    def set_max(self, max: Union[float, None]):
        self.max = max

    def get_nominal(self) -> Union[float, None]:
        return self.nominal

    def set_nominal(self, nominal: Union[float, None]):
        self.nominal = nominal

    def get_unbounded(self) -> bool:
        return self.unbounded

    def set_unbounded(self, unbounded: bool):
        self.unbounded = unbounded


class RealType6:
    def __init__(
        self,
        quantity: Union[str, None] = None,
        unit: Union[str, None] = None,
        display_unit: Union[str, None] = None,
        relative_quantity: bool = False,
        min: Union[float, None] = None,
        max: Union[float, None] = None,
        nominal: Union[float, None] = None,
        unbounded: bool = False,
    ):
        self.quantity: Union[str, None] = _cast(None, quantity)
        self.unit: Union[str, None] = _cast(None, unit)
        self.display_unit: Union[str, None] = _cast(None, display_unit)
        self.relative_quantity: bool = relative_quantity
        self.min: Union[float, None] = _cast(float, min)
        self.max: Union[float, None] = _cast(float, max)
        self.nominal: Union[float, None] = _cast(float, nominal)
        self.unbounded: bool = unbounded

    def get_quantity(self) -> Union[str, None]:
        return self.quantity

    def set_quantity(self, quantity: Union[str, None]):
        self.quantity = quantity

    def get_unit(self) -> Union[str, None]:
        return self.unit

    def set_unit(self, unit: Union[str, None]):
        self.unit = unit

    def get_display_unit(self) -> Union[str, None]:
        return self.display_unit

    def set_display_unit(self, display_unit: Union[str, None]):
        self.display_unit = display_unit

    def get_relative_quantity(self) -> bool:
        return self.relative_quantity

    def set_relative_quantity(self, relative_quantity: bool):
        self.relative_quantity = relative_quantity

    def get_min(self) -> Union[float, None]:
        return self.min

    def set_min(self, min: Union[float, None]):
        self.min = min

    def get_max(self) -> Union[float, None]:
        return self.max

    def set_max(self, max: Union[float, None]):
        self.max = max

    def get_nominal(self) -> Union[float, None]:
        return self.nominal

    def set_nominal(self, nominal: Union[float, None]):
        self.nominal = nominal

    def get_unbounded(self) -> bool:
        return self.unbounded

    def set_unbounded(self, unbounded: bool):
        self.unbounded = unbounded


class IntegerType:
    """declaredType -- If present, name of type defined with type_definitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx.
    max
    >
    = start
    >
    = min required

    """

    def __init__(
        self,
        declared_type: Union[str, None] = None,
        start: Union[int, None] = None,
        quantity: Union[str, None] = None,
        min: Union[int, None] = None,
        max: Union[int, None] = None,
    ):
        self.declared_type: Union[str, None] = _cast(None, declared_type)
        self.start: Union[int, None] = _cast(int, start)
        self.quantity: Union[str, None] = _cast(None, quantity)
        self.min: Union[int, None] = _cast(int, min)
        self.max: Union[int, None] = _cast(int, max)

    def get_declared_type(self) -> Union[str, None]:
        return self.declared_type

    def set_declared_type(self, declared_type: Union[str, None]):
        self.declared_type = declared_type

    def get_start(self) -> Union[int, None]:
        return self.start

    def set_start(self, start: Union[int, None]):
        self.start = start

    def get_quantity(self) -> Union[str, None]:
        return self.quantity

    def set_quantity(self, quantity: Union[str, None]):
        self.quantity = quantity

    def get_min(self) -> Union[int, None]:
        return self.min

    def set_min(self, min: Union[int, None]):
        self.min = min

    def get_max(self) -> Union[int, None]:
        return self.max

    def set_max(self, max: Union[int, None]):
        self.max = max


class IntegerType7:
    def __init__(
        self,
        quantity: Union[str, None] = None,
        min: Union[int, None] = None,
        max: Union[int, None] = None,
    ):
        self.quantity: Union[str, None] = _cast(str, quantity)
        self.min: Union[int, None] = _cast(int, min)
        self.max: Union[int, None] = _cast(int, max)

    def get_quantity(self) -> Union[str, None]:
        return self.quantity

    def set_quantity(self, quantity: Union[str, None]):
        self.quantity = quantity

    def get_min(self) -> Union[int, None]:
        return self.min

    def set_min(self, min: Union[int, None]):
        self.min = min

    def get_max(self) -> Union[int, None]:
        return self.max

    def set_max(self, max: Union[int, None]):
        self.max = max


class BooleanType:
    """declaredType -- If present, name of type defined with type_definitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx

    """

    def __init__(
        self,
        declared_type: Union[str, None] = None,
        start: Union[bool, None] = None,
    ):
        self.declared_type: Union[str, None] = _cast(str, declared_type)
        self.start: Union[bool, None] = _cast(bool, start)

    def get_declared_type(self) -> Union[str, None]:
        return self.declared_type

    def set_declared_type(self, declared_type: Union[str, None]):
        self.declared_type = declared_type

    def get_start(self) -> Union[bool, None]:
        return self.start

    def set_start(self, start: Union[bool, None]):
        self.start = start


class StringType:
    """declaredType -- If present, name of type defined with type_definitions / SimpleType providing defaults.
    start -- Value before initialization, if initial=exact or approx

    """

    def __init__(
        self,
        declared_type: Union[str, None] = None,
        start: Union[str, None] = None,
    ):
        self.declared_type: Union[str, None] = _cast(None, declared_type)
        self.start: Union[str, None] = _cast(None, start)

    def get_declared_type(self) -> Union[str, None]:
        return self.declared_type

    def set_declared_type(self, declared_type: Union[str, None]):
        self.declared_type = declared_type

    def get_start(self) -> Union[str, None]:
        return self.start

    def set_start(self, start: Union[str, None]):
        self.start = start


class EnumerationType:
    """declaredType -- Name of type defined with type_definitions / SimpleType
    max -- max
    >
    = min required
    start -- Value before initialization, if initial=exact or approx.
    max
    >
    = start
    >
    = min required

    """

    def __init__(
        self,
        declared_type: Union[str, None] = None,
        quantity: Union[str, None] = None,
        min: Union[int, None] = None,
        max: Union[int, None] = None,
        start: Union[int, None] = None,
    ):
        self.declared_type: Union[str, None] = _cast(str, declared_type)
        self.quantity: Union[str, None] = _cast(None, quantity)
        self.min: Union[int, None] = _cast(int, min)
        self.max: Union[int, None] = _cast(int, max)
        self.start: Union[int, None] = _cast(int, start)

    def get_declared_type(self) -> Union[str, None]:
        notSnakeCase: str

        return self.declared_type

    def set_declared_type(self, declared_type: Union[str, None]):
        self.declared_type = declared_type

    def get_quantity(self) -> Union[str, None]:
        return self.quantity

    def set_quantity(self, quantity: Union[str, None]):
        self.quantity = quantity

    def get_min(self) -> Union[int, None]:
        return self.min

    def set_min(self, min: Union[int, None]):
        self.min = min

    def get_max(self) -> Union[int, None]:
        return self.max

    def set_max(self, max: Union[int, None]):
        self.max = max

    def get_start(self) -> Union[int, None]:
        return self.start

    def set_start(self, start: Union[int, None]):
        self.start = start


class ToolType:
    """ToolType -- tool specific annotation (ignored by other tools).
    name -- Name of tool that can interpret the annotation. "name" must be unique with respect to all other elements of the VendorAnnotation list.

    """

    def __init__(
        self,
        name: str,
        anytypeobjs: Union[List[Any], None] = None,
    ):
        self.name: str = name
        self.anytypeobjs: List[Any] = anytypeobjs or []

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_anytypeobjs_(self) -> List[Any]:
        return self.anytypeobjs

    def set_anytypeobjs_(self, anytypeobjs: List[Any]):
        self.anytypeobjs = anytypeobjs


class BaseUnitType:
    """BaseUnitType -- BaseUnit_value = factor*Unit_value + offset
    kg -- Exponent of SI base unit "kg"
    m -- Exponent of SI base unit "m"
    s -- Exponent of SI base unit "s"
    A -- Exponent of SI base unit "A"
    K -- Exponent of SI base unit "K"
    mol -- Exponent of SI base unit "mol"
    cd -- Exponent of SI base unit "cd"
    rad -- Exponent of SI derived unit "rad"

    """

    def __init__(
        self,
        kg: int = 0,
        m: int = 0,
        s: int = 0,
        A: int = 0,  # noqa: N803
        K: int = 0,  # noqa: N803
        mol: int = 0,
        cd: int = 0,
        rad: int = 0,
        factor: float = 1.0,
        offset: float = 0.0,
    ):
        self.kg: int = _cast(int, kg)
        self.m: int = _cast(int, m)
        self.s: int = _cast(int, s)
        self.A: int = _cast(int, A)
        self.K: int = _cast(int, K)
        self.mol: int = _cast(int, mol)
        self.cd: int = _cast(int, cd)
        self.rad: int = _cast(int, rad)
        self.factor: float = _cast(float, factor)
        self.offset: float = _cast(float, offset)

    def get_kg(self):
        return self.kg

    def set_kg(self, kg):
        self.kg = kg

    def get_m(self):
        return self.m

    def set_m(self, m):
        self.m = m

    def get_s(self):
        return self.s

    def set_s(self, s):
        self.s = s

    def get_A(self):  # noqa: N802
        return self.A

    def set_A(self, A):  # noqa: N803, N802
        self.A = A

    def get_K(self):  # noqa: N802
        return self.K

    def set_K(self, K):  # noqa: N803, N802
        self.K = K

    def get_mol(self):
        return self.mol

    def set_mol(self, mol):
        self.mol = mol

    def get_cd(self):
        return self.cd

    def set_cd(self, cd):
        self.cd = cd

    def get_rad(self):
        return self.rad

    def set_rad(self, rad):
        self.rad = rad

    def get_factor(self):
        return self.factor

    def set_factor(self, factor):
        self.factor = factor

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset


class DisplayUnitType:
    """DisplayUnitType -- DisplayUnit_value = factor*Unit_value + offset
    name -- Name of DisplayUnit element, e.g.
    ,
    . "name" must be unique with respect to all other "names" of the DisplayUnit definitions of the same Unit (different Unit elements may have the same DisplayUnit names).

    """

    def __init__(
        self,
        name: str,
        factor: float = 1.0,
        offset: float = 0.0,
    ):
        self.name: str = name
        self.factor: float = _cast(float, factor)
        self.offset: float = _cast(float, offset)

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_factor(self) -> float:
        return self.factor

    def set_factor(self, factor: float):
        self.factor = factor

    def get_offset(self) -> float:
        return self.offset

    def set_offset(self, offset: float):
        self.offset = offset


class EnumerationType8:
    def __init__(
        self,
        quantity=None,
        item=None,
    ):
        self.quantity = _cast(None, quantity)
        self.item = [] if item is None else item

    def get_item(self):
        return self.item

    def set_item(self, item):
        self.item = item

    def add_item(self, value):
        self.item.append(value)

    def insert_item_at(self, index, value):
        self.item.insert(index, value)

    def replace_item_at(self, index, value):
        self.item[index] = value

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity


class EnumerationItem:
    """value -- Must be a unique number in the same enumeration"""

    def __init__(
        self,
        name: str,
        value: int,
        description: Union[str, None] = None,
    ):
        self.name: str = name
        self.value: int = value
        self.description: Union[str, None] = description

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_value(self) -> int:
        return self.value

    def set_value(self, value: int):
        self.value = value

    def get_description(self) -> Union[str, None]:
        return self.description

    def set_description(self, description: Union[str, None]):
        self.description = description
