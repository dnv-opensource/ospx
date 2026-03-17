from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dictIO import DictParser

from ospx.ospSimulationCase import OspSimulationCase


def test_init_reads_simulation_and_lib_source() -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_simple")
    assert case_dict is not None

    # Execute
    osp_case = OspSimulationCase(case_dict)

    # Assert
    assert osp_case.name == "demoCase"
    assert osp_case.simulation is not None
    assert osp_case.simulation.start_time == 0
    assert osp_case.simulation.stop_time == 10
    assert osp_case.simulation.base_step_size == 0.01
    assert osp_case.lib_source.name == "simple"


def test_init_falls_back_to_case_dict_name_if_simulation_name_missing() -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_simple")
    assert case_dict is not None
    del case_dict["run"]["simulation"]["name"]

    # Execute
    osp_case = OspSimulationCase(case_dict)

    # Assert
    assert osp_case.name == case_dict.name
    assert osp_case.simulation.name == case_dict.name


def test_check_all_fmus_exist_raises_for_missing_fmu_key() -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_minimal_inspect")
    assert case_dict is not None
    del case_dict["systemStructure"]["components"]["difference"]["fmu"]
    osp_case = OspSimulationCase(case_dict)

    # Execute & Assert
    with pytest.raises(ValueError, match="'fmu' element missing"):
        osp_case.setup()


def test_check_all_fmus_exist_raises_for_missing_fmu_file() -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_minimal_inspect")
    assert case_dict is not None
    case_dict["systemStructure"]["components"]["difference"]["fmu"] = "simple/not_existing_file.fmu"
    osp_case = OspSimulationCase(case_dict)

    # Execute & Assert
    with pytest.raises(FileNotFoundError):
        osp_case.setup()


def test_copy_fmu_to_case_folder_copies_fmu_and_osp_model_description(tmp_path: Path) -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_simple")
    assert case_dict is not None
    osp_case = OspSimulationCase(case_dict)
    osp_case.case_folder = tmp_path

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    fmu_file = source_dir / "demo.fmu"
    _ = fmu_file.write_text("fmu-content")

    osp_model_description = source_dir / "demo_OspModelDescription.xml"
    _ = osp_model_description.write_text("<OspModelDescription />")

    # Execute
    copy_fmu_to_case_folder = osp_case._copy_fmu_to_case_folder  # pyright: ignore[reportPrivateUsage]
    copied_fmu = copy_fmu_to_case_folder(fmu_file)

    # Assert
    assert copied_fmu == (tmp_path / "demo.fmu").resolve().absolute()
    assert (tmp_path / "demo.fmu").exists()
    assert (tmp_path / "demo_OspModelDescription.xml").exists()


def test_check_components_step_size_sets_missing_step_sizes() -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_simple")
    assert case_dict is not None
    osp_case = OspSimulationCase(case_dict)

    component_without_step = MagicMock()
    component_without_step.step_size = None
    component_with_step = MagicMock()
    component_with_step.step_size = 0.02

    osp_case.system_structure = MagicMock()
    osp_case.system_structure.components = {
        "a": component_without_step,
        "b": component_with_step,
    }
    osp_case.simulation.base_step_size = 0.01

    # Execute
    check_components_step_size = osp_case._check_components_step_size  # pyright: ignore[reportPrivateUsage]
    check_components_step_size()

    # Assert
    assert component_without_step.step_size == 0.01
    assert component_with_step.step_size == 0.02


def test_write_osp_system_structure_xml() -> None:
    # Prepare
    case_dict = DictParser.parse("test_caseDict_simple")
    assert case_dict is not None
    # Execute
    osp_case = OspSimulationCase(case_dict)
    osp_case.simulation = MagicMock()
    osp_case.simulation.start_time = 0.0
    osp_case.simulation.base_step_size = 0.01
    osp_case.simulation.algorithm = "fixedStep"
    osp_case.simulation.stop_time = 10.0

    # Mock system structure
    osp_case.system_structure = MagicMock()
    component = MagicMock()
    component.name = "component1"
    component.fmu = MagicMock()
    component.fmu.file = Path("component1.fmu")
    component.step_size = 0.01
    component.fmu.default_experiment = None
    component.variables_with_start_values = {}

    osp_case.system_structure.components = {"component1": component}
    osp_case.system_structure.connections = MagicMock()
    osp_case.system_structure.connections.values.return_value = []

    osp_case.case_folder = Path.cwd()

    # Execute
    with (
        patch("ospx.ospSimulationCase.DictWriter.write") as mock_write,
        patch.object(osp_case, "_correct_wrong_xml_namespace") as mock_correct,
    ):
        osp_case.write_osp_system_structure_xml()

    # Assert
    mock_write.assert_called_once()
    mock_correct.assert_called_once()
