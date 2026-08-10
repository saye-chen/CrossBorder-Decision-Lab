#!/usr/bin/env python3
"""Evaluate a read-only dual-run package and decide whether it may reach owner review."""

from __future__ import annotations

import hashlib
from pathlib import Path

from compare_legacy_f01 import compare_legacy_f01
from ecae_common import ECAEError, cli_main, content_hash, load_json
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration
from validate_schema import validate_object


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PLAN_PATH = ROOT / "integrations/consumer-production-acceptance-plan.json"
REQUIRED_CASES = {"normal", "near_decision_threshold", "negative_or_harm", "expired", "invalidation_triggered", "scope_mismatch", "missing_required_field"}
FAIL_CLOSED_CASES = {"expired", "invalidation_triggered", "scope_mismatch", "missing_required_field"}
SOURCE_TREE_ROOTS = ("agents", "backends", "integrations", "references", "schemas", "scripts")


def f01_source_tree_hash() -> str:
    """Hash executable F01 source and contracts without generated evaluation artifacts."""
    digest = hashlib.sha256()
    paths = [ROOT / "SKILL.md"]
    for relative in SOURCE_TREE_ROOTS:
        paths.extend(path for path in (ROOT / relative).rglob("*") if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts)
    for path in sorted(paths, key=lambda item: item.relative_to(ROOT).as_posix()):
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _plan_row(domain_id: str) -> dict:
    plan = load_json(PLAN_PATH)
    matches = [item for item in plan["domains"] if item["domain_id"] == domain_id]
    if len(matches) != 1:
        raise ECAEError("PRODUCTION_PLAN_DOMAIN_NOT_UNIQUE", "Domain is not uniquely present in the production plan", domain_id)
    return matches[0]


def evaluate_consumer_production_run(value: dict) -> dict:
    package = value.get("package", value)
    if not isinstance(package, dict):
        raise ECAEError("PRODUCTION_RUN_MISSING", "package must be an object")
    validate_object(package, "consumer-production-run.schema.json", verify_hash=False)
    migration = load_default_migration()
    validate_consumer_migration(migration)
    if package["migration_id"] != migration["migration_id"]:
        raise ECAEError("PRODUCTION_RUN_MIGRATION_MISMATCH", "Run is bound to another migration")
    contract = contract_for(migration, package["domain_id"])
    plan = _plan_row(package["domain_id"])
    if not plan["owner_identity"] or package["owner_assignment"]["identity"] != plan["owner_identity"]:
        raise ECAEError("PRODUCTION_RUN_OWNER_IDENTITY_MISMATCH", "Assigned owner identity does not match the production plan")
    if package["owner_assignment"]["role"] != contract["acceptance"]["consumer_owner_role"]:
        raise ECAEError("PRODUCTION_RUN_OWNER_ROLE_MISMATCH", "Assigned owner role does not match the consumer contract")
    if package["code_binding"]["contract_hash"] != content_hash(contract):
        raise ECAEError("PRODUCTION_RUN_CONTRACT_HASH_MISMATCH", "Run does not bind the exact consumer contract")
    adapter = load_json(REPO / plan["adapter_ref"])
    if package["code_binding"]["adapter_hash"] != content_hash(adapter):
        raise ECAEError("PRODUCTION_RUN_ADAPTER_HASH_MISMATCH", "Run does not bind the exact consumer adapter")
    if package["run_class"] == "fixture_non_production" and package["code_binding"]["f01_source_tree_hash"] != f01_source_tree_hash():
        raise ECAEError("FIXTURE_F01_SOURCE_TREE_HASH_MISMATCH", "Fixture run does not bind the current F01 source tree")

    case_ids = [item["case_id"] for item in package["cases"]]
    if len(case_ids) != len(set(case_ids)):
        raise ECAEError("PRODUCTION_RUN_CASE_DUPLICATE", "Case ids must be unique")
    observed_classes = {item["case_class"] for item in package["cases"]}
    if not REQUIRED_CASES <= observed_classes:
        raise ECAEError("PRODUCTION_RUN_CASE_MATRIX_INCOMPLETE", "All seven required production case classes are mandatory", sorted(REQUIRED_CASES - observed_classes))

    results = []
    blocking_cases = []
    disposition_failures = []
    fail_closed_semantic_failures = []
    for item in package["cases"]:
        comparison = compare_legacy_f01({
            "migration": migration,
            "domain_id": package["domain_id"],
            "fixture_id": item["case_id"],
            "run_class": package["run_class"],
            "legacy_result": item["legacy_result"],
            "f01_result": item["f01_result"],
            "numeric_tolerance": package["numeric_tolerance"],
        })
        expected_disposition = "not_required" if comparison["difference_class"] == "equivalent" else "owner_acknowledged_restriction" if comparison["difference_class"] == "expected_restriction" else None
        disposition_valid = expected_disposition is not None and item["difference_disposition"] == expected_disposition
        if not comparison["eligible_for_acceptance"]:
            blocking_cases.append(item["case_id"])
        if not disposition_valid:
            disposition_failures.append(item["case_id"])
        f01_result = item["f01_result"]
        if item["case_class"] in FAIL_CLOSED_CASES:
            safe_claim = f01_result["claim_class"] in {"inconclusive", "descriptive", "attributed"}
            safe_value = f01_result["numeric_value"] is None
            safe_actions = set(f01_result["allowed_actions"]) <= {"review", "descriptive_only", "request_recompute"}
            recompute_present = item["case_class"] not in {"expired", "invalidation_triggered"} or "request_recompute" in f01_result["allowed_actions"]
            if not all((safe_claim, safe_value, safe_actions, recompute_present)):
                fail_closed_semantic_failures.append(item["case_id"])
        results.append({
            "case_id": item["case_id"],
            "case_class": item["case_class"],
            "difference_class": comparison["difference_class"],
            "eligible_for_acceptance": comparison["eligible_for_acceptance"],
            "difference_disposition": item["difference_disposition"],
            "disposition_valid": disposition_valid,
            "legacy_hash": comparison["legacy_hash"],
            "f01_hash": comparison["f01_hash"],
            "blocking_reasons": comparison["blocking_reasons"],
        })

    rollback = package["rollback_drill"]
    rollback_pass = all((
        rollback["executed"],
        rollback["blocked_actions_enforced"],
        rollback["recompute_request_created"],
        not rollback["causal_wording_allowed"],
        rollback["incremental_state"] == "unknown",
        not rollback["business_write_observed"],
    ))
    production_evidence = package["run_class"] == "production_dual_run"
    eligible = production_evidence and not blocking_cases and not disposition_failures and not fail_closed_semantic_failures and rollback_pass
    return {
        "schema_version": "1.0.0",
        "evaluation_id": f"{package['run_id']}-EVALUATION",
        "domain_id": package["domain_id"],
        "run_class": package["run_class"],
        "package_hash": content_hash(package),
        "case_count": len(results),
        "case_results": results,
        "blocking_cases": blocking_cases,
        "disposition_failures": disposition_failures,
        "fail_closed_semantic_failures": fail_closed_semantic_failures,
        "rollback_drill_pass": rollback_pass,
        "eligible_for_owner_acceptance": eligible,
        "next_state": "ready_for_owner_review" if eligible else "blocking_difference" if blocking_cases or fail_closed_semantic_failures else "evidence_incomplete_or_nonproduction",
        "consumer_owner_decision_required": True,
        "producer_self_acceptance_forbidden": True,
        "business_actions_executed": False,
        "external_write": False,
    }


if __name__ == "__main__":
    cli_main(evaluate_consumer_production_run, __doc__ or "Evaluate consumer production run")
