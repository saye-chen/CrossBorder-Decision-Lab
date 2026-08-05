#!/usr/bin/env python3
"""D05 deterministic gate, impact closure and incident recovery rules."""
from __future__ import annotations

ACTION_RANK = {"collect_evidence": 0, "reversible_preparation": 1, "limited_internal_test": 2, "external_commercial_action": 3}
REDLINES = {"prohibited_sale", "prohibited_transport", "major_safety_risk", "certificate_fraud", "unauthorized_protected_asset", "missing_legal_entity_or_license", "sanctions_or_enforcement_block", "qualified_professional_negative_opinion", "uncontrolled_recall_risk"}


def evaluate_gate(*, redlines, evidence_gaps, professional_reviews, requested_action, staging=False):
    redline_set = set(redlines)
    unknown_redlines = redline_set - REDLINES
    if unknown_redlines:
        return {"status": "blocked", "action_ceiling": "collect_evidence", "reasons": ["unknown_redline_taxonomy"]}
    if redline_set:
        return {"status": "blocked", "action_ceiling": "collect_evidence", "reasons": sorted(redline_set)}
    if evidence_gaps:
        return {"status": "evidence_required", "action_ceiling": "collect_evidence", "reasons": sorted(set(evidence_gaps))}
    if professional_reviews:
        return {"status": "professional_review", "action_ceiling": "reversible_preparation", "reasons": sorted(set(professional_reviews))}
    ceiling = "reversible_preparation" if staging else requested_action
    if staging and ACTION_RANK[requested_action] > ACTION_RANK[ceiling]:
        return {"status": "continue_reversible_preparation", "action_ceiling": ceiling, "reasons": ["controlled_staging_cap"]}
    return {"status": "continue_with_conditions", "action_ceiling": ceiling, "reasons": []}


def impact_closure(changed_fields, dependency_graph):
    affected = set(changed_fields)
    queue = list(changed_fields)
    while queue:
        source = queue.pop(0)
        for dependent in dependency_graph.get(source, []):
            if dependent not in affected:
                affected.add(dependent); queue.append(dependent)
    universe = set(dependency_graph)
    for values in dependency_graph.values(): universe.update(values)
    return {"affected": sorted(affected), "preserved": sorted(universe - affected)}


INCIDENT_TRANSITIONS = {
    "detected": {"triaged"}, "triaged": {"contained", "investigation"}, "contained": {"investigation", "remediation", "exit"},
    "investigation": {"contained", "remediation", "professional_recheck", "exit"}, "remediation": {"professional_recheck", "recovery_review", "exit"},
    "professional_recheck": {"remediation", "recovery_review", "exit"}, "recovery_review": {"recovered", "remediation", "exit"},
    "recovered": set(), "exit": set(),
}


def validate_incident_transition(previous, current, *, affected_actions, frozen_actions, root_cause=None, recovery_conditions=None, professional_recheck=None):
    errors = []
    if current not in INCIDENT_TRANSITIONS.get(previous, set()): errors.append(f"forbidden incident transition: {previous} -> {current}")
    if previous == "detected" and not set(affected_actions).issubset(set(frozen_actions)): errors.append("triage requires all affected actions frozen")
    if current in {"recovery_review", "recovered"} and not root_cause: errors.append("recovery requires root cause")
    if current == "recovered" and (not recovery_conditions or not professional_recheck): errors.append("recovery requires conditions and professional recheck")
    return errors
