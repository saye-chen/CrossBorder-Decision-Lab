#!/usr/bin/env python3
"""Authoritative repository-owned ERDG decision-contract validator."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_compat_path = Path(__file__).with_name("validate_domain_contract_compat.py")
_spec = importlib.util.spec_from_file_location("erdg_compat", _compat_path)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load compatibility validator: {_compat_path}")
_compat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_compat)
PROFESSIONAL_FIELDS = _compat.PROFESSIONAL_FIELDS
OWNERS = _compat.OWNERS
CLAIM_STATES = _compat.CLAIM_STATES


def _erdg_errors(payload: dict[str, Any]) -> list[str]:
    errors = []
    active_contract = payload.get("erdg_contract", payload.get("erdg_contract"))
    if active_contract not in {None, "ERDG-CONTRACT-2026.01", "F03-CONTRACT-2026.01"}:
        errors.append("unsupported erdg_contract")
    envelopes = payload.get("handoff_envelopes", [])
    if not isinstance(envelopes, list):
        errors.append("handoff_envelopes must be a list")
        envelopes = []
    for index, envelope in enumerate(envelopes):
        prefix = f"handoff_envelopes[{index}]"
        if not isinstance(envelope, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("message_id", "message_version", "source_domain", "target_domain", "decision_question", "object_ref", "runtime_versions", "allowed_uses", "forbidden_uses", "participant_status", "lineage"):
            if field not in envelope:
                errors.append(f"{prefix}.{field} is required")
        if set(envelope.get("allowed_uses", [])) & set(envelope.get("forbidden_uses", [])):
            errors.append(f"{prefix} allowed and forbidden uses overlap")
        if envelope.get("participant_status") not in {"contributed", "blocked", "inconclusive", "not_required"}:
            errors.append(f"{prefix}.participant_status is invalid")
        if not envelope.get("lineage", {}).get("input_hash"):
            errors.append(f"{prefix}.lineage.input_hash is required")
        object_ref = envelope.get("object_ref", {})
        if not isinstance(object_ref, dict) or not object_ref.get("object_id") or not object_ref.get("object_version"):
            errors.append(f"{prefix}.object_ref requires object_id and object_version")
        versions = envelope.get("runtime_versions")
        if not isinstance(versions, dict) or not versions:
            errors.append(f"{prefix}.runtime_versions must be non-empty")
        if envelope.get("participant_status") != "contributed" and not envelope.get("failure_reason"):
            errors.append(f"{prefix}.failure_reason is required for non-contributed status")
        extensions = envelope.get("extensions", {})
        if not isinstance(extensions, dict):
            errors.append(f"{prefix}.extensions must be an object")
        elif any(":" not in key for key in extensions):
            errors.append(f"{prefix}.extensions keys must be namespaced")
    if payload.get("external_write") not in {None, False, "forbidden"}:
        errors.append("ERDG cannot authorize external writes")
    if payload.get("production_ready") is True:
        errors.append("ERDG production_ready cannot be asserted by a decision payload")
    return errors


def validate(payload: dict[str, Any]) -> list[str]:
    return _compat.validate(payload) + _erdg_errors(payload)


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
