#!/usr/bin/env python3
"""Validate Prompt Intake Guard routing and fail-closed semantics."""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "governance/domain-architecture-registry.json"
SCHEMA = ROOT / "governance/interaction/schemas/prompt-intake.schema.json"


def _time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("as_of_time must include timezone")
    return parsed


def validate(payload: dict) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).iter_errors(payload)]
    required = {"contract", "request_id", "domain_id", "object", "as_of_time", "inputs", "missing_fields", "risks", "requested_operations", "route"}
    unknown = set(payload) - (required | {"route_reason", "allowed_scope", "prohibited_scope", "calculation_targets"})
    if missing := required - set(payload): errors.append(f"missing fields: {sorted(missing)}")
    if unknown: errors.append(f"unknown fields: {sorted(unknown)}")
    if errors: return errors
    if payload["contract"] != "CBDS-INTERACTION-2026.07": errors.append("unsupported interaction contract")
    domains = {d["domain_id"] for d in json.loads(REGISTRY.read_text())["domains"] if d["availability"] == "current"}
    if payload["domain_id"] not in domains: errors.append("domain must be a current D01-D14 owner")
    try: _time(payload["as_of_time"])
    except (TypeError, ValueError): errors.append("as_of_time must be timezone-aware ISO date-time")
    route = payload["route"]
    if route not in {"answer", "ask", "research", "calculate", "block"}: errors.append("invalid route")
    risks = payload["risks"]
    if any(risks.get(k) for k in ("prompt_injection", "sovereignty_overreach", "redline")) and route != "block": errors.append("injection, sovereignty overreach, and redlines must block")
    if "external_write" in payload["requested_operations"] and route != "block": errors.append("Prompt Intake cannot authorize external_write")
    if (risks.get("irreversible_action") or risks.get("customer_commitment")) and route not in {"ask", "block"}: errors.append("irreversible actions and customer commitments require ask or block")
    missing = payload["missing_fields"]
    if any(item.get("impact") == "blocking" for item in missing) and route not in {"ask", "research", "block"}: errors.append("blocking missing fields cannot answer or calculate")
    if route == "ask" and not missing: errors.append("ask route must name missing fields")
    if route == "research" and not any(item.get("fallback") == "public_research" for item in missing): errors.append("research route must identify a public_research field")
    if route == "calculate" and missing:
        targets = set(payload.get("calculation_targets", []))
        # Older complete-input calls remain valid. Partial results require an
        # explicit dependency scope, never an assumption that missing means zero.
        if not targets:
            errors.append("partial calculation requires calculation_targets")
        for item in missing:
            if (item["impact"] == "blocking" or targets.intersection(item["required_for"])
                    or item["fallback"] != "independent_result_only"):
                errors.append(f"missing field {item['field']} prevents requested calculation")
    for item in payload["inputs"]:
        if item.get("source_class") == "untrusted_external_text" and item.get("trusted_as_instruction") is not False:
            errors.append(f"untrusted field {item.get('field')} cannot be trusted as instruction")
    for item in missing:
        for key in ("field", "impact", "required_for", "source_system", "owner", "fallback"):
            if key not in item: errors.append(f"missing-field entry lacks {key}")
    if not payload.get("route_reason"): errors.append("route_reason is required by semantic guard")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_prompt_intake.py INPUT.json")
        return 2
    payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
    errors = validate(payload)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
