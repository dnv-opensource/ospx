import os
from glob import glob
from pathlib import Path
from shutil import rmtree
from zipfile import ZipFile

import pytest

from ospx.utils.zip import add_file_content_to_zip


@pytest.fixture(scope="package", autouse=True)
def chdir():
    os.chdir(Path(__file__).parent.absolute() / "test_dicts")


ospx_dirs = [
    "xyz",
]
ospx_files = [
    "parsed*",
    "*.xml",
    "*.fmu",
    "*.csv",
    "*.ssd",
    "statisticsDict",
    "watchDict",
    "caseDict_imported_from_test_import_OspSystemStructure_xml",
]


def _remove_ospx_dirs_and_files():
    for folder in ospx_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in ospx_files:
        for file in Path(".").rglob(pattern):
            if not file.name.startswith("test_"):
                file.unlink(missing_ok=True)


def _create_test_fmu():
    model_description_file: Path = Path("test_fmu_modelDescription.xml")
    model_description: str = ""
    with open(model_description_file, "r") as f:
        model_description = f.read()
    fmu_file: Path = Path("test_fmu.fmu")
    fmu_file.unlink(missing_ok=True)
    add_file_content_to_zip(
        zip_file=fmu_file,
        file_name="modelDescription.xml",
        file_content=model_description,
    )


def _remove_test_fmu():
    Path("test_fmu.fmu").unlink()


@pytest.fixture(autouse=True)
def default_setup_and_teardown(caplog):
    _remove_ospx_dirs_and_files()
    _create_test_fmu()
    yield
    # _remove_test_fmu()
    _remove_ospx_dirs_and_files()


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level("WARNING")
    caplog.clear()
