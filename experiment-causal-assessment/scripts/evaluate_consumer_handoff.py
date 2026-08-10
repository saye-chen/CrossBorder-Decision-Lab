#!/usr/bin/env python3
"""Evaluate a consumer's bounded use of an ECAE handoff without taking its decision sovereignty."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, parse_time
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration
from validate_schema import validate_object


GRADE_RANK = {f"CE{i}": i for i in range(6)}
CURRENT_STATUSES = {"handed_off", "replayed", "current"}


def _result(domain_id: str, intended_use: str, decision: str, reasons: list[str], *, effective_use: str, grade: str | None, recompute: bool = False) -> dict:
    causal_allowed = decision == "accept" and grade in {"CE4", "CE5"}
    return {
        "domain_id": domain_id,
        "intended_use": intended_use,
        "decision": decision,
        "effective_use": effective_use,
        "causal_wording_allowed": causal_allowed,
        "incremental_zero_fill_forbidden": True,
        "recompute_required": recompute,
        "reasons": sorted(set(reasons)),
        "business_owner_decision_required": True,
        "external_write": False,
    }


def evaluate_consumer_handoff(value: dict) -> dict:
    migration = value.get("migration") or load_default_migration()
    validate_consumer_migration(migration)
    domain_id = value.get("domain_id")
    if not isinstance(domain_id, str):
        raise ECAEError("MISSING_DOMAIN", "domain_id is required")
    contract = contract_for(migration, domain_id)
    intended_use = value.get("intended_use")
    requirements = {item["use"]: item for item in contract["use_requirements"]}
    if intended_use not in requirements:
        return _result(domain_id, str(intended_use), "reject", ["USE_NOT_CONTRACTED"], effective_use="none", grade=None)
    requirement = requirements[intended_use]
    handoff = value.get("handoff")
    if not isinstance(handoff, dict):
        raise ECAEError("MISSING_HANDOFF", "handoff is required")
    validate_object(handoff, "causal-handoff.schema.json")
    grade = handoff["causal_evidence_grade"]

    if handoff["consumer"] != domain_id:
        return _result(domain_id, intended_use, "reject", ["CONSUMER_MISMATCH"], effective_use="none", grade=grade)
    if handoff["schema_version"] not in {version for profile in migration["mapping_profiles"] if profile["profile_id"] == contract["mapping_profile"] for version in profile["accepted_schema_versions"]}:
        return _result(domain_id, intended_use, "reject", ["HANDOFF_SCHEMA_VERSION_NOT_ACCEPTED"], effective_use="none", grade=grade)
    if handoff["status"] not in CURRENT_STATUSES:
        return _result(domain_id, intended_use, "request_recompute", ["HANDOFF_NOT_CURRENT"], effective_use="descriptive_only", grade=grade, recompute=True)
    if handoff["business_owner_decision_required"] is not True or handoff["external_write"] is not False:
        return _result(domain_id, intended_use, "reject", ["SOVEREIGNTY_VIOLATION"], effective_use="none", grade=grade)

    as_of = parse_time(value.get("as_of_time"), "as_of_time")
    if parse_time(handoff["expires_at"], "expires_at") <= as_of:
        return _result(domain_id, intended_use, "request_recompute", ["HANDOFF_EXPIRED"], effective_use="descriptive_only", grade=grade, recompute=True)
    events = set(value.get("active_events", []))
    invalidation = events & set(handoff["invalidation_triggers"])
    recompute = events & set(handoff["recompute_triggers"])
    if invalidation or recompute:
        reasons = [f"INVALIDATION_TRIGGER:{item}" for item in sorted(invalidation)] + [f"RECOMPUTE_TRIGGER:{item}" for item in sorted(recompute)]
        return _result(domain_id, intended_use, "request_recompute", reasons, effective_use="descriptive_only", grade=grade, recompute=True)

    target = value.get("target_context", {})
    applicability = handoff["applicability"]
    scope_reasons = []
    if target.get("platform") and target["platform"] not in applicability["platforms"]:
        scope_reasons.append("PLATFORM_OUT_OF_SCOPE")
    if target.get("country") and target["country"] not in applicability["countries"]:
        scope_reasons.append("COUNTRY_OUT_OF_SCOPE")
    if target.get("treatment_version") and target["treatment_version"] != applicability["treatment_version"]:
        scope_reasons.append("TREATMENT_VERSION_OUT_OF_SCOPE")
    if target.get("population") and target["population"] != applicability["population"]:
        scope_reasons.append("POPULATION_OUT_OF_SCOPE")
    if scope_reasons:
        return _result(domain_id, intended_use, "reject", scope_reasons, effective_use="none", grade=grade)

    missing_payload = [field for field in requirement["required_payload_fields"] if field not in value.get("consumer_payload", {}) or value.get("consumer_payload", {}).get(field) is None]
    if missing_payload:
        return _result(domain_id, intended_use, "reject", [f"MISSING_QUALIFIED_PAYLOAD:{field}" for field in missing_payload], effective_use="none", grade=grade)
    if requirement["required_handoff_action"] not in handoff["allowed_actions"]:
        return _result(domain_id, intended_use, "reject", ["HANDOFF_ACTION_NOT_ALLOWED"], effective_use="none", grade=grade)
    if requirement["required_handoff_action"] in handoff["prohibited_actions"]:
        return _result(domain_id, intended_use, "reject", ["HANDOFF_ACTION_EXPLICITLY_PROHIBITED"], effective_use="none", grade=grade)

    minimum = requirement["minimum_grade"]
    claim_ceiling = handoff["claim_ceiling"] if handoff["claim_ceiling"] in GRADE_RANK else grade
    effective_rank = min(GRADE_RANK[grade], GRADE_RANK[claim_ceiling])
    requested_claim_grade = value.get("requested_claim_grade", minimum)
    if requested_claim_grade not in GRADE_RANK:
        raise ECAEError("INVALID_REQUESTED_CLAIM_GRADE", "requested_claim_grade must be CE0-CE5")
    if GRADE_RANK[requested_claim_grade] > effective_rank:
        return _result(domain_id, intended_use, "degrade", ["REQUEST_EXCEEDS_CLAIM_CEILING"], effective_use=requirement["fallback_use"], grade=grade)
    if effective_rank < GRADE_RANK[minimum]:
        return _result(domain_id, intended_use, "degrade", [f"GRADE_BELOW_USE_MINIMUM:{minimum}"], effective_use=requirement["fallback_use"], grade=grade)
    if (grade == "CE5" or requirement["requires_independent_review"]) and handoff["review_status"] != "independent_accepted":
        return _result(domain_id, intended_use, "degrade", ["INDEPENDENT_REVIEW_REQUIRED"], effective_use=requirement["fallback_use"], grade=grade)

    acceptance = contract["acceptance"]
    if acceptance["status"] == "pending_consumer_owner":
        return _result(domain_id, intended_use, "hold_pending_consumer_acceptance", ["CONSUMER_OWNER_ACCEPTANCE_PENDING"], effective_use="descriptive_only", grade=grade)
    if acceptance["status"] == "rejected":
        return _result(domain_id, intended_use, "reject", ["CONSUMER_OWNER_REJECTED_CONTRACT"], effective_use="none", grade=grade)
    if intended_use not in acceptance["accepted_uses"]:
        return _result(domain_id, intended_use, "reject", ["USE_NOT_ACCEPTED_BY_CONSUMER_OWNER"], effective_use="none", grade=grade)
    return _result(domain_id, intended_use, "accept", [], effective_use=intended_use, grade=grade)


if __name__ == "__main__":
    cli_main(evaluate_consumer_handoff, __doc__ or "Evaluate consumer handoff")
