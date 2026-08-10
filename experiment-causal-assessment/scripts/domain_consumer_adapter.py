#!/usr/bin/env python3
"""Shared fail-closed runtime for consumer-owned D01-D13 ECAE adapter records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ecae_common import ECAEError, content_hash
from evaluate_consumer_handoff import evaluate_consumer_handoff
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration
from validate_schema import validate_object


ROOT = Path(__file__).resolve().parents[2]
RECEIPT_SCHEMA = "domain-consumer-receipt.schema.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def adapter_acceptance_paths(adapter_path: Path) -> tuple[Path, Path]:
    return adapter_path, adapter_path.with_name("acceptance.json")


def validate_adapter(adapter_path: Path) -> list[str]:
    adapter_file, acceptance_file = adapter_acceptance_paths(adapter_path)
    errors: list[str] = []
    if not adapter_file.is_file() or not acceptance_file.is_file():
        return ["adapter_or_acceptance_missing"]
    adapter, acceptance = load(adapter_file), load(acceptance_file)
    migration = load_default_migration()
    try:
        validate_consumer_migration(migration)
        contract = contract_for(migration, adapter.get("domain_id"))
    except Exception as exc:
        return [f"authoritative_migration:{exc}"]
    exact = {
        "consumer": contract["skill"], "runtime": f"{contract['runtime_prefix']}-2026.07",
        "migration_id": migration["migration_id"], "consumer_contract_version": contract["contract_version"],
        "receipt_schema": "experiment-causal-assessment/schemas/domain-consumer-receipt.schema.json",
        "consumer_runtime": "experiment-causal-assessment/scripts/domain_consumer_adapter.py",
        "unknown_incremental_value_policy": "unknown_never_zero_fill", "automated_contract_accepted": True,
        "independent_owner_accepted": False, "production_dual_run_completed": False, "external_write": False,
    }
    for field, expected in exact.items():
        if adapter.get(field) != expected:
            errors.append(f"adapter.{field}:expected:{expected!r}")
    uses = {item["use"]: item["minimum_grade"] for item in contract["use_requirements"]}
    payload = {item["use"]: item["required_payload_fields"] for item in contract["use_requirements"]}
    if adapter.get("minimum_grade_by_use") != uses or set(adapter.get("allowed_uses", [])) != set(uses):
        errors.append("adapter.allowed_uses:contract_mismatch")
    if adapter.get("required_payload_by_use") != payload:
        errors.append("adapter.required_payload_by_use:contract_mismatch")
    if not set(contract["retained_sovereignty"]) <= set(adapter.get("retained_sovereignty", [])):
        errors.append("adapter.retained_sovereignty:incomplete")
    if not set(adapter.get("retained_sovereignty", [])) <= set(adapter.get("forbidden_writeback", [])):
        errors.append("adapter.forbidden_writeback:sovereignty_gap")
    if not set(contract["prohibited_legacy_mappings"]) <= set(adapter.get("prohibited_legacy_mappings", [])):
        errors.append("adapter.prohibited_legacy_mappings:incomplete")
    if acceptance.get("adapter_hash") != content_hash(adapter):
        errors.append("acceptance.adapter_hash:mismatch")
    if acceptance.get("local_fixture_status") != "verified" or acceptance.get("automated_contract_accepted") is not True:
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
    for field in ("receipt_schema", "consumer_runtime"):
        if not (ROOT / adapter.get(field, "")).is_file():
            errors.append(f"adapter.{field}:missing")
    return errors


def receipt_hash(receipt: dict) -> str:
    return content_hash({key: value for key, value in receipt.items() if key != "receipt_hash"})


def validate_receipt(receipt: dict, adapter_path: Path, *, migration: dict | None = None) -> list[str]:
    errors: list[str] = []
    try:
        validate_object(receipt, RECEIPT_SCHEMA, verify_hash=False)
    except ECAEError as exc:
        return [f"receipt_schema:{exc.code}"]
    adapter = load(adapter_path)
    authoritative = migration or load_default_migration()
    try:
        validate_consumer_migration(authoritative)
        contract = contract_for(authoritative, adapter["domain_id"])
    except Exception:
        return ["migration:authoritative_contract_invalid"]
    if receipt["receipt_hash"] != receipt_hash(receipt):
        errors.append("receipt_hash:mismatch")
    exact = {
        "domain_id": adapter["domain_id"], "runtime_version": adapter["runtime"],
        "migration_id": authoritative["migration_id"], "contract_version": contract["contract_version"],
        "business_action_owner": contract["runtime_prefix"], "external_write": False,
    }
    for field, expected in exact.items():
        if receipt.get(field) != expected:
            errors.append(f"{field}:binding_mismatch")
    accepted = receipt["decision"] == "accept"
    qualified = accepted and receipt["effective_use"] == receipt["intended_use"] and receipt["causal_wording_allowed"] is True and receipt["causal_evidence_grade"] in {"CE4", "CE5"} and bool(receipt["consumer_owner_acceptance_ref"])
    if receipt["accepted_by_consumer_owner"] is not accepted:
        errors.append("accepted_by_consumer_owner:decision_mismatch")
    if receipt["qualified_payload_state"] != ("qualified" if qualified else "unknown"):
        errors.append("qualified_payload_state:derived_state_mismatch")
    if receipt["downstream_use_allowed"] is not qualified:
        errors.append("downstream_use_allowed:derived_state_mismatch")
    if qualified and not isinstance(receipt["qualified_payload"], dict):
        errors.append("qualified_payload:missing")
    if not qualified and receipt["qualified_payload"] is not None:
        errors.append("qualified_payload:unknown_must_not_carry_value")
    if accepted:
        acceptance = contract["acceptance"]
        if acceptance["status"] not in {"accepted", "conditionally_accepted"}:
            errors.append("authoritative_acceptance:missing")
        if receipt["consumer_owner_acceptance_ref"] != acceptance["signed_record_ref"]:
            errors.append("consumer_owner_acceptance_ref:mismatch")
        if receipt["intended_use"] not in acceptance["accepted_uses"]:
            errors.append("intended_use:not_accepted")
    return errors


def build_receipt(context: dict, adapter_path: Path, *, migration: dict | None = None) -> dict:
    adapter_errors = validate_adapter(adapter_path)
    if adapter_errors:
        raise ECAEError("CONSUMER_ADAPTER_INVALID", "consumer adapter is invalid", adapter_errors)
    adapter = load(adapter_path)
    authoritative = migration or load_default_migration()
    validate_consumer_migration(authoritative)
    contract = contract_for(authoritative, adapter["domain_id"])
    handoff = context.get("handoff")
    if not isinstance(handoff, dict):
        raise ECAEError("MISSING_HANDOFF", "handoff is required")
    intended_use = context.get("intended_use", adapter["allowed_uses"][0])
    result = evaluate_consumer_handoff({
        "migration": authoritative, "domain_id": adapter["domain_id"], "intended_use": intended_use,
        "requested_claim_grade": context.get("requested_claim_grade", adapter["minimum_grade_by_use"].get(intended_use)),
        "handoff": handoff, "as_of_time": context.get("as_of_time"), "active_events": context.get("active_events", []),
        "target_context": context.get("target_context", {}), "consumer_payload": context.get("consumer_payload", {}),
    })
    accepted = result["decision"] == "accept"
    acceptance_ref = contract["acceptance"]["signed_record_ref"] if accepted else None
    qualified = accepted and result["causal_wording_allowed"] and handoff["causal_evidence_grade"] in {"CE4", "CE5"} and bool(acceptance_ref)
    seed = {"domain_id": adapter["domain_id"], "handoff_ref": handoff["object_id"], "handoff_hash": handoff["content_hash"], "use": intended_use, "decision": result["decision"]}
    receipt = {
        "schema_version": "1.0.0", "runtime_version": adapter["runtime"],
        "receipt_id": f"{contract['runtime_prefix']}-ECAE-RECEIPT-{content_hash(seed)[:16]}", "domain_id": adapter["domain_id"],
        "migration_id": authoritative["migration_id"], "contract_version": contract["contract_version"],
        "handoff_ref": handoff["object_id"], "handoff_content_hash": handoff["content_hash"], "causal_result_ref": handoff["causal_result_ref"],
        "causal_evidence_grade": handoff["causal_evidence_grade"], "claim_ceiling": handoff["claim_ceiling"],
        "intended_use": intended_use, "decision": result["decision"], "effective_use": result["effective_use"],
        "qualified_payload_state": "qualified" if qualified else "unknown", "qualified_payload": context.get("consumer_payload", {}) if qualified else None,
        "downstream_use_allowed": qualified, "causal_wording_allowed": result["causal_wording_allowed"], "reasons": result["reasons"],
        "accepted_by_consumer_owner": accepted, "consumer_owner_acceptance_ref": acceptance_ref,
        "business_owner_decision_required": True, "business_action_owner": contract["runtime_prefix"], "external_write": False,
        "receipt_hash": "0" * 64,
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    errors = validate_receipt(receipt, adapter_path, migration=authoritative)
    if errors:
        raise ECAEError("CONSUMER_RECEIPT_INVALID", "consumer receipt is invalid", errors)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, type=Path)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    try:
        if args.input is None:
            errors = validate_adapter(args.adapter)
            if errors:
                raise ECAEError("CONSUMER_ADAPTER_INVALID", "consumer adapter is invalid", errors)
            adapter = load(args.adapter)
            result = {"valid": True, "domain_id": adapter["domain_id"], "local_fixture": "verified", "production_dual_run": False, "owner_acceptance": "pending", "external_write": False}
        else:
            result = build_receipt(load(args.input), args.adapter)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (ECAEError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "qualified_payload_state": "unknown", "downstream_use_allowed": False, "external_write": False}, ensure_ascii=False, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
