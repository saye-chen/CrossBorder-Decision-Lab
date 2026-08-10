#!/usr/bin/env python3
"""Build deterministic D01-D13 non-production consumer dual-run preflight evidence."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from ecae_common import canonical_json, content_hash, load_json
from evaluate_consumer_production_run import evaluate_consumer_production_run, f01_source_tree_hash
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PLAN_PATH = ROOT / "integrations/consumer-production-acceptance-plan.json"
OUTPUT_ROOT = ROOT / "evaluations/consumer-production-preflight"
SUMMARY_PATH = ROOT / "evaluations/consumer-production-preflight-summary.json"
CASE_CLASSES = ("normal", "near_decision_threshold", "negative_or_harm", "expired", "invalidation_triggered", "scope_mismatch", "missing_required_field")


def _sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _legacy_hash(contract: dict) -> str:
    digest = hashlib.sha256()
    paths = contract["legacy_assets"]["paths"]
    if not paths:
        return _sha256(contract["legacy_assets"])
    for relative in sorted(paths):
        path = REPO / relative
        payload = path.read_bytes()
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _result(case_class: str, scope_key: str) -> dict:
    if case_class == "normal":
        return {"claim_class": "descriptive", "grade_label": "CE2", "scope_key": scope_key, "numeric_value": 1.0, "allowed_actions": ["review"]}
    if case_class == "near_decision_threshold":
        return {"claim_class": "descriptive", "grade_label": "CE2", "scope_key": scope_key, "numeric_value": 1e-09, "allowed_actions": ["review"]}
    if case_class == "negative_or_harm":
        return {"claim_class": "descriptive", "grade_label": "CE2", "scope_key": scope_key, "numeric_value": -1.0, "allowed_actions": ["review"]}
    actions = ["request_recompute"] if case_class in {"expired", "invalidation_triggered"} else []
    return {"claim_class": "inconclusive", "grade_label": "CE0", "scope_key": scope_key, "numeric_value": None, "allowed_actions": actions}


def build_package(plan_row: dict, migration: dict, source_tree_hash: str) -> dict:
    domain_id = plan_row["domain_id"]
    contract = contract_for(migration, domain_id)
    adapter = load_json(REPO / plan_row["adapter_ref"])
    scope_key = f"US|SIMULATED|{domain_id}|2026-08"
    cases = []
    for index, case_class in enumerate(CASE_CLASSES, 1):
        result = _result(case_class, scope_key)
        case_id = f"{domain_id}-PREFLIGHT-{index:02d}"
        snapshot_hash = _sha256({"domain_id": domain_id, "case_class": case_class, "input_version": "1.0.0"})
        cases.append({
            "case_id": case_id,
            "case_class": case_class,
            "snapshot_hash": snapshot_hash,
            "legacy_result": copy.deepcopy(result),
            "f01_result": copy.deepcopy(result),
            "difference_disposition": "not_required",
            "evidence_refs": [f"synthetic://{domain_id}/legacy/{case_id}", f"synthetic://{domain_id}/f01/{case_id}"],
        })
    return {
        "schema_version": "1.0.0",
        "run_id": f"ECAE-CONSUMER-RUN-{domain_id}-PREFLIGHT-20260810",
        "migration_id": migration["migration_id"],
        "domain_id": domain_id,
        "run_class": "fixture_non_production",
        "execution_mode": "read_only_shadow_dual_run",
        "frozen_before_results": True,
        "owner_assignment": {
            "identity": plan_row["owner_identity"],
            "role": plan_row["consumer_owner_role"],
            "independent_of_ecae_implementation": True,
            "responsibility_accepted": True,
        },
        "data_snapshot": {
            "source_ref": f"synthetic://ecae/consumer-preflight/{domain_id}",
            "snapshot_hash": _sha256({"domain_id": domain_id, "cases": [item["snapshot_hash"] for item in cases]}),
            "authorized": True,
            "read_only": True,
            "captured_at": "2026-08-10T00:00:00Z",
            "maximum_event_time": "2026-08-09T23:59:59Z",
            "business_timezone": "Asia/Shanghai",
        },
        "code_binding": {
            "legacy_code_ref": f"repository://{domain_id}/legacy-assets",
            "legacy_code_hash": _legacy_hash(contract),
            "f01_commit_hash": None,
            "f01_source_tree_hash": source_tree_hash,
            "adapter_hash": content_hash(adapter),
            "contract_hash": content_hash(contract),
            "environment_refs": ["local://python-runtime", "local://f01-source-tree"],
        },
        "numeric_tolerance": 1e-09,
        "cases": cases,
        "rollback_drill": {
            "executed": True,
            "trigger": "expiry",
            "causal_wording_allowed": False,
            "incremental_state": "unknown",
            "blocked_actions_enforced": True,
            "recompute_request_created": True,
            "business_write_observed": False,
            "evidence_refs": [f"synthetic://{domain_id}/rollback/expiry"],
        },
        "business_actions_executed": False,
        "external_write": False,
    }


def build_preflight() -> tuple[list[tuple[dict, dict]], dict]:
    migration = load_default_migration()
    validate_consumer_migration(migration)
    plan = load_json(PLAN_PATH)
    source_tree_hash = f01_source_tree_hash()
    pairs = []
    for row in plan["domains"]:
        package = build_package(row, migration, source_tree_hash)
        evaluation = evaluate_consumer_production_run(package)
        if any((evaluation["blocking_cases"], evaluation["disposition_failures"], evaluation["fail_closed_semantic_failures"], not evaluation["rollback_drill_pass"])):
            raise RuntimeError(f"consumer preflight failed for {row['domain_id']}")
        pairs.append((package, evaluation))
    summary = {
        "schema_version": "1.0.0",
        "preflight_id": "ECAE-CONSUMER-PREFLIGHT-2026-08-10",
        "run_class": "fixture_non_production",
        "status": "passed_non_production",
        "owner_identity": "Miles Chen",
        "domain_count": len(pairs),
        "case_count": sum(evaluation["case_count"] for _, evaluation in pairs),
        "blocking_case_count": sum(len(evaluation["blocking_cases"]) for _, evaluation in pairs),
        "disposition_failure_count": sum(len(evaluation["disposition_failures"]) for _, evaluation in pairs),
        "fail_closed_semantic_failure_count": sum(len(evaluation["fail_closed_semantic_failures"]) for _, evaluation in pairs),
        "rollback_drills_passed": sum(bool(evaluation["rollback_drill_pass"]) for _, evaluation in pairs),
        "fixture_eligible_for_owner_acceptance_count": sum(bool(evaluation["eligible_for_owner_acceptance"]) for _, evaluation in pairs),
        "source_tree_hash": source_tree_hash,
        "domains": [
            {
                "domain_id": package["domain_id"],
                "package_ref": f"evaluations/consumer-production-preflight/{package['domain_id']}-run.json",
                "evaluation_ref": f"evaluations/consumer-production-preflight/{package['domain_id']}-evaluation.json",
                "package_hash": evaluation["package_hash"],
                "case_count": evaluation["case_count"],
                "blocking_cases": evaluation["blocking_cases"],
                "rollback_drill_pass": evaluation["rollback_drill_pass"],
                "production_evidence": False,
            }
            for package, evaluation in pairs
        ],
        "production_evidence_created": False,
        "production_owner_acceptance_created": False,
        "business_actions_executed": False,
        "external_write": False,
    }
    return pairs, summary


def main() -> int:
    pairs, summary = build_preflight()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for package, evaluation in pairs:
        domain_id = package["domain_id"]
        (OUTPUT_ROOT / f"{domain_id}-run.json").write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (OUTPUT_ROOT / f"{domain_id}-evaluation.json").write_text(json.dumps(evaluation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
