#!/usr/bin/env python3
"""Execute the JSON-Schema subset used by LIFD without a runtime dependency."""

from __future__ import annotations

import json
import re
from typing import Any


def validate(instance: Any, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    root = root or schema
    errors: list[str] = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}:unsupported_ref"]
        resolved = root
        for part in ref[2:].split("/"):
            resolved = resolved[part.replace("~1", "/").replace("~0", "~")]
        return validate(instance, resolved, root, path)

    expected = schema.get("type")
    types = expected if isinstance(expected, list) else [expected] if expected else []
    matches_type = not types or any(
        (candidate == "object" and isinstance(instance, dict))
        or (candidate == "array" and isinstance(instance, list))
        or (candidate == "string" and isinstance(instance, str))
        or (candidate == "boolean" and isinstance(instance, bool))
        or (candidate == "number" and isinstance(instance, (int, float)) and not isinstance(instance, bool))
        or (candidate == "integer" and isinstance(instance, int) and not isinstance(instance, bool))
        or (candidate == "null" and instance is None)
        for candidate in types
    )
    if not matches_type:
        return [f"{path}:type"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}:const")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}:enum")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}:minLength")
        if schema.get("pattern") and not re.fullmatch(schema["pattern"], instance):
            errors.append(f"{path}:pattern")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}:required")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}.{key}:additional")
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate(value, properties[key], root, f"{path}.{key}"))
    if isinstance(instance, list):
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}:uniqueItems")
        for index, value in enumerate(instance):
            errors.extend(validate(value, schema.get("items", {}), root, f"{path}[{index}]"))
    return errors
