"""Standalone FMU patcher entry point for the ospx repository."""

import importlib.util
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).resolve().parent / "src" / "ospx" / "utils" / "fmu_patch.py"
SPEC = importlib.util.spec_from_file_location("ospx_repo_fmu_patch", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Could not load FMU patch utility from {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
main = MODULE.main


if __name__ == "__main__":
    raise SystemExit(main())
