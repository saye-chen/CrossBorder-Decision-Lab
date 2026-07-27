#!/usr/bin/env python3
"""Compatibility entry point for the repository-owned ERDG decision contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path

# One-release introspection compatibility for consumers that audit ownership
# registration from this historical entrypoint. The normative registry now
# lives in governance/erdg/scripts/validate_domain_contract_compat.py.
COMPATIBILITY_OWNERS = {
    "advertising": "advertising-analysis-measurement-optimization",
    "advertising_measurement": "advertising-analysis-measurement-optimization",
    "advertising_scaling": "advertising-analysis-measurement-optimization",
}

_impl = Path(__file__).resolve().parents[2] / "governance/erdg/scripts/validate_contract.py"
_spec = importlib.util.spec_from_file_location("erdg_decision_contract", _impl)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load ERDG contract validator: {_impl}")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

validate = _module.validate
main = _module.main
PROFESSIONAL_FIELDS = _module.PROFESSIONAL_FIELDS
OWNERS = _module.OWNERS
CLAIM_STATES = _module.CLAIM_STATES

if __name__ == "__main__":
    raise SystemExit(main())
