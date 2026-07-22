#!/usr/bin/env python3
"""Validate LIFD outputs through the repository shared decision-contract kernel."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[2] / "scripts/validate_decision_contract.py"), run_name="__main__")
