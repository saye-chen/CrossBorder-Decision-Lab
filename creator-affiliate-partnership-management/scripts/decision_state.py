#!/usr/bin/env python3
"""Validate progressive CAPM report inheritance and recomputation closure."""
from __future__ import annotations
import argparse
from capm_common import emit, load_json, sha256_json


REQUIRED = {"report_id", "parent_report_id", "object_id", "object_version", "changed_fields", "new_evidence_ids",
            "affected_claims", "affected_calculations", "preserved_constraints", "superseded_actions",
            "current_actions", "next_recompute_trigger"}


def validate(data: dict, parent: dict | None = None) -> dict:
    errors = []
    missing = sorted(REQUIRED - set(data))
    if missing: errors.append(f"missing:{','.join(missing)}")
    if data.get("report_id") == data.get("parent_report_id"):
        errors.append("report_cannot_parent_itself")
    if data.get("parent_report_id") and parent is None:
        errors.append("parent_state_required")
    if parent is not None:
        if data.get("parent_report_id") != parent.get("report_id"):
            errors.append("parent_report_mismatch")
        if data.get("object_id") != parent.get("object_id"):
            errors.append("object_changed_without_new_chain")
        if data.get("object_version") == parent.get("object_version") and data.get("changed_fields"):
            errors.append("changed_fields_without_new_object_version")
        inherited = set(parent.get("current_actions", [])) - set(data.get("superseded_actions", []))
        if not inherited.issubset(set(data.get("current_actions", []))):
            errors.append("current_actions_dropped_without_supersede")
    superseded = set(data.get("superseded_actions", []))
    current = set(data.get("current_actions", []))
    if superseded & current:
        errors.append("superseded_action_still_current")
    sensitive = {"currency", "tax", "refund_basis", "rights", "object_id", "evidence_withdrawal"}
    if sensitive & set(data.get("changed_fields", [])) and not data.get("affected_calculations"):
        errors.append("sensitive_change_without_recalculation")
    if data.get("new_object", False) and data.get("parent_report_id"):
        errors.append("new_object_cannot_inherit_parent_evidence")
    if data.get("new_object", False) and (data.get("new_evidence_ids") or data.get("preserved_constraints")):
        errors.append("new_object_cannot_inherit_evidence_or_constraints")
    if data.get("evidence_withdrawal_ids") and not data.get("affected_claims"):
        errors.append("evidence_withdrawal_without_affected_claims")
    if not data.get("next_recompute_trigger"):
        errors.append("missing_recompute_trigger")
    return {"valid": not errors, "errors": errors, "state_hash": sha256_json(data)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); p.add_argument("--parent"); a = p.parse_args(); result = validate(load_json(a.input), load_json(a.parent) if a.parent else None); emit(result); raise SystemExit(0 if result["valid"] else 1)
