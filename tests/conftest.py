import logging
import os
from pathlib import Path
from shutil import rmtree

import pytest

from ospx.utils.zip import add_file_content_to_zip


@pytest.fixture(scope="package", autouse=True)
def chdir() -> None:
    """
    Fixture that changes the current working directory to the 'test_working_directory' folder.
    This fixture is automatically used for the entire package.
    """
    os.chdir(Path(__file__).parent.absolute() / "test_working_directory")


@pytest.fixture(scope="package", autouse=True)
def test_dir() -> Path:
    """
    Fixture that returns the absolute path of the directory containing the current file.
    This fixture is automatically used for the entire package.
    """
    return Path(__file__).parent.absolute()


output_dirs: list[str] = []
output_files: list[str] = [
    "parsed*",
    "*.xml",
    "*.fmu",
    "*.csv",
    "*.ssd",
    "statisticsDict",
    "watchDict",
    "caseDict_imported_from_test_import_OspSystemStructure_xml",
]


@pytest.fixture(autouse=True)
def default_setup_and_teardown():
    """
    Fixture that performs setup and teardown actions before and after each test function.
    It removes the output directories and files specified in 'output_dirs' and 'output_files' lists.
    """
    _remove_output_dirs_and_files()
    _create_test_fmu()
    yield
    # _remove_test_fmu()
    _remove_output_dirs_and_files()


def _remove_output_dirs_and_files() -> None:
    """
    Helper function that removes the output directories and files specified in 'output_dirs' and 'output_files' lists.
    """
    for folder in output_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in output_files:
        for file in Path.cwd().glob(pattern):
            _file = Path(file)
            if not _file.name.startswith("test_"):
                _file.unlink(missing_ok=True)


def _create_test_fmu() -> None:
    model_description_file: Path = Path("test_fmu_modelDescription.xml")
    model_description: str = ""
    with Path.open(model_description_file) as f:
        model_description = f.read()
    fmu_file: Path = Path("test_fmu.fmu")
    fmu_file.unlink(missing_ok=True)
    _ = add_file_content_to_zip(
        zip_file=fmu_file,
        file_name="modelDescription.xml",
        file_content=model_description,
    )


def _remove_test_fmu() -> None:
    Path("test_fmu.fmu").unlink()


@pytest.fixture(autouse=True)
def setup_logging(caplog: pytest.LogCaptureFixture) -> None:
    """
    Fixture that sets up logging for each test function.
    It sets the log level to 'INFO' and clears the log capture.
    """
    caplog.set_level("INFO")
    caplog.clear()


@pytest.fixture(autouse=True)
def logger() -> logging.Logger:
    """Fixture that returns the logger object."""
    return logging.getLogger()
