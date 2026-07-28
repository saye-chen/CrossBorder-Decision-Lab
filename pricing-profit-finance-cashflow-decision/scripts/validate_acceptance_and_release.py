#!/usr/bin/env python3
"""Validate technical consumer acceptance, rollback drills, and PPFC maturity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOMAINS = {"CIDM", "AAMO", "CIG", "LIFD", "CAPM", "MBCM", "PLCO"}
ROLLBACK_FIELDS = {
    "source_reader_retained", "previous_contract_readable", "previous_result_recomputed",
    "new_result_invalidated", "business_action_unchanged", "lineage_preserved",
}


def validate_acceptance(data: dict[str, Any], rollback: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("retirement_allowed") is not False:
        errors.append("RETIREMENT_PREMATURE")
    if data.get("external_write") is not False:
        errors.append("ACCEPTANCE_EXTERNAL_WRITE_FORBIDDEN")
    if data.get("acceptance_kind") != "computed_technical_compatibility":
        errors.append("ACCEPTANCE_KIND_INVALID")
    if data.get("business_execution_acceptance") is not False:
        errors.append("BUSINESS_EXECUTION_CANNOT_BE_AUTO_ACCEPTED")
    items = data.get("acceptances", [])
    if {item.get("domain") for item in items} != DOMAINS:
        errors.append("ACCEPTANCE_DOMAIN_INVENTORY_INCOMPLETE")
    drills = {item["drill_id"]: item for item in rollback.get("drills", [])}
    for item in items:
        domain = item.get("domain", "UNKNOWN")
        if not item.get("scope") or not item.get("dual_run_fixture") or not item.get("retained_sovereignty"):
            errors.append(f"{domain}:ACCEPTANCE_SCOPE_INCOMPLETE")
        drill = drills.get(item.get("rollback_drill"))
        if drill is None or drill.get("domain") != domain or drill.get("status") != "passed":
            errors.append(f"{domain}:ROLLBACK_DRILL_NOT_PASSED")
        if item.get("status") != "technically_accepted":
            errors.append(f"{domain}:TECHNICAL_ACCEPTANCE_INCOMPLETE")
        if item.get("dual_run_status") != "equivalent":
            errors.append(f"{domain}:DUAL_RUN_NOT_EQUIVALENT")
        if item.get("sovereignty_check") != "passed":
            errors.append(f"{domain}:SOVEREIGNTY_CHECK_NOT_PASSED")
        forbidden_human_fields = {
            "accepted_by", "accepted_role", "accepted_at", "reviewer_identity",
            "reviewer_role", "conflict_of_interest",
        }
        if forbidden_human_fields & set(item):
            errors.append(f"{domain}:HUMAN_SIGNATURE_NOT_PART_OF_TECHNICAL_ACCEPTANCE")
    return errors


def validate_rollback(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("external_write") is not False:
        errors.append("ROLLBACK_EXTERNAL_WRITE_FORBIDDEN")
    drills = data.get("drills", [])
    if {item.get("domain") for item in drills} != DOMAINS:
        errors.append("ROLLBACK_DOMAIN_INVENTORY_INCOMPLETE")
    if len({item.get("drill_id") for item in drills}) != len(drills):
        errors.append("ROLLBACK_DRILL_ID_DUPLICATE")
    for item in drills:
        domain = item.get("domain", "UNKNOWN")
        if item.get("status") != "passed":
            errors.append(f"{domain}:ROLLBACK_NOT_PASSED")
        for field in ROLLBACK_FIELDS:
            if item.get(field) is not True:
                errors.append(f"{domain}:ROLLBACK_CONTROL_FAILED:{field}")
    return errors


def validate_l3(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    review = data.get("substantive_review", {})
    if data.get("l3_passed") is True:
        if (
            data.get("review_status") != "passed"
            or review.get("status") != "passed"
            or data.get("review_method") != "isolated_substantive_evidence_review"
            or data.get("human_signature_required") is not False
            or review.get("evidence_isolated_from_claim") is not True
            or review.get("dimensions_reviewed") != len(data.get("required_review_dimensions", []))
            or review.get("p0_open") != 0
            or review.get("p1_open") != 0
            or review.get("decision") != "approved_for_l3_controlled_pilot"
        ):
            errors.append("L3_CANNOT_PASS_WITHOUT_SUBSTANTIVE_EVIDENCE_REVIEW")
    elif data.get("review_status") == "passed":
        errors.append("L3_REVIEW_STATUS_CONTRADICTS_GATE")
    if data.get("l4_status") != "controlled pilot":
        errors.append("L4_MUST_REMAIN_CONTROLLED_PILOT")
    return errors


def compute(acceptance: dict[str, Any], rollback: dict[str, Any], l3: dict[str, Any]) -> dict[str, Any]:
    errors = (
        validate_rollback(rollback)
        + validate_acceptance(acceptance, rollback)
        + validate_l3(l3)
    )
    accepted = sum(item.get("status") == "technically_accepted" for item in acceptance.get("acceptances", []))
    rollback_passed = sum(item.get("status") == "passed" for item in rollback.get("drills", []))
    blockers = []
    if accepted != 7:
        blockers.append("CONSUMER_TECHNICAL_ACCEPTANCE_INCOMPLETE")
    if rollback_passed != 7:
        blockers.append("ROLLBACK_DRILL_INCOMPLETE")
    if l3.get("l3_passed") is not True:
        blockers.append("L3_SUBSTANTIVE_REVIEW_PENDING")
    return {
        "valid": not errors,
        "release_ready": not errors and not blockers,
        "production_ready": False,
        "accepted_consumers": accepted,
        "rollback_drills_passed": rollback_passed,
        "l3_passed": l3.get("l3_passed") is True,
        "maturity": "L3 Expert / controlled pilot" if not errors and not blockers else "L3 pending / controlled pilot",
        "blockers": blockers,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    acceptance = json.loads((ROOT / "evaluations/consumer-acceptance.json").read_text(encoding="utf-8"))
    rollback = json.loads((ROOT / "evaluations/rollback-drill.json").read_text(encoding="utf-8"))
    l3 = json.loads((ROOT / "evaluations/l3-review-package.json").read_text(encoding="utf-8"))
    result = compute(acceptance, rollback, l3)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
