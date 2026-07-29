#!/usr/bin/env python3
"""Validate a v2 handoff and fail closed for unavailable target architecture domains."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "governance/erdg/schemas/handoff-envelope.schema.json"
REGISTRY = ROOT / "governance/domain-architecture-registry.json"


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(payload, schema)
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        return [f"schema validation failed: {exc}"]

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_id = {item["domain_id"]: item for item in registry["domains"]}
    for endpoint_name in ("source", "target"):
        endpoint = payload[endpoint_name]
        registered = by_id.get(endpoint["domain_id"])
        if registered is None:
            errors.append(f"{endpoint_name}: unknown domain_id")
            continue
        if endpoint["skill"] != registered["skill"] or endpoint["availability"] != registered["availability"]:
            errors.append(f"{endpoint_name}: endpoint identity or availability differs from registry")
        if registered["availability"] != "current":
            errors.append(f"{endpoint_name}: {registered['domain_id']} is {registered['availability']} and cannot execute")
        if payload["packet_type"] not in registered["accepted_packet_types"]:
            errors.append(f"{endpoint_name}: packet type is not accepted by {registered['domain_id']}")

    source = by_id.get(payload["source"]["domain_id"])
    target = by_id.get(payload["target"]["domain_id"])
    for endpoint_name, domain in (("source", source), ("target", target)):
        if domain:
            runtime = payload["runtime_versions"].get(domain["skill"], "")
            expected = domain["runtime_prefix"]
            if not re.fullmatch(rf"{re.escape(expected)}-20\d{{2}}\.\d{{2}}", runtime):
                errors.append(f"{endpoint_name}: missing or invalid runtime version for {domain['skill']}")
    if source and payload["authority"]["source_authority"] not in source["owned_decision_types"]:
        errors.append("authority.source_authority is not owned by source domain")
    if target and payload["authority"]["target_authority"] not in target["owned_decision_types"]:
        errors.append("authority.target_authority is not owned by target domain")
    if payload["authority"]["ownership_transfer"] is not False:
        errors.append("cross-domain handoff cannot transfer decision ownership")
    if set(payload["allowed_uses"]) & set(payload["forbidden_uses"]):
        errors.append("allowed and forbidden uses overlap")
    if payload["message_id"] in payload.get("prerequisite_message_ids", []):
        errors.append("handoff cannot depend on itself")
    if target and payload["gate_binding"]["gate_id"] not in target["blocking_gates"]:
        errors.append("gate is not registered for target domain")
    if payload["packet_type"] == "action_request":
        gate = payload["gate_binding"]
        if gate["gate_id"] != "G4_ACTION_QUALIFICATION" or gate["gate_status"] != "passed":
            errors.append("action_request requires passed G4_ACTION_QUALIFICATION")
    if payload["participant_status"] in {"blocked", "inconclusive", "partially_contributed"} and not payload.get("failure_reason"):
        errors.append("non-contributed participant status requires failure_reason")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    failures = validate(payload)
    if failures:
        print("ERDG handoff v2 rejected:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("ERDG handoff v2 accepted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
