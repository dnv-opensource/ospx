from pathlib import Path

import pytest

from ospx.fmi.fmu import FMU


def test_conftest_create_test_fmu():
    pass


def test_fmu_instantiation():
    # Prepare
    fmu_file: Path = Path("test_fmu.fmu")
    # Execute
    fmu = FMU(fmu_file)
    # Assert
    assert isinstance(fmu, FMU)


@pytest.fixture()
def test_fmu() -> FMU:
    fmu_file: Path = Path("test_fmu.fmu")
    return FMU(fmu_file)


def test_fmu_variables_number(test_fmu: FMU):
    assert len(test_fmu.variables) == 34


def test_fmu_units_number(test_fmu: FMU):
    assert len(test_fmu.units) == 0


def test_fmu_variables_fmi_data_type(test_fmu: FMU):
    assert test_fmu.variables["Variable_1_IN_Real"].data_type == "Real"
    assert type(test_fmu.variables["Variable_1_IN_Real"].start) == float
    assert test_fmu.variables["Variable_2_IN_Integer"].data_type == "Integer"
    assert test_fmu.variables["Variable_3_IN_Bool"].data_type == "Boolean"
    assert test_fmu.variables["Variable_4_OUT_Real"].data_type == "Real"
    assert test_fmu.variables["Variable_5_OUT_Integer"].data_type == "Integer"
    assert test_fmu.variables["Variable_6_OUT_Bool"].data_type == "Boolean"


def test_fmu_variables_start_value(test_fmu: FMU):
    assert test_fmu.variables["Vector_1_IN[0]"].start == 10.0
    assert test_fmu.variables["Vector_1_IN[1]"].start == 11.0
    assert test_fmu.variables["Vector_1_IN[2]"].start == 12.0


# def test_fmu():
# Prepare

# Execute

# Assert
