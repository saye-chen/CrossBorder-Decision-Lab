#!/usr/bin/env python3
"""Apply an immutable follow-up event while preserving one current conclusion."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, canonical_hash, parse_time

RECALCULATING = {"evidence_update", "parameter_refresh", "scope_change", "scenario_override", "rollback"}
NONCALCULATING = {"clarification", "accept", "reject", "execute", "observe"}


def validate_state(state: dict[str, Any]) -> None:
    history = state.get("history")
    if not isinstance(history, list) or not history:
        raise PPFCError("history must be non-empty")
    current = [item for item in history if item.get("is_current") is True]
    if len(current) != 1:
        raise PPFCError("decision chain must have exactly one current conclusion")
    if current[0].get("decision_id") != state.get("current_decision_id") or current[0].get("version") != state.get("current_version"):
        raise PPFCError("current pointer and history disagree")
    seen = set()
    for item in history:
        key = (item.get("decision_id"), item.get("version"))
        if key in seen: raise PPFCError("duplicate decision version")
        seen.add(key)


def update(payload: dict[str, Any]) -> dict[str, Any]:
    state, event = copy.deepcopy(payload.get("state")), payload.get("event")
    if not isinstance(state, dict) or not isinstance(event, dict):
        raise PPFCError("state and event are required")
    validate_state(state)
    event_type = event.get("event_type")
    if event_type not in RECALCULATING | NONCALCULATING:
        raise PPFCError("invalid event_type")
    parse_time(event.get("occurred_at"), "event.occurred_at")
    if any(turn.get("idempotency_key") == event.get("idempotency_key") for turn in state.get("turns", [])):
        return {"state": state, "idempotent_replay": True, "requires_recompute": False}
    changed = event.get("changed_ids", [])
    if event_type in RECALCULATING and not changed:
        raise PPFCError("recalculating event requires changed_ids")
    if event_type in NONCALCULATING and event.get("old_input_hash") != event.get("new_input_hash"):
        raise PPFCError("non-calculating event cannot change input hash")
    current = next(item for item in state["history"] if item["is_current"])
    requires_recompute = event_type in RECALCULATING
    if requires_recompute:
        new_decision = payload.get("new_decision")
        if not isinstance(new_decision, dict):
            raise PPFCError("recalculating event requires new_decision")
        required = {"decision_id", "version", "status", "input_hash", "parameter_snapshot_id", "model_version", "conclusion", "created_at"}
        if required - set(new_decision): raise PPFCError("new_decision is incomplete")
        if new_decision["input_hash"] != event["new_input_hash"]:
            raise PPFCError("new decision input hash does not match event")
        parse_time(new_decision["created_at"], "new_decision.created_at")
        current["is_current"] = False
        if current["status"] not in {"closed", "retired", "rejected"}: current["status"] = "superseded"
        new_decision = {**new_decision, "is_current": True, "supersedes": f"{current['decision_id']}@{current['version']}"}
        state["history"].append(new_decision)
        state["current_decision_id"] = new_decision["decision_id"]; state["current_version"] = new_decision["version"]
        if event_type in {"parameter_refresh", "scope_change"}:
            state["pending_acceptance"] = sorted(set(state.get("pending_acceptance", [])) | {new_decision["decision_id"]})
    state.setdefault("turns", []).append({
        "turn_id": event["turn_id"], "event_id": event["event_id"], "event_type": event_type,
        "occurred_at": event["occurred_at"], "idempotency_key": event["idempotency_key"],
        "changed_ids": changed,
    })
    state["lineage"] = {"state_hash": "sha256:" + canonical_hash({k: v for k, v in state.items() if k != "lineage"}), "runtime_version": "PPFC-2026.07"}
    validate_state(state)
    return {"state": state, "idempotent_replay": False, "requires_recompute": requires_recompute}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8")); result = update(payload)
    except (OSError, json.JSONDecodeError, PPFCError) as exc:
        print(f"PPFC_CONTINUITY=BLOCKED: {exc}", file=sys.stderr); return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
