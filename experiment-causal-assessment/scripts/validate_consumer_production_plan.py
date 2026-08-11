#!/usr/bin/env python3
"""Validate the D01-D13 production-acceptance plan without inventing production evidence."""

from __future__ import annotations

from pathlib import Path

from ecae_common import ECAEError, cli_main, content_hash, load_json
from evaluate_consumer_production_run import evaluate_consumer_production_run
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration
from validate_schema import validate_object


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
EXPECTED = [f"D{index:02d}" for index in range(1, 14)]


def validate_consumer_production_plan(value: dict) -> dict:
    plan = value.get("plan", value)
    if not isinstance(plan, dict):
        raise ECAEError("PRODUCTION_PLAN_MISSING", "plan must be an object")
    validate_object(plan, "consumer-production-plan.schema.json", verify_hash=False)
    migration = load_default_migration()
    validate_consumer_migration(migration)
    if plan["migration_id"] != migration["migration_id"]:
        raise ECAEError("PRODUCTION_PLAN_MIGRATION_MISMATCH", "Plan is bound to another migration")
    domains = [item["domain_id"] for item in plan["domains"]]
    if domains != EXPECTED:
        raise ECAEError("PRODUCTION_PLAN_DOMAIN_SET_MISMATCH", "Plan must contain D01-D13 exactly and in order", domains)

    for item in plan["domains"]:
        contract = contract_for(migration, item["domain_id"])
        expected = {
            "skill": contract["skill"],
            "consumer_owner_role": contract["acceptance"]["consumer_owner_role"],
            "contract_version": contract["contract_version"],
            "contract_content_hash": content_hash(contract),
            "local_acceptance_ref": contract["dual_run"]["local_fixture_ref"],
        }
        mismatches = {field: {"expected": wanted, "observed": item.get(field)} for field, wanted in expected.items() if item.get(field) != wanted}
        if mismatches:
            raise ECAEError("PRODUCTION_PLAN_CONTRACT_MISMATCH", "Production plan does not bind the exact consumer contract", {"domain_id": item["domain_id"], "mismatches": mismatches})
        for field in ("adapter_ref", "local_acceptance_ref"):
            if not (REPO / item[field]).is_file():
                raise ECAEError("PRODUCTION_PLAN_ARTIFACT_MISSING", "Plan references a missing local artifact", {"domain_id": item["domain_id"], "field": field, "path": item[field]})
        if item["readiness_status"] == "waiting_owner_and_production_snapshot":
            if item["owner_identity"] is not None or any(item[field] is not None for field in ("production_snapshot_ref", "production_run_package_ref", "difference_evidence_ref", "rollback_evidence_ref", "signed_acceptance_ref")):
                raise ECAEError("PRODUCTION_PLAN_FALSE_EVIDENCE", "Waiting status cannot carry owner or production evidence", item["domain_id"])
        fixture_refs = (item["fixture_run_package_ref"], item["fixture_evaluation_ref"])
        if item["fixture_preflight_status"] == "pending" and any(fixture_refs):
            raise ECAEError("PRODUCTION_PLAN_FALSE_FIXTURE_EVIDENCE", "Pending fixture preflight cannot carry evidence refs", item["domain_id"])
        if item["fixture_preflight_status"] == "passed":
            if not all(fixture_refs):
                raise ECAEError("PRODUCTION_PLAN_FIXTURE_EVIDENCE_MISSING", "Passed fixture preflight requires run and evaluation evidence", item["domain_id"])
            package_path, evaluation_path = (REPO / ref for ref in fixture_refs)
            if not package_path.is_file() or not evaluation_path.is_file():
                raise ECAEError("PRODUCTION_PLAN_FIXTURE_ARTIFACT_MISSING", "Fixture preflight references a missing artifact", item["domain_id"])
            package = load_json(package_path)
            evaluation = load_json(evaluation_path)
            observed = evaluate_consumer_production_run(package)
            if evaluation != observed:
                raise ECAEError("PRODUCTION_PLAN_FIXTURE_EVALUATION_DRIFT", "Stored fixture evaluation does not match deterministic replay", item["domain_id"])
            fixture_pass = all((
                package["domain_id"] == item["domain_id"],
                package["run_class"] == "fixture_non_production",
                package["owner_assignment"]["identity"] == item["owner_identity"],
                not evaluation["blocking_cases"],
                not evaluation["disposition_failures"],
                not evaluation["fail_closed_semantic_failures"],
                evaluation["rollback_drill_pass"],
                not evaluation["eligible_for_owner_acceptance"],
                evaluation["next_state"] == "evidence_incomplete_or_nonproduction",
                not evaluation["business_actions_executed"],
                not evaluation["external_write"],
            ))
            if not fixture_pass:
                raise ECAEError("PRODUCTION_PLAN_FIXTURE_PREFLIGHT_FAILED", "Fixture preflight did not pass all non-production controls", item["domain_id"])
        if item["readiness_status"] == "fixture_preflight_passed_waiting_production_snapshot":
            if not item["owner_identity"] or item["fixture_preflight_status"] != "passed" or item["production_snapshot_ref"] is not None:
                raise ECAEError("PRODUCTION_PLAN_READINESS_STATE_MISMATCH", "Fixture-passed waiting state requires an owner, passed fixture, and no production snapshot", item["domain_id"])

    gates = plan["completion_gate"]
    derived = {
        "owners_assigned": all(item["owner_identity"] for item in plan["domains"]),
        "fixture_preflights_passed": all(item["fixture_preflight_status"] == "passed" and item["fixture_run_package_ref"] and item["fixture_evaluation_ref"] for item in plan["domains"]),
        "production_snapshots_bound": all(item["production_snapshot_ref"] for item in plan["domains"]),
        "production_dual_runs_completed": all(item["production_run_package_ref"] for item in plan["domains"]),
        "differences_dispositioned": all(item["difference_evidence_ref"] for item in plan["domains"]),
        "rollback_drills_passed": all(item["rollback_evidence_ref"] for item in plan["domains"]),
        "owner_acceptances_signed": all(item["signed_acceptance_ref"] for item in plan["domains"]),
    }
    derived["l4_production_acceptance_complete"] = all(derived.values())
    mismatch = {key: {"declared": gates[key], "derived": expected} for key, expected in derived.items() if gates[key] is not expected}
    if mismatch:
        raise ECAEError("PRODUCTION_PLAN_GATE_MISMATCH", "Plan gates must be derived from evidence references", mismatch)
    return {
        "valid": True,
        "domain_count": len(domains),
        "wave_1": [item["domain_id"] for item in plan["domains"] if item["priority_wave"] == 1],
        "wave_2": [item["domain_id"] for item in plan["domains"] if item["priority_wave"] == 2],
        "owners_assigned": sum(bool(item["owner_identity"]) for item in plan["domains"]),
        "fixture_preflights_passed": sum(item["fixture_preflight_status"] == "passed" for item in plan["domains"]),
        "production_runs_bound": sum(bool(item["production_run_package_ref"]) for item in plan["domains"]),
        "l4_production_acceptance_complete": gates["l4_production_acceptance_complete"],
        "external_write": False,
    }


if __name__ == "__main__":
    cli_main(validate_consumer_production_plan, __doc__ or "Validate consumer production plan")
