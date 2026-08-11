#!/usr/bin/env python3
"""Validate that consumer acceptance is signed by the consumer owner, not by ECAE itself."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, content_hash, parse_time
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration
from validate_schema import validate_object


def validate_consumer_acceptance(value: dict) -> dict:
    migration = value.get("migration") or load_default_migration()
    validate_consumer_migration(migration)
    record = value.get("record")
    if not isinstance(record, dict):
        raise ECAEError("MISSING_ACCEPTANCE_RECORD", "record is required")
    validate_object(record, "consumer-acceptance.schema.json")
    contract = contract_for(migration, record["domain_id"])
    expected_hash = content_hash(contract)
    if record["migration_id"] != migration["migration_id"] or record["contract_version"] != contract["contract_version"]:
        raise ECAEError("ACCEPTANCE_CONTRACT_MISMATCH", "Acceptance is bound to another migration or contract version")
    if record["contract_content_hash"] != expected_hash:
        raise ECAEError("ACCEPTANCE_CONTRACT_HASH_MISMATCH", "Acceptance does not bind the exact consumer contract", {"declared": record["contract_content_hash"], "expected": expected_hash})
    if record["reviewer"]["role"] != contract["acceptance"]["consumer_owner_role"]:
        raise ECAEError("REVIEWER_NOT_CONSUMER_OWNER", "Only the bound consumer-owner role may accept or reject", {"declared": record["reviewer"]["role"], "expected": contract["acceptance"]["consumer_owner_role"]})
    if record["reviewer"]["identity"].strip().upper() in {"ECAE", "F01", "ECAE_IMPLEMENTER", "PRODUCER"}:
        raise ECAEError("PRODUCER_SELF_ACCEPTANCE_FORBIDDEN", "ECAE producer or implementer cannot sign consumer acceptance")
    if record["acceptance_scope"] == "controlled_pilot_non_production" and record["production_evidence_claimed"] is not False:
        raise ECAEError("FALSE_PRODUCTION_EVIDENCE", "Controlled-pilot acceptance cannot claim production evidence")
    if parse_time(record["expires_at"], "expires_at") <= parse_time(record["reviewed_at"], "reviewed_at"):
        raise ECAEError("ACCEPTANCE_EXPIRY_INVALID", "Acceptance expiry must follow review time")
    contracted_uses = {item["use"] for item in contract["use_requirements"]}
    unknown_uses = set(record["accepted_uses"]) - contracted_uses
    if unknown_uses:
        raise ECAEError("UNCONTRACTED_USE_ACCEPTED", "Acceptance cannot create a new use", sorted(unknown_uses))
    return {
        "valid": True,
        "domain_id": record["domain_id"],
        "decision": record["decision"],
        "acceptance_scope": record["acceptance_scope"],
        "accepted_uses": record["accepted_uses"],
        "reaccept_on_contract_change": True,
        "business_owner_decision_required": True,
        "external_write": False,
    }


if __name__ == "__main__":
    cli_main(validate_consumer_acceptance, __doc__ or "Validate consumer acceptance")
