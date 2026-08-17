#!/usr/bin/env python3
"""Evaluate an end-to-end CAPM action ceiling without taking adjacent-domain sovereignty."""
from __future__ import annotations
import argparse
from capm_common import emit, load_json, sha256_json
from partnership_economics import commission_ceiling, fixed_fee_ceiling
from validate_ecae_handoff import qualified_receipt_from

GATES = ("G1A", "G1B", "G2", "G3", "G4", "G5", "G6")
STATUSES = {"pass", "blocked", "inconclusive", "not_applicable"}
HIGH_RISK = {"pay", "sign", "ship_sample", "publish", "reuse", "paid_amplification", "scale"}


def evaluate(data: dict) -> dict:
    required = ("decision_id", "object", "scope", "input_quality", "evidence", "gates", "candidate_actions")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    obj = data["object"]
    for key in ("canonical_id", "object_version", "object_type"):
        if not obj.get(key): raise ValueError(f"object.{key} required")
    if data["input_quality"] not in {"Q0", "Q1", "Q2", "Q3"}:
        raise ValueError("invalid input_quality")
    evidence_ids = {item.get("evidence_id") for item in data["evidence"]}
    if None in evidence_ids or len(evidence_ids) != len(data["evidence"]):
        raise ValueError("evidence IDs must be present and unique")

    gates, blocked, recovery = {}, set(), []
    for gate in GATES:
        item = data["gates"].get(gate)
        if not isinstance(item, dict) or item.get("status") not in STATUSES:
            raise ValueError(f"invalid gate: {gate}")
        evidence_ids = item.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids or any(not isinstance(x, str) or not x.strip() for x in evidence_ids):
            raise ValueError(f"gate evidence required: {gate}")
        undeclared = set(evidence_ids) - {item.get("evidence_id") for item in data["evidence"]}
        if undeclared:
            raise ValueError(f"gate evidence not declared: {gate}: {sorted(undeclared)}")
        state = item["status"]
        gate_blocked = set(item.get("blocked_actions", []))
        if state in {"blocked", "inconclusive"}: blocked |= gate_blocked
        gates[gate] = {"status": state, "blocked_actions": sorted(gate_blocked), "evidence_ids": sorted(set(evidence_ids)), "owner_skill": item.get("owner_skill", "creator-affiliate-partnership-management")}
        recovery.extend(item.get("recovery_evidence", []))

    candidates = set(data["candidate_actions"])
    if data["input_quality"] in {"Q0", "Q1"}:
        blocked |= candidates & HIGH_RISK
    allowed = candidates - blocked
    legacy_causal = data.get("causal_evidence_level", "C0")
    ecae_receipt = qualified_receipt_from(data)
    incremental_qualified = bool(ecae_receipt and ecae_receipt["incremental_claim_allowed"])
    forbidden_claims = [] if incremental_qualified else ["incremental"]

    calculations = {}
    economics = data.get("economics")
    if economics:
        if economics.get("commission"):
            calculations["commission"] = commission_ceiling(economics["commission"])
        if economics.get("fixed_fee"):
            calculations["fixed_fee"] = fixed_fee_ceiling(economics["fixed_fee"])
        if any(value.get("status") == "blocked" for value in calculations.values()):
            blocked |= candidates & {"pay", "sign", "scale"}; allowed -= blocked

    if any(gates[g]["status"] == "blocked" for g in ("G1A", "G1B", "G2", "G3")):
        posture = "Blocked"
    elif not allowed:
        posture = "Hold"
    elif allowed & HIGH_RISK:
        posture = "Test" if data["input_quality"] != "Q3" else "Conditional Go"
    else:
        posture = "Investigate"
    return {
        "runtime_version": "CAPM-2026.07", "decision_id": data["decision_id"], "object": obj,
        "posture": posture, "allowed_actions": sorted(allowed), "blocked_actions": sorted(blocked),
        "gates": gates, "recovery_evidence": sorted(set(recovery)), "calculations": calculations,
        "causal_label": "f01_incremental_eligible" if incremental_qualified else ("legacy_c_label_non_equivalent" if legacy_causal in {"C2", "C3"} else "attributed_or_inconclusive"),
        "ecae_consumer_receipt": ecae_receipt,
        "forbidden_claims": forbidden_claims, "input_hash": sha256_json(data),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("input", nargs="?"); args = parser.parse_args(); emit(evaluate(load_json(args.input)))
