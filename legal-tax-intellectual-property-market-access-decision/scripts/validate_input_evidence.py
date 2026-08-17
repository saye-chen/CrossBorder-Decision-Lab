#!/usr/bin/env python3
"""Validate D05 draft inputs, evidence, dynamic rules and opinion receipts."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None: raise ValueError("timezone required")
    return parsed


def validate_schema(name: str, value: dict) -> list[str]:
    try:
        schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(value, schema, format_checker=jsonschema.FormatChecker())
        return []
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError, jsonschema.ValidationError) as exc:
        return [str(exc)]


def validate_evidence(value: dict, as_of_time: str) -> list[str]:
    errors = validate_schema("evidence-record.schema.json", value)
    if errors:
        return errors
    as_of = parse_time(as_of_time)
    if value["verified_at"] and parse_time(value["verified_at"]) > as_of:
        errors.append("evidence verified_at is after decision as_of_time")
    if value["expires_at"] and parse_time(value["expires_at"]) <= as_of and value["state"] == "current":
        errors.append("expired evidence cannot be current")
    if set(value["supports_claims"]) & set(value["opposes_claims"]):
        errors.append("evidence cannot support and oppose the same claim without conflict state")
    if value["source_type"] == "synthetic_fixture" and "production_decision" in value["allowed_uses"]:
        errors.append("synthetic evidence cannot support production decisions")
    return errors


def validate_rule(value: dict, as_of_time: str) -> list[str]:
    errors = validate_schema("dynamic-rule.schema.json", value)
    if errors:
        return errors
    as_of = parse_time(as_of_time)
    if parse_time(value["verified_at"]) > as_of:
        errors.append("rule verified_at is after decision as_of_time")
    if parse_time(value["effective_at"]) > as_of and value["state"] == "current":
        errors.append("future rule cannot be current")
    if value["expires_at"] and parse_time(value["expires_at"]) <= as_of and value["state"] == "current":
        errors.append("expired rule cannot be current")
    return errors


def validate_opinion(value: dict, as_of_time: str, jurisdiction: str, object_ref: str, intended_use: str) -> list[str]:
    errors = validate_schema("professional-opinion-receipt.schema.json", value)
    if errors:
        return errors
    as_of = parse_time(as_of_time)
    if value["state"] == "accepted_as_bounded_evidence":
        if jurisdiction not in value["jurisdictions"]:
            errors.append("accepted opinion jurisdiction mismatch")
        if object_ref not in value["object_refs"]:
            errors.append("accepted opinion object mismatch")
        if intended_use not in value["allowed_uses"]:
            errors.append("accepted opinion use mismatch")
        if value["conflict_of_interest"] in {"unresolved", "undisclosed"}:
            errors.append("accepted opinion has unresolved conflict of interest")
        if parse_time(value["verified_at"]) > as_of or parse_time(value["expires_at"]) <= as_of:
            errors.append("accepted opinion is not current at decision time")
    return errors
