#!/usr/bin/env python3
"""Validate D05 draft object/state schemas and fail-closed transitions."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"

STATES = {
    "intake", "screening", "evidence_required", "professional_review",
    "conditionally_cleared", "cleared_for_named_use", "blocked", "suspended",
    "remediation", "withdrawn", "expired", "superseded", "closed",
}
TRANSITIONS = {
    None: {"intake"},
    "intake": {"screening", "evidence_required", "withdrawn"},
    "screening": {"evidence_required", "professional_review", "conditionally_cleared", "blocked", "withdrawn"},
    "evidence_required": {"screening", "professional_review", "blocked", "withdrawn", "expired"},
    "professional_review": {"evidence_required", "conditionally_cleared", "blocked", "withdrawn", "expired"},
    "conditionally_cleared": {"cleared_for_named_use", "evidence_required", "blocked", "suspended", "expired"},
    "cleared_for_named_use": {"suspended", "remediation", "expired", "superseded", "closed"},
    "blocked": {"remediation", "withdrawn", "closed"},
    "suspended": {"remediation", "withdrawn", "closed"},
    "remediation": {"evidence_required", "professional_review", "conditionally_cleared", "blocked", "withdrawn"},
    "withdrawn": {"closed"},
    "expired": {"evidence_required", "professional_review", "remediation", "closed"},
    "superseded": {"closed"},
    "closed": set(),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_instance(schema_name: str, value: dict) -> list[str]:
    try:
        schema = load_json(SCHEMAS / schema_name)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(value, schema, format_checker=jsonschema.FormatChecker())
        return []
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError, jsonschema.ValidationError) as exc:
        return [str(exc)]


def validate_transition(value: dict, *, staging: bool = False) -> list[str]:
    errors = validate_instance("access-decision-state.schema.json", value)
    if errors:
        return errors
    current = value["state"]
    previous = value["previous_state"]
    if previous is not None and previous not in STATES:
        errors.append(f"unknown previous state: {previous}")
    elif current not in TRANSITIONS.get(previous, set()):
        errors.append(f"forbidden transition: {previous!r} -> {current!r}")
    if staging and current == "cleared_for_named_use":
        errors.append("controlled staging cannot emit cleared_for_named_use")
    if current in {"blocked", "suspended", "expired"} and not value.get("blocked_actions"):
        errors.append(f"{current} requires blocked_actions")
    if set(value.get("allowed_actions", [])) & set(value.get("blocked_actions", [])):
        errors.append("allowed_actions and blocked_actions overlap")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in {"object", "state"}:
        print("usage: validate_object_state.py object|state FILE", file=sys.stderr)
        return 2
    value = load_json(Path(argv[2]))
    errors = (
        validate_instance("canonical-access-object.schema.json", value)
        if argv[1] == "object"
        else validate_transition(value)
    )
    if errors:
        print("D05 draft validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print(f"D05 draft {argv[1]} validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
