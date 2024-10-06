import logging
import os
from pathlib import Path
from shutil import rmtree

import pytest

from ospx.utils.zip import add_file_content_to_zip


@pytest.fixture(scope="package", autouse=True)
def chdir() -> None:
    os.chdir(Path(__file__).parent.absolute() / "test_dicts")


@pytest.fixture(scope="package", autouse=True)
def test_dir() -> Path:
    return Path(__file__).parent.absolute()


output_dirs = []
output_files = [
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
    _remove_output_dirs_and_files()
    _create_test_fmu()
    yield
    # _remove_test_fmu()
    _remove_output_dirs_and_files()


def _remove_output_dirs_and_files() -> None:
    for folder in output_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in output_files:
        for file in Path.cwd().glob(pattern):
            _file = Path(file)
            if not _file.name.startswith("test_"):
                _file.unlink(missing_ok=True)


def _create_test_fmu():
    model_description_file: Path = Path("test_fmu_modelDescription.xml")
    model_description: str = ""
    with open(model_description_file, "r") as f:
        model_description = f.read()
    fmu_file: Path = Path("test_fmu.fmu")
    fmu_file.unlink(missing_ok=True)
    _ = add_file_content_to_zip(
        zip_file=fmu_file,
        file_name="modelDescription.xml",
        file_content=model_description,
    )


def _remove_test_fmu():
    Path("test_fmu.fmu").unlink()


@pytest.fixture(autouse=True)
def setup_logging(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")
    caplog.clear()


@pytest.fixture(autouse=True)
def logger() -> logging.Logger:
    return logging.getLogger()
