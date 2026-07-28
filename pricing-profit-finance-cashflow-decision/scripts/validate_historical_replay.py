#!/usr/bin/env python3
"""Keep PPFC at controlled pilot until authorized mature replay evidence passes."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "case_id", "case_type", "authorization_reference", "deidentified",
    "decision_as_of_time", "input_hash", "result_hash", "model_version",
    "parameter_snapshot_version", "actual_outcome", "matured_at",
    "concurrent_interventions", "counterfactual_and_alternatives",
    "incident_and_rollback", "independent_review", "drift_assessment",
}
CASE_TYPES = {"pricing", "cash_or_financial_risk", "failure_or_exit"}


def validate(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    cases = data.get("cases", [])
    valid_cases: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for index, case in enumerate(cases):
        missing = sorted(REQUIRED - set(case))
        if missing:
            errors.append(f"case[{index}].missing:{','.join(missing)}")
            continue
        identity = (str(case["input_hash"]), str(case["result_hash"]))
        if identity in identities:
            errors.append(f"case[{index}].duplicate_hash_pair")
        identities.add(identity)
        for field in ("input_hash", "result_hash"):
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(case[field])):
                errors.append(f"case[{index}].invalid:{field}")
        if case["case_type"] not in CASE_TYPES:
            errors.append(f"case[{index}].invalid:case_type")
        if case["deidentified"] is not True:
            errors.append(f"case[{index}].not_deidentified")
        if not str(case["authorization_reference"]).strip():
            errors.append(f"case[{index}].missing_authorization")
        outcome = case["actual_outcome"]
        if not isinstance(outcome, dict) or not outcome.get("measures"):
            errors.append(f"case[{index}].invalid:actual_outcome")
        review = case["independent_review"]
        if (
            not isinstance(review, dict)
            or review.get("status") != "passed"
            or not review.get("reviewer_role")
            or review.get("conflict_of_interest") not in {"none", "disclosed_and_mitigated"}
        ):
            errors.append(f"case[{index}].invalid:independent_review")
        incident = case["incident_and_rollback"]
        if (
            not isinstance(incident, dict)
            or not isinstance(incident.get("incident_observed"), bool)
            or not isinstance(incident.get("rollback_tested"), bool)
        ):
            errors.append(f"case[{index}].invalid:incident_and_rollback")
        drift = case["drift_assessment"]
        if (
            not isinstance(drift, dict)
            or drift.get("status") not in {"stable", "drifted", "inconclusive"}
            or not drift.get("checked_at")
        ):
            errors.append(f"case[{index}].invalid:drift_assessment")
        valid_cases.append(case)

    types = {case.get("case_type") for case in valid_cases}
    ready = (
        len(valid_cases) >= int(data.get("minimum_authorized_cases", 3))
        and CASE_TYPES <= types
        and not errors
    )
    if data.get("production_ready") is True:
        errors.append("production_ready_is_validator_computed")
    return {
        "valid": not errors,
        "production_ready": ready,
        "maturity": "L4 Production" if ready else "controlled pilot",
        "authorized_case_count": len(valid_cases),
        "covered_case_types": sorted(item for item in types if item),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", nargs="?", type=Path,
        default=ROOT / "evaluations/historical-replay-template.json",
    )
    args = parser.parse_args()
    result = validate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
