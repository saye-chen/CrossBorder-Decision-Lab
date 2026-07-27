#!/usr/bin/env python3
"""Resolve an approved, in-scope ERDG threshold, weight, formula or redline."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from erdg_common import parse_time

SCOPE_RANK = {"global": 0, "partial": 1, "policy_override": 2, "combination": 3}


def matches(parameter: dict[str, Any], context: dict[str, Any], when: datetime) -> bool:
    start = parse_time(parameter.get("effective_from"), "effective_from")
    end_raw = parameter.get("effective_to")
    end = parse_time(end_raw, "effective_to") if end_raw else None
    if when < start or (end and when > end):
        return False
    for field in ("country", "platform", "category", "lifecycle", "seller_type"):
        expected = parameter.get(field)
        if expected not in {None, "*"} and expected != context.get(field):
            return False
    if parameter.get("approval", {}).get("status") != "approved":
        return False
    scope = parameter.get("scope")
    calibration = parameter.get("calibration_status")
    if scope in {"partial", "combination"}:
        if calibration != "real_calibrated" or not parameter.get("evidence_level"):
            return False
    if scope == "policy_override" and calibration != "policy_override":
        return False
    return True


def resolve(payload: dict[str, Any]) -> dict[str, Any]:
    parameter_id = payload.get("parameter_id")
    context = payload.get("context")
    candidates = payload.get("parameters")
    if not parameter_id or not isinstance(context, dict) or not isinstance(candidates, list):
        raise ValueError("parameter_id, context and parameters are required")
    when = parse_time(payload.get("as_of_time"), "as_of_time")
    for candidate in candidates:
        if candidate.get("parameter_id") != parameter_id:
            continue
        if candidate.get("scope") == "policy_override" and candidate.get("calibration_status") != "policy_override":
            raise ValueError("policy_override scope requires explicit policy_override calibration_status")
    applicable = [p for p in candidates if p.get("parameter_id") == parameter_id and matches(p, context, when)]
    redlines = [p for p in applicable if p.get("parameter_type") == "redline" and p.get("scope") == "global"]
    if redlines:
        selected = sorted(redlines, key=lambda p: p.get("version", ""))[-1]
        return {"status": "resolved", "selected": selected, "reason": "non_relaxable_global_redline"}
    if not applicable:
        return {"status": "inconclusive", "selected": None, "reason": "no_approved_applicable_parameter"}
    selected = sorted(applicable, key=lambda p: (SCOPE_RANK.get(p.get("scope"), -1), p.get("version", "")))[-1]
    if selected.get("scope") == "policy_override":
        for field in ("effective_to", "maximum_exposure", "rollback_version"):
            if not selected.get(field):
                raise ValueError(f"policy_override requires {field}")
    return {"status": "resolved", "selected": selected, "reason": f"approved_{selected.get('scope')}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(resolve(payload), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
