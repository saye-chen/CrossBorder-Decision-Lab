#!/usr/bin/env python3
"""Build and validate CAPM's consumer-side receipt for a live ECAE D10 handoff."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from capm_common import emit, load_json, sha256_json
from validate_schema_instance import validate as validate_schema


CAPM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = CAPM_ROOT.parent
F01_SCRIPTS = REPO_ROOT / "experiment-causal-assessment" / "scripts"


RECEIPT_SCHEMA = json.loads((CAPM_ROOT / "schemas" / "ecae_consumer_receipt.schema.json").read_text(encoding="utf-8"))
INTENDED_USES = {"incremental_partnership_support", "high_stakes_partnership_support"}


def _f01_modules():
    required = [F01_SCRIPTS / name for name in ("evaluate_consumer_handoff.py", "validate_consumer_migration.py", "validate_schema.py")]
    if not all(path.is_file() for path in required):
        raise ValueError("ECAE consumer runtime is unavailable; incremental claims remain blocked")
    if str(F01_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(F01_SCRIPTS))
    evaluator = importlib.import_module("evaluate_consumer_handoff")
    migration = importlib.import_module("validate_consumer_migration")
    return evaluator.evaluate_consumer_handoff, migration.contract_for, migration.load_default_migration, migration.validate_consumer_migration


def receipt_hash(receipt: dict) -> str:
    return sha256_json({key: value for key, value in receipt.items() if key != "receipt_hash"})


def validate_receipt(receipt: dict, *, migration: dict | None = None) -> list[str]:
    errors = validate_schema(receipt, RECEIPT_SCHEMA)
    if errors:
        return errors
    if receipt["receipt_hash"] != receipt_hash(receipt):
        errors.append("$.receipt_hash:mismatch")
    qualified = (
        receipt["decision"] == "accept"
        and receipt["effective_use"] == receipt["intended_use"]
        and receipt["causal_evidence_grade"] in {"CE4", "CE5"}
        and receipt["causal_wording_allowed"] is True
        and receipt["accepted_by_consumer_owner"] is True
        and isinstance(receipt["consumer_owner_acceptance_ref"], str)
        and bool(receipt["consumer_owner_acceptance_ref"].strip())
    )
    if receipt["incremental_claim_allowed"] is not qualified:
        errors.append("$.incremental_claim_allowed:derived_state_mismatch")
    if receipt["decision"] != "accept" and receipt["causal_wording_allowed"]:
        errors.append("$.causal_wording_allowed:non_accepting_receipt")
    if receipt["accepted_by_consumer_owner"] != (receipt["decision"] == "accept"):
        errors.append("$.accepted_by_consumer_owner:decision_mismatch")
    try:
        _, contract_for, load_default_migration, validate_consumer_migration = _f01_modules()
        authoritative_migration = migration or load_default_migration()
        validate_consumer_migration(authoritative_migration)
        contract = contract_for(authoritative_migration, "D10")
    except Exception:
        errors.append("$.migration:authoritative_contract_invalid")
        return errors
    if receipt["migration_id"] != authoritative_migration["migration_id"] or receipt["contract_version"] != contract["contract_version"]:
        errors.append("$.migration:binding_mismatch")
    if receipt["decision"] == "accept":
        acceptance = contract["acceptance"]
        if acceptance["status"] not in {"accepted", "conditionally_accepted"}:
            errors.append("$.accepted_by_consumer_owner:authoritative_acceptance_missing")
        if receipt["consumer_owner_acceptance_ref"] != acceptance["signed_record_ref"]:
            errors.append("$.consumer_owner_acceptance_ref:authoritative_reference_mismatch")
        if receipt["intended_use"] not in acceptance["accepted_uses"]:
            errors.append("$.intended_use:not_accepted_by_consumer_owner")
    return errors


def build_receipt(context: dict, *, migration: dict | None = None) -> dict:
    if not isinstance(context, dict):
        raise ValueError("ecae_handoff_context must be an object")
    handoff = context.get("handoff")
    if not isinstance(handoff, dict):
        raise ValueError("ecae_handoff_context.handoff is required")
    intended_use = context.get("intended_use", "incremental_partnership_support")
    if intended_use not in INTENDED_USES:
        raise ValueError("CAPM ECAE intended_use is not contracted")
    evaluate_consumer_handoff, contract_for, load_default_migration, validate_consumer_migration = _f01_modules()
    authoritative_migration = migration or load_default_migration()
    validate_consumer_migration(authoritative_migration)
    contract = contract_for(authoritative_migration, "D10")
    evaluation = evaluate_consumer_handoff({
        "migration": authoritative_migration,
        "domain_id": "D10",
        "intended_use": intended_use,
        "requested_claim_grade": context.get("requested_claim_grade", next(item["minimum_grade"] for item in contract["use_requirements"] if item["use"] == intended_use)),
        "handoff": handoff,
        "as_of_time": context.get("as_of_time"),
        "active_events": context.get("active_events", []),
        "target_context": context.get("target_context", {}),
        "consumer_payload": context.get("consumer_payload", {}),
    })
    accepted = evaluation["decision"] == "accept"
    acceptance_ref = contract["acceptance"]["signed_record_ref"] if accepted else None
    qualified = accepted and evaluation["causal_wording_allowed"] and handoff["causal_evidence_grade"] in {"CE4", "CE5"} and bool(acceptance_ref)
    seed = {
        "migration_id": authoritative_migration["migration_id"],
        "contract_version": contract["contract_version"],
        "handoff_ref": handoff["object_id"],
        "handoff_content_hash": handoff["content_hash"],
        "intended_use": intended_use,
        "decision": evaluation["decision"],
    }
    receipt = {
        "schema_version": "1.0.0",
        "runtime_version": "CAPM-2026.07",
        "receipt_id": f"CAPM-ECAE-RECEIPT-{sha256_json(seed)[:16]}",
        "domain_id": "D10",
        "migration_id": authoritative_migration["migration_id"],
        "contract_version": contract["contract_version"],
        "handoff_ref": handoff["object_id"],
        "handoff_content_hash": handoff["content_hash"],
        "causal_evidence_grade": handoff["causal_evidence_grade"],
        "claim_ceiling": handoff["claim_ceiling"],
        "intended_use": intended_use,
        "decision": evaluation["decision"],
        "effective_use": evaluation["effective_use"],
        "causal_wording_allowed": evaluation["causal_wording_allowed"],
        "incremental_claim_allowed": qualified,
        "reasons": evaluation["reasons"],
        "accepted_by_consumer_owner": accepted,
        "consumer_owner_acceptance_ref": acceptance_ref,
        "business_owner_decision_required": True,
        "external_write": False,
        "receipt_hash": "0" * 64,
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    errors = validate_receipt(receipt, migration=authoritative_migration)
    if errors:
        raise ValueError("invalid CAPM ECAE receipt: " + ",".join(errors))
    return receipt


def qualified_receipt_from(data: dict, *, migration: dict | None = None) -> dict | None:
    direct = data.get("ecae_consumer_receipt")
    if direct is not None:
        if not isinstance(direct, dict):
            raise ValueError("ecae_consumer_receipt must be an object")
        errors = validate_receipt(direct, migration=migration)
        if errors:
            raise ValueError("invalid CAPM ECAE receipt: " + ",".join(errors))
        return direct
    context = data.get("ecae_handoff_context")
    if context is None:
        return None
    return build_receipt(context, migration=migration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?")
    args = parser.parse_args()
    try:
        emit(build_receipt(load_json(args.input)))
    except (ValueError, KeyError) as exc:
        emit({"valid": False, "error": str(exc), "incremental_claim_allowed": False, "external_write": False})
        raise SystemExit(2)
