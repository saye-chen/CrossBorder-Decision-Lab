#!/usr/bin/env python3
"""Validate executable connector and platform-knowledge governance depth."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONNECTOR = ROOT / "governance/connectors/connector-lifecycle-contract.json"
KNOWLEDGE = ROOT / "governance/platform-knowledge/knowledge-lifecycle-contract.json"


def validate(connector: dict | None = None, knowledge: dict | None = None) -> list[str]:
    errors: list[str] = []
    connector = connector or json.loads(CONNECTOR.read_text())
    knowledge = knowledge or json.loads(KNOWLEDGE.read_text())
    expected_connector_states = {"draft", "contract_only", "controlled_pilot", "active", "suspended", "retired"}
    if set(connector.get("states", [])) != expected_connector_states:
        errors.append("connector lifecycle state drift")
    if connector.get("current_repository_ceiling") != "contract_only":
        errors.append("connector repository ceiling widened")
    transitions = {(x.get("from"), x.get("to")): set(x.get("requires", [])) for x in connector.get("transitions", [])}
    if "independent_review" not in transitions.get(("controlled_pilot", "active"), set()):
        errors.append("connector activation lacks independent review")
    if "reconciliation_pass" not in transitions.get(("suspended", "controlled_pilot"), set()):
        errors.append("connector recovery lacks reconciliation")
    required_failures = {"empty_response", "partial_failure", "auth_failure", "rate_limit", "schema_drift", "duplicate_or_replay", "lineage_mismatch"}
    if set(connector.get("failure_semantics", {})) != required_failures:
        errors.append("connector failure semantics incomplete")
    required_write = {"erdg_passed_packet", "exact_owner", "exact_target", "approved_operation", "human_approval", "expiry", "dry_run", "rollback", "idempotency", "audit_destination"}
    if set(connector.get("write_requirements", [])) != required_write:
        errors.append("connector action gateway binding incomplete")
    connector_prohibited = {"self_approval", "state_skip", "secret_in_repository", "empty_as_zero", "partial_as_total_success", "transport_as_decision", "automatic_reactivation"}
    if not connector_prohibited <= set(connector.get("prohibited", [])):
        errors.append("connector prohibited shortcuts incomplete")

    expected_knowledge_states = {"draft", "reviewed", "active", "stale", "invalidated", "archived"}
    if set(knowledge.get("states", [])) != expected_knowledge_states:
        errors.append("knowledge lifecycle state drift")
    knowledge_transitions = {(x.get("from"), x.get("to")): set(x.get("requires", [])) for x in knowledge.get("transitions", [])}
    if "impact_closure" not in knowledge_transitions.get(("active", "invalidated"), set()):
        errors.append("knowledge invalidation lacks impact closure")
    if "new_evidence" not in knowledge_transitions.get(("stale", "reviewed"), set()):
        errors.append("stale knowledge can reactivate without new evidence")
    required_knowledge_prohibited = {"same_source_as_independent", "manual_expiry_override", "scope_broadening", "inference_to_causality", "direct_score_change", "direct_budget_or_bid_change", "direct_replenishment_change", "external_write"}
    if not required_knowledge_prohibited <= set(knowledge.get("prohibited", [])):
        errors.append("knowledge prohibited uses incomplete")
    if set(knowledge.get("consumer_responses", [])) != {"accepted", "rejected", "recompute_required", "out_of_scope"}:
        errors.append("knowledge consumer responses incomplete")
    return errors


if __name__ == "__main__":
    errors = validate()
    print("OPERATIONAL_GOVERNANCE_DEPTH=PASS" if not errors else "OPERATIONAL_GOVERNANCE_DEPTH=FAIL\n- " + "\n- ".join(errors))
    raise SystemExit(0 if not errors else 2)
