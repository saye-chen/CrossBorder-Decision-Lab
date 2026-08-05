#!/usr/bin/env python3
"""Normalize every current-domain evaluation case onto one auditable schema."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance/professional-evaluation-registry.json"
OUTPUT = ROOT / "evaluations/professional-evaluation-index.json"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical(value).encode("utf-8"))


def strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [canonical(x) if isinstance(x, (dict, list)) else str(x) for x in value]
    if isinstance(value, dict):
        return [canonical(value)]
    return [str(value)]


def first(case: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in case and case[name] not in (None, "", [], {}):
            return case[name]
    return None


def normalize(row: dict[str, Any], case: dict[str, Any], golden_hash: str) -> dict[str, Any]:
    source_id = str(case["id"])
    source_hash = digest_json(case)
    object_value = first(case, "object_ref", "object_scope", "object", "canonical_object")
    object_ref = strings(object_value)[0] if object_value is not None else f"{row['domain_id']}:evaluation-object@v1"
    version = str(first(case, "object_version", "version") or (object_ref.rsplit("@", 1)[1] if "@" in object_ref else "v1"))
    evidence = strings(first(case, "evidence", "evidence_ids", "supporting_evidence")) or [f"source-case:{source_id}"]
    counter = strings(first(case, "counterevidence", "counter_evidence", "counterexample", "conflicts")) or [f"mutation-oracle:{source_id}"]
    expected = first(case, "expected_status", "expected_state", "expected", "expected_output", "expected_guard")
    expected_state = canonical(expected) if isinstance(expected, (dict, list)) else str(expected or "assertion_defined")
    required = strings(first(case, "must", "assertions", "required_behaviors")) or list(row["semantic_markers"])
    forbidden = strings(first(case, "forbidden", "forbidden_behaviors")) or ["跨域越权", "把合成评测当作L4证据"]
    missing = strings(first(case, "missing", "missing_data", "gaps"))
    calculation_signal = any(
        token in key.lower()
        for key in case
        for token in ("calcul", "model", "metric", "score", "formula")
    )
    rollback = "restore_last_validated_version_and_recompute_dependents"
    claim_id = f"CL-{source_id}"
    root_cause_id = f"RC-{source_id}"
    return {
        "schema_version": "1.0.0",
        "case_id": f"PRO-{row['domain_id']}-{source_id}",
        "domain_id": row["domain_id"],
        "skill": row["skill"],
        "runtime": row["runtime"],
        "source_catalog": row["catalog"],
        "source_case_id": source_id,
        "source_hash": source_hash,
        "golden_hash": golden_hash,
        "mode": str(first(case, "mode", "group", "category", "family") or "standard"),
        "object_ref": object_ref,
        "object_version": version,
        "inputs": {"provided": sorted(str(x) for x in case), "missing": missing},
        "evidence": evidence,
        "counterevidence": counter,
        "claims": [{
            "id": claim_id,
            "assertion": expected_state,
            "evidence_refs": evidence,
            "counterevidence_refs": counter,
            "decision_impact": "sets_the_bounded_domain_action_ceiling",
        }],
        "root_cause": {
            "id": root_cause_id,
            "assertion": f"domain_adjudication_required_for:{source_id}",
            "evidence_refs": evidence,
            "counterevidence_refs": counter,
        },
        "actions": [{
            "action": f"execute_required_behavior_for:{source_id}",
            "root_cause_ref": root_cause_id,
            "success_condition": expected_state,
            "stop_condition": forbidden[0],
            "rollback": rollback,
        }],
        "expected_state": expected_state,
        "required_behaviors": required,
        "forbidden_behaviors": forbidden,
        "calculations": [{
            "status": "source_defined" if calculation_signal else "not_applicable",
            "validator": row["numeric_validator"],
        }],
        "sovereignty": {
            "owner": row["skill"],
            "allowed_uses": ["decision_support", "engineering_evaluation"],
            "forbidden_uses": ["external_write", "production_ready", "l4_claim"],
        },
        "state_transition": {
            "from": "unassessed",
            "to": expected_state,
            "trigger": f"evaluate:{source_id}",
        },
        "rollback": rollback,
        "semantic_assertions": list(row["semantic_markers"]) + ["反证必须能够改变结论", "主权边界不可越权"],
        "evidence_fingerprint": source_hash,
    }


def build() -> dict[str, Any]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cases: list[dict[str, Any]] = []
    domains: list[dict[str, Any]] = []
    for row in registry["domains"]:
        catalog_path = ROOT / row["catalog"]
        golden_path = ROOT / row["golden"]
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        source_cases = catalog["cases"]
        golden_hash = digest_bytes(golden_path.read_bytes())
        normalized = [normalize(row, case, golden_hash) for case in source_cases]
        cases.extend(normalized)
        domains.append({
            "domain_id": row["domain_id"],
            "skill": row["skill"],
            "source_case_count": len(source_cases),
            "source_catalog_hash": digest_bytes(catalog_path.read_bytes()),
            "golden_hash": golden_hash,
        })
    return {
        "schema_version": "1.0.0",
        "authority": "governance/professional-evaluation-registry.json",
        "l4_external_assurance": "separate_not_inferred",
        "domain_count": len(domains),
        "case_count": len(cases),
        "domains": domains,
        "cases": cases,
    }


if __name__ == "__main__":
    output = build()
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PROFESSIONAL_EVALUATION_INDEX_BUILT domains={output['domain_count']} cases={output['case_count']}")
