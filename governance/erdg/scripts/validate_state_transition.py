#!/usr/bin/env python3
"""Validate append-only ERDG claim, decision, action and replay state transitions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from erdg_common import parse_time

TRANSITIONS = {
    "claim": {
        "hypothesis": {"proposed", "rejected", "inconclusive"},
        "proposed": {"validated", "rejected", "blocked", "inconclusive"},
        "validated": {"superseded"},
        "rejected": {"superseded"},
        "blocked": {"proposed", "superseded"},
        "inconclusive": {"proposed", "superseded"},
        "superseded": set(),
    },
    "decision": {
        "draft": {"review", "withdrawn"},
        "review": {"approved", "rejected", "blocked", "withdrawn"},
        "approved": {"effective", "withdrawn"},
        "rejected": {"superseded"},
        "blocked": {"review", "withdrawn"},
        "effective": {"superseded", "withdrawn"},
        "superseded": set(),
        "withdrawn": set(),
    },
    "action": {
        "planned": {"approved", "cancelled"},
        "approved": {"executing", "cancelled"},
        "executing": {"paused", "completed", "failed", "rolled_back"},
        "paused": {"executing", "cancelled", "rolled_back"},
        "completed": {"rolled_back"},
        "failed": {"rolled_back", "cancelled"},
        "rolled_back": set(),
        "cancelled": set(),
    },
    "replay": {
        "not_started": {"evidence_frozen"},
        "evidence_frozen": {"replayed"},
        "replayed": {"independently_reviewed", "inconclusive"},
        "independently_reviewed": {"calibrated", "no_change", "inconclusive"},
        "calibrated": set(),
        "no_change": set(),
        "inconclusive": set(),
    },
    "recovery": {
        "detected": {"frozen", "escalated"},
        "frozen": {"triaged", "escalated"},
        "triaged": {"recalculating", "escalated"},
        "recalculating": {"partially_recovered", "recovered", "escalated"},
        "partially_recovered": {"recalculating", "recovered", "escalated"},
        "recovered": {"closed", "escalated"},
        "escalated": {"recalculating", "closed"},
        "closed": set(),
    },
}


def validate(payload: dict[str, Any]) -> list[str]:
    errors = []
    machine = payload.get("machine")
    if machine not in TRANSITIONS:
        return ["unknown state machine"]
    current = payload.get("from")
    target = payload.get("to")
    if current not in TRANSITIONS[machine]:
        errors.append("unknown current state")
    elif target not in TRANSITIONS[machine][current]:
        errors.append(f"illegal {machine} transition {current}->{target}")
    for field in ("actor", "occurred_at", "reason", "input_version"):
        if not payload.get(field):
            errors.append(f"{field} is required")
    if machine == "action" and target == "approved" and not payload.get("approved_decision_id"):
        errors.append("action approval requires approved_decision_id")
    return errors


def validate_history(payload: dict[str, Any]) -> list[str]:
    errors = []
    machine = payload.get("machine")
    events = payload.get("events")
    if machine not in TRANSITIONS:
        return ["unknown state machine"]
    if not isinstance(events, list) or not events:
        return ["events must be a non-empty list"]
    last_time = None
    current = None
    effective_count = 0
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"events[{index}] must be an object")
            continue
        event_payload = {**event, "machine": machine}
        errors.extend(f"events[{index}]: {error}" for error in validate(event_payload))
        try:
            occurred = parse_time(event.get("occurred_at"), f"events[{index}].occurred_at")
            if last_time and occurred < last_time:
                errors.append(f"events[{index}]: history is not append-only chronological")
            last_time = occurred
        except ValueError as exc:
            errors.append(str(exc))
        if current is not None and event.get("from") != current:
            errors.append(f"events[{index}]: state continuity broken")
        current = event.get("to")
        if machine == "decision" and current == "effective":
            effective_count += 1
    if machine == "decision" and effective_count > 1 and not payload.get("supersession_chain_complete"):
        errors.append("decision history has multiple effective events without complete supersession")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        errors = validate(payload)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(f"BLOCKED: {error}" for error in errors), file=sys.stderr)
        return 1
    print("PASS: state transition is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
