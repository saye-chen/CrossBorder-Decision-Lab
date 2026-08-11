#!/usr/bin/env python3
"""Fail-closed validation for the D01-D13 ECAE consumer migration contract."""

from __future__ import annotations

import json
from pathlib import Path

from ecae_common import ECAEError, cli_main, content_hash
from validate_schema import validate_object


F01_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = F01_ROOT.parent
DEFAULT_MIGRATION = F01_ROOT / "integrations" / "consumer-migration.json"
DOMAIN_REGISTRY = REPO_ROOT / "governance" / "domain-architecture-registry.json"
EXPECTED_DOMAINS = [f"D{i:02d}" for i in range(1, 14)]


def load_default_migration() -> dict:
    return json.loads(DEFAULT_MIGRATION.read_text(encoding="utf-8"))


def contract_for(migration: dict, domain_id: str) -> dict:
    matches = [item for item in migration.get("consumers", []) if item.get("domain_id") == domain_id]
    if len(matches) != 1:
        raise ECAEError("CONSUMER_CONTRACT_NOT_UNIQUE", "Expected one consumer contract", {"domain_id": domain_id, "count": len(matches)})
    return matches[0]


def _profile_for(migration: dict, profile_id: str) -> dict:
    matches = [item for item in migration.get("mapping_profiles", []) if item.get("profile_id") == profile_id]
    if len(matches) != 1:
        raise ECAEError("MAPPING_PROFILE_NOT_UNIQUE", "Expected one mapping profile", {"profile_id": profile_id, "count": len(matches)})
    return matches[0]


def validate_consumer_migration(value: dict) -> dict:
    migration = value.get("migration", value)
    if not isinstance(migration, dict):
        raise ECAEError("MISSING_MIGRATION", "migration must be an object")
    validate_object(migration, "consumer-migration.schema.json", verify_hash=False)

    domains = [item["domain_id"] for item in migration["consumers"]]
    if domains != EXPECTED_DOMAINS:
        raise ECAEError("CONSUMER_SET_MISMATCH", "Consumers must be D01-D13 exactly and in order", {"actual": domains})
    if len(set(domains)) != len(domains):
        raise ECAEError("DUPLICATE_CONSUMER", "Consumer contracts must be unique")

    registry = json.loads(DOMAIN_REGISTRY.read_text(encoding="utf-8"))
    authoritative = {item["domain_id"]: item for item in registry["domains"] if item["domain_id"] in EXPECTED_DOMAINS}
    handoff_schema = json.loads((F01_ROOT / "schemas" / "causal-handoff.schema.json").read_text(encoding="utf-8"))
    handoff_required = set(handoff_schema["required"])
    forbidden_grade_tokens = {"C0", "C1", "C2", "C3", "CE4", "CE5", "E6", "E7", "attributed", "incremental"}
    fixture_count = 0
    rollback_count = 0
    controlled_pilot_acceptance_count = 0

    for contract in migration["consumers"]:
        domain_id = contract["domain_id"]
        source = authoritative.get(domain_id)
        if source is None:
            raise ECAEError("DOMAIN_REGISTRY_MISSING", "Consumer is absent from domain registry", domain_id)
        if contract["skill"] != source["skill"] or contract["runtime_prefix"] != source["runtime_prefix"]:
            raise ECAEError(
                "DOMAIN_BINDING_MISMATCH",
                "Consumer skill/runtime differs from the authoritative domain registry",
                {"domain_id": domain_id, "contract": [contract["skill"], contract["runtime_prefix"]], "registry": [source["skill"], source["runtime_prefix"]]},
            )
        if source.get("external_write_authority") is not False or contract["external_write"] is not False:
            raise ECAEError("EXTERNAL_WRITE_AUTHORITY_VIOLATION", "Migration cannot grant external-write authority", domain_id)

        assets = contract["legacy_assets"]
        if assets["paths"] and assets["absence_reason"] is not None:
            raise ECAEError("LEGACY_ASSET_STATE_CONFLICT", "Present legacy assets cannot also have an absence reason", domain_id)
        if not assets["paths"] and not assets["absence_reason"]:
            raise ECAEError("LEGACY_ASSET_ABSENCE_UNEXPLAINED", "Empty legacy asset inventory requires a reason", domain_id)
        missing_assets = [path for path in assets["paths"] if not (REPO_ROOT / path).is_file()]
        if missing_assets:
            raise ECAEError("LEGACY_ASSET_MISSING", "Declared legacy assets do not exist", {"domain_id": domain_id, "paths": missing_assets})

        profile = _profile_for(migration, contract["mapping_profile"])
        required = set(profile["required_fields"])
        mapped = {item["source"] for item in profile["field_mappings"]}
        if required != mapped:
            raise ECAEError("FIELD_MAPPING_INCOMPLETE", "Every profile-required field must have exactly one mapping", {"profile_id": profile["profile_id"], "missing": sorted(required - mapped), "extra": sorted(mapped - required)})
        if not required <= handoff_required:
            raise ECAEError("HANDOFF_FIELD_UNKNOWN", "Mapping profile names fields outside the causal handoff contract", sorted(required - handoff_required))
        if len(mapped) != len(profile["field_mappings"]):
            raise ECAEError("DUPLICATE_FIELD_MAPPING", "Mapping profile source fields must be unique", profile["profile_id"])
        if profile["accepted_schema_versions"] != ["1.0.0"]:
            raise ECAEError("UNFROZEN_HANDOFF_VERSION", "WP11 accepts only the reviewed causal handoff schema version", profile["accepted_schema_versions"])

        uses = [item["use"] for item in contract["use_requirements"]]
        if len(uses) != len(set(uses)):
            raise ECAEError("DUPLICATE_CONSUMER_USE", "Use requirements must be unique", domain_id)
        if any(item["minimum_grade"] in {"CE4", "CE5"} and item["fallback_use"] != "descriptive_only" for item in contract["use_requirements"]):
            raise ECAEError("UNSAFE_GRADE_FALLBACK", "Causal/incremental uses must degrade to descriptive_only", domain_id)
        if contract["legacy_automatic_ceiling"] != "CE0" or contract["legacy_reassessment_ceiling"] in {"CE4", "CE5"}:
            raise ECAEError("LEGACY_AUTO_UPGRADE", "Legacy evidence cannot be grandfathered into CE4/CE5", domain_id)
        tokens = set(contract["prohibited_legacy_mappings"])
        if not tokens or not any(any(token in item for token in forbidden_grade_tokens) for item in tokens):
            raise ECAEError("LEGACY_MAPPING_DENYLIST_WEAK", "Each domain needs an explicit legacy semantic denylist", domain_id)
        if not set(contract["retained_sovereignty"]) <= set(contract["forbidden_writeback"]):
            raise ECAEError("SOVEREIGNTY_WRITEBACK_GAP", "All retained sovereignty must be forbidden writeback", domain_id)

        acceptance = contract["acceptance"]
        if acceptance["status"] == "pending_consumer_owner" and (acceptance["signed_record_ref"] is not None or acceptance["accepted_uses"]):
            raise ECAEError("FALSE_ACCEPTANCE_EVIDENCE", "Pending acceptance cannot carry a signature or accepted uses", domain_id)
        if acceptance["status"] in {"accepted", "conditionally_accepted", "rejected"} and acceptance["signed_record_ref"] is None:
            raise ECAEError("SIGNED_ACCEPTANCE_MISSING", "A terminal consumer decision requires a signed record", domain_id)
        if acceptance["status"] in {"accepted", "conditionally_accepted"}:
            record_path = REPO_ROOT / acceptance["signed_record_ref"]
            if not record_path.is_file():
                raise ECAEError("SIGNED_ACCEPTANCE_MISSING", "Controlled-pilot acceptance record does not exist", domain_id)
            record = json.loads(record_path.read_text(encoding="utf-8"))
            validate_object(record, "consumer-acceptance.schema.json")
            if record["domain_id"] != domain_id or record["migration_id"] != migration["migration_id"]:
                raise ECAEError("ACCEPTANCE_BINDING_MISMATCH", "Acceptance record is bound to another domain or migration", domain_id)
            if record["acceptance_scope"] != "controlled_pilot_non_production" or record["production_evidence_claimed"] is not False:
                raise ECAEError("FALSE_PRODUCTION_EVIDENCE", "Local acceptance must remain explicitly non-production", domain_id)
            if record["contract_content_hash"] != content_hash(contract):
                raise ECAEError("ACCEPTANCE_CONTRACT_HASH_MISMATCH", "Acceptance does not bind the exact consumer contract", domain_id)
            if record["content_hash"] != content_hash(record):
                raise ECAEError("ACCEPTANCE_CONTENT_HASH_MISMATCH", "Acceptance record content hash is invalid", domain_id)
            eligible_uses = [item["use"] for item in contract["use_requirements"] if item["requires_independent_review"] is False]
            if acceptance["accepted_uses"] != eligible_uses or record["accepted_uses"] != eligible_uses:
                raise ECAEError("CONTROLLED_PILOT_USE_SCOPE_MISMATCH", "Controlled-pilot acceptance must include exactly the non-high-stakes uses", domain_id)
            controlled_pilot_acceptance_count += 1
        if acceptance["production_status"] == "not_executed" and acceptance["production_signed_record_ref"] is not None:
            raise ECAEError("FALSE_PRODUCTION_ACCEPTANCE", "Unexecuted production acceptance cannot have a signed record", domain_id)

        dual = contract["dual_run"]
        if dual["local_fixture_status"] == "fixture_verified":
            fixture_count += 1
            if not dual["local_fixture_ref"] or not (REPO_ROOT / dual["local_fixture_ref"]).is_file():
                raise ECAEError("LOCAL_FIXTURE_EVIDENCE_MISSING", "Verified fixture requires an evidence file", domain_id)
        if dual["production_status"] == "completed" and not dual["production_evidence_ref"]:
            raise ECAEError("PRODUCTION_DUAL_RUN_EVIDENCE_MISSING", "Completed production dual-run requires evidence", domain_id)
        if contract["rollback"]["local_drill_status"] == "fixture_verified":
            rollback_count += 1

    gates = migration["completion_gate"]
    derived_production_runs = all(item["dual_run"]["production_status"] == "completed" and item["dual_run"]["production_evidence_ref"] for item in migration["consumers"])
    derived_differences = all(item["dual_run"]["difference_status"] == "production_dispositioned" and item["dual_run"]["difference_evidence_ref"] for item in migration["consumers"])
    derived_controlled_pilot_acceptance = controlled_pilot_acceptance_count == 13
    derived_production_acceptance = all(item["acceptance"]["production_status"] in {"accepted", "conditionally_accepted"} and item["acceptance"]["production_signed_record_ref"] for item in migration["consumers"])
    derived_rollbacks = all(item["rollback"]["production_drill_evidence_ref"] for item in migration["consumers"])
    expected_gates = {
        "all_production_dual_runs_completed": bool(derived_production_runs),
        "all_production_differences_dispositioned": bool(derived_differences),
        "all_controlled_pilot_consumer_acceptances_signed": bool(derived_controlled_pilot_acceptance),
        "all_production_consumer_acceptances_signed": bool(derived_production_acceptance),
        "all_production_rollback_drills_passed": bool(derived_rollbacks),
    }
    mismatches = {key: {"declared": gates[key], "derived": expected} for key, expected in expected_gates.items() if gates[key] is not expected}
    if mismatches:
        raise ECAEError("COMPLETION_GATE_MISMATCH", "Completion gates must be derived from evidence", mismatches)
    derived_wp11_controlled_pilot = gates["local_contract_implementation_complete"] and derived_controlled_pilot_acceptance
    if gates["wp11_controlled_pilot_complete"] is not derived_wp11_controlled_pilot:
        raise ECAEError("WP11_CONTROLLED_PILOT_GATE_MISMATCH", "Controlled-pilot WP11 requires local implementation and 13 bounded owner acceptances", {"declared": gates["wp11_controlled_pilot_complete"], "derived": derived_wp11_controlled_pilot})
    derived_l4_production = all(expected_gates[key] for key in ("all_production_dual_runs_completed", "all_production_differences_dispositioned", "all_production_consumer_acceptances_signed", "all_production_rollback_drills_passed"))
    if gates["l4_production_acceptance_complete"] is not derived_l4_production:
        raise ECAEError("L4_PRODUCTION_GATE_MISMATCH", "L4 production acceptance cannot exceed its production evidence", {"declared": gates["l4_production_acceptance_complete"], "derived": derived_l4_production})
    if gates["local_contract_implementation_complete"] is not (fixture_count == 13 and rollback_count == 13):
        raise ECAEError("LOCAL_IMPLEMENTATION_GATE_MISMATCH", "Local implementation gate requires all fixture and rollback drills", {"fixtures": fixture_count, "rollbacks": rollback_count})

    return {
        "valid": True,
        "migration_id": migration["migration_id"],
        "consumer_count": len(domains),
        "local_fixture_verified": fixture_count,
        "local_rollback_verified": rollback_count,
        "production_dual_runs_completed": sum(item["dual_run"]["production_status"] == "completed" for item in migration["consumers"]),
        "controlled_pilot_consumer_acceptances": controlled_pilot_acceptance_count,
        "production_consumer_acceptances": sum(item["acceptance"]["production_status"] in {"accepted", "conditionally_accepted"} for item in migration["consumers"]),
        "wp11_controlled_pilot_complete": gates["wp11_controlled_pilot_complete"],
        "l4_production_acceptance_complete": gates["l4_production_acceptance_complete"],
        "external_write": False,
    }


if __name__ == "__main__":
    cli_main(validate_consumer_migration, __doc__ or "Validate consumer migration")
