#!/usr/bin/env python3
"""Validate a Decision Cycle against the authoritative D01-D14 registry."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = json.loads((ROOT / "governance/domain-architecture-registry.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "governance/erdg/schemas/decision-cycle.schema.json").read_text(encoding="utf-8"))
DOMAINS = {item["domain_id"]: item for item in REGISTRY["domains"]}
DECISION_OWNERS = {
    decision_type: item["domain_id"]
    for item in REGISTRY["domains"]
    for decision_type in item["owned_decision_types"]
}


def validate(payload: dict) -> list[str]:
    errors = [
        f"schema: {error.message}"
        for error in sorted(jsonschema.Draft202012Validator(SCHEMA).iter_errors(payload), key=lambda item: list(item.path))
    ]
    if errors:
        return errors
    if payload["architecture_version"] != REGISTRY["architecture_version"]:
        errors.append("architecture_version does not match the authoritative registry")

    participants = {item["domain_id"]: item for item in payload["participants"]}
    if len(participants) != len(payload["participants"]):
        errors.append("participants contain duplicate domains")
    for domain_id, participant in participants.items():
        domain = DOMAINS.get(domain_id)
        if domain is None:
            errors.append(f"unknown participant domain: {domain_id}")
            continue
        if participant["availability"] != domain["availability"]:
            errors.append(f"{domain_id}: availability does not match registry")
        if domain["availability"] != "current" and participant["status"] not in {"pending", "blocked", "not_required"}:
            errors.append(f"{domain_id}: unavailable domain cannot execute")

    stages = {item["stage_id"]: item for item in payload["stages"]}
    if len(stages) != len(payload["stages"]):
        errors.append("stages contain duplicate stage IDs")
    for stage_id, stage in stages.items():
        missing = sorted(set(stage["participant_domains"]) - set(participants))
        if missing:
            errors.append(f"{stage_id}: stage participants are not registered in cycle: {missing}")
        unknown_dependencies = sorted(set(stage["dependencies"]) - set(stages))
        if unknown_dependencies:
            errors.append(f"{stage_id}: unknown stage dependencies: {unknown_dependencies}")
        unavailable = [
            domain_id
            for domain_id in stage["participant_domains"]
            if domain_id in DOMAINS and DOMAINS[domain_id]["availability"] != "current"
        ]
        if unavailable and stage["status"] not in {"pending", "blocked", "skipped"}:
            errors.append(f"{stage_id}: stage cannot execute unavailable domains: {unavailable}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(stage_id: str) -> None:
        if stage_id in visiting:
            errors.append(f"stage dependency cycle detected at {stage_id}")
            return
        if stage_id in visited or stage_id not in stages:
            return
        visiting.add(stage_id)
        for dependency in stages[stage_id]["dependencies"]:
            visit(dependency)
        visiting.remove(stage_id)
        visited.add(stage_id)

    for stage_id in stages:
        visit(stage_id)

    for gate in payload["gates"]:
        missing = sorted(set(gate["required_stage_ids"]) - set(stages))
        if missing:
            errors.append(f"{gate['gate_id']}: unknown required stages: {missing}")
        if gate["status"] == "passed":
            incomplete = [
                stage_id
                for stage_id in gate["required_stage_ids"]
                if stage_id in stages and stages[stage_id]["status"] != "completed"
            ]
            if incomplete:
                errors.append(f"{gate['gate_id']}: passed gate has incomplete stages: {incomplete}")
        if gate["status"] in {"blocked", "partially_passed"}:
            if not gate["blocking_reasons"] or not gate["recovery_requirements"]:
                errors.append(f"{gate['gate_id']}: blocked or partial gate requires reasons and recovery")

    for decision in payload["current_effective_decisions"]:
        expected = DECISION_OWNERS.get(decision["decision_type"])
        if expected is None:
            errors.append(f"unknown decision type: {decision['decision_type']}")
        elif decision["owner_domain_id"] != expected:
            errors.append(f"{decision['decision_type']}: owner must be {expected}, got {decision['owner_domain_id']}")
        elif DOMAINS[expected]["availability"] != "current":
            errors.append(f"{decision['decision_type']}: unavailable owner cannot issue an effective decision")

    if payload["current_phase"] == "blocked" and "partial_failure" not in payload:
        errors.append("blocked cycle requires partial_failure")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    errors = validate(json.loads(args.input.read_text(encoding="utf-8")))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ERDG decision cycle v2 semantic validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
