#!/usr/bin/env python3
"""Validate WP6 D04/D05 temporary, professional-opinion and localization contracts."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "d04": "manufacturing-quality-handoff.schema.json",
    "d05": "market-access-review-request.schema.json",
    "opinion": "professional-opinion.schema.json",
    "localization": "localization-profile.schema.json",
    "migration": "temporary-contract-migration.schema.json",
}
FORBIDDEN_ASSERTIONS = {"validated", "compliant", "legal", "no_infringement", "approved_for_market", "manufacturable", "quality_released"}


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_errors(name: str, value: dict) -> list[str]:
    schema = json.loads((ROOT / "schemas" / SCHEMAS[name]).read_text(encoding="utf-8"))
    return [f"{name}:schema:{e.message}" for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)]


def detect_cycle(nodes: set[str], dependencies: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in dependencies.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in nodes)


def validate(package: dict, now: str = "2026-07-28T12:00:00Z") -> list[str]:
    errors: list[str] = []
    for name in SCHEMAS:
        value = package.get(name)
        if not isinstance(value, dict):
            errors.append(f"missing:{name}")
        else:
            errors.extend(schema_errors(name, value))
    if errors:
        return errors

    d04, d05, opinion, local, migration = (package[x] for x in ("d04", "d05", "opinion", "localization", "migration"))
    versions = {d04["object_ref"]["object_version"], d05["object_ref"]["object_version"], opinion["object_ref"]["object_version"], local["object_ref"]["object_version"], migration["object_version"]}
    if len(versions) != 1:
        errors.append("object_version_mismatch")

    fields = {x["field_id"] for x in d04["specifications"]}
    dependencies = {x["field_id"]: x["depends_on"] for x in d04["specifications"]}
    for field, refs in dependencies.items():
        for ref in refs:
            if ref not in fields:
                errors.append(f"d04:orphan_dependency:{field}:{ref}")
    if detect_cycle(fields, dependencies):
        errors.append("d04:dependency_cycle")
    for spec in d04["specifications"]:
        try:
            nominal = Decimal(spec["nominal"]) if spec["nominal"] is not None else None
            lsl = Decimal(spec["lsl"]) if spec["lsl"] is not None else None
            usl = Decimal(spec["usl"]) if spec["usl"] is not None else None
        except InvalidOperation:
            errors.append(f"d04:non_decimal:{spec['field_id']}")
            continue
        if lsl is not None and usl is not None and lsl > usl:
            errors.append(f"d04:inverted_limits:{spec['field_id']}")
        if nominal is not None and lsl is not None and nominal < lsl:
            errors.append(f"d04:nominal_below_lsl:{spec['field_id']}")
        if nominal is not None and usl is not None and nominal > usl:
            errors.append(f"d04:nominal_above_usl:{spec['field_id']}")
        if spec["criticality"] == "safety_critical" and not spec["evidence_ids"]:
            errors.append(f"d04:safety_ctq_without_evidence:{spec['field_id']}")
    for ctq in d04["ctqs"]:
        if ctq["measurement_system_status"] == "not_computable" and ctq["state"] == "proposed":
            errors.append(f"d04:not_computable_cannot_pass:{ctq['ctq_id']}")
    for material in d04["materials"]:
        if material["substitution"] == "candidate" and not material["revalidation_scope"]:
            errors.append(f"d04:substitution_without_revalidation:{material['material_id']}")

    if d05["status"] in FORBIDDEN_ASSERTIONS:
        errors.append("d05:sovereignty_overreach")
    object_version = d05["object_ref"]["object_version"]
    for claim in d05["claims"]:
        if claim["object_version"] != object_version:
            errors.append(f"d05:claim_version_mismatch:{claim['claim_id']}")
        if not claim["evidence_ids"] and claim["allowed_uses"]:
            errors.append(f"d05:unsupported_claim_has_allowed_use:{claim['claim_id']}")
    for question in d05["review_questions"]:
        if not question["source_ref"] or not question["rule_version"] or not question["verified_at"]:
            if question["state"] != "blocked":
                errors.append(f"d05:dynamic_rule_without_provenance:{question['question_id']}")
        if question["expires_at"] and dt(question["expires_at"]) <= dt(now) and question["state"] != "blocked":
            errors.append(f"d05:expired_rule_not_blocked:{question['question_id']}")

    scope = set(opinion["credential_scope"])
    topics = {q["topic"] for q in d05["review_questions"]}
    if not topics <= scope:
        errors.append("opinion:outside_credential_scope")
    if d05["scope"]["jurisdiction"] not in opinion["jurisdictions"]:
        errors.append("opinion:jurisdiction_mismatch")
    if opinion["conflict_of_interest"] == "undisclosed":
        errors.append("opinion:undisclosed_conflict")
    if dt(opinion["expires_at"]) <= dt(now) and opinion["opinion_state"] != "expired":
        errors.append("opinion:expired_not_marked")
    if opinion["claim_upgrade_allowed"]:
        errors.append("opinion:cannot_upgrade_claim")

    all_items = local["market_facts"] + local["adaptation_requirements"] + local["cultural_usage_hypotheses"] + local["regulated_policy_questions"]
    for item in all_items:
        if item["value_state"] == "observed" and (not item["source_ref"] or not item["verified_at"]):
            errors.append(f"localization:observed_without_provenance:{item['item_id']}")
        if item["expires_at"] and dt(item["expires_at"]) <= dt(now) and item["state"] != "blocked":
            errors.append(f"localization:expired_not_blocked:{item['item_id']}")
    if local["translation_complete"] and not all_items:
        errors.append("localization:translation_is_not_localization")
    if (local["country"] == "ZZ" or local["platform"] == "unknown") and local["status"] != "blocked":
        errors.append("localization:unknown_market_must_block")
    if any(x["value_state"] in {"missing", "unknown"} for x in all_items) and not local["evidence_gaps"]:
        errors.append("localization:missing_without_evidence_gap")

    mapping_sources = [x["source_field"] for x in migration["mappings"]]
    if len(mapping_sources) != len(set(mapping_sources)):
        errors.append("migration:duplicate_source_field")
    for item in migration["mappings"]:
        if item["criticality"] in {"major", "safety_critical"} and item["classification"] != "lossless":
            errors.append(f"migration:critical_not_lossless:{item['source_field']}")
        if item["classification"] != "unmapped" and not item["target_field"]:
            errors.append(f"migration:missing_target:{item['source_field']}")
    if any(x["status"] != "accepted" for x in migration["consumer_acceptance"]):
        errors.append("migration:consumer_not_accepted")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        package = json.loads(args.input.read_text(encoding="utf-8"))
        errors = validate(package)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"PIPM_WP6=BLOCKED:{exc}", file=sys.stderr)
        return 1
    if errors:
        print("PIPM_WP6=BLOCKED:" + "|".join(errors), file=sys.stderr)
        return 1
    print("PIPM_WP6=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
