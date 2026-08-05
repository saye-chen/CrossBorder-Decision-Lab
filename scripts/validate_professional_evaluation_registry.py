#!/usr/bin/env python3
"""Fail closed when the 13-domain professional evaluation evidence drifts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "governance/professional-evaluation-registry.json"
INDEX_PATH = ROOT / "evaluations/professional-evaluation-index.json"
PLACEHOLDERS = (
    "controlled tradeoff for",
    "could reverse if confirmed",
    "field_0_0",
    "field_i_j",
    "<todo>",
    "tbd",
)
REQUIRED_CASE_FIELDS = {
    "schema_version", "case_id", "domain_id", "skill", "runtime", "source_catalog",
    "source_case_id", "source_hash", "golden_hash", "mode", "object_ref", "object_version",
    "inputs", "evidence", "counterevidence", "claims", "root_cause", "actions", "expected_state", "required_behaviors",
    "forbidden_behaviors", "calculations", "sovereignty", "state_transition", "rollback",
    "semantic_assertions", "evidence_fingerprint",
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def digest_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_domains() -> dict[str, dict[str, Any]]:
    architecture = json.loads((ROOT / "governance/domain-architecture-registry.json").read_text(encoding="utf-8"))
    return {x["domain_id"]: x for x in architecture["domains"] if x["availability"] == "current"}


def validate(registry: dict[str, Any] | None = None, index: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    registry = registry or json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    index = index or json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / registry.get("normalized_schema", "")).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        errors.append(f"normalized case schema invalid: {exc.message}")
    schema_validator = jsonschema.Draft202012Validator(schema)
    rows = registry.get("domains", [])
    current = current_domains()
    by_domain = {x.get("domain_id"): x for x in rows}
    if set(by_domain) != set(current) or len(rows) != 13:
        errors.append("registry must cover exactly current D01-D13 once")
    policy = registry.get("policy", {})
    if policy.get("l4_external_assurance") != "reported separately and never inferred from synthetic evaluations":
        errors.append("L4 separation policy missing")
    if policy.get("compatibility_paths_are_authoritative") is not False:
        errors.append("compatibility paths must not be authoritative")

    source_cases: dict[tuple[str, str], dict[str, Any]] = {}
    expected_count = 0
    for domain_id, row in by_domain.items():
        if domain_id not in current:
            continue
        arch = current[domain_id]
        if row.get("skill") != arch["skill"] or not row.get("runtime", "").startswith(arch["runtime_prefix"] + "-"):
            errors.append(f"{domain_id}: architecture identity/runtime mismatch")
        for key in ("catalog", "golden", "semantic_validator", "numeric_validator"):
            path = ROOT / str(row.get(key, ""))
            if not path.is_file():
                errors.append(f"{domain_id}: missing {key} {row.get(key)}")
        catalog_path = ROOT / str(row.get("catalog", ""))
        golden_path = ROOT / str(row.get("golden", ""))
        if not catalog_path.is_file() or not golden_path.is_file():
            continue
        try:
            source = json.loads(catalog_path.read_text(encoding="utf-8"))
            cases = source["cases"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            errors.append(f"{domain_id}: invalid source catalog: {exc}")
            continue
        if len(cases) < int(row.get("minimum_cases", 1)):
            errors.append(f"{domain_id}: catalog below minimum case count")
        ids = [str(x.get("id", "")) for x in cases]
        if "" in ids or len(ids) != len(set(ids)):
            errors.append(f"{domain_id}: source case ids missing or duplicated")
        expected_count += len(cases)
        source_cases.update({(domain_id, str(x["id"])): x for x in cases if x.get("id")})
        golden_text = golden_path.read_text(encoding="utf-8")
        for marker in row.get("semantic_markers", []):
            if marker not in golden_text:
                errors.append(f"{domain_id}: golden missing semantic marker {marker}")
        lowered = golden_text.lower()
        for token in PLACEHOLDERS:
            if token in lowered:
                errors.append(f"{domain_id}: placeholder in golden: {token}")

    normalized = index.get("cases", [])
    if index.get("domain_count") != 13 or index.get("l4_external_assurance") != "separate_not_inferred":
        errors.append("normalized index scope or L4 separation invalid")
    if index.get("case_count") != expected_count or len(normalized) != expected_count:
        errors.append("normalized index case count does not match authoritative catalogs")
    if len({x.get("case_id") for x in normalized}) != len(normalized):
        errors.append("normalized case ids are not unique")
    indexed_keys: set[tuple[str, str]] = set()
    index_domains = {x.get("domain_id"): x for x in index.get("domains", [])}
    if set(index_domains) != set(current) or len(index.get("domains", [])) != 13:
        errors.append("normalized domain index must cover current D01-D13 exactly once")
    for domain_id, row in by_domain.items():
        if domain_id not in current:
            continue
        record = index_domains.get(domain_id, {})
        catalog_path = ROOT / row["catalog"]
        golden_path = ROOT / row["golden"]
        if record.get("skill") != row["skill"]:
            errors.append(f"{domain_id}: normalized domain owner mismatch")
        if catalog_path.is_file() and record.get("source_catalog_hash") != digest_path(catalog_path):
            errors.append(f"{domain_id}: source catalog fingerprint drift")
        if golden_path.is_file() and record.get("golden_hash") != digest_path(golden_path):
            errors.append(f"{domain_id}: normalized golden fingerprint drift")
    for case in normalized:
        for violation in schema_validator.iter_errors(case):
            errors.append(f"{case.get('case_id','?')}: schema violation at {'/'.join(map(str, violation.path))}: {violation.message}")
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            errors.append(f"{case.get('case_id','?')}: missing fields {sorted(missing)}")
            continue
        key = (case["domain_id"], case["source_case_id"])
        indexed_keys.add(key)
        source = source_cases.get(key)
        if source is None:
            errors.append(f"{case['case_id']}: source case not found")
            continue
        expected_hash = digest_json(source)
        if case["source_hash"] != expected_hash or case["evidence_fingerprint"] != expected_hash:
            errors.append(f"{case['case_id']}: source evidence fingerprint drift")
        row = by_domain.get(case["domain_id"], {})
        golden_path = ROOT / str(row.get("golden", ""))
        if golden_path.is_file() and case["golden_hash"] != digest_path(golden_path):
            errors.append(f"{case['case_id']}: golden fingerprint drift")
        if case["skill"] != row.get("skill") or case["runtime"] != row.get("runtime"):
            errors.append(f"{case['case_id']}: owner/runtime mismatch")
        if not case["evidence"] or not case["counterevidence"]:
            errors.append(f"{case['case_id']}: evidence/counterevidence missing")
        root_cause = case.get("root_cause", {})
        if not set(root_cause.get("evidence_refs", [])) <= set(case["evidence"]):
            errors.append(f"{case['case_id']}: root cause references unknown evidence")
        if not set(root_cause.get("counterevidence_refs", [])) <= set(case["counterevidence"]):
            errors.append(f"{case['case_id']}: root cause references unknown counterevidence")
        for claim in case.get("claims", []):
            if not set(claim.get("evidence_refs", [])) <= set(case["evidence"]):
                errors.append(f"{case['case_id']}: claim references unknown evidence")
            if not set(claim.get("counterevidence_refs", [])) <= set(case["counterevidence"]):
                errors.append(f"{case['case_id']}: claim references unknown counterevidence")
        if not case.get("claims") or not case.get("actions"):
            errors.append(f"{case['case_id']}: claim or action linkage missing")
        if any(action.get("root_cause_ref") != root_cause.get("id") for action in case.get("actions", [])):
            errors.append(f"{case['case_id']}: action is not linked to root cause")
        if any(action.get("rollback") != case.get("rollback") for action in case.get("actions", [])):
            errors.append(f"{case['case_id']}: action rollback does not match case rollback")
        if not case["required_behaviors"] or not case["forbidden_behaviors"]:
            errors.append(f"{case['case_id']}: must/forbidden behavior missing")
        sovereignty = case.get("sovereignty", {})
        if sovereignty.get("owner") != case["skill"] or "external_write" not in sovereignty.get("forbidden_uses", []):
            errors.append(f"{case['case_id']}: sovereignty guard invalid")
        if "l4_claim" not in sovereignty.get("forbidden_uses", []):
            errors.append(f"{case['case_id']}: synthetic-to-L4 escalation guard missing")
        if not case.get("calculations") or not all(x.get("validator") for x in case["calculations"]):
            errors.append(f"{case['case_id']}: recomputation validator missing")
        if not case.get("rollback") or len(case.get("semantic_assertions", [])) < 2:
            errors.append(f"{case['case_id']}: rollback or semantic assertion missing")
        text = canonical(case).lower()
        if any(token in text for token in PLACEHOLDERS):
            errors.append(f"{case['case_id']}: placeholder in normalized case")
    if indexed_keys != set(source_cases):
        errors.append("normalized index does not bind every authoritative source case exactly once")
    golden_hashes = {x.get("golden_hash") for x in index.get("domains", [])}
    if len(golden_hashes) < 10:
        errors.append("golden reports insufficiently differentiated")
    return errors


if __name__ == "__main__":
    errors = validate()
    print("PROFESSIONAL_EVALUATION_REGISTRY=PASS" if not errors else "PROFESSIONAL_EVALUATION_REGISTRY=FAIL\n- " + "\n- ".join(errors))
    raise SystemExit(0 if not errors else 2)
