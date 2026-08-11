#!/usr/bin/env python3
"""Classify semantic, grade, scope, numeric and action differences in a consumer dual-run."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, content_hash, require_fields
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration
from validate_schema import validate_object


CLAIM_ORDER = {"inconclusive": 0, "descriptive": 1, "attributed": 2, "causal": 3, "incremental": 4}


def compare_legacy_f01(value: dict) -> dict:
    migration = value.get("migration") or load_default_migration()
    validate_consumer_migration(migration)
    require_fields(value, ["domain_id", "fixture_id", "run_class", "legacy_result", "f01_result"])
    contract = contract_for(migration, value["domain_id"])
    legacy = value["legacy_result"]
    f01 = value["f01_result"]
    for name, item in (("legacy_result", legacy), ("f01_result", f01)):
        if not isinstance(item, dict):
            raise ECAEError("INVALID_DUAL_RUN_RESULT", f"{name} must be an object")
        require_fields(item, ["claim_class", "grade_label", "scope_key", "numeric_value", "allowed_actions"], name)
        if item["claim_class"] not in CLAIM_ORDER:
            raise ECAEError("INVALID_CLAIM_CLASS", f"{name}.claim_class is invalid")

    differences = []
    blockers = []

    def add(dimension: str, old, new, blocking: bool, reason: str) -> None:
        differences.append({"dimension": dimension, "legacy": old, "f01": new, "blocking": blocking, "reason": reason})
        if blocking:
            blockers.append(reason)

    if legacy["claim_class"] != f01["claim_class"]:
        legacy_overclaim = legacy["claim_class"] in {"causal", "incremental"}
        f01_more_permissive = CLAIM_ORDER[f01["claim_class"]] > CLAIM_ORDER[legacy["claim_class"]]
        blocking = legacy_overclaim or f01_more_permissive
        reason = "legacy_causal_or_incremental_semantics_not_grandfathered" if legacy_overclaim else ("f01_semantics_more_permissive_than_legacy" if f01_more_permissive else "f01_expected_claim_restriction")
        add("claim", legacy["claim_class"], f01["claim_class"], blocking, reason)
    if legacy["grade_label"] != f01["grade_label"]:
        forbidden = legacy["grade_label"] in contract["prohibited_legacy_mappings"] or legacy["grade_label"] not in {"CE0", "CE1", "CE2", "CE3", "CE4", "CE5"}
        add("grade", legacy["grade_label"], f01["grade_label"], forbidden, "legacy_grade_requires_semantic_reassessment" if forbidden else "grade_changed")
    if legacy["scope_key"] != f01["scope_key"]:
        add("scope", legacy["scope_key"], f01["scope_key"], True, "population_platform_country_time_or_treatment_scope_changed")

    old_value, new_value = legacy["numeric_value"], f01["numeric_value"]
    if (old_value is None) != (new_value is None):
        add("numeric", old_value, new_value, True, "numeric_availability_changed")
    elif old_value is not None:
        try:
            tolerance = float(value.get("numeric_tolerance", 1e-9))
            difference = abs(float(old_value) - float(new_value))
        except (TypeError, ValueError) as exc:
            raise ECAEError("INVALID_NUMERIC_COMPARISON", "numeric values and tolerance must be finite numeric values") from exc
        if difference > tolerance:
            add("numeric", old_value, new_value, True, "numeric_difference_exceeds_preregistered_tolerance")

    old_actions, new_actions = set(legacy["allowed_actions"]), set(f01["allowed_actions"])
    if old_actions != new_actions:
        newly_allowed = new_actions - old_actions
        add("action", sorted(old_actions), sorted(new_actions), bool(newly_allowed), "f01_newly_allows_consumer_action" if newly_allowed else "f01_expected_action_restriction")

    dimensions = {item["dimension"] for item in differences if item["blocking"]}
    if not differences:
        classification = "equivalent"
    elif not blockers:
        classification = "expected_restriction"
    elif len(dimensions) > 1:
        classification = "multiple_blocking"
    elif "scope" in dimensions:
        classification = "blocking_scope"
    elif "numeric" in dimensions:
        classification = "blocking_numeric"
    else:
        classification = "blocking_semantic"
    report = {
        "schema_version": "1.0.0",
        "difference_id": f"ECAE-DIFF-{value['domain_id']}-{value['fixture_id']}",
        "domain_id": value["domain_id"],
        "fixture_id": value["fixture_id"],
        "run_class": value["run_class"],
        "difference_class": classification,
        "differences": differences,
        "blocking_reasons": sorted(set(blockers)),
        "requires_consumer_disposition": bool(differences),
        "eligible_for_acceptance": not blockers,
        "legacy_hash": content_hash(legacy),
        "f01_hash": content_hash(f01),
        "external_write": False,
    }
    validate_object(report, "consumer-difference.schema.json", verify_hash=False)
    return report


if __name__ == "__main__":
    cli_main(compare_legacy_f01, __doc__ or "Compare legacy and F01")
