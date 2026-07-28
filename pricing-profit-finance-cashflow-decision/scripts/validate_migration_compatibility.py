#!/usr/bin/env python3
"""Validate PPFC migration inventory and deterministic equivalence fixtures."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from calculate_pricing_economics import calculate_scenario


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIMENSIONS = {
    "subject_id", "currency", "tax_basis", "quantity_unit",
    "business_as_of_time", "parameter_snapshot_version", "model_version",
}
EXPECTED_DOMAINS = {"ERDG", "CIDM", "AAMO", "LIFD", "CIG", "CAPM", "MBCM", "PLCO"}
ALLOWED_MIGRATION_STATUSES = {"adapter_registered", "adapter_ready", "dual_run_equivalent", "not_migrated"}


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("retirement_allowed") is not False:
        errors.append("RETIREMENT_MUST_REMAIN_BLOCKED")
    if set(payload.get("comparison_dimensions", [])) != REQUIRED_DIMENSIONS:
        errors.append("COMPARISON_DIMENSIONS_INCOMPLETE")
    consumers = payload.get("consumers", [])
    if {item.get("domain") for item in consumers} != EXPECTED_DOMAINS:
        errors.append("CONSUMER_INVENTORY_INCOMPLETE")
    if any(item.get("retirement_allowed") is not False for item in consumers):
        errors.append("CONSUMER_RETIREMENT_PREMATURE")
    if any(item.get("migration_status") not in ALLOWED_MIGRATION_STATUSES for item in consumers):
        errors.append("UNSUPPORTED_MIGRATION_CLAIM")
    if payload.get("rollback", {}).get("external_write") is not False:
        errors.append("ROLLBACK_EXTERNAL_WRITE_FORBIDDEN")

    seen: set[str] = set()
    for case in payload.get("equivalence_cases", []):
        case_id = case.get("case_id")
        if not case_id or case_id in seen:
            errors.append("DUPLICATE_OR_MISSING_EQUIVALENCE_CASE")
            continue
        seen.add(case_id)
        missing = REQUIRED_DIMENSIONS - set(case)
        if missing:
            errors.append(f"{case_id}:MISSING_DIMENSIONS:{','.join(sorted(missing))}")
            continue
        result = calculate_scenario(case["input"])
        actual = {
            "recognized_net_revenue": result["revenue_bridge"]["recognized_net_revenue"],
            "platform_fee": result["fees"]["platform"],
            "pre_ad_contribution": result["profit_bridge"]["pre_ad_contribution"],
            "operating_profit": result["profit_bridge"]["operating_profit"],
        }
        if actual != case["expected"]:
            errors.append(f"{case_id}:EQUIVALENCE_DIFFERENCE")
    if len(seen) < 2:
        errors.append("INSUFFICIENT_EQUIVALENCE_CASES")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest", nargs="?",
        type=Path,
        default=ROOT / "evaluations/migration-compatibility.json",
    )
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        print("PPFC_MIGRATION=BLOCKED")
        for error in errors:
            print(error)
        return 1
    print("PPFC_MIGRATION=PASS")
    print(f"consumers={len(payload['consumers'])}")
    print(f"equivalence_cases={len(payload['equivalence_cases'])}")
    print("retirement_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
