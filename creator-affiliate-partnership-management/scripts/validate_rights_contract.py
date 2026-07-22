#!/usr/bin/env python3
"""Validate requested content uses against a CAPM rights record."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from capm_common import emit, load_json, sha256_json


DIMENSIONS = ("platform", "use", "territory", "edit", "identity_use", "ai_use")


def parse_time(value: str, name: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise ValueError(f"{name}: invalid ISO-8601") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{name}: timezone required")
    return dt.astimezone(timezone.utc)


def validate(data: dict) -> dict:
    required = ("rights_id", "content_id", "creator_id", "start_at", "end_at", "granted", "requested", "evidence_ids")
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if not isinstance(data.get("evidence_ids"), list) or not data["evidence_ids"]:
        raise ValueError("evidence_ids must be non-empty")
    start, end = parse_time(data["start_at"], "start_at"), parse_time(data["end_at"], "end_at")
    as_of = parse_time(data.get("as_of_time", datetime.now(timezone.utc).isoformat()), "as_of_time")
    if start >= end:
        raise ValueError("rights start must be before end")
    blocked = []
    if data.get("revoked_at"):
        revoked = parse_time(data["revoked_at"], "revoked_at")
        if revoked <= as_of:
            blocked.append("revoked")
    if not start <= as_of < end:
        blocked.append("outside_valid_period")
    granted, requested = data["granted"], data["requested"]
    for dim in DIMENSIONS:
        allowed = set(granted.get(dim, []))
        wanted = set(requested.get(dim, []))
        if not wanted.issubset(allowed):
            blocked.append(f"ungranted:{dim}:{sorted(wanted - allowed)}")
    return {"rights_id": data["rights_id"], "status": "blocked" if blocked else "validated",
            "blocked_reasons": blocked, "blocked_actions": data.get("requested_actions", []) if blocked else [],
            "allowed_actions": [] if blocked else data.get("requested_actions", []), "input_hash": sha256_json(data)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); emit(validate(load_json(a.input)))
