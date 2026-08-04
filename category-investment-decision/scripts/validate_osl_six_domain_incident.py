#!/usr/bin/env python3
"""Validate the OSL six-domain incident and execute its recovery closure oracle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from reality_recovery import build_root_batch

EXPECTED = {"CIM", "PPFC", "SPPQ", "LIFD", "PLCO", "CIDM"}
STATUSES = {"proposed", "validated", "blocked", "inconclusive"}
DEPTH = {"mechanism", "calculation", "counter_evidence", "action", "stop_condition", "rollback", "allowed_use", "forbidden_use"}

def validate(data: dict) -> list[str]:
    errors: list[str] = []
    runtime = data.get("runtime", {})
    if runtime != {"research_mode": "online_realtime", "connector_mode": "reserved_interface"}:
        errors.append("runtime_contract_invalid")
    domains = data.get("domains", [])
    names = {item.get("domain") for item in domains}
    if names != EXPECTED or len(domains) != 6:
        errors.append("six_domain_set_invalid")
    decision_ids = set()
    for item in domains:
        domain = item.get("domain", "unknown")
        if item.get("status") not in STATUSES:
            errors.append(f"invalid_status:{domain}")
        if any(not str(item.get(field, "")).strip() for field in DEPTH):
            errors.append(f"shallow_domain_contract:{domain}")
        decision_id = item.get("decision_id")
        if not decision_id or decision_id in decision_ids:
            errors.append(f"decision_identity_invalid:{domain}")
        decision_ids.add(decision_id)
        if domain != "CIDM" and "investment" in item.get("allowed_use", "").lower():
            errors.append(f"authority_violation:{domain}")
    if next((x for x in domains if x.get("domain") == "CIDM"), {}).get("allowed_use") != "sole investment decision":
        errors.append("cidm_sovereignty_missing")

    invalid = data.get("invalidated_evidence", {})
    edge_targets = {edge.get("target") for edge in data.get("lineage_edges", []) if edge.get("source") == invalid.get("evidence_id")}
    if edge_targets != decision_ids:
        errors.append("root_lineage_incomplete")
    event = {"batch_id": data.get("recovery", {}).get("batch_id"), "invalidated_evidence_ids": [invalid.get("evidence_id")], "detected_at": invalid.get("detected_at")}
    consumers = [{"consumer_id": d["domain"], "decision_id": d.get("decision_id"), "current_effective_decision_id": d.get("decision_id"), "dependency_ids": [invalid.get("evidence_id")], "risk_flags": [], "assets": [], "blast_radius": 6, "decision_tier_may_change": True, "action_status": "planned"} for d in domains if d.get("domain") in EXPECTED]
    try:
        batch = build_root_batch(event, data.get("lineage_edges", []), consumers, data.get("recovery", {}).get("calibration", {}))
        frozen = {c["consumer_id"] for c in batch["consumers"] if c["recovery_status"] == "frozen" and c["action_status"] == "paused"}
        if frozen != EXPECTED:
            errors.append("recovery_did_not_freeze_all_domains")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f"recovery_execution_failed:{exc}")
    recovery = data.get("recovery", {})
    if recovery.get("previous_effective_decision_id") == recovery.get("new_effective_decision_id") or recovery.get("old_decision_status") != "superseded" or recovery.get("new_decision") != "Do Not Do Yet":
        errors.append("decision_supersession_invalid")
    return errors

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, required=True); args = parser.parse_args()
    errors = validate(json.loads(args.input.read_text(encoding="utf-8")))
    if errors: raise SystemExit("\n".join(errors))
    print("OSL six-domain incident: PASS")

if __name__ == "__main__": main()
