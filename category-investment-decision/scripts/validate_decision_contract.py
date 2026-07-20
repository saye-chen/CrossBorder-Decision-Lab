#!/usr/bin/env python3
"""Validate single-skill and cross-skill decision contracts.

The validator protects decision ownership, professional completeness, evidence
lineage, score write-back state, transferability, and threshold crossings.  It
does not make business judgments; it rejects structurally unsafe decisions.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


OWNERS = {
    "investment": "category-investment-decision",
    "capital_portfolio": "category-investment-decision",
    "lifecycle_capital": "category-investment-decision",
    "competition": "competitive-intelligence-monitoring",
    "competitive_intelligence": "competitive-intelligence-monitoring",
    "content": "video-link-breakdown",
    "content_creative": "video-link-breakdown",
    "content_migration": "video-link-breakdown",
    "customer_growth": "consumer-insights-customer-growth",
    "customer_experience": "consumer-insights-customer-growth",
    "service_recovery": "consumer-insights-customer-growth",
    "loyalty": "consumer-insights-customer-growth",
    "reputation": "consumer-insights-customer-growth",
    "crm_orchestration": "consumer-insights-customer-growth",
    "advertising": "advertising-analysis-measurement-optimization",
    "advertising_measurement": "advertising-analysis-measurement-optimization",
    "advertising_scaling": "advertising-analysis-measurement-optimization",
    "logistics": "logistics-inventory-fulfillment-decision",
    "inventory": "logistics-inventory-fulfillment-decision",
    "replenishment": "logistics-inventory-fulfillment-decision",
    "fulfillment": "logistics-inventory-fulfillment-decision",
    "reverse_logistics": "logistics-inventory-fulfillment-decision",
    "logistics_incident": "logistics-inventory-fulfillment-decision",
    "listing_conversion": "platform-store-listing-conversion",
    "page_conversion": "platform-store-listing-conversion",
    "listing_incident": "platform-store-listing-conversion",
    "listing_migration": "platform-store-listing-conversion",
}
SKILLS = set(OWNERS.values())
CLAIM_STATES = {"observed", "estimated", "hypothesis", "proposed", "validated", "rejected", "blocked", "inconclusive", "superseded"}
ADJUSTMENT_STATES = {"proposed", "validated", "rejected"}
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
VERSION_PREFIX = {
    "category-investment-decision":"CIDM", "competitive-intelligence-monitoring":"CIM",
    "video-link-breakdown":"VLB", "consumer-insights-customer-growth":"CIG",
    "advertising-analysis-measurement-optimization":"D09", "logistics-inventory-fulfillment-decision":"D07",
    "platform-store-listing-conversion":"D08",
}
PROFESSIONAL_FIELDS = (
    "object_boundary",
    "conclusion",
    "evidence_summary",
    "counterevidence",
    "commercial_constraints",
    "risks_and_redlines",
    "actions",
    "success_conditions",
    "stop_conditions",
    "limitations_and_missing_data",
)


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    decision_type = payload.get("decision_type")
    expected_owner = OWNERS.get(decision_type)
    owner = payload.get("decision_owner")
    if expected_owner is None:
        errors.append(f"unknown decision_type: {decision_type!r}")
    elif owner != expected_owner:
        errors.append(f"decision_owner must be {expected_owner!r} for {decision_type!r}")

    mode = payload.get("mode")
    if mode not in {"single", "multi"}:
        errors.append("mode must be 'single' or 'multi'")
    participants = payload.get("participating_skills")
    if not isinstance(participants, list) or not participants:
        errors.append("participating_skills must be a non-empty list")
        participants = []
    else:
        unknown = sorted(set(participants) - SKILLS)
        if unknown:
            errors.append(f"unknown participating skills: {unknown}")
        if owner not in participants:
            errors.append("decision_owner must appear in participating_skills")
        if mode == "single" and len(set(participants)) != 1:
            errors.append("single mode must contain exactly one participating skill")
        if mode == "multi" and len(set(participants)) < 2:
            errors.append("multi mode must contain at least two participating skills")

    if not nonempty(payload.get("runtime_versions")):
        errors.append("runtime_versions is required")
    elif isinstance(payload["runtime_versions"], dict):
        missing_versions = sorted(set(participants) - set(payload["runtime_versions"]))
        if missing_versions:
            errors.append(f"missing runtime versions for: {missing_versions}")
        for skill in participants:
            version=str(payload["runtime_versions"].get(skill,""));prefix=VERSION_PREFIX.get(skill,"")
            if not re.fullmatch(rf"{re.escape(prefix)}-20\d{{2}}\.\d{{2}}",version): errors.append(f"invalid runtime version for {skill}: {version!r}")

    results=payload.get("participant_results")
    if not isinstance(results,dict): errors.append("participant_results must be an object covering every participating skill");results={}
    else:
        missing=sorted(set(participants)-set(results));extra=sorted(set(results)-set(participants))
        if missing: errors.append(f"missing participant results for: {missing}")
        if extra: errors.append(f"participant results include non-participants: {extra}")
        for skill,result in results.items():
            if not isinstance(result,dict) or result.get("status") not in {"contributed","blocked","inconclusive","not_required"}: errors.append(f"participant result {skill} has invalid status")
            elif result.get("status")!="contributed" and not nonempty(result.get("reason")): errors.append(f"participant result {skill} requires failure or exclusion reason")

    professional = payload.get("professional_core")
    if not isinstance(professional, dict):
        errors.append("professional_core must be an object")
    else:
        for field in PROFESSIONAL_FIELDS:
            if not nonempty(professional.get(field)):
                errors.append(f"professional_core.{field} must not be empty")

    objects = payload.get("objects")
    if not isinstance(objects, list) or not objects:
        errors.append("objects must contain at least one canonical object")
        objects = []
    object_ids: set[str] = set()
    for index, obj in enumerate(objects):
        if not isinstance(obj, dict):
            errors.append(f"objects[{index}] must be an object")
            continue
        for field in ("canonical_id", "country", "platform", "category", "lifecycle"):
            if not nonempty(obj.get(field)):
                errors.append(f"objects[{index}].{field} must not be empty")
        if nonempty(obj.get("canonical_id")):
            object_ids.add(obj["canonical_id"])

    evidence = payload.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        evidence = []
    elif not evidence: errors.append("evidence must contain at least one traceable item")
    evidence_by_id: dict[str, dict] = {}
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be an object")
            continue
        evidence_id = item.get("id")
        if not nonempty(evidence_id):
            errors.append(f"evidence[{index}].id must not be empty")
            continue
        if evidence_id in evidence_by_id:
            errors.append(f"duplicate evidence id: {evidence_id}")
        evidence_by_id[evidence_id] = item
        if item.get("source_skill") not in participants:
            errors.append(f"evidence {evidence_id} producer is not a participating skill")
        for field in ("evidence_type", "source_ref", "observed_at", "fingerprint"):
            if not nonempty(item.get(field)):
                errors.append(f"evidence {evidence_id}.{field} must not be empty")

    claims = payload.get("claims", [])
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    elif not claims: errors.append("claims must contain at least one owned claim")
    claim_ids: set[str] = set()
    claim_dependencies: dict[str, list[str]] = {}
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be an object")
            continue
        claim_id = claim.get("id")
        if not nonempty(claim_id):
            errors.append(f"claims[{index}].id must not be empty")
            continue
        if claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim_id}")
        claim_ids.add(claim_id)
        if claim.get("producer_skill") not in participants:
            errors.append(f"claim {claim_id} producer is not a participating skill")
        claim_domain = claim.get("claim_domain")
        domain_owner = OWNERS.get(claim_domain)
        if domain_owner is None:
            errors.append(f"claim {claim_id} has invalid claim_domain")
        elif claim.get("producer_skill") != domain_owner:
            errors.append(f"claim {claim_id} crosses domain authority: {claim_domain} belongs to {domain_owner}")
        if claim.get("state") not in CLAIM_STATES:
            errors.append(f"claim {claim_id} has invalid state")
        if claim.get("object_id") not in object_ids:
            errors.append(f"claim {claim_id} references unknown object_id")
        refs = claim.get("evidence_ids", [])
        if not isinstance(refs, list):
            errors.append(f"claim {claim_id}.evidence_ids must be a list")
        else:
            for ref in refs:
                if ref not in evidence_by_id:
                    errors.append(f"claim {claim_id} references unknown evidence {ref}")
        if claim.get("state") == "observed" and not refs:
            errors.append(f"observed claim {claim_id} requires direct evidence")
        if claim.get("state") == "observed" and isinstance(refs, list):
            non_direct = {
                "proxy", "estimate", "estimated", "inference", "inferred",
                "benchmark", "external_statement",
            }
            unsafe_refs = [
                ref for ref in refs
                if ref in evidence_by_id
                and str(evidence_by_id[ref].get("evidence_class", "")).lower() in non_direct
            ]
            if unsafe_refs:
                errors.append(
                    f"observed claim {claim_id} cannot rely on non-direct evidence: {unsafe_refs}"
                )
        if claim.get("effective_now") and claim.get("state") != "validated":
            errors.append(f"claim {claim_id} cannot be effective before validation")
        if not nonempty(claim.get("allowed_uses")) or not isinstance(claim.get("forbidden_uses"), list):
            errors.append(f"claim {claim_id} requires allowed_uses and forbidden_uses")
        elif set(claim["allowed_uses"]) & set(claim["forbidden_uses"]):
            errors.append(f"claim {claim_id} has overlapping allowed and forbidden uses")
        dependencies = claim.get("derived_from_claim_ids", [])
        if not isinstance(dependencies, list):
            errors.append(f"claim {claim_id}.derived_from_claim_ids must be a list")
            dependencies = []
        claim_dependencies[claim_id] = dependencies

    for claim_id, dependencies in claim_dependencies.items():
        for dependency in dependencies:
            if dependency not in claim_ids:
                errors.append(f"claim {claim_id} derives from unknown claim {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(claim_id: str) -> None:
        if claim_id in visiting:
            errors.append(f"cyclic claim dependency detected at {claim_id}")
            return
        if claim_id in visited:
            return
        visiting.add(claim_id)
        for dependency in claim_dependencies.get(claim_id, []):
            if dependency in claim_dependencies:
                visit(dependency)
        visiting.remove(claim_id)
        visited.add(claim_id)

    for claim_id in claim_dependencies:
        visit(claim_id)

    summary_ids=set()
    if isinstance(professional,dict):
        summary_ids=set(re.findall(r"(?<![A-Z0-9])E\d+(?!\d)",json.dumps(professional.get("evidence_summary",[]),ensure_ascii=False)))
    missing_summary=sorted(summary_ids-set(evidence_by_id))
    if missing_summary: errors.append(f"professional evidence summary references unknown evidence: {missing_summary}")

    unresolved_redlines = payload.get("unresolved_redlines", [])
    if not isinstance(unresolved_redlines, list):
        errors.append("unresolved_redlines must be a list")
        unresolved_redlines = []
    calculations = payload.get("calculations", [])
    if not isinstance(calculations, list):
        errors.append("calculations must be a list")
        calculations = []
    calculation_ids = {item.get("id") for item in calculations if isinstance(item, dict)}
    for item in calculations:
        if not isinstance(item, dict):
            errors.append("each calculation must be an object")
            continue
        for field in ("id", "calculator", "input_hash", "output_hash"):
            if not nonempty(item.get(field)):
                errors.append(f"calculation.{field} must not be empty")
        if item.get("status") != "complete":
            errors.append(f"calculation {item.get('id')} is not complete")

    adjustments = payload.get("adjustments", [])
    if not isinstance(adjustments, list):
        errors.append("adjustments must be a list")
        adjustments = []
    for index, adjustment in enumerate(adjustments):
        if not isinstance(adjustment, dict):
            errors.append(f"adjustments[{index}] must be an object")
            continue
        adjustment_id = adjustment.get("id", f"index-{index}")
        status = adjustment.get("status")
        if status not in ADJUSTMENT_STATES:
            errors.append(f"adjustment {adjustment_id} has invalid status")
        if adjustment.get("target_skill") != owner:
            errors.append(f"adjustment {adjustment_id} must target the decision owner")
        if adjustment.get("proposer_skill") not in participants:
            errors.append(f"adjustment {adjustment_id} proposer is not a participating skill")
        if adjustment.get("effective_now") and status != "validated":
            errors.append(f"adjustment {adjustment_id} cannot be effective before validation")
        if adjustment.get("effective_now"):
            if adjustment.get("accepted_by") != owner or adjustment.get("recomputed_by") != owner:
                errors.append(f"effective adjustment {adjustment_id} must be accepted and recomputed by owner")
        transfer = adjustment.get("transferability", "same_product")
        if transfer in {"cross_category", "all_different"} and adjustment.get("effective_now"):
            errors.append(f"adjustment {adjustment_id} cannot be effective for {transfer}")
        if transfer == "similar_product" and status == "validated" and not nonempty(adjustment.get("validation_ids")):
            errors.append(f"similar-product adjustment {adjustment_id} requires validation_ids")
        refs = adjustment.get("evidence_ids", [])
        for ref in refs if isinstance(refs, list) else []:
            if ref not in evidence_by_id:
                errors.append(f"adjustment {adjustment_id} references unknown evidence {ref}")
        for field in ("original_score", "proposed_score"):
            if field in adjustment and not is_number(adjustment[field]):
                errors.append(f"adjustment {adjustment_id}.{field} must be finite")
        if adjustment.get("crosses_threshold"):
            unique_fingerprints = {
                evidence_by_id[ref].get("fingerprint")
                for ref in refs if ref in evidence_by_id
            }
            if len(unique_fingerprints) < 2:
                errors.append(f"threshold-crossing adjustment {adjustment_id} needs two independent evidence fingerprints")
            if not adjustment.get("target_object_direct_evidence"):
                errors.append(f"threshold-crossing adjustment {adjustment_id} needs direct target-object evidence")
            if unresolved_redlines:
                errors.append(f"threshold-crossing adjustment {adjustment_id} blocked by unresolved redlines")
            required_calcs = adjustment.get("required_calculation_ids", [])
            if not required_calcs or not set(required_calcs).issubset(calculation_ids):
                errors.append(f"threshold-crossing adjustment {adjustment_id} lacks required calculations")
            before_confidence = adjustment.get("original_confidence")
            after_confidence = adjustment.get("proposed_confidence")
            if before_confidence not in CONFIDENCE_RANK or after_confidence not in CONFIDENCE_RANK:
                errors.append(f"threshold-crossing adjustment {adjustment_id} requires valid confidence states")
            elif CONFIDENCE_RANK[after_confidence] < CONFIDENCE_RANK[before_confidence]:
                errors.append(f"threshold-crossing adjustment {adjustment_id} cannot lower confidence")

    if decision_type in {"investment", "capital_portfolio", "lifecycle_capital"}:
        required = set(payload.get("required_calculation_ids", []))
        if not required:
            errors.append("investment decisions require required_calculation_ids")
        elif not required.issubset(calculation_ids):
            errors.append("investment decision references missing calculations")

    if payload.get("calculation_required"):
        required = set(payload.get("required_calculation_ids", []))
        if not required:
            errors.append("calculation_required decisions require required_calculation_ids")
        elif not required.issubset(calculation_ids):
            errors.append("calculation_required decision references missing calculations")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON decision contract")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("INVALID: root must be an object", file=sys.stderr)
        return 2
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    print("PASS: decision contract is structurally safe and professionally complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
