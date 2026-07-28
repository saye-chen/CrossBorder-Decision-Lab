#!/usr/bin/env python3
"""Apply one immutable product-decision event with optimistic concurrency control."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

RECALCULATING = {"evidence_update", "product_fact_change", "scope_change", "scenario_override", "validation_result", "incident_or_recall", "rollback", "retire"}
NONCALCULATING = {"clarification", "cross_domain_accept", "cross_domain_reject", "action_update"}


class StateError(ValueError):
    pass


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_state(state: dict) -> None:
    history = state.get("history", [])
    current = [x for x in history if x.get("is_current") is True]
    if len(current) != 1:
        raise StateError("exactly one current decision is required")
    if current[0].get("decision_id") != state.get("current_decision_id") or current[0].get("version") != state.get("current_version"):
        raise StateError("current pointer mismatch")
    keys = [(x.get("decision_id"), x.get("version")) for x in history]
    if len(keys) != len(set(keys)):
        raise StateError("duplicate decision version")


def update(payload: dict) -> dict:
    state = copy.deepcopy(payload.get("state"))
    event = copy.deepcopy(payload.get("event"))
    if not isinstance(state, dict) or not isinstance(event, dict):
        raise StateError("state and event are required")
    validate_state(state)
    if event.get("event_type") not in RECALCULATING | NONCALCULATING:
        raise StateError("invalid event type")
    if any(x.get("idempotency_key") == event.get("idempotency_key") for x in state.get("events", [])):
        return {"state": state, "idempotent_replay": True, "requires_recompute": False}
    if event.get("expected_revision") != state.get("chain_revision"):
        raise StateError("revision conflict")
    if event.get("sequence") != state.get("next_sequence"):
        raise StateError("event sequence mismatch")
    occurred, recorded = parse_time(event["occurred_at"]), parse_time(event["recorded_at"])
    if recorded < occurred:
        raise StateError("recorded_at precedes occurred_at")
    if event["object_id"] != state["object_ref"]["object_id"]:
        raise StateError("object mismatch")
    if event["event_type"] not in {"product_fact_change", "scope_change"} and event["object_version"] != state["object_ref"]["object_version"]:
        raise StateError("object version mismatch")
    if event["event_type"] in NONCALCULATING and event["old_input_hash"] != event["new_input_hash"]:
        raise StateError("non-calculating event changed input hash")
    if event["event_type"] in RECALCULATING and not event["changed_node_ids"]:
        raise StateError("recalculating event requires changed nodes")
    current = next(x for x in state["history"] if x["is_current"])
    if event["event_type"] == "retire" and state["product_lifecycle_stage"] == "PLC8":
        raise StateError("retired object cannot be re-retired or reactivated")
    requires = event["event_type"] in RECALCULATING
    if requires:
        new = copy.deepcopy(payload.get("new_decision"))
        if not isinstance(new, dict):
            raise StateError("new decision required")
        for field in ("decision_id", "version", "status", "object_version", "input_hash", "created_at"):
            if not new.get(field):
                raise StateError(f"new decision missing {field}")
        if new["input_hash"] != event["new_input_hash"]:
            raise StateError("new decision input hash mismatch")
        if event["event_type"] not in {"rollback"} and new["decision_id"] == current["decision_id"] and new["version"] == current["version"]:
            raise StateError("new decision must be immutable new version")
        current["is_current"] = False
        if current["status"] not in {"retired", "rejected"}:
            current["status"] = "superseded"
        new.update(is_current=True, supersedes=f"{current['decision_id']}@{current['version']}")
        state["history"].append(new)
        state["current_decision_id"], state["current_version"] = new["decision_id"], new["version"]
        state["decision_state"] = new["status"]
        if event["event_type"] in {"product_fact_change", "scope_change"}:
            state["object_ref"]["object_version"] = new["object_version"]
            state["acceptance_state"] = "pending"
        if event["event_type"] == "incident_or_recall":
            state["decision_state"], state["action_state"] = "blocked", "stopped"
        if event["event_type"] == "retire":
            state["product_lifecycle_stage"], state["decision_state"], state["action_state"] = "PLC8", "retired", "stopped"
        if event["event_type"] == "rollback":
            plan = payload.get("rollback_plan")
            if not isinstance(plan, dict):
                raise StateError("rollback plan required")
            if plan.get("executed_actions") and (not plan.get("compensating_actions") or not plan.get("residual_exposure")):
                raise StateError("executed actions require compensation and residual exposure")
    elif event["event_type"] == "cross_domain_accept":
        state["acceptance_state"] = "accepted"
    elif event["event_type"] == "cross_domain_reject":
        state["acceptance_state"] = "rejected"
    elif event["event_type"] == "action_update":
        action_state = payload.get("action_state")
        if action_state not in {"proposed", "approved", "executing", "completed", "stopped", "superseded", "failed"}:
            raise StateError("invalid action state")
        state["action_state"] = action_state
    event["late_arrival"] = bool(state.get("events") and occurred < max(parse_time(x["occurred_at"]) for x in state["events"]))
    state.setdefault("events", []).append(event)
    state["chain_revision"] += 1
    state["next_sequence"] += 1
    state["lineage"] = {"state_hash": canonical_hash({k: v for k, v in state.items() if k != "lineage"}), "runtime_version": "PIPM-2026.01"}
    validate_state(state)
    return {"state": state, "idempotent_replay": False, "requires_recompute": requires}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); args = parser.parse_args()
    try:
        result = update(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, KeyError, ValueError, StateError) as exc:
        print(f"PIPM_CONTINUITY=BLOCKED:{exc}", file=sys.stderr); return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
