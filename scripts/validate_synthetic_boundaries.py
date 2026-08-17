#!/usr/bin/env python3
"""Ensure synthetic evaluation assets cannot claim production assurance."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = "synthetic:"
FORBIDDEN_KEYS = {
    "production_ready": True,
    "l4_gate_closed": True,
    "l4_external_review_gate_closed": True,
    "external_review_passed": True,
}


def contains_marker(value: object) -> bool:
    if isinstance(value, str):
        return MARKER in value
    if isinstance(value, dict):
        return any(contains_marker(k) or contains_marker(v) for k, v in value.items())
    if isinstance(value, list):
        return any(contains_marker(item) for item in value)
    return False


def forbidden_claims(value: object, path: str = "$", found: list[str] | None = None) -> list[str]:
    found = found if found is not None else []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, bool) and (key, item) in FORBIDDEN_KEYS:
                found.append(f"{path}.{key}")
            forbidden_claims(item, f"{path}.{key}", found)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            forbidden_claims(item, f"{path}[{index}]", found)
    return found


def audit() -> dict:
    violations: list[dict[str, object]] = []
    scanned = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix != ".json" or ".git" in path.parts:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        scanned += 1
        if contains_marker(payload):
            claims = forbidden_claims(payload)
            if claims:
                violations.append({"path": str(path.relative_to(ROOT)), "claims": claims})
    return {"status": "BLOCKED" if violations else "PASS", "scanned_json": scanned, "violations": violations}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["violations"] else 0)
