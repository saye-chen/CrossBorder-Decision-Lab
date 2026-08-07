#!/usr/bin/env python3
"""Fail-closed candidate funnel, cross-platform evidence and handoff validator."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "references/candidate-funnel-contract.json").read_text(encoding="utf-8"))
OBJECT_KEYS = ("product_concept_id", "country", "platform")


class FunnelError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def validate_task_card(card: dict[str, Any]) -> list[str]:
    required = {"task_id", "country", "platform", "product_scope", "lifecycle", "price_band", "seller_profile", "capital_limit", "loss_limit", "time_window", "risk_posture", "objective"}
    errors = []
    missing = sorted(required - set(card))
    if missing:
        errors.append("task_card missing: " + ", ".join(missing))
    if card.get("seller_profile") == "unknown":
        errors.append("unknown seller profile must use seller-agnostic")
    return errors


def validate_gate(gate: Any, name: str) -> list[str]:
    if not isinstance(gate, dict):
        return [f"{name} gate missing"]
    errors = []
    if gate.get("status") not in CONTRACT["gate_statuses"]:
        errors.append(f"{name} gate status invalid")
    if not _nonempty_list(gate.get("checks")):
        errors.append(f"{name} gate requires checks")
    if gate.get("status") in {"inconclusive", "blocked"} and not _nonempty_list(gate.get("reasons")):
        errors.append(f"{name} gate {gate.get('status')} requires reasons")
    if gate.get("status") == "pass" and gate.get("formal_review_complete") is False and gate.get("claim") in {"compliant", "ip_clear", "risk_free"}:
        errors.append(f"{name} rapid pass cannot claim formal clearance")
    if gate.get("formal_review_complete") is True and not _nonempty_list(gate.get("evidence_ids")):
        errors.append(f"{name} formal review requires evidence_ids")
    return errors


def validate_cross_platform(rows: Any) -> list[str]:
    if rows is None:
        return []
    if not isinstance(rows, list):
        return ["cross_platform_evidence must be a list"]
    errors = []
    for index, row in enumerate(rows):
        prefix = f"cross_platform_evidence[{index}]"
        if not isinstance(row, dict):
            errors.append(prefix + " must be an object")
            continue
        required = {"relationship", "platforms", "observation_window", "evidence_ids", "source_family_ids", "comparable_basis", "alternative_explanations", "decision_effect"}
        missing = sorted(required - set(row))
        if missing:
            errors.append(prefix + " missing: " + ", ".join(missing))
        if row.get("relationship") not in CONTRACT["cross_platform_relationships"]:
            errors.append(prefix + " relationship invalid")
        if not isinstance(row.get("platforms"), list) or len(set(row.get("platforms", []))) != 2:
            errors.append(prefix + " requires exactly two distinct platforms")
        if not _nonempty_list(row.get("evidence_ids")):
            errors.append(prefix + " requires evidence_ids")
        families = row.get("source_family_ids")
        if not _nonempty_list(families):
            errors.append(prefix + " requires source_family_ids")
        if row.get("relationship") == "CONFIRMATION" and len(set(families or [])) < 2:
            errors.append(prefix + " confirmation requires two independent source families")
        if row.get("relationship") == "CONFLICT" and row.get("resolution_status") not in {"open", "resolved"}:
            errors.append(prefix + " conflict requires resolution_status")
        if not _nonempty_list(row.get("alternative_explanations")):
            errors.append(prefix + " requires alternative explanations")
    return errors


def validate_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    errors = []
    if payload.get("contract_version") != CONTRACT["contract_version"]:
        errors.append("unsupported contract_version")
    errors.extend(validate_task_card(payload.get("task_card", {})))
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict):
        raise FunnelError("candidate missing")
    required = {"candidate_id", "decision_object", "stage", "research_mode", "status", "source_evidence_ids", "source_family_ids", "promotion_reasons", "rejection_reasons", "missing_data", "weakest_assumption", "next_validation", "stop_conditions", "reentry_conditions", "supply_chain_gate", "ip_compliance_gate"}
    missing = sorted(required - set(candidate))
    if missing:
        errors.append("candidate missing: " + ", ".join(missing))
    obj = candidate.get("decision_object", {})
    if not isinstance(obj, dict) or any(not obj.get(key) for key in OBJECT_KEYS):
        errors.append("decision_object incomplete")
    stage = candidate.get("stage")
    mode = candidate.get("research_mode")
    if stage not in CONTRACT["stages"]:
        errors.append("invalid stage")
    elif mode != CONTRACT["stage_research_mode"][stage]:
        errors.append("research_mode does not match stage")
    if candidate.get("status") not in CONTRACT["statuses"]:
        errors.append("invalid candidate status")
    if not _nonempty_list(candidate.get("source_evidence_ids")):
        errors.append("candidate requires raw evidence")
    if not _nonempty_list(candidate.get("source_family_ids")):
        errors.append("candidate requires source families")
    if not candidate.get("weakest_assumption"):
        errors.append("weakest_assumption required")
    if not _nonempty_list(candidate.get("next_validation")):
        errors.append("next_validation required")
    if not _nonempty_list(candidate.get("stop_conditions")):
        errors.append("stop_conditions required")
    if candidate.get("status") == "rejected" and not _nonempty_list(candidate.get("rejection_reasons")):
        errors.append("rejected candidate requires rejection_reasons")
    if stage in {"DEEP_DIVE", "INVESTMENT_CANDIDATE"} and not _nonempty_list(candidate.get("promotion_reasons")):
        errors.append("deep stages require promotion_reasons")
    errors.extend(validate_gate(candidate.get("supply_chain_gate"), "supply_chain"))
    errors.extend(validate_gate(candidate.get("ip_compliance_gate"), "ip_compliance"))
    errors.extend(validate_cross_platform(candidate.get("cross_platform_evidence")))
    blocked_gate = any((candidate.get(name) or {}).get("status") == "blocked" for name in ("supply_chain_gate", "ip_compliance_gate"))
    if blocked_gate and candidate.get("status") not in {"blocked", "rejected"}:
        errors.append("blocked early gate requires blocked or rejected status")
    if stage == "INVESTMENT_CANDIDATE":
        if candidate.get("status") not in {"proposed_test", "conditional_entry"}:
            errors.append("investment candidate must be proposed_test or conditional_entry")
        if any((candidate.get(name) or {}).get("status") != "pass" for name in ("supply_chain_gate", "ip_compliance_gate")):
            errors.append("investment candidate requires both early gates to pass")
        if any((candidate.get(name) or {}).get("formal_review_complete") is not True for name in ("supply_chain_gate", "ip_compliance_gate")):
            errors.append("investment candidate requires formal supply-chain and IP/compliance review")
        open_conflicts = [row for row in candidate.get("cross_platform_evidence", []) if row.get("relationship") == "CONFLICT" and row.get("resolution_status") != "resolved"]
        if open_conflicts:
            errors.append("investment candidate cannot contain unresolved cross-platform conflict")
        erdg = payload.get("erdg_validation", {})
        if erdg.get("status") != "passed" or erdg.get("contract") != "ERDG-CONTRACT-2026.07":
            errors.append("investment candidate requires ERDG passed")
    if errors:
        raise FunnelError("; ".join(errors))
    return {"status": "valid", "candidate_id": candidate["candidate_id"], "stage": stage, "packet_hash": digest(payload)}


def transition(payload: dict[str, Any], new_stage: str, reason: str) -> dict[str, Any]:
    validate_candidate(payload)
    old_stage = payload["candidate"]["stage"]
    if new_stage not in CONTRACT["allowed_transitions"].get(old_stage, []):
        raise FunnelError(f"transition {old_stage}->{new_stage} forbidden")
    if not reason:
        raise FunnelError("transition reason required")
    result = json.loads(json.dumps(payload))
    result["candidate"]["stage"] = new_stage
    result["candidate"]["research_mode"] = CONTRACT["stage_research_mode"][new_stage]
    result.setdefault("transition_ledger", []).append({
        "from": old_stage, "to": new_stage, "reason": reason,
        "changed_at": datetime.now().astimezone().isoformat(timespec="seconds")
    })
    validate_candidate(result)
    return result


def compile_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    validate_candidate(payload)
    candidate = payload["candidate"]
    if candidate["stage"] != "INVESTMENT_CANDIDATE":
        raise FunnelError("handoff requires INVESTMENT_CANDIDATE")
    handoff = payload.get("handoff")
    if not isinstance(handoff, dict):
        raise FunnelError("handoff section missing")
    required = {"destinations", "validated_facts", "proof_bound_claims", "prohibited_claims", "target_segments", "purchase_jobs", "price_profit_redlines", "hypotheses", "success_conditions", "stop_conditions", "rollback", "outcome_writeback", "external_write"}
    missing = sorted(required - set(handoff))
    errors = []
    if missing:
        errors.append("handoff missing: " + ", ".join(missing))
    if set(handoff.get("destinations", [])) - set(CONTRACT["handoff_destinations"]):
        errors.append("unsupported handoff destination")
    if not _nonempty_list(handoff.get("destinations")):
        errors.append("handoff destination required")
    if handoff.get("external_write") is not False:
        errors.append("handoff cannot authorize external write")
    if not _nonempty_list(handoff.get("stop_conditions")) or not handoff.get("rollback"):
        errors.append("handoff requires stop and rollback")
    if not _nonempty_list(handoff.get("success_conditions")) or not handoff.get("outcome_writeback"):
        errors.append("handoff requires success conditions and outcome writeback")
    proof_ids = {item.get("proof_id") for item in handoff.get("validated_facts", []) if isinstance(item, dict)}
    for claim in handoff.get("proof_bound_claims", []):
        if not isinstance(claim, dict) or claim.get("proof_id") not in proof_ids:
            errors.append("every handoff claim requires a validated proof_id")
    if errors:
        raise FunnelError("; ".join(errors))
    return {
        "contract_version": CONTRACT["contract_version"],
        "candidate_id": candidate["candidate_id"],
        "decision_object": candidate["decision_object"],
        "decision_status": candidate["status"],
        "handoff": handoff,
        "external_write": False,
        "source_packet_hash": digest(payload),
        "status": "proposed"
    }


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in {"validate", "transition", "handoff"}:
        print("usage: candidate_funnel.py validate INPUT | transition INPUT NEW_STAGE REASON | handoff INPUT", file=sys.stderr)
        return 2
    payload = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    if argv[1] == "validate":
        result = validate_candidate(payload)
    elif argv[1] == "transition":
        if len(argv) < 5:
            raise FunnelError("transition requires NEW_STAGE and REASON")
        result = transition(payload, argv[3], argv[4])
    else:
        result = compile_handoff(payload)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except (FunnelError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
