#!/usr/bin/env python3
"""Prevent CAPM production claims without authorized mature historical replays."""
from __future__ import annotations
import argparse
import re
from capm_common import emit, load_json


REQUIRED = {"case_id", "authorization_reference", "deidentified", "input_hash", "result_hash", "actual_outcome",
            "maturity_checked_at", "independent_review", "bias_and_calibration", "failure_or_exit_covered"}


def validate(data: dict) -> dict:
    cases = data.get("cases", [])
    errors = []
    for idx, case in enumerate(cases):
        missing = sorted(REQUIRED - set(case))
        if missing: errors.append(f"case[{idx}].missing:{','.join(missing)}")
        for field in ("input_hash", "result_hash"):
            value = str(case.get(field, ""))
            if not re.fullmatch(r"[0-9a-f]{64}", value): errors.append(f"case[{idx}].invalid:{field}")
        if not case.get("deidentified"): errors.append(f"case[{idx}].not_deidentified")
        if not str(case.get("authorization_reference", "")).strip(): errors.append(f"case[{idx}].invalid:authorization_reference")
        review = case.get("independent_review")
        if not isinstance(review, dict) or review.get("status") != "passed" or not review.get("reviewer_role") or review.get("conflict_of_interest") not in {"none", "disclosed_and_mitigated"}:
            errors.append(f"case[{idx}].invalid:independent_review")
        outcome = case.get("actual_outcome")
        if not isinstance(outcome, dict) or not outcome.get("matured_at") or not outcome.get("measures"):
            errors.append(f"case[{idx}].invalid:actual_outcome")
        calibration = case.get("bias_and_calibration")
        if not isinstance(calibration, dict) or not calibration.get("prediction_error"):
            errors.append(f"case[{idx}].invalid:bias_and_calibration")
    domains = {case.get("case_type") for case in cases}
    unique = {(c.get("input_hash"), c.get("result_hash")) for c in cases}
    if len(unique) != len(cases): errors.append("duplicate_replay_cases")
    ready = len(cases) >= 3 and {"creator", "affiliate"}.issubset(domains) and any(c.get("failure_or_exit_covered") for c in cases) and not errors
    if data.get("production_ready") and not ready:
        errors.append("production_claim_without_replay_gate")
    return {"valid": not errors, "production_ready": ready, "maturity": "L4 Production" if ready else "controlled pilot",
            "authorized_case_count": len(cases), "errors": errors}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); result = validate(load_json(a.input)); emit(result); raise SystemExit(0 if result["valid"] else 1)
