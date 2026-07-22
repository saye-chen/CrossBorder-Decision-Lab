#!/usr/bin/env python3
"""Validate the CAPM cross-skill envelope and idempotency semantics."""
from __future__ import annotations
import argparse
from datetime import datetime
from capm_common import canonical_json, emit, load_json, sha256_json


STATUSES = {"proposed", "validated", "blocked", "inconclusive", "superseded"}
REQUIRED = {"contract_id", "contract_version", "message_id", "correlation_id", "sender", "receiver", "object",
            "scope", "status", "source_evidence_level", "causal_evidence_level", "claim_ids", "evidence_ids",
            "calculation_ids", "allowed_uses", "forbidden_uses", "blocked_actions", "accepted_by_receiver",
            "lineage", "validity", "payload", "idempotency_key"}


def validate(data: dict, seen_idempotency_keys: set[str] | None = None) -> dict:
    errors = []
    missing = sorted(REQUIRED - set(data))
    if missing:
        errors.append(f"missing:{','.join(missing)}")
    if data.get("status") not in STATUSES:
        errors.append("invalid:status")
    for party in ("sender", "receiver"):
        obj = data.get(party, {})
        if not obj.get("skill") or not obj.get("runtime_version"):
            errors.append(f"invalid:{party}_runtime")
        elif not str(obj.get("runtime_version")).startswith(("CAPM-", "CIDM-", "CIM-", "VLB-", "CIG-", "AAMO-", "LIFD-", "PLCO-", "unavailable")):
            errors.append(f"invalid:{party}_runtime_format")
    if data.get("source_evidence_level") not in {"S0", "S1", "S2", "S3", "S4"}:
        errors.append("invalid:source_evidence_level")
    if set(data.get("allowed_uses", [])) & set(data.get("forbidden_uses", [])):
        errors.append("conflict:allowed_forbidden_uses")
    if data.get("status") == "validated" and not data.get("evidence_ids"):
        errors.append("invalid:validated_without_evidence")
    causal = data.get("causal_evidence_level")
    if causal not in {"C0", "C1", "C2", "C3"}:
        errors.append("invalid:causal_evidence_level")
    if causal not in {"C2", "C3"} and "incremental" in canonical_json(data.get("payload", {})).lower():
        errors.append("invalid:incremental_without_causal_evidence")
    validity = data.get("validity", {})
    try:
        start = datetime.fromisoformat(validity["valid_from"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(validity["expires_at"].replace("Z", "+00:00"))
        if start >= end: errors.append("invalid:validity_period")
        scope_time = datetime.fromisoformat(data.get("scope", {}).get("as_of_time", "").replace("Z", "+00:00"))
        if scope_time >= end: errors.append("invalid:expired_message")
    except Exception:
        errors.append("invalid:validity_time")
    lineage = data.get("lineage", {})
    for field in ("input_hash", "output_hash", "schema_hash"):
        value = lineage.get(field, "")
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value.lower()):
            errors.append(f"invalid:{field}")
    receiver = data.get("receiver", {})
    accepted = data.get("accepted_by_receiver", {}).get("status")
    if receiver.get("runtime_version") == "unavailable" and accepted == "accepted":
        errors.append("invalid:unavailable_receiver_accepted")
    receipt = data.get("accepted_by_receiver", {})
    if accepted in {"accepted", "rejected"} and not receipt.get("checked_at"):
        errors.append("invalid:receiver_decision_without_checked_at")
    if accepted == "pending" and receipt.get("checked_at"):
        errors.append("invalid:pending_with_checked_at")
    if not data.get("idempotency_key"):
        errors.append("invalid:idempotency_key")
    if seen_idempotency_keys is not None and data.get("idempotency_key") in seen_idempotency_keys:
        errors.append("duplicate:idempotency_key")
    if data.get("status") == "superseded" and not data.get("supersedes_message_id"):
        errors.append("invalid:superseded_without_predecessor")
    return {"valid": not errors, "errors": errors, "message_hash": sha256_json(data)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); result = validate(load_json(a.input)); emit(result); raise SystemExit(0 if result["valid"] else 1)
