#!/usr/bin/env python3
"""Repository-discoverable entrypoint for CIDM opportunity signal tests."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

test_file = Path(__file__).resolve().parents[1] / "tests/test_opportunity_signal_governance.py"
# Keep this discoverable entrypoint import-safe: unittest discovery must not
# interpret a child process's SystemExit(0) as an import error.
if __name__ == "__main__":
    raise SystemExit(subprocess.run([sys.executable, str(test_file)], check=False).returncode)
