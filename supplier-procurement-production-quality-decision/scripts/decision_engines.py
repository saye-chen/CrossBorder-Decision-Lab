#!/usr/bin/env python3
from __future__ import annotations

from sppq_core import ModelError, digest, evaluate

REQUIRED_MODELS = {
    "supplier_selection": ["capacity", "concentration"],
    "procurement_commitment": ["quote_normalization", "bom_rollup", "should_cost", "total_cost_of_ownership"],
    "sample_approval": ["measurement_system"],
    "production_release": ["process_stability", "capacity"],
    "batch_quality_release": ["sampling", "quantity_reconciliation", "escape_risk"],
    "supplier_recovery_exit": ["recovery_choice", "cost_of_quality"],
}


def need(d, fields):
    return [field for field in fields if d.get(field) not in (True, "passed", "approved", "complete")]


def evidence_failures(kind,d):
    rows = d.get("evidence_bindings", [])
    if not rows:
        return ["evidence_bindings_required"]
    failures = []
    for index, row in enumerate(rows):
        if not row.get("id") or not row.get("object_version") or len(str(row.get("hash", ""))) != 64:
            failures.append(f"invalid_evidence_binding:{index}")
    for model in REQUIRED_MODELS[kind]:
        field=f"model_inputs.{model}"
        supporting=[row for row in rows if field in row.get("supported_fields",[])]
        if not supporting:failures.append(f"evidence_not_bound_to_model:{model}");continue
        expected=digest(d.get("model_inputs",{}).get(model))
        if not any(row.get("input_hashes",{}).get(model)==expected for row in supporting):failures.append(f"evidence_input_hash_mismatch:{model}")
    return failures


def execute_required_models(kind, d):
    failures = []
    calculations = []
    inputs = d.get("model_inputs", {})
    for model in REQUIRED_MODELS[kind]:
        if model not in inputs:
            failures.append(f"missing_model_input:{model}")
            continue
        try:
            evaluated=evaluate({"model": model, "input": inputs[model]});evaluated["input"]=inputs[model];calculations.append(evaluated)
        except (ModelError, KeyError, TypeError, ValueError) as exc:
            failures.append(f"model_not_computable:{model}:{exc}")
    return failures, calculations


def supplier_selection(d):
    failures = need(d, ["identity_verified", "facility_verified", "network_disclosed", "evidence_traceable", "segregation_of_duties"])
    if d.get("critical_redline"):
        failures.append("critical_redline")
    if d.get("correlated_sources"):
        failures.append("correlated_sources")
    return result(d, failures, "supplier_selection", ["supplier_identity", "facility", "network", "capacity", "quality_history"])


def procurement_commitment(d):
    failures = need(d, ["supplier_approved", "specification_current", "bom_current", "quote_current", "capital_gate", "cash_gate", "compliance_gate", "quality_agreement"])
    try:
        if d.get("quantity", 0) < d.get("moq", 0):
            failures.append("below_moq")
    except TypeError:
        failures.append("invalid_quantity_or_moq")
    if d.get("external_execution_requested"):
        failures.append("external_execution_forbidden")
    return result(d, failures, "procurement_commitment", ["quote", "bom", "moq", "payment_terms", "lead_time", "change_control"])


def sample_approval(d):
    failures = need(d, ["sample_identity", "source_traceable", "specification_current", "measurement_acceptable", "ctq_complete"])
    if d.get("failed_ctqs", 0) > 0:
        failures.append("ctq_failure")
    if d.get("sample_type") not in {"concept", "engineering", "golden", "first_article", "pilot", "retention"}:
        failures.append("invalid_sample_type")
    return result(d, failures, "sample_approval", ["sample_type", "ctq", "measurement", "deviation", "revalidation"])


def production_release(d):
    failures = need(d, ["sample_approved", "specification_current", "bom_current", "process_route_current", "control_plan_ready", "measurement_acceptable", "capacity_feasible", "compliance_gate", "segregation_of_duties"])
    if d.get("release_quantity", 0) <= 0:
        failures.append("release_quantity_required")
    return result(d, failures, "production_release", ["sample", "process", "control_plan", "capacity", "exposure_limit"])


def batch_quality_release(d):
    failures = need(d, ["production_released", "batch_lineage_complete", "inspection_complete", "quantity_balanced", "measurement_acceptable", "segregation_of_duties"])
    if d.get("critical_defects", 0) > 0:
        failures.append("critical_defect")
    if d.get("inspection_decision") not in {"accept", "reject"}:
        failures.append("inspection_decision_missing")
    if d.get("inspection_decision") == "reject":
        failures.append("inspection_rejected")
    return result(d, failures, "batch_quality_release", ["batch", "inspection", "quantity", "deviation", "escape_risk"])


def supplier_recovery_exit(d):
    failures = need(d, ["affected_scope_known", "containment_active", "owner_assigned", "evidence_preserved"])
    if d.get("capa_claimed") and not d.get("capa_effectiveness_verified"):
        failures.append("capa_not_effective")
    if not d.get("options"):
        failures.append("recovery_options_required")
    return result(d, failures, "supplier_recovery_exit", ["containment", "root_cause", "capa", "switch", "exit", "residual_risk"], "recovery_required")


def result(d, failures, kind, mechanisms, blocked="blocked"):
    model_failures, calculations = execute_required_models(kind, d)
    failures.extend(evidence_failures(kind,d))
    failures.extend(model_failures)
    outputs = {row["model"]: row["output"] for row in calculations}
    if outputs.get("capacity", {}).get("feasible") is False:
        failures.append("calculated_capacity_not_feasible")
    if outputs.get("process_stability", {}).get("stable") is False:
        failures.append("calculated_process_not_stable")
    if outputs.get("measurement_system", {}).get("acceptable") is False:
        failures.append("calculated_measurement_not_acceptable")
    if outputs.get("sampling", {}).get("decision") == "reject":
        failures.append("calculated_sampling_rejected")
    if outputs.get("quantity_reconciliation", {}).get("balanced") is False:
        failures.append("calculated_quantity_not_balanced")
    failures = list(dict.fromkeys(failures))
    return {"decision_type": kind, "status": blocked if failures else "validated", "failures": failures, "mechanisms": mechanisms, "calculations": calculations}


ROUTES = {
    "supplier_selection": supplier_selection,
    "procurement_commitment": procurement_commitment,
    "sample_approval": sample_approval,
    "production_release": production_release,
    "batch_quality_release": batch_quality_release,
    "supplier_recovery_exit": supplier_recovery_exit,
}


def decide(kind, payload):
    if kind not in ROUTES:
        raise ModelError("unknown_decision_type")
    return ROUTES[kind](payload)
