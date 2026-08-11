#!/usr/bin/env python3
"""Validate PPFC's D06 consumer adapter against the authoritative F01 contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for path in (REPO / "pricing-profit-finance-cashflow-decision" / "scripts", REPO / "experiment-causal-assessment" / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ppfc_common import canonical_hash
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration


def validate() -> list[str]:
    adapter = json.loads((HERE / "adapter.json").read_text(encoding="utf-8"))
    acceptance = json.loads((HERE / "acceptance.json").read_text(encoding="utf-8"))
    migration = load_default_migration()
    errors: list[str] = []
    try:
        validate_consumer_migration(migration)
        contract = contract_for(migration, "D06")
    except Exception as exc:
        return [f"authoritative_migration:{exc}"]
    exact = {
        "domain_id": "D06", "consumer": contract["skill"], "migration_id": migration["migration_id"],
        "consumer_contract_version": contract["contract_version"], "unknown_incremental_value_policy": "unknown_never_zero_fill",
        "noncausal_fallback_policy": "explicit_noncausal_scenario_only", "external_write": False,
        "independent_owner_accepted": False, "production_dual_run_completed": False,
    }
    for field, expected in exact.items():
        if adapter.get(field) != expected:
            errors.append(f"adapter.{field}:expected:{expected!r}")
    contracted = {item["use"]: item["minimum_grade"] for item in contract["use_requirements"]}
    if set(adapter.get("allowed_uses", [])) != set(contracted) or adapter.get("minimum_grade_by_use") != contracted:
        errors.append("adapter.allowed_uses:contract_mismatch")
    if not set(contract["retained_sovereignty"]) <= set(adapter.get("retained_sovereignty", [])):
        errors.append("adapter.retained_sovereignty:incomplete")
    if not set(adapter.get("retained_sovereignty", [])) <= set(adapter.get("forbidden_writeback", [])):
        errors.append("adapter.forbidden_writeback:sovereignty_gap")
    if not set(contract["prohibited_legacy_mappings"]) <= set(adapter.get("prohibited_legacy_mappings", [])):
        errors.append("adapter.prohibited_legacy_mappings:incomplete")
    for field in ("handoff_schema", "receipt_schema", "consumer_validator", "consumer_calculator"):
        path = adapter.get(field)
        if not isinstance(path, str) or not (REPO / path).is_file():
            errors.append(f"adapter.{field}:missing")
    if acceptance.get("adapter_hash") != canonical_hash(adapter):
        errors.append("acceptance.adapter_hash:mismatch")
    if acceptance.get("automated_contract_accepted") is not True or acceptance.get("local_fixture_status") != "verified":
        errors.append("acceptance.local_contract:not_verified")
    if acceptance.get("production_dual_run_completed") is not False or acceptance.get("independent_owner_accepted") is not False:
        errors.append("acceptance.false_production_or_owner_claim")
    if acceptance.get("controlled_pilot_owner_accepted") is not True or acceptance.get("owner_acceptance_status") != "conditionally_accepted_controlled_pilot":
        errors.append("acceptance.controlled_pilot_owner_state:not_accepted")
    if acceptance.get("signed_owner_acceptance_ref") != contract["acceptance"]["signed_record_ref"]:
        errors.append("acceptance.controlled_pilot_owner_record:mismatch")
    if acceptance.get("production_ready") is not False:
        errors.append("acceptance.false_production_claim")
    if acceptance.get("external_write") is not False or not all(acceptance.get("checks", {}).values()):
        errors.append("acceptance.checks:incomplete")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        raise SystemExit("PPFC_ECAE_CONSUMER_ADAPTER=BLOCKED\n- " + "\n- ".join(failures))
    print("PPFC_ECAE_CONSUMER_ADAPTER=PASS local_fixture=verified controlled_pilot_owner_acceptance=accepted production_dual_run=false")
