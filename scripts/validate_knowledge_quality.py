#!/usr/bin/env python3
"""Validate the eight knowledge and delivery quality controls."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "governance/knowledge-quality/knowledge-quality-register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def actual_scale() -> dict:
    professional = load(ROOT / "governance/professional-evaluation-registry.json")
    index = load(ROOT / "evaluations/professional-evaluation-index.json")
    mutations = load(ROOT / "governance/release-mutation-contract.json")
    system = load(ROOT / "governance/system-release.json")
    domains = professional.get("domains", [])
    spec = importlib.util.spec_from_file_location("release_integrity_for_scale", ROOT / "scripts/validate_release_integrity.py")
    release_integrity = importlib.util.module_from_spec(spec); spec.loader.exec_module(release_integrity)
    return {
        "registered_domains": len(domains),
        "registered_validation_entrypoints": len(release_integrity.command_paths()),
        "registered_source_cases": int(index.get("case_count", -1)),
        "anti_tamper_mutations": len(mutations.get("mutations", [])),
        "maturity": system.get("maturity"),
        "production_ready": system.get("production_ready"),
    }


def validate(data: dict, as_of: dt.date | None = None) -> list[str]:
    as_of = as_of or dt.date.today()
    errors: list[str] = []
    architecture = load(ROOT / "governance/domain-architecture-registry.json")
    current_domains = {row["domain_id"] for row in architecture.get("domains", []) if row.get("availability") == "current"}
    if data.get("contract") != "CBDS-KNOWLEDGE-QUALITY-2026.07":
        errors.append("unsupported knowledge quality contract")

    fact_ids: set[str] = set()
    registered_source_refs: set[str] = set()
    for fact in data.get("dynamic_facts", []):
        fid = fact.get("fact_id")
        if not fid or fid in fact_ids:
            errors.append(f"duplicate or missing fact_id: {fid}")
        fact_ids.add(fid)
        for key in ("owner_domain", "scope", "source_refs", "reviewed_at", "expires_at", "status", "allowed_uses", "invalidation_conditions"):
            if not fact.get(key): errors.append(f"fact {fid} lacks {key}")
        if fact.get("owner_domain") not in current_domains: errors.append(f"fact {fid} has unknown owner domain")
        for ref in fact.get("source_refs", []):
            registered_source_refs.add(ref)
            source_path = ROOT / ref
            if not source_path.is_file(): errors.append(f"fact {fid} source missing: {ref}")
            elif ref.startswith("governance/platform-knowledge/cards/"):
                card = load(source_path)
                scope = fact.get("scope", {})
                comparisons = {
                    "owner_domain": (fact.get("owner_domain"), card.get("owner_domain")),
                    "platform": (scope.get("platform"), card.get("platform")),
                    "reviewed_at": (fact.get("reviewed_at"), card.get("reviewed_at")),
                    "expires_at": (fact.get("expires_at"), card.get("expires_at")),
                }
                for field, (registered, authoritative) in comparisons.items():
                    if registered != authoritative: errors.append(f"fact {fid} {field} drifted from {ref}")
                if not set(fact.get("allowed_uses", [])) <= set(card.get("allowed_uses", [])): errors.append(f"fact {fid} broadens allowed uses")
        try:
            reviewed = dt.date.fromisoformat(fact["reviewed_at"]); expires = dt.date.fromisoformat(fact["expires_at"])
            if reviewed > expires: errors.append(f"fact {fid} has invalid validity window")
            if fact.get("status") == "active" and as_of > expires: errors.append(f"fact {fid} is expired but active")
        except (KeyError, ValueError): errors.append(f"fact {fid} has invalid dates")
    card_refs = {str(path.relative_to(ROOT)) for path in (ROOT / "governance/platform-knowledge/cards").glob("*.json")}
    missing_cards = card_refs - registered_source_refs
    if missing_cards: errors.append(f"platform knowledge cards lack dynamic-fact coverage: {sorted(missing_cards)}")
    duplicate_card_coverage = {ref for ref in registered_source_refs if sum(ref in fact.get("source_refs", []) for fact in data.get("dynamic_facts", [])) > 1}
    if duplicate_card_coverage: errors.append(f"platform cards have ambiguous duplicate coverage: {sorted(duplicate_card_coverage)}")

    constraint_ids: set[str] = set()
    for item in data.get("constraints", []):
        cid = item.get("constraint_id")
        if not cid or cid in constraint_ids: errors.append(f"duplicate or missing constraint_id: {cid}")
        constraint_ids.add(cid)
        for key in ("owner", "status", "source_ref", "consumers", "impact_on_change"):
            if not item.get(key): errors.append(f"constraint {cid} lacks {key}")
        if item.get("source_ref") and not (ROOT / item["source_ref"]).is_file(): errors.append(f"constraint {cid} source missing")
        unknown_consumers = set(item.get("consumers", [])) - current_domains
        if unknown_consumers: errors.append(f"constraint {cid} has unknown consumers: {sorted(unknown_consumers)}")
        if item.get("status") not in {"active", "draft", "stale", "invalidated", "archived"}: errors.append(f"constraint {cid} has invalid status")

    normalized_checks: dict[str, str] = {}
    for check in data.get("deliveries", []):
        cid = check.get("check_id", "?")
        for key in ("owner_domain", "object_ref", "country", "platform", "weakest_assumption", "evidence_state", "counterevidence", "constraint_refs", "success_conditions", "stop_conditions", "rollback_conditions", "result_states"):
            if not check.get(key): errors.append(f"delivery {cid} lacks {key}")
        if check.get("owner_domain") not in current_domains: errors.append(f"delivery {cid} has unknown owner domain")
        missing_refs = set(check.get("constraint_refs", [])) - constraint_ids
        if missing_refs: errors.append(f"delivery {cid} has unknown constraints: {sorted(missing_refs)}")
        if set(check.get("result_states", [])) != {"passed", "failed", "unknown", "not_applicable"}: errors.append(f"delivery {cid} has incomplete result states")
        signature = re.sub(r"[^a-z0-9]+", " ", " ".join(check.get("success_conditions", []) + check.get("stop_conditions", [])).lower()).strip()
        if signature and signature in normalized_checks: errors.append(f"duplicate generic delivery check: {normalized_checks[signature]} and {cid}")
        normalized_checks[signature] = cid

    for route in data.get("missing_data_routes", []):
        rid = route.get("route_id", "?")
        for key in ("field", "authoritative_location", "retrieval_spec", "decision_impact", "frozen_conclusions", "fallback_experiment", "recompute_mode"):
            if not route.get(key): errors.append(f"missing-data route {rid} lacks {key}")
        if route.get("recompute_mode") not in {"recalculation", "rebase", "new_decision_object"}: errors.append(f"missing-data route {rid} has invalid recompute mode")

    expected_scale = actual_scale()
    if data.get("scale_claims") != expected_scale: errors.append(f"scale claims drift: expected {expected_scale}, got {data.get('scale_claims')}")

    policy = data.get("health_policy", {})
    required_health = {"finding_id", "owner", "detected_at", "due_at", "affected_consumers", "freeze_action", "recovery_batch_id", "closure_evidence"}
    if set(policy.get("required_finding_fields", [])) != required_health: errors.append("health finding contract is incomplete")
    if policy.get("auto_close") is not False: errors.append("health findings must not auto-close")
    if policy.get("expired_critical_fact_action") != "freeze_consumers_and_start_reality_recovery": errors.append("expired critical facts must freeze consumers")
    findings_dir = ROOT / "governance/knowledge-quality/findings"
    for path in findings_dir.glob("*.json") if findings_dir.is_dir() else []:
        finding = load(path)
        missing = required_health - set(finding)
        if missing: errors.append(f"health finding {path.name} lacks {sorted(missing)}")
        if finding.get("owner") not in current_domains | {"repository"}: errors.append(f"health finding {path.name} has unknown owner")
        if finding.get("status") == "closed" and not finding.get("closure_evidence"): errors.append(f"health finding {path.name} closed without evidence")

    for raw in data.get("scaffolds", []):
        path = ROOT / raw
        if not path.is_file(): errors.append(f"missing scaffold: {raw}")
        else:
            if path.suffix == ".json":
                template = load(path)
                if "REQUIRED" not in json.dumps(template): errors.append(f"scaffold has no required placeholders: {raw}")
            elif path.name != "new_governed_knowledge_asset.py": errors.append(f"unsupported scaffold executable: {raw}")

    anti = data.get("anti_gaming", {})
    if anti.get("max_normalized_self_check_duplicates") != 1: errors.append("duplicate self-check ceiling was weakened")
    if set(anti.get("threshold_changes_require", [])) != {"change_impact", "independent_review", "replay_evidence"}: errors.append("threshold-change evidence was weakened")
    for fragment in anti.get("forbidden_evaluation_fragments", []):
        if len(fragment.split()) < 3: errors.append(f"anti-gaming fragment is too generic: {fragment}")
    scan_paths = [ROOT / "scripts", ROOT / "governance/interaction/scripts", ROOT / "governance/platform-knowledge/scripts"]
    excluded = {Path(__file__).resolve(), (ROOT / "scripts/test_knowledge_quality.py").resolve()}
    for base in scan_paths:
        for path in base.glob("*.py"):
            if path.resolve() in excluded: continue
            text = path.read_text(encoding="utf-8").lower()
            for fragment in anti.get("forbidden_evaluation_fragments", []):
                if fragment.lower() in text: errors.append(f"forbidden evaluation-specific bypass in {path.relative_to(ROOT)}: {fragment}")
    return errors


def main() -> int:
    data = load(REGISTER)
    errors = validate(data)
    print("KNOWLEDGE_QUALITY=PASS" if not errors else "KNOWLEDGE_QUALITY=FAIL\n- " + "\n- ".join(errors))
    return 0 if not errors else 2


if __name__ == "__main__": raise SystemExit(main())
