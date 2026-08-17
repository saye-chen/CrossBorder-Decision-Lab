#!/usr/bin/env python3
"""Validate executable L3 audit coverage and standalone professional reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_professional_report import validate as validate_report


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIMENSIONS = {
    "single_skill", "multi_skill", "report_depth", "scenario_breadth",
    "complex_scenario", "continuous_challenge", "extreme_scenario", "stress_test",
}
REQUIRED_SCENARIO_TYPES = REQUIRED_DIMENSIONS - {"report_depth", "scenario_breadth"}
REQUIRED_SCENARIO_COUNT = 17
def validate(matrix: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if matrix.get("scope") != "synthetic_and_deterministic_only":
        errors.append("L3_SCOPE_MUST_BE_SYNTHETIC")
    if matrix.get("real_case_calibration_deferred") is not True:
        errors.append("REAL_CASE_CALIBRATION_MUST_REMAIN_DEFERRED")
    if matrix.get("production_claim_allowed") is not False:
        errors.append("PRODUCTION_CLAIM_FORBIDDEN")

    dimensions = matrix.get("dimensions", [])
    dimension_ids = {item.get("id") for item in dimensions}
    if dimension_ids != REQUIRED_DIMENSIONS:
        errors.append("AUDIT_DIMENSION_COVERAGE_INCOMPLETE")
    scenarios = matrix.get("scenarios", [])
    if len(scenarios) != REQUIRED_SCENARIO_COUNT:
        errors.append(f"AUDIT_SCENARIO_COUNT_MUST_BE_{REQUIRED_SCENARIO_COUNT}")
    scenario_ids = [item.get("id") for item in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("AUDIT_SCENARIO_ID_DUPLICATE")
    scenario_index = {item.get("id"): item for item in scenarios}
    for item in dimensions:
        dimension = item.get("id", "UNKNOWN")
        if item.get("required") is not True or not item.get("evidence"):
            errors.append(f"{dimension}:AUDIT_EVIDENCE_INCOMPLETE")
        for scenario_id in item.get("scenarios", []):
            if scenario_id not in scenario_index:
                errors.append(f"{dimension}:UNKNOWN_SCENARIO:{scenario_id}")
        for evidence in item.get("evidence", []):
            if not (ROOT / evidence).is_file():
                errors.append(f"{dimension}:MISSING_EVIDENCE:{evidence}")
    covered_types = {item.get("type") for item in scenarios}
    if not REQUIRED_SCENARIO_TYPES <= covered_types:
        errors.append("AUDIT_SCENARIO_TYPE_INCOMPLETE")

    report_registry = matrix.get("report_types", [])
    if len(report_registry) != 3:
        errors.append("REPORT_TYPE_REGISTRY_MUST_HAVE_THREE")
    if len({item.get("type") for item in report_registry}) != len(report_registry):
        errors.append("REPORT_TYPE_REGISTRY_DUPLICATE")
    if len({item.get("artifact") for item in report_registry}) != len(report_registry):
        errors.append("REPORT_ARTIFACT_REGISTRY_DUPLICATE")

    valid_reports = 0
    report_types: set[str] = set()
    for registered in report_registry:
        relative = registered.get("artifact", "")
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"MISSING_GOLDEN_REPORT:{relative}")
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        try:
            validate_report(report)
        except Exception as exc:
            errors.append(f"INVALID_GOLDEN_REPORT:{relative}:{exc}")
            continue
        valid_reports += 1
        report_types.add(report["report_type"])
        if report.get("report_type") != registered.get("type"):
            errors.append(f"REPORT_TYPE_REGISTRY_MISMATCH:{relative}")
        scope = report.get("scope", {})
        if not {"country", "platform", "currency", "tax_basis"} <= set(scope):
            errors.append(f"REPORT_SCOPE_INCOMPLETE:{relative}")
        if len(report.get("candidates", [])) < 3:
            errors.append(f"REPORT_SCENARIO_COMPARISON_INCOMPLETE:{relative}")
        if not report.get("sensitivity", {}).get("flip_condition"):
            errors.append(f"REPORT_FLIP_CONDITION_MISSING:{relative}")
        for action in report.get("actions", []):
            if not {"action", "owner", "status", "reversibility"} <= set(action):
                errors.append(f"REPORT_ACTION_CONTRACT_INCOMPLETE:{relative}")
    if len(report_types) != len(report_registry):
        errors.append("GOLDEN_REPORT_TYPES_NOT_DISTINCT")

    return {
        "valid": not errors,
        "dimensions_passed": len(dimension_ids & REQUIRED_DIMENSIONS) if not errors else 0,
        "scenario_count": len(scenarios),
        "golden_reports_valid": valid_reports,
        "l3_expert": not errors,
        "l4_status": "controlled pilot",
        "errors": errors,
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    matrix = json.loads((ROOT / "evaluations/l3-audit-matrix.json").read_text(encoding="utf-8"))
    result = validate(matrix)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
