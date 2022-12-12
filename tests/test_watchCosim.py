from pathlib import Path
from typing import List

import pytest

from ospx.watch.watchCosim import CosimWatcher


def test_file_not_found_exception():
    # Prepare
    source_file: Path = Path("this_file_does_not_exist")
    csv_file_names: List[str] = []
    skip_values: int = 0
    latest_values: int = 0
    watcher = CosimWatcher(
        csv_file_names,
        skip_values,
        latest_values,
        scale_factor=1.0,
    )
    # Execute and Assert
    with pytest.raises(FileNotFoundError):
        watcher.read_watch_dict(source_file)


def test_read_watch_dict():
    # Prepare
    source_file = Path("test_watchDict")
    csv_file_names = [
        "test_result_file_difference.csv",
        "test_result_file_divident.csv",
        "test_result_file_minuend.csv",
        "test_result_file_quotient.csv",
        "test_result_file_subtrahend.csv",
    ]
    skip_values = 0
    latest_values = 0
    watcher = CosimWatcher(
        csv_file_names,
        skip_values,
        latest_values,
        scale_factor=1.0,
    )
    # Execute
    watcher.read_watch_dict(source_file)
    # Assert
