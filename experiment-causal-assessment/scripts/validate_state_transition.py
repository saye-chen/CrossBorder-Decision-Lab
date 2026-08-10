#!/usr/bin/env python3
"""Validate ECAE lifecycle transitions and their prerequisite evidence."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, require_fields


ALLOWED = {
    "draft": {"preregistered", "blocked", "redesign_required", "cancelled"},
    "preregistered": {"eligibility_checked", "blocked", "redesign_required", "cancelled"},
    "eligibility_checked": {"approved_to_launch", "blocked", "redesign_required", "cancelled"},
    "approved_to_launch": {"running", "cancelled", "blocked"},
    "running": {"monitoring", "analysis_locked", "stopped_for_harm", "stopped_for_futility", "stopped_for_success", "data_failed", "cancelled"},
    "monitoring": {"analysis_locked", "stopped_for_harm", "stopped_for_futility", "stopped_for_success", "data_failed", "cancelled"},
    "analysis_locked": {"analyzed", "data_failed", "inconclusive"},
    "analyzed": {"reviewed", "inconclusive", "invalidated", "superseded"},
    "reviewed": {"handed_off", "replayed", "invalidated", "superseded"},
    "handed_off": {"replayed", "invalidated", "superseded", "stale"},
    "replayed": {"handed_off", "invalidated", "superseded", "stale"},
    "stale": {"replayed", "invalidated", "superseded"},
    "blocked": {"draft", "redesign_required", "cancelled"},
    "redesign_required": {"draft", "cancelled"},
    "data_failed": {"analysis_locked", "redesign_required", "cancelled"},
    "inconclusive": {"reviewed", "redesign_required", "superseded"},
    "stopped_for_harm": {"analysis_locked", "reviewed", "invalidated"},
    "stopped_for_futility": {"analysis_locked", "reviewed", "invalidated"},
    "stopped_for_success": {"analysis_locked", "reviewed", "invalidated"},
    "cancelled": set(),
    "superseded": set(),
    "invalidated": set(),
}


def validate_transition(value: dict) -> dict:
    require_fields(value, ["from_status", "to_status", "evidence_refs", "trigger", "actor", "occurred_at"])
    source, target = value["from_status"], value["to_status"]
    if source not in ALLOWED:
        raise ECAEError("UNKNOWN_STATE", f"Unknown source state: {source}")
    if target not in ALLOWED[source]:
        raise ECAEError("ILLEGAL_TRANSITION", f"Transition {source} -> {target} is forbidden")
    if not value["evidence_refs"]:
        raise ECAEError("MISSING_TRANSITION_EVIDENCE", "Every transition requires evidence_refs")
    if target == "approved_to_launch" and value.get("eligibility_passed") is not True:
        raise ECAEError("ELIGIBILITY_NOT_PASSED", "approved_to_launch requires eligibility_passed=true")
    if target == "analyzed" and value.get("analysis_locked") is not True:
        raise ECAEError("ANALYSIS_NOT_LOCKED", "analyzed requires analysis_locked=true")
    if target == "handed_off" and value.get("review_accepted") is not True:
        raise ECAEError("REVIEW_NOT_ACCEPTED", "handed_off requires review_accepted=true")
    return {"valid": True, "from_status": source, "to_status": target, "terminal": not ALLOWED[target]}


if __name__ == "__main__":
    cli_main(validate_transition, __doc__ or "Validate transition")
