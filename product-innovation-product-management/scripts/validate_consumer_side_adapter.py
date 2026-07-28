#!/usr/bin/env python3
"""Execute one consumer-owned PIPM adapter and its negative-path contract tests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CONTRACT = "PIPM-CONSUMER-2026.01"


def canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def evaluate(adapter: dict[str, Any], message: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if adapter.get("contract") != CONTRACT:
        errors.append("CONTRACT_VERSION_UNSUPPORTED")
    if message.get("contract") != CONTRACT:
        errors.append("MESSAGE_VERSION_MISMATCH")
    payload = message.get("payload")
    if not isinstance(payload, dict):
        errors.append("PAYLOAD_INVALID")
        payload = {}
    missing = sorted(set(adapter.get("required_fields", [])) - set(payload))
    if missing:
        errors.append("REQUIRED_FIELDS_MISSING:" + ",".join(missing))
    forbidden = sorted(set(adapter.get("forbidden_fields", [])) & set(payload))
    if forbidden:
        errors.append("FORBIDDEN_FIELDS_PRESENT:" + ",".join(forbidden))
    if message.get("use") not in adapter.get("allowed_uses", []):
        errors.append("USE_NOT_ALLOWED")
    if message.get("external_write") is not False:
        errors.append("EXTERNAL_WRITE_FORBIDDEN")
    accepted = not errors
    return {
        "accepted": accepted,
        "decision": "accepted" if accepted else "blocked",
        "errors": errors,
        "mapped": {
            adapter["field_mapping"][field]: payload[field]
            for field in adapter.get("required_fields", [])
            if field in payload and field in adapter.get("field_mapping", {})
        } if accepted else {},
        "retained_sovereignty": adapter.get("retained_sovereignty", []),
    }


def exercise(adapter: dict[str, Any]) -> dict[str, bool]:
    valid_payload = {field: f"fixture:{field}" for field in adapter["required_fields"]}
    valid = {
        "contract": CONTRACT,
        "use": "decision_support",
        "external_write": False,
        "payload": valid_payload,
    }
    version = {**valid, "contract": "PIPM-CONSUMER-1900.01"}
    missing = {**valid, "payload": dict(valid_payload)}
    missing["payload"].pop(adapter["required_fields"][0])
    forbidden = {**valid, "payload": {**valid_payload, adapter["forbidden_fields"][0]: True}}
    external = {**valid, "external_write": True}
    return {
        "valid_accepts": evaluate(adapter, valid)["accepted"],
        "version_mismatch_blocks": not evaluate(adapter, version)["accepted"],
        "missing_required_blocks": not evaluate(adapter, missing)["accepted"],
        "forbidden_writeback_blocks": not evaluate(adapter, forbidden)["accepted"],
        "external_execution_blocks": not evaluate(adapter, external)["accepted"],
    }


def validate_files(adapter_path: Path, acceptance_path: Path) -> list[str]:
    adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    checks = exercise(adapter)
    if not all(checks.values()):
        errors.extend(name for name, passed in checks.items() if not passed)
    if acceptance.get("consumer") != adapter.get("consumer"):
        errors.append("CONSUMER_MISMATCH")
    if acceptance.get("adapter_hash") != canonical_hash(adapter):
        errors.append("ADAPTER_HASH_MISMATCH")
    if acceptance.get("checks") != checks:
        errors.append("CHECK_EVIDENCE_MISMATCH")
    if acceptance.get("automated_contract_accepted") is not all(checks.values()):
        errors.append("ACCEPTANCE_STATE_MISMATCH")
    if acceptance.get("independent_owner_accepted") is not False:
        errors.append("INDEPENDENT_ACCEPTANCE_PREMATURE")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter", type=Path)
    parser.add_argument("acceptance", type=Path)
    args = parser.parse_args()
    errors = validate_files(args.adapter, args.acceptance)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
