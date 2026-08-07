#!/usr/bin/env python3
"""Validate connector manifests and referenced field contracts."""

from __future__ import annotations

import argparse
import json
import pathlib
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[3]
MANIFEST_SCHEMA = ROOT / "governance/connectors/schemas/connector-manifest.schema.json"
FIELD_SCHEMA = ROOT / "governance/connectors/schemas/field-contract.schema.json"


def validate_manifest(manifest: dict) -> list[str]:
    schema = json.loads(MANIFEST_SCHEMA.read_text())
    errors = [f"manifest schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(manifest)]
    if manifest.get("contract") != "CBDS-CONNECTOR-2026.08": errors.append("unsupported connector contract")
    status = manifest.get("status")
    permissions = manifest.get("permissions", {})
    if status == "contract_only" and permissions.get("write") is not False: errors.append("contract_only connector must be read-only")
    if permissions.get("write") and status not in {"controlled_pilot", "active"}: errors.append("write permission requires controlled_pilot or active")
    isolation = manifest.get("credential_isolation", {})
    if isolation.get("repository_secret_forbidden") is not True: errors.append("repository secrets must be forbidden")
    expected_failure = {"empty_response": "missing_not_zero", "partial_failure": "isolate_affected_fields", "auth_failure": "fail_closed", "rate_limit": "retry_bounded_then_inconclusive"}
    if manifest.get("failure_semantics") != expected_failure: errors.append("failure semantics must match fail-closed contract")
    field_path = ROOT / manifest.get("field_contract", "")
    if not field_path.is_file():
        errors.append("referenced field contract does not exist")
        return errors
    fields = json.loads(field_path.read_text())
    field_schema = json.loads(FIELD_SCHEMA.read_text())
    errors.extend(f"field schema: {error.message}" for error in Draft202012Validator(field_schema).iter_errors(fields))
    if fields.get("contract") != "CBDS-CONNECTOR-FIELDS-2026.08": errors.append("unsupported field contract")
    if fields.get("connector_id") != manifest.get("connector_id"): errors.append("field contract connector mismatch")
    canonical = set()
    for field in fields.get("fields", []):
        if field.get("missing_semantics") != "unknown_not_zero": errors.append("field missing semantics must be unknown_not_zero")
        name = field.get("canonical_field")
        if name in canonical: errors.append(f"duplicate canonical field: {name}")
        canonical.add(name)
        if field.get("type") == "decimal_string" and not field.get("unit"): errors.append(f"decimal field {name} requires unit/currency")
        if field.get("type") == "datetime" and not field.get("timezone"): errors.append(f"datetime field {name} requires timezone rule")
    contextual_keys = {"seller_id", "marketplace_id", "marketplace", "profile_id", "date", "snapshot_date", "attribution_window", "tenant_id", "warehouse_id", "snapshot_time"}
    if not set(fields.get("object_key", [])) <= (canonical | contextual_keys): errors.append("object key is not resolvable")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("paths", nargs="+"); args = parser.parse_args(); failures = {}
    for raw in args.paths:
        path = pathlib.Path(raw); errors = validate_manifest(json.loads(path.read_text()))
        if errors: failures[str(path)] = errors
    print(json.dumps({"valid": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__": raise SystemExit(main())
