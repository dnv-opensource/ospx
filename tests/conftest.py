import logging
import os
from glob import glob
from pathlib import Path
from shutil import rmtree

import pytest
from pytest import LogCaptureFixture

from ospx.utils.zip import add_file_content_to_zip


@pytest.fixture(scope="package", autouse=True)
def chdir():
    os.chdir(Path(__file__).parent.absolute() / "test_dicts")


@pytest.fixture(scope="package", autouse=True)
def test_dir():
    return Path(__file__).parent.absolute()


output_dirs = [
    "xyz",
]
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
def default_setup_and_teardown(caplog: LogCaptureFixture):
    _remove_output_dirs_and_files()
    _create_test_fmu()
    yield
    # _remove_test_fmu()
    _remove_output_dirs_and_files()


def _remove_output_dirs_and_files():
    for folder in output_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in output_files:
        for file in glob(pattern):
            file = Path(file)
            if not file.name.startswith("test_"):
                file.unlink(missing_ok=True)


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
def setup_logging(caplog: LogCaptureFixture):
    caplog.set_level("WARNING")
    caplog.clear()


@pytest.fixture(autouse=True)
def logger():
    return logging.getLogger()
