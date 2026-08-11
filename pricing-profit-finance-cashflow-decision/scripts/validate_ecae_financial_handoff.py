#!/usr/bin/env python3
"""Build and validate PPFC's consumer-owned receipt for an ECAE D06 handoff."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ppfc_common import canonical_hash, parse_time
from validate_schema_instance import validate as validate_schema


PPFC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PPFC_ROOT.parent
F01_SCRIPTS = REPO_ROOT / "experiment-causal-assessment" / "scripts"
RECEIPT_SCHEMA = json.loads((PPFC_ROOT / "schemas" / "ecae_financial_receipt.schema.json").read_text(encoding="utf-8"))
INTENDED_USES = {"incremental_economic_input", "high_stakes_financial_support"}


def _f01_modules():
    required = [F01_SCRIPTS / name for name in ("evaluate_consumer_handoff.py", "validate_consumer_migration.py")]
    if not all(path.is_file() for path in required):
        raise ValueError("ECAE consumer runtime is unavailable; incremental economics remain blocked")
    if str(F01_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(F01_SCRIPTS))
    evaluator = importlib.import_module("evaluate_consumer_handoff")
    migration = importlib.import_module("validate_consumer_migration")
    return evaluator.evaluate_consumer_handoff, migration.contract_for, migration.load_default_migration, migration.validate_consumer_migration


def _decimal_string(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} is invalid") from exc
    if not number.is_finite():
        raise ValueError(f"{field} must be finite")
    return value


def _interval(value: object, field: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"lower", "point", "upper"}:
        raise ValueError(f"{field} requires lower point upper")
    parsed = {key: _decimal_string(value[key], f"{field}.{key}") for key in ("lower", "point", "upper")}
    if not (Decimal(parsed["lower"]) <= Decimal(parsed["point"]) <= Decimal(parsed["upper"])):
        raise ValueError(f"{field} must be ordered")
    return parsed


def _snapshot(value: object, as_of_time: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError("economic_parameter_snapshot must be an object")
    expected_hash = canonical_hash({key: item for key, item in value.items() if key != "content_hash"})
    if value.get("content_hash") != expected_hash:
        raise ValueError("economic_parameter_snapshot.content_hash mismatch")
    if parse_time(value.get("valid_until"), "economic_parameter_snapshot.valid_until") <= parse_time(as_of_time, "as_of_time"):
        raise ValueError("economic_parameter_snapshot is expired")
    if not isinstance(value.get("snapshot_id"), str) or not value["snapshot_id"]:
        raise ValueError("economic_parameter_snapshot.snapshot_id is required")
    if not isinstance(value.get("currency"), str) or len(value["currency"]) != 3:
        raise ValueError("economic_parameter_snapshot.currency must be ISO-like")
    _interval(value.get("unit_contribution_interval"), "economic_parameter_snapshot.unit_contribution_interval")
    return value


def receipt_hash(receipt: dict) -> str:
    return canonical_hash({key: value for key, value in receipt.items() if key != "receipt_hash"})


def validate_receipt(receipt: dict, *, migration: dict | None = None) -> list[str]:
    errors = validate_schema(receipt, RECEIPT_SCHEMA)
    if errors:
        return errors
    if receipt["receipt_hash"] != receipt_hash(receipt):
        errors.append("$.receipt_hash:mismatch")
    payload_present = receipt["effect_estimate"] is not None and receipt["effect_interval"] is not None and receipt["economic_parameter_snapshot"] is not None
    qualified = (
        receipt["decision"] == "accept" and receipt["effective_use"] == receipt["intended_use"]
        and receipt["causal_evidence_grade"] in {"CE4", "CE5"} and receipt["causal_wording_allowed"] is True
        and receipt["accepted_by_consumer_owner"] is True and bool(receipt["consumer_owner_acceptance_ref"])
        and payload_present
    )
    expected_state = "qualified" if qualified else "unknown"
    if receipt["incremental_input_state"] != expected_state:
        errors.append("$.incremental_input_state:derived_state_mismatch")
    if receipt["incremental_economics_allowed"] is not qualified:
        errors.append("$.incremental_economics_allowed:derived_state_mismatch")
    if not qualified and payload_present:
        errors.append("$.incremental_input:unknown_must_not_carry_values")
    if not qualified and any(receipt[field] is not None for field in ("effect_estimate", "effect_interval", "economic_parameter_snapshot")):
        errors.append("$.incremental_input:partial_unknown_payload_forbidden")
    if receipt["accepted_by_consumer_owner"] != (receipt["decision"] == "accept"):
        errors.append("$.accepted_by_consumer_owner:decision_mismatch")
    if qualified:
        try:
            if Decimal(receipt["effect_estimate"]) != Decimal(receipt["effect_interval"]["point"]):
                errors.append("$.effect_estimate:point_mismatch")
            _snapshot(receipt["economic_parameter_snapshot"], receipt["evaluated_as_of_time"])
        except (ValueError, InvalidOperation):
            errors.append("$.incremental_input:invalid")
    try:
        _, contract_for, load_default_migration, validate_consumer_migration = _f01_modules()
        authoritative = migration or load_default_migration()
        validate_consumer_migration(authoritative)
        contract = contract_for(authoritative, "D06")
    except Exception:
        errors.append("$.migration:authoritative_contract_invalid")
        return errors
    if receipt["migration_id"] != authoritative["migration_id"] or receipt["contract_version"] != contract["contract_version"]:
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
    if not isinstance(context, dict) or not isinstance(context.get("handoff"), dict):
        raise ValueError("ecae_handoff_context.handoff is required")
    handoff = context["handoff"]
    intended_use = context.get("intended_use", "incremental_economic_input")
    if intended_use not in INTENDED_USES:
        raise ValueError("PPFC ECAE intended_use is not contracted")
    evaluate, contract_for, load_default_migration, validate_migration = _f01_modules()
    authoritative = migration or load_default_migration()
    validate_migration(authoritative)
    contract = contract_for(authoritative, "D06")
    requirement = next(item for item in contract["use_requirements"] if item["use"] == intended_use)
    payload = context.get("consumer_payload", {})
    if not isinstance(payload, dict):
        raise ValueError("consumer_payload must be an object")
    evaluation = evaluate({
        "migration": authoritative, "domain_id": "D06", "intended_use": intended_use,
        "requested_claim_grade": context.get("requested_claim_grade", requirement["minimum_grade"]),
        "handoff": handoff, "as_of_time": context.get("as_of_time"), "active_events": context.get("active_events", []),
        "target_context": context.get("target_context", {}), "consumer_payload": payload,
    })
    accepted = evaluation["decision"] == "accept"
    acceptance_ref = contract["acceptance"]["signed_record_ref"] if accepted else None
    parsed_payload = None
    if accepted:
        effect_interval = _interval(payload.get("effect_interval"), "effect_interval")
        effect_estimate = _decimal_string(payload.get("effect_estimate"), "effect_estimate")
        if Decimal(effect_estimate) != Decimal(effect_interval["point"]):
            raise ValueError("effect_estimate must equal effect_interval.point")
        parsed_payload = (effect_estimate, effect_interval, _snapshot(payload.get("economic_parameter_snapshot"), context.get("as_of_time")))
    qualified = accepted and evaluation["causal_wording_allowed"] and handoff["causal_evidence_grade"] in {"CE4", "CE5"} and bool(acceptance_ref) and parsed_payload is not None
    seed = {"migration_id": authoritative["migration_id"], "contract_version": contract["contract_version"], "handoff_ref": handoff["object_id"], "handoff_content_hash": handoff["content_hash"], "intended_use": intended_use, "decision": evaluation["decision"]}
    receipt = {
        "schema_version": "1.0.0", "runtime_version": "PPFC-2026.07",
        "receipt_id": f"PPFC-ECAE-RECEIPT-{canonical_hash(seed)[:16]}", "domain_id": "D06",
        "migration_id": authoritative["migration_id"], "contract_version": contract["contract_version"],
        "handoff_ref": handoff["object_id"], "handoff_content_hash": handoff["content_hash"], "causal_result_ref": handoff["causal_result_ref"],
        "evaluated_as_of_time": context.get("as_of_time"),
        "causal_evidence_grade": handoff["causal_evidence_grade"], "claim_ceiling": handoff["claim_ceiling"], "intended_use": intended_use,
        "decision": evaluation["decision"], "effective_use": evaluation["effective_use"], "incremental_input_state": "qualified" if qualified else "unknown",
        "effect_estimate": parsed_payload[0] if qualified else None, "effect_interval": parsed_payload[1] if qualified else None,
        "economic_parameter_snapshot": parsed_payload[2] if qualified else None, "incremental_economics_allowed": qualified,
        "causal_wording_allowed": evaluation["causal_wording_allowed"], "reasons": evaluation["reasons"],
        "accepted_by_consumer_owner": accepted, "consumer_owner_acceptance_ref": acceptance_ref,
        "business_owner_decision_required": True, "financial_decision_owner": "PPFC", "external_write": False, "receipt_hash": "0" * 64,
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    errors = validate_receipt(receipt, migration=authoritative)
    if errors:
        raise ValueError("invalid PPFC ECAE receipt: " + ",".join(errors))
    return receipt


def receipt_from(data: dict, *, migration: dict | None = None) -> dict | None:
    direct = data.get("ecae_financial_receipt")
    if direct is not None:
        if not isinstance(direct, dict):
            raise ValueError("ecae_financial_receipt must be an object")
        errors = validate_receipt(direct, migration=migration)
        if errors:
            raise ValueError("invalid PPFC ECAE receipt: " + ",".join(errors))
        return direct
    context = data.get("ecae_handoff_context")
    return None if context is None else build_receipt(context, migration=migration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build_receipt(json.loads(args.input.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2, sort_keys=True))
    except (ValueError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "incremental_input_state": "unknown", "incremental_economics_allowed": False, "external_write": False}, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit(2)
