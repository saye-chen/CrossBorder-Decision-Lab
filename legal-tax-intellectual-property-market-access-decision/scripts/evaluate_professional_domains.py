#!/usr/bin/env python3
"""Deterministic D05 coverage and escalation models; never issues professional opinions."""
from __future__ import annotations

from collections.abc import Iterable

RESERVED_PROFESSIONAL_TYPES = {"customs_hs", "ip_screening", "tax_customs"}
HIGH_RISK_CLAIM_TAGS = {"medical", "health", "safety", "environmental", "comparative", "absolute", "children"}


def evaluate_coverage(required: Iterable[str], matched: Iterable[str], mismatched: Iterable[str], unknown: Iterable[str]) -> str:
    required_set = set(required)
    matched_set = set(matched)
    mismatch_set = set(mismatched)
    unknown_set = set(unknown)
    if not required_set:
        return "inconclusive"
    if (matched_set | mismatch_set | unknown_set) - required_set:
        return "inconclusive"
    if mismatch_set:
        return "not_covered"
    if unknown_set or matched_set != required_set:
        return "partially_covered"
    return "covered"


def assess_claim(*, direct_evidence: bool, object_match: bool, scope_match: bool, current: bool, risk_tags: Iterable[str], professional_opinion: bool) -> dict:
    tags = set(risk_tags)
    high_risk = bool(tags & HIGH_RISK_CLAIM_TAGS)
    gaps = []
    if not direct_evidence: gaps.append("direct_evidence")
    if not object_match: gaps.append("object_match")
    if not scope_match: gaps.append("scope_match")
    if not current: gaps.append("current_evidence")
    if high_risk and not professional_opinion: gaps.append("qualified_professional_review")
    return {
        "result": "covered" if not gaps else "review_required" if gaps == ["qualified_professional_review"] else "not_covered",
        "gaps": gaps,
        "professional_review_required": high_risk,
        "claim_upgrade_allowed": False,
    }


def route_assessment(assessment_type: str, *, active_hit: bool = False, unresolved: bool = False, unavailable_source: bool = False) -> dict:
    review = assessment_type in RESERVED_PROFESSIONAL_TYPES or active_hit or unresolved or unavailable_source
    if unavailable_source or unresolved:
        result = "inconclusive"
    elif active_hit:
        result = "review_required"
    elif assessment_type in RESERVED_PROFESSIONAL_TYPES:
        result = "review_required"
    else:
        result = "screening_only"
    return {"result": result, "professional_review_required": review, "confirmed_professional_conclusion": False}


def certificate_coverage(required: dict, certificate: dict) -> dict:
    dimensions = ["issuer", "holder", "standard", "standard_version", "model", "bom_version", "factory", "sample_batch", "jurisdiction", "use", "validity"]
    matched, mismatched, unknown = [], [], []
    for key in dimensions:
        wanted, actual = required.get(key), certificate.get(key)
        if wanted in (None, "") or actual in (None, ""):
            unknown.append(key)
        elif wanted == actual:
            matched.append(key)
        else:
            mismatched.append(key)
    return {"result": evaluate_coverage(dimensions, matched, mismatched, unknown), "matched": matched, "mismatched": mismatched, "unknown": unknown}

def assess_transaction_chain(d: dict) -> dict:
    required=("seller","buyer","importer","ship_from","ship_to","goods_flow","funds_flow","incoterm","valuation_basis","origin","hs_candidate","business_time")
    missing=[x for x in required if not d.get(x)]; conflicts=[]
    if d.get("importer") and d.get("declared_importer") and d["importer"]!=d["declared_importer"]: conflicts.append("importer_identity")
    if d.get("origin") and d.get("certificate_origin") and d["origin"]!=d["certificate_origin"]: conflicts.append("origin")
    return {"result":"review_required" if not missing and not conflicts else "inconclusive","missing":missing,"conflicts":conflicts,"tax_or_customs_conclusion_issued":False}

def assess_claim_context(d: dict) -> dict:
    required=("claim_id","text","language","medium","audience","object_version","country","platform","evidence_ids","valid_until")
    missing=[x for x in required if not d.get(x)]; mismatch=[]
    if d.get("evidence_object_version")!=d.get("object_version"):mismatch.append("object_version")
    if d.get("evidence_mediums") and d.get("medium") not in d["evidence_mediums"]:mismatch.append("medium")
    return {"result":"covered" if not missing and not mismatch else "not_covered","missing":missing,"mismatched":mismatch,"copy_rewrite_cannot_inherit_evidence":bool(mismatch)}
