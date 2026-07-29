#!/usr/bin/env python3
"""Authoritative repository-owned ERDG decision-contract validator."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_domain_path = Path(__file__).with_name("validate_domain_contract.py")
_spec = importlib.util.spec_from_file_location("erdg_domain_contract", _domain_path)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load domain validator: {_domain_path}")
_domain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_domain)
PROFESSIONAL_FIELDS = _domain.PROFESSIONAL_FIELDS
OWNERS = _domain.OWNERS
CLAIM_STATES = _domain.CLAIM_STATES

_handoff_path = Path(__file__).with_name("validate_handoff.py")
_handoff_spec = importlib.util.spec_from_file_location("erdg_handoff", _handoff_path)
if _handoff_spec is None or _handoff_spec.loader is None:
    raise RuntimeError(f"cannot load handoff validator: {_handoff_path}")
_handoff = importlib.util.module_from_spec(_handoff_spec)
_handoff_spec.loader.exec_module(_handoff)


def _erdg_errors(payload: dict[str, Any]) -> list[str]:
    errors = []
    active_contract = payload.get("erdg_contract")
    if active_contract != "ERDG-CONTRACT-2026.07":
        errors.append("erdg_contract must be ERDG-CONTRACT-2026.07")
    envelopes = payload.get("handoff_envelopes", [])
    if not isinstance(envelopes, list):
        errors.append("handoff_envelopes must be a list")
        envelopes = []
    for index, envelope in enumerate(envelopes):
        if not isinstance(envelope, dict):
            errors.append(f"handoff_envelopes[{index}] must be an object")
            continue
        errors.extend(f"handoff_envelopes[{index}]: {error}" for error in _handoff.validate(envelope))
    if payload.get("external_write") not in {None, False, "forbidden"}:
        errors.append("ERDG cannot authorize external writes")
    if payload.get("production_ready") is True:
        errors.append("ERDG production_ready cannot be asserted by a decision payload")
    return errors


def validate(payload: dict[str, Any]) -> list[str]:
    return _domain.validate(payload) + _erdg_errors(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON decision contract")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("INVALID: root must be an object", file=sys.stderr)
        return 2
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    print("PASS: ERDG decision contract is structurally safe and professionally complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
