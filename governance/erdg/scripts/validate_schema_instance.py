#!/usr/bin/env python3
"""Validate ERDG instances against complete JSON Schema Draft 2020-12 semantics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    del path  # Kept for compatibility with the previous function signature.
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{error.json_path}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        instance = json.loads(args.instance.read_text(encoding="utf-8"))
        errors = validate_instance(instance, schema)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(f"BLOCKED: {error}" for error in errors), file=sys.stderr)
        return 1
    print("PASS: ERDG schema instance is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
