#!/usr/bin/env python3
"""Fail-closed external Action Gateway policy evaluator."""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone


def authorize(request: dict, manifest: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    reasons = []
    if manifest.get("status") not in {"controlled_pilot", "active"}: reasons.append("connector is not write-eligible")
    if manifest.get("permissions", {}).get("write") is not True: reasons.append("connector manifest is read-only")
    required = ("action_id", "decision_id", "owner_domain", "target", "operation", "idempotency_key", "decision_binding", "human_approval", "expires_at", "dry_run", "rollback", "audit_destination")
    for key in required:
        if not request.get(key): reasons.append(f"missing {key}")
    approval = request.get("human_approval", {})
    if approval.get("status") != "approved" or not approval.get("approver") or not approval.get("approved_at"): reasons.append("explicit human approval is absent")
    dry_run = request.get("dry_run", {})
    if dry_run.get("status") != "passed" or not dry_run.get("result_hash"): reasons.append("dry run is absent or failed")
    if not request.get("rollback", {}).get("steps") or not request.get("rollback", {}).get("owner"): reasons.append("rollback is incomplete")
    binding = request.get("decision_binding", {})
    if binding.get("erdg_contract") != "ERDG-CONTRACT-2026.07" or binding.get("validation_status") != "passed": reasons.append("decision binding is not ERDG-passed")
    if binding.get("decision_id") != request.get("decision_id") or binding.get("owner_domain") != request.get("owner_domain"): reasons.append("decision binding identity or owner mismatch")
    if request.get("operation") not in binding.get("allowed_operations", []): reasons.append("operation is outside the approved decision ceiling")
    if binding.get("target_ref") != request.get("target"): reasons.append("target does not match the approved decision binding")
    packet_hash = binding.get("packet_hash", "")
    if not isinstance(packet_hash, str) or len(packet_hash) != 64 or any(char not in "0123456789abcdef" for char in packet_hash): reasons.append("decision packet hash is invalid")
    try:
        expiry = datetime.fromisoformat(request.get("expires_at", "").replace("Z", "+00:00"))
        if expiry.tzinfo is None or expiry <= now: reasons.append("authorization is expired or lacks timezone")
    except ValueError: reasons.append("expires_at is invalid")
    return {"authorized": not reasons, "status": "authorized" if not reasons else "denied", "reasons": reasons, "external_write": not reasons}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: authorize_action.py REQUEST.json MANIFEST.json")
        return 2
    request, manifest = (json.loads(pathlib.Path(p).read_text()) for p in sys.argv[1:])
    result = authorize(request, manifest); print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result["authorized"] else 1


if __name__ == "__main__": raise SystemExit(main())
