#!/usr/bin/env python3
"""D05 entry point for the repository-owned ERDG decision contract."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_IMPL = Path(__file__).resolve().parents[2] / "governance/erdg/scripts/validate_contract.py"
_SPEC = importlib.util.spec_from_file_location("d05_erdg_contract", _IMPL)
core = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(core)

validate = core.validate

if __name__ == "__main__":
    raise SystemExit(core.main())
