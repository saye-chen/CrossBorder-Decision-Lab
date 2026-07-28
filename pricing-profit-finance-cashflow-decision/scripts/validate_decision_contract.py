#!/usr/bin/env python3
"""Validate shared ERDG decisions or PPFC cross-domain envelopes."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from ppfc_common import PPFCError
from validate_cross_domain_envelope import validate as validate_envelope

ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "governance/erdg/scripts/validate_contract.py"
SPEC = importlib.util.spec_from_file_location("erdg_decision_contract", CORE_PATH)
CORE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CORE)


def validate(payload: dict) -> dict:
    if payload.get("contract") == "PPFC-XDOMAIN-2026.01":
        return validate_envelope(payload)
    errors = CORE.validate(payload)
    if errors:
        raise PPFCError("erdg:" + "|".join(errors))
    return {"valid": True, "contract_type": "erdg_shared", "decision_owner": payload["decision_owner"], "erdg_contract": "ERDG-CONTRACT-2026.01"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise PPFCError("root must be object")
        result = validate(payload)
    except (OSError, json.JSONDecodeError, PPFCError) as exc:
        print(f"PPFC_DECISION_CONTRACT=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
