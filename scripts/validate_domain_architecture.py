#!/usr/bin/env python3
"""Validate the D01-D14 target architecture without treating planned domains as live."""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "governance/domain-architecture-registry.json"
SCHEMA_PATH = ROOT / "governance/domain-architecture-registry.schema.json"
MATURITY_PATH = ROOT / "governance/domain-maturity-status.json"


def validate() -> list[str]:
    errors: list[str] = []
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(registry, schema)
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError, jsonschema.ValidationError) as exc:
        return [f"domain architecture registry is invalid: {exc}"]

    domains = registry["domains"]
    expected_ids = [f"D{index:02d}" for index in range(1, 15)]
    ids = [item["domain_id"] for item in domains]
    if ids != expected_ids:
        errors.append(f"domain IDs must be ordered D01-D14, got {ids}")

    for field in ("skill", "runtime_prefix"):
        values = [item[field] for item in domains]
        if len(values) != len(set(values)):
            errors.append(f"{field} must be unique")

    owners: dict[str, str] = {}
    authorities: dict[str, str] = {}
    known_ids = set(ids)
    for domain in domains:
        domain_id = domain["domain_id"]
        if domain_id in domain["hard_dependencies"] or domain_id in domain["optional_dependencies"]:
            errors.append(f"{domain_id}: self dependency is forbidden")
        unknown_dependencies = sorted(
            (set(domain["hard_dependencies"]) | set(domain["optional_dependencies"])) - known_ids
        )
        if unknown_dependencies:
            errors.append(f"{domain_id}: unknown dependencies {unknown_dependencies}")
        for decision_type in domain["owned_decision_types"]:
            previous = owners.setdefault(decision_type, domain_id)
            if previous != domain_id:
                errors.append(f"decision type {decision_type!r} has multiple owners: {previous}, {domain_id}")
        for authority in domain["decision_authorities"]:
            previous = authorities.setdefault(authority, domain_id)
            if previous != domain_id:
                errors.append(f"decision authority {authority!r} has multiple owners: {previous}, {domain_id}")

    current = {item["skill"] for item in domains if item["availability"] == "current"}
    unavailable = {item["skill"] for item in domains if item["availability"] in {"next_build", "planned"}}
    non_domain_utility_skills = {"article-draft-publisher", "authored-voice"}
    discovered = {path.parent.name for path in ROOT.glob("*/SKILL.md")} - non_domain_utility_skills
    if current != discovered:
        errors.append(f"current registry/repository mismatch missing={sorted(discovered-current)} extra={sorted(current-discovered)}")
    accidentally_live = sorted(skill for skill in unavailable if (ROOT / skill / "SKILL.md").is_file())
    if accidentally_live:
        errors.append(f"planned or next-build domains cannot expose live SKILL.md: {accidentally_live}")

    maturity = json.loads(MATURITY_PATH.read_text(encoding="utf-8"))
    mature_skills = {item["skill"] for item in maturity["domains"]}
    if mature_skills != current:
        errors.append(f"current registry/maturity mismatch missing={sorted(current-mature_skills)} extra={sorted(mature_skills-current)}")

    adapters = {path.parent.name for path in (ROOT / "governance/erdg/adapters").glob("*/adapter.json")}
    if adapters != current:
        errors.append(f"current registry/adapter mismatch missing={sorted(current-adapters)} extra={sorted(adapters-current)}")
    for skill in sorted(current):
        adapter_path = ROOT / "governance/erdg/adapters" / skill / "adapter.json"
        try:
            adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{skill}: invalid ERDG adapter: {exc}")
            continue
        domain = next(item for item in domains if item["skill"] == skill)
        if adapter.get("version") != "2.0.0":
            errors.append(f"{skill}: adapter version must be 2.0.0")
        if adapter.get("contract") != "ERDG-CONTRACT-2026.07":
            errors.append(f"{skill}: adapter must use ERDG-CONTRACT-2026.07")
        if adapter.get("handoff_schema") != "governance/erdg/schemas/handoff-envelope.schema.json":
            errors.append(f"{skill}: adapter does not route the sole v2 handoff schema")
        if adapter.get("decision_cycle_schema") != "governance/erdg/schemas/decision-cycle.schema.json":
            errors.append(f"{skill}: adapter does not route Decision Cycle")
        if adapter.get("accepts_v1") is not False:
            errors.append(f"{skill}: adapter must reject v1")
        if adapter.get("owned_decision_types") != domain["owned_decision_types"]:
            errors.append(f"{skill}: adapter decision ownership differs from registry")

    plane = registry["governance_plane"]
    if plane["owns_business_decisions"] is not False:
        errors.append("ERDG governance plane must not own business decisions")
    if plane["contract"] != "ERDG-CONTRACT-2026.07":
        errors.append("all domains must use the authoritative ERDG-CONTRACT-2026.07")

    orchestrators = [item for item in domains if "orchestration" in item["architecture_roles"]]
    if [item["domain_id"] for item in orchestrators] != ["D14"]:
        errors.append("D14 must be the sole orchestration domain")
    else:
        orchestrator = orchestrators[0]
        expected_types = {
            "task_orchestration",
            "dependency_plan",
            "conflict_escalation",
            "operating_posture_synthesis",
            "approved_resource_sequencing",
        }
        expected_constraints = {
            "preserve_domain_decision_sovereignty",
            "accept_only_owner_approved_decisions",
            "sequence_only_within_approved_envelopes",
            "escalate_conflicts_without_adjudicating_professional_conclusions",
            "no_external_write",
        }
        if set(orchestrator["owned_decision_types"]) != expected_types:
            errors.append("D14 may own orchestration and synthesis only, not professional decisions")
        if set(orchestrator.get("orchestration_constraints", [])) != expected_constraints:
            errors.append("D14 orchestration sovereignty constraints are incomplete")
        if orchestrator["external_write_authority"] is not False:
            errors.append("D14 cannot own external write authority")
        forbidden_authority_fragments = (
            "capital allocation",
            "capital add-reduce-exit",
            "budget approval",
            "professional conclusion",
            "root cause decision",
        )
        authority_text = " ".join(orchestrator["decision_authorities"]).lower()
        if any(fragment in authority_text for fragment in forbidden_authority_fragments):
            errors.append("D14 decision authority overlaps a professional or capital owner")

    d05 = next((item for item in domains if item["domain_id"] == "D05"), None)
    if d05 is None:
        errors.append("D05 must be registered")
    else:
        expected_d05_types = {
            "market_access_gate",
            "compliance_action_ceiling",
            "claim_use_boundary",
            "professional_review_routing",
            "compliance_recovery",
        }
        if set(d05["owned_decision_types"]) != expected_d05_types:
            errors.append("D05 owns commercial gates and professional-review routing only")
        forbidden_d05_types = {
            "legal_access",
            "regulatory_compliance",
            "tax_treatment",
            "intellectual_property",
            "certification_access",
            "legal_conclusion",
            "freedom_to_operate_opinion",
        }
        if set(d05["owned_decision_types"]) & forbidden_d05_types:
            errors.append("D05 cannot register reserved qualified-professional conclusions")
        required_outputs = {"professional_review_request", "professional_opinion_receipt"}
        if not required_outputs.issubset(d05["provides"]):
            errors.append("D05 must route and receive qualified professional review explicitly")
        if "professional_opinion" in d05["provides"]:
            errors.append("D05 cannot present itself as the issuer of a professional opinion")
        if d05["external_write_authority"] is not False:
            errors.append("D05 cannot own external write authority")

    for name in ("handoff-envelope.schema.json", "decision-cycle.schema.json"):
        path = ROOT / "governance/erdg/schemas" / name
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(value)
        except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
            errors.append(f"{name}: invalid schema: {exc}")
    retired = (
        ROOT / "governance/erdg/schemas/handoff-envelope-v2.schema.json",
        ROOT / "governance/erdg/scripts/validate_handoff_v2.py",
        ROOT / "governance/erdg/scripts/migrate_contract.py",
        ROOT / "governance/erdg/migration-manifest.json",
    )
    for path in retired:
        if path.exists():
            errors.append(f"retired v1 or dual-track artifact must not exist: {path.relative_to(ROOT)}")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        raise SystemExit("Domain architecture validation failed:\n- " + "\n- ".join(failures))
    print("Domain architecture validation passed for D01-D14; 13 current and D14 planned.")
