#!/usr/bin/env python3
"""Validate PPFC work-package-2 structure, object schemas, and state semantics."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/object-lifecycle-and-state.md",
    "schemas/economic-subject.schema.json",
    "schemas/dynamic-parameter-rule.schema.json",
    "schemas/parameter-snapshot.schema.json",
    "schemas/decision-state.schema.json",
    "references/input-evidence-and-reconciliation.md",
    "schemas/input-envelope.schema.json",
    "schemas/evidence-record.schema.json",
    "schemas/economic-reconciliation.schema.json",
    "schemas/reconciliation-result.schema.json",
    "schemas/period-delta-bridge.schema.json",
    "scripts/reconcile_economic_ledger.py",
    "scripts/test_reconciliation.py",
    "scripts/build_period_delta_bridge.py",
    "scripts/test_period_delta_bridge.py",
    "references/pricing-model-routing-and-archetypes.md",
    "references/platform-pricing-mechanism-cards.md",
    "references/professional-depth-governance.md",
    "references/skill-integration-protocol.md",
    "references/data-contract-and-automation.md",
    "references/output-protocols/professional-report-delivery.md",
    "references/unit-economics-roas-and-price-recalculation.md",
    "references/dynamic-parameter-and-freight-rules.md",
    "schemas/pricing-route.schema.json",
    "schemas/pricing-scenario.schema.json",
    "schemas/freight-route.schema.json",
    "scripts/ppfc_common.py",
    "scripts/route_pricing_model.py",
    "scripts/resolve_dynamic_parameters.py",
    "scripts/calculate_dynamic_freight.py",
    "scripts/calculate_pricing_economics.py",
    "scripts/test_pricing_models.py",
    "references/cross-domain-contract-and-exception-tree.md",
    "schemas/cross-domain-envelope.schema.json",
    "schemas/exception-report.schema.json",
    "scripts/validate_cross_domain_envelope.py",
    "scripts/validate_decision_contract.py",
    "scripts/test_cross_domain_contract.py",
    "references/localization-temporary-contract.md",
    "schemas/localization-temporary-contract.schema.json",
    "schemas/localization-migration.schema.json",
    "scripts/validate_localization_contract.py",
    "scripts/test_localization_contract.py",
    "references/professional-output-and-continuity.md",
    "schemas/professional-report.schema.json",
    "schemas/continuous-decision-state.schema.json",
    "schemas/decision-change-event.schema.json",
    "scripts/validate_professional_report.py",
    "scripts/compute_parameter_change_impact.py",
    "scripts/update_continuous_decision.py",
    "scripts/test_output_continuity.py",
    "references/mixed-batch-evaluation-contract.md",
    "schemas/mixed-batch-scenario.schema.json",
    "scripts/evaluate_mixed_batch_scenario.py",
    "scripts/test_mixed_batch_economics.py",
    "scripts/test_evaluation_catalog.py",
    "evaluations/fixtures/evaluation-catalog.json",
    "evaluations/golden/mixed-batch-10pct.input.json",
    "evaluations/golden/mixed-batch-10pct.expected.json",
    "references/migration-compatibility-and-rollback.md",
    "evaluations/migration-compatibility.json",
    "scripts/validate_migration_compatibility.py",
    "scripts/test_migration_compatibility.py",
    "evaluations/historical-replay-template.json",
    "scripts/validate_historical_replay.py",
    "scripts/test_historical_replay.py",
    "scripts/evaluate_business_model_scenario.py",
    "scripts/test_business_model_scenarios.py",
    "evaluations/fixtures/evaluation-execution-map.json",
    "scripts/validate_evaluation_execution.py",
    "scripts/test_evaluation_execution.py",
    "evaluations/consumer-adapters.json",
    "scripts/validate_consumer_adapters.py",
    "scripts/test_consumer_adapters.py",
    "scripts/evaluate_consumer_financial_boundaries.py",
    "scripts/test_consumer_financial_boundaries.py",
    "evaluations/consumer-acceptance.json",
    "evaluations/l3-audit-matrix.json",
    "evaluations/golden/single-skill-pricing-report.json",
    "evaluations/golden/multi-skill-complex-report.json",
    "evaluations/golden/continuous-pressure-report.json",
    "evaluations/rollback-drill.json",
    "evaluations/l3-review-package.json",
    "scripts/validate_acceptance_and_release.py",
    "scripts/validate_l3_audit.py",
    "scripts/test_acceptance_and_release.py",
    "scripts/test_l3_audit_matrix.py",
)
EXPECTED_STATES = {
    "draft",
    "proposed",
    "validated",
    "accepted",
    "executed",
    "observed",
    "closed",
    "inconclusive",
    "blocked",
    "rejected",
    "expired",
    "superseded",
    "rolled_back",
    "retired",
}
FORBIDDEN_TRANSITIONS = {
    ("draft", "executed"),
    ("proposed", "executed"),
    ("blocked", "accepted"),
    ("blocked", "executed"),
    ("expired", "validated"),
    ("expired", "accepted"),
    ("closed", "executed"),
    ("retired", "executed"),
}


class ContractError(ValueError):
    pass


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"{relative}: invalid JSON: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_structure() -> None:
    missing = [relative for relative in REQUIRED_FILES if not (ROOT / relative).is_file()]
    require(not missing, f"missing required files: {missing}")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
    require(frontmatter is not None, "SKILL.md frontmatter is missing")
    keys = {
        line.split(":", 1)[0].strip()
        for line in frontmatter.group(1).splitlines()
        if ":" in line
    }
    require(keys == {"name", "description"}, f"frontmatter keys must be name and description: {keys}")
    require("PPFC-2026.07" in skill, "runtime version is missing")
    require("ERDG-CONTRACT-2026.07" in skill, "ERDG contract is missing")
    for relative in REQUIRED_FILES:
        if relative.endswith((".md", ".json")) and relative != "SKILL.md":
            require(relative in skill, f"SKILL.md does not route {relative}")


def validate_schema_contracts() -> None:
    schemas = {relative: load_json(relative) for relative in REQUIRED_FILES if relative.startswith("schemas/") and relative.endswith(".json")}
    for relative, schema in schemas.items():
        require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{relative}: wrong draft")
        require(schema.get("type") == "object", f"{relative}: root must be object")
        require(schema.get("additionalProperties") is False, f"{relative}: root must fail closed")
        require(bool(schema.get("required")), f"{relative}: required list is empty")

    dynamic = schemas["schemas/dynamic-parameter-rule.schema.json"]
    dynamic_required = set(dynamic["required"])
    require(
        {"calculation_basis", "scope", "valid_from", "recorded_at", "source", "refresh_policy"} <= dynamic_required,
        "dynamic rule omits basis, scope, bitemporal, provenance, or refresh contract",
    )
    parameter_types = set(dynamic["properties"]["parameter_type"]["enum"])
    require(
        {"amount", "rate", "fixed_plus_rate", "tiered", "piecewise", "minimum", "conditional", "fx", "tax"} <= parameter_types,
        "dynamic rule does not cover required parameter families",
    )

    snapshot = schemas["schemas/parameter-snapshot.schema.json"]
    unresolved = snapshot["properties"]["unresolved_parameters"]["items"]["properties"]["status"]["enum"]
    require(
        {"MISSING_PARAMETER", "EXPIRED_PARAMETER", "BLOCKED_AMBIGUOUS_RULE", "BLOCKED_INVALID_BASIS"} <= set(unresolved),
        "snapshot omits fail-closed parameter statuses",
    )

    state = schemas["schemas/decision-state.schema.json"]
    states = set(state["properties"]["status"]["enum"])
    require(states == EXPECTED_STATES, f"state registry drift: {sorted(states ^ EXPECTED_STATES)}")

    evidence = schemas["schemas/evidence-record.schema.json"]
    require(
        set(evidence["properties"]["evidence_grade"]["enum"]) == {f"E{i}" for i in range(8)},
        "evidence registry must contain E0-E7",
    )
    reconciliation = schemas["schemas/economic-reconciliation.schema.json"]
    require(
        {"order_lines", "cost_components", "inventory", "cash_events", "reported_totals", "evidence_records"}
        <= set(reconciliation["required"]),
        "reconciliation schema omits a required ledger",
    )
    result = schemas["schemas/reconciliation-result.schema.json"]
    require(
        {"status", "data_quality", "action_ceiling", "differences", "blocking_errors", "input_hash", "result_hash"}
        <= set(result["required"]),
        "reconciliation result omits status, quality, lineage, or failure contract",
    )
    route = schemas["schemas/pricing-route.schema.json"]
    require("merchant_archetype" in route["properties"], "pricing route omits merchant archetype")
    scenario = schemas["schemas/pricing-scenario.schema.json"]
    require(
        {"price", "quantity", "discount_rate", "pass_through_tax_rate", "refund_rate", "fees"}
        <= set(scenario["required"]),
        "pricing scenario omits mandatory recalculation inputs",
    )
    freight = schemas["schemas/freight-route.schema.json"]
    require(freight["properties"]["segments"]["minItems"] == 1, "freight route must contain a segment")
    envelope = schemas["schemas/cross-domain-envelope.schema.json"]
    require(
        {"allowed_uses", "forbidden_uses", "blocked_actions", "accepted_by_receiver", "lineage"} <= set(envelope["required"]),
        "cross-domain envelope omits sovereignty, acceptance, or lineage",
    )
    exception = schemas["schemas/exception-report.schema.json"]
    require(
        {"failed_fields", "valid_retained_outputs", "action_ceiling", "recovery_owner"} <= set(exception["required"]),
        "exception report omits partial-failure or recovery semantics",
    )
    localization = schemas["schemas/localization-temporary-contract.schema.json"]
    require(
        {"fx", "tax", "unit_system", "time_zone", "settlement_calendar", "dynamic_rule", "validity"} <= set(localization["required"]),
        "localization contract omits currency, tax, unit, time, settlement, rule, or validity",
    )
    migration = schemas["schemas/localization-migration.schema.json"]
    require(
        {"field_mappings", "dual_run", "differences", "acceptance", "rollback"} <= set(migration["required"]),
        "localization migration omits mapping, dual-run, difference, acceptance, or rollback",
    )
    report = schemas["schemas/professional-report.schema.json"]
    require(
        {"current_conclusion", "history_refs", "stop_conditions", "rollback_conditions", "exit_conditions", "lineage"} <= set(report["required"]),
        "professional report omits continuity, action control, or lineage",
    )
    continuous = schemas["schemas/continuous-decision-state.schema.json"]
    require(
        {"current_decision_id", "current_version", "history", "turns", "dependencies"} <= set(continuous["required"]),
        "continuous state omits current pointer, history, turns, or dependencies",
    )
    change = schemas["schemas/decision-change-event.schema.json"]
    require(
        {"event_type", "changed_ids", "old_input_hash", "new_input_hash", "idempotency_key"} <= set(change["required"]),
        "change event omits event semantics, hashes, or idempotency",
    )
    mixed = schemas["schemas/mixed-batch-scenario.schema.json"]
    require(
        {"batch", "sample_policy", "orders", "channel_claims", "costs", "cash_events", "ending_inventory_nrv", "cash_limit"} <= set(mixed["required"]),
        "mixed batch schema omits capacity, claims, costs, inventory, or cash",
    )


def validate_transition(from_status: str | None, to_status: str) -> None:
    require(to_status in EXPECTED_STATES, f"unknown target status: {to_status}")
    if from_status is None:
        require(to_status == "draft", "initial state must be draft")
        return
    require(from_status in EXPECTED_STATES, f"unknown source status: {from_status}")
    require((from_status, to_status) not in FORBIDDEN_TRANSITIONS, f"forbidden transition: {from_status}->{to_status}")


def validate_dynamic_rule_semantics(rule: dict[str, Any]) -> None:
    value = rule.get("value")
    expression = rule.get("rule_expression")
    require((value is None) != (expression is None), "exactly one of value or rule_expression is required")
    require(rule.get("calculation_basis"), "calculation_basis is required")
    require(rule.get("scope"), "scope must contain at least one dimension")
    require(rule.get("valid_from"), "valid_from is required")
    require(rule.get("recorded_at"), "recorded_at is required")
    require(rule.get("source", {}).get("content_fingerprint"), "source fingerprint is required")
    require(rule.get("approval_status") == "approved", "only approved rules can become authoritative")


def main() -> int:
    try:
        validate_structure()
        validate_schema_contracts()
        validate_transition(None, "draft")
        for transition in FORBIDDEN_TRANSITIONS:
            try:
                validate_transition(*transition)
            except ContractError:
                continue
            raise ContractError(f"forbidden transition was accepted: {transition}")
    except ContractError as exc:
        print(f"PPFC_STRUCTURE_CONTRACT=FAIL: {exc}", file=sys.stderr)
        return 1
    print("PPFC_STRUCTURE_CONTRACT=PASS")
    print(f"root={ROOT}")
    print(f"required_files={len(REQUIRED_FILES)}")
    print(f"states={len(EXPECTED_STATES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
