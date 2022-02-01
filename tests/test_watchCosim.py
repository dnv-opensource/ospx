import os
from pathlib import Path, PurePath

import pytest
from ospx.watch.watchCosim import CosimWatcher


def test_file_not_found_exception():
    # Prepare
    source_file = Path('this_file_does_not_exist')
    csv_file_names = []
    skip_values = 0
    latest_values = 0
    watcher = CosimWatcher(csv_file_names, skip_values, latest_values)
    # Execute and Assert
    with pytest.raises(FileNotFoundError):
        watcher.read_watch_dict(source_file)


def test_read_watch_dict():
    # Prepare
    source_file = Path('test_watchDict')
    csv_file_names = [
        'difference_20220201_235959_999999.csv',
        'divident_20220201_235959_999999.csv',
        'minuend_20220201_235959_999999.csv',
        'quotient_20220201_235959_999999.csv',
        'subtrahend_20220201_235959_999999.csv',
    ]
    skip_values = 0
    latest_values = 0
    watcher = CosimWatcher(csv_file_names, skip_values, latest_values)
    # Execute
    watcher.read_watch_dict(source_file)
    # Assert
