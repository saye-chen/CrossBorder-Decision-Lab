#!/usr/bin/env python3
"""Validate an ECAE object against its JSON Schema and content hash contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ecae_common import ECAEError, content_hash, emit, failure, load_json, parse_time, schema_root, success


def validate_object(value: dict, schema_name: str, *, verify_hash: bool = True) -> dict:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from referencing import Registry, Resource
    except ImportError as exc:
        raise ECAEError("DEPENDENCY_UNAVAILABLE", "jsonschema is required for schema validation") from exc

    schema_path = schema_root() / schema_name
    if not schema_path.exists():
        raise ECAEError("SCHEMA_NOT_FOUND", f"Unknown schema: {schema_name}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = Registry()
    for candidate_path in schema_root().glob("*.json"):
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        if candidate.get("$id"):
            registry = registry.with_resource(candidate["$id"], Resource.from_contents(candidate))
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        details = [
            {"path": "$" + "".join(f"[{part!r}]" for part in error.absolute_path), "message": error.message}
            for error in errors
        ]
        raise ECAEError("SCHEMA_VALIDATION_FAILED", f"Object failed {schema_name}", details)

    if "created_at" in value and "updated_at" in value:
        if parse_time(value["updated_at"], "updated_at") < parse_time(value["created_at"], "created_at"):
            raise ECAEError("OBJECT_TIME_ORDER_INVALID", "updated_at cannot precede created_at")
    if value.get("content_hash") == "PENDING" and value.get("status") not in {"draft", "preregistered"}:
        raise ECAEError("PENDING_HASH_NOT_ALLOWED", "Only draft/preregistered objects may use content_hash=PENDING")

    if verify_hash and value.get("content_hash") not in (None, "PENDING"):
        actual = content_hash(value)
        if value["content_hash"] != actual:
            raise ECAEError(
                "CONTENT_HASH_MISMATCH",
                "content_hash does not match canonical object content",
                {"declared": value["content_hash"], "computed": actual},
            )
    return {"schema": schema_name, "valid": True, "computed_content_hash": content_hash(value)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", help="Schema filename, e.g. causal-question.schema.json")
    parser.add_argument("input", help="JSON object path")
    parser.add_argument("--skip-hash", action="store_true", help="Skip declared content_hash verification")
    args = parser.parse_args()
    try:
        emit(success(validate_object(load_json(args.input), args.schema, verify_hash=not args.skip_hash)))
    except ECAEError as exc:
        emit(failure(exc))
        sys.exit(2)


if __name__ == "__main__":
    main()
