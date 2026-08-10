#!/usr/bin/env python3
"""Validate F01 blueprint bindings, foundation registry and WP-00/01 governance."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    registry = load("governance/foundation-capability-registry.json")
    schema = load("governance/foundation-capability-registry.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors.extend(f"foundation_registry:{e.message}" for e in validator.iter_errors(registry))

    foundations = {row["foundation_id"]: row for row in registry.get("foundations", [])}
    if set(foundations) != {"F01", "F02"}:
        errors.append("foundation registry must contain exactly F01 and F02")
    f01 = foundations.get("F01", {})
    if f01.get("name") != "experiment-causal-assessment" or f01.get("runtime_prefix") != "ECAE":
        errors.append("F01 canonical name/runtime drifted")
    if f01.get("availability") != "current" or f01.get("maturity") != "controlled_pilot":
        errors.append("F01 must be current/controlled_pilot after the L1-L3 release gate")
    if f01.get("owns_business_decisions") is not False or f01.get("external_write_authority") is not False:
        errors.append("F01 cannot own business decisions or external writes")
    expected_consumers = {f"D{i:02d}" for i in range(1, 15)}
    if set(f01.get("consumers", [])) != expected_consumers:
        errors.append("F01 consumers must be D01-D14")
    expected_gates = [
        "Q1_DECISION_ACTIONABILITY", "Q2_TREATMENT_DEFINITION", "Q3_ETHICS_COMPLIANCE",
        "Q4_ASSIGNMENT_IDENTIFICATION", "Q5_UNIT_INTERFERENCE", "Q6_METRIC_TIME",
        "Q7_SAMPLE_PRECISION", "Q8_DATA_AUDITABILITY", "Q9_STOPPING_MULTIPLICITY",
        "Q10_VALUE_OF_INFORMATION",
    ]
    if f01.get("blocking_gates") != expected_gates:
        errors.append("F01 Q1-Q10 registry semantics drifted from the approved blueprint")

    inventory = load("governance/f01-existing-capability-inventory.json")
    blueprint = inventory.get("blueprint", {})
    if blueprint.get("sha256") != sha256(blueprint.get("path", "")):
        errors.append("inventory blueprint hash mismatch")
    domains = inventory.get("domains", [])
    if [row.get("domain_id") for row in domains] != [f"D{i:02d}" for i in range(1, 14)]:
        errors.append("WP-00 inventory must cover D01-D13 in order")
    debts = inventory.get("technical_debts", [])
    if len(debts) != 10 or len({row.get("id") for row in debts}) != 10:
        errors.append("WP-00 must preserve ten unique technical debts")
    if inventory.get("wp00_result", {}).get("status") != "complete":
        errors.append("WP-00 inventory is not complete")

    trace = load("governance/f01-requirements-traceability.json")
    requirements = trace.get("requirements", [])
    ids = [row.get("id") for row in requirements]
    if len(ids) != len(set(ids)) or len(ids) < 30:
        errors.append("traceability requires at least thirty unique requirements")
    covered_wps = {row.get("work_package") for row in requirements}
    expected_wps = {f"WP-{i:02d}" for i in range(14)}
    if covered_wps != expected_wps:
        errors.append(f"traceability WP coverage mismatch: {sorted(expected_wps - covered_wps)}")
    allowed_status = {"planned", "in_progress", "complete", "blocked"}
    for row in requirements:
        if row.get("priority") not in {"P0", "P1", "P2"}:
            errors.append(f"{row.get('id')}:invalid priority")
        if row.get("status") not in allowed_status:
            errors.append(f"{row.get('id')}:invalid status")
        for path in row.get("artifacts", []) + row.get("tests", []):
            if Path(path).is_absolute() or ".." in Path(path).parts:
                errors.append(f"{row.get('id')}:unsafe path:{path}")
            elif row.get("status") in {"complete", "in_progress"} and not (ROOT / path).exists():
                errors.append(f"{row.get('id')}:missing traced evidence:{path}")

    manifest = load("governance/f01-implementation-manifest.json")
    if manifest.get("blueprint", {}).get("sha256") != sha256(manifest["blueprint"]["path"]):
        errors.append("implementation manifest blueprint hash mismatch")
    packages = manifest.get("work_packages", [])
    if [row.get("id") for row in packages] != [f"WP-{i:02d}" for i in range(14)]:
        errors.append("implementation manifest must contain WP-00 through WP-13")
    for package in packages:
        if package.get("status") in {"complete", "in_progress"}:
            for path in package.get("evidence", []):
                if not (ROOT / path).exists():
                    errors.append(f"{package.get('id')}:missing manifest evidence:{path}")
    if manifest.get("availability") != "current" or manifest.get("maturity") != "controlled_pilot":
        errors.append("implementation manifest release state must be current/controlled_pilot")
    boundaries = manifest.get("release_boundaries", {})
    if boundaries.get("l1_structure") is not True:
        errors.append("earned L1 structure boundary is not recorded")
    if any(boundaries.get(key) is not True for key in ("implementation_complete", "l1_structure", "l2_contract", "l3_expert")):
        errors.append("earned L1-L3 controlled-pilot boundary is incomplete")
    if any(boundaries.get(key) for key in ("independent_review", "l4_external_assurance", "production_ready", "external_write_authority")):
        errors.append("unearned L4 or production boundary marked complete")
    return sorted(set(errors))


if __name__ == "__main__":
    failures = validate()
    print("F01_GOVERNANCE=PASS" if not failures else "F01_GOVERNANCE=FAIL\n- " + "\n- ".join(failures))
    raise SystemExit(0 if not failures else 2)
