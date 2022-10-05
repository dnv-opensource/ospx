from pathlib import Path

import pytest

from ospx.fmi.fmu import FMU
from ospx.fmi.variable import ScalarVariable
from ospx.fmi.unit import Unit


def test_conftest_create_test_fmu():
    assert True