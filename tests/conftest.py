import os
from glob import glob
from pathlib import Path
from shutil import rmtree

import pytest


@pytest.fixture(scope='package', autouse=True)
def chdir():
    os.chdir(Path(__file__).parent.absolute() / 'test_dicts')


ospx_dirs = [
    'xyz',
]
ospx_files = [
    'parsed*',
    '*.xml',
    '*.fmu',
    '*.csv',
    '*.ssd',
    'statisticsDict',
    'watchDict',
    'caseDict_imported_from_test_import_OspSystemStructure_xml'
]


@pytest.fixture(autouse=True)
def default_setup_and_teardown(caplog):
    _remove_ospx_dirs_and_files()
    yield
    _remove_ospx_dirs_and_files()


def _remove_ospx_dirs_and_files():
    for folder in ospx_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in ospx_files:
        for file in Path('.').rglob(pattern):
            if not file.name.startswith('test_'):
                file.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level('WARNING')
    caplog.clear()
