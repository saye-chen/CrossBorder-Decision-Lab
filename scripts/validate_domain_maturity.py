#!/usr/bin/env python3
"""Validate the single-source nine-domain maturity ledger and replay claims."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "governance/domain-maturity-status.json"
EXPECTED = {
    "category-investment-decision", "competitive-intelligence-monitoring", "video-link-breakdown",
    "consumer-insights-customer-growth", "advertising-analysis-measurement-optimization",
    "logistics-inventory-fulfillment-decision", "platform-store-listing-conversion",
    "creator-affiliate-partnership-management", "marketing-brand-campaign-management",
}

def validate_replay(data: dict, expected_skill: str | None = None) -> dict:
    errors: list[str] = []
    if expected_skill and data.get("skill") != expected_skill:
        errors.append("skill_mismatch")
    cases = data.get("cases")
    if not isinstance(cases, list):
        return {"valid": False, "production_ready": False, "authorized_cases": 0, "errors": ["cases_not_array"]}
    ids: set[str] = set(); fingerprints: set[tuple[str, str]] = set()
    for index, case in enumerate(cases):
        prefix = f"case[{index}]"
        required = {"case_id", "case_type", "authorization_reference", "deidentified", "input_hash", "result_hash", "actual_outcome", "maturity_checked_at", "independent_review", "bias_and_calibration", "incident_and_rollback", "drift_assessment"}
        missing = sorted(required - set(case))
        if missing: errors.append(f"{prefix}.missing:{','.join(missing)}")
        case_id = case.get("case_id")
        if not case_id or case_id in ids: errors.append(f"{prefix}.duplicate_or_empty_case_id")
        ids.add(case_id)
        pair = (str(case.get("input_hash", "")), str(case.get("result_hash", "")))
        if pair in fingerprints: errors.append(f"{prefix}.duplicate_fingerprint")
        fingerprints.add(pair)
        for field in ("input_hash", "result_hash"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(case.get(field, ""))): errors.append(f"{prefix}.invalid_{field}")
        if case.get("deidentified") is not True or not str(case.get("authorization_reference", "")).strip(): errors.append(f"{prefix}.authorization_or_deidentification")
        outcome = case.get("actual_outcome", {})
        if not isinstance(outcome, dict) or not outcome.get("matured_at") or not outcome.get("measures"): errors.append(f"{prefix}.actual_outcome")
        review = case.get("independent_review", {})
        if not isinstance(review, dict) or review.get("status") != "passed" or not review.get("reviewer_role") or review.get("conflict_of_interest") not in {"none", "disclosed_and_mitigated"}: errors.append(f"{prefix}.independent_review")
        calibration = case.get("bias_and_calibration", {})
        if not isinstance(calibration, dict) or "prediction_error" not in calibration or "incorrect_or_surprising_findings" not in calibration: errors.append(f"{prefix}.calibration")
        incident = case.get("incident_and_rollback", {})
        if not isinstance(incident, dict) or not isinstance(incident.get("incident_observed"), bool) or not isinstance(incident.get("rollback_tested"), bool): errors.append(f"{prefix}.incident_and_rollback")
        drift = case.get("drift_assessment", {})
        if not isinstance(drift, dict) or drift.get("status") not in {"stable", "drifted", "inconclusive"} or not drift.get("checked_at"): errors.append(f"{prefix}.drift")
    minimum = data.get("minimum_authorized_cases", 3)
    if not isinstance(minimum, int) or minimum < 3: errors.append("invalid_minimum_authorized_cases")
    ready = not errors and len(cases) >= minimum
    if data.get("production_ready") is True and not ready: errors.append("production_claim_without_closed_gate")
    if data.get("production_ready") is not ready: errors.append("production_ready_not_computed_state")
    return {"valid": not errors, "production_ready": ready and not errors, "authorized_cases": len(cases), "errors": errors}

def validate_status() -> list[str]:
    data = json.loads(STATUS.read_text(encoding="utf-8")); errors: list[str] = []
    domains = data.get("domains", []); names = {d.get("skill") for d in domains}
    if names != EXPECTED: errors.append(f"domain_set_mismatch:{sorted(EXPECTED ^ names)}")
    if len(domains) != len(names): errors.append("duplicate_domain")
    for domain in domains:
        skill = domain.get("skill"); cases = domain.get("authorized_real_cases")
        if domain.get("l1") != "passed" or domain.get("l2") != "passed" or domain.get("l3") not in {"passed_automated_gate", "not_passed"}: errors.append(f"{skill}:invalid_l1_l3_state")
        if domain.get("l4") != "passed":
            if domain.get("maturity") != "controlled pilot": errors.append(f"{skill}:non_l4_must_be_controlled_pilot")
            if cases != 0: errors.append(f"{skill}:unverified_nonzero_case_count")
        skill_text = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
        if "`controlled pilot`" not in skill_text: errors.append(f"{skill}:missing_explicit_controlled_pilot_label")
        if str(domain.get("runtime")) not in skill_text: errors.append(f"{skill}:runtime_ledger_mismatch")
        replay_path=ROOT/str(domain.get("replay_manifest",""))
        if not replay_path.is_file(): errors.append(f"{skill}:replay_manifest_missing")
        else:
            replay=json.loads(replay_path.read_text(encoding="utf-8")); actual_cases=replay.get("cases")
            if not isinstance(actual_cases,list): errors.append(f"{skill}:replay_cases_not_array")
            elif len(actual_cases) != cases: errors.append(f"{skill}:replay_case_count_mismatch")
            if domain.get("l4") != "passed" and replay.get("production_ready") is not False: errors.append(f"{skill}:unclosed_replay_claim")
    return errors

if __name__ == "__main__":
    if len(sys.argv) == 1:
        found = validate_status()
        if found: raise SystemExit("Domain maturity validation failed:\n- " + "\n- ".join(found))
        print("Domain maturity validation passed for 9 skills.")
    else:
        path = Path(sys.argv[1]); expected = sys.argv[2] if len(sys.argv) > 2 else None
        result = validate_replay(json.loads(path.read_text(encoding="utf-8")), expected)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit(0 if result["valid"] else 1)
