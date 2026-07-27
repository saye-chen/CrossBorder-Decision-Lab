#!/usr/bin/env python3
"""Repository-wide entry point for the ERDG multi-domain decision contract."""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path

_impl = Path(__file__).resolve().parents[1] / "governance/erdg/scripts/validate_contract.py"
_spec = importlib.util.spec_from_file_location("erdg_decision_contract_core", _impl)
core = importlib.util.module_from_spec(_spec); assert _spec and _spec.loader; _spec.loader.exec_module(core)
validate = core.validate

if __name__ == "__main__":
    raise SystemExit(core.main())
