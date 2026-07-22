#!/usr/bin/env python3
"""Execute the JSON-Schema subset used by CAPM without an external dependency."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path
from capm_common import emit, load_json


def resolve(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"): raise ValueError(f"unsupported ref: {ref}")
    value = root
    for part in ref[2:].split("/"): value = value[part.replace("~1", "/").replace("~0", "~")]
    return value


def validate(instance, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    root = root or schema; errors = []
    if "$ref" in schema: return validate(instance, resolve(root, schema["$ref"]), root, path)
    expected = schema.get("type")
    types = expected if isinstance(expected, list) else [expected] if expected else []
    type_ok = not types or any((t == "object" and isinstance(instance, dict)) or (t == "array" and isinstance(instance, list)) or
                               (t == "string" and isinstance(instance, str)) or (t == "boolean" and isinstance(instance, bool)) or
                               (t == "number" and isinstance(instance, (int, float)) and not isinstance(instance, bool)) or
                               (t == "integer" and isinstance(instance, int) and not isinstance(instance, bool)) or
                               (t == "null" and instance is None) for t in types)
    if not type_ok: return [f"{path}:type"]
    if "enum" in schema and instance not in schema["enum"]: errors.append(f"{path}:enum")
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0): errors.append(f"{path}:minLength")
        if schema.get("pattern") and not re.fullmatch(schema["pattern"], instance): errors.append(f"{path}:pattern")
        if schema.get("format") == "date-time":
            try:
                dt = datetime.fromisoformat(instance.replace("Z", "+00:00"))
                if dt.tzinfo is None: raise ValueError
            except Exception: errors.append(f"{path}:date-time")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance: errors.append(f"{path}.{key}:required")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties: errors.append(f"{path}.{key}:additional")
        for key, value in instance.items():
            if key in properties: errors.extend(validate(value, properties[key], root, f"{path}.{key}"))
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0): errors.append(f"{path}:minItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in instance]
            if len(encoded) != len(set(encoded)): errors.append(f"{path}:uniqueItems")
        for idx, value in enumerate(instance): errors.extend(validate(value, schema.get("items", {}), root, f"{path}[{idx}]"))
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("schema"); parser.add_argument("input", nargs="?"); args = parser.parse_args()
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8")); result = {"valid": True, "errors": validate(load_json(args.input), schema)}
    result["valid"] = not result["errors"]; emit(result); raise SystemExit(0 if result["valid"] else 1)
