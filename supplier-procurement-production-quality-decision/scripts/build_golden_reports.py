#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
from sppq_core import evaluate

ROOT = pathlib.Path(__file__).resolve().parents[1]

CONFIG = {
    "supplier_selection": (
        ["identity_chain", "supply_network", "capacity", "quality_history"],
        ["identity", "facility", "critical_redline", "segregation_of_duties"],
        ["D01", "D03"],
        ["retain_validated_supplier", "qualify_controlled_backup"],
    ),
    "procurement_commitment": (
        ["quote_normalization", "bom_rollup", "total_cost", "commercial_terms"],
        ["supplier_approval", "capital_authority", "cash_constraint", "compliance"],
        ["D01", "D05", "D06"],
        ["phased_purchase_order", "renegotiate_terms_and_quantity"],
    ),
    "sample_approval": (
        ["sample_chain", "ctq_coverage", "measurement_system", "revalidation"],
        ["identity", "specification", "measurement_system"],
        ["D03", "D05"],
        ["approve_controlled_sample", "repeat_sample_after_correction"],
    ),
    "production_release": (
        ["approved_sample", "process_stability", "control_plan", "capacity"],
        ["sample", "specification", "bom", "capacity", "compliance"],
        ["D03", "D05", "D06", "D07"],
        ["release_limited_pilot", "hold_and_close_process_gap"],
    ),
    "batch_quality_release": (
        ["batch_lineage", "sampling", "quantity_reconciliation", "escape_risk"],
        ["production_release", "lineage", "measurement_system", "critical_defect"],
        ["D05", "D07", "D13"],
        ["release_traceable_batch", "quarantine_and_resample"],
    ),
    "supplier_recovery_exit": (
        ["containment", "root_cause", "capa_effectiveness", "switch_exit"],
        ["affected_scope", "containment", "accountable_owner"],
        ["D01", "D05", "D06", "D07", "D13"],
        ["controlled_supplier_recovery", "activate_qualified_exit"],
    ),
}

CALCULATIONS = {
    "supplier_selection": [
        ("capacity", {"available_hours": 10, "units_per_hour": 10, "yield_rate": 0.9, "changeover_hours": 1, "uptime_rate": 0.8, "demand": 50}),
        ("concentration", {"shares": [0.5, 0.3, 0.2]}),
    ],
    "procurement_commitment": [
        ("quote_normalization", {"currency": "CNY", "fx_rate": 0.14, "quantity": 100, "unit_price": 10, "extra_costs": [20]}),
        ("bom_rollup", {"components": [{"quantity": 2, "unit_cost": 3, "scrap_rate": 0.02}]}),
        ("should_cost", {"currency": "USD", "unit": "piece", "as_of_time": "2026-07-29T00:00:00Z", "direct_material": 5, "direct_labor": 2, "machine_process": 1, "manufacturing_overhead": 1, "packaging_testing": 0.5, "risk_allowance": 0.5}),
        ("total_cost_of_ownership", {"currency": "USD", "unit": "piece", "as_of_time": "2026-07-29T00:00:00Z", "d06_inputs_accepted": True, "d07_inputs_accepted": True, "purchase": 100, "inspection": 3, "quality_failure": 7, "delay": 5, "switch_exit": 10}),
    ],
    "sample_approval": [
        ("measurement_system", {"study_variation": 1, "tolerance": 10, "process_variation": 5}),
    ],
    "production_release": [
        ("process_stability", {"values": [10, 10.1, 9.9, 10, 10.05], "max_range": 0.3}),
        ("capacity", {"available_hours": 10, "units_per_hour": 10, "yield_rate": 0.9, "changeover_hours": 1, "uptime_rate": 0.8, "demand": 50}),
    ],
    "batch_quality_release": [
        ("sampling", {"lot_id": "L1", "lot_size": 1000, "sampling_plan_id": "PLAN-1", "defect_class": "major", "sample_representative": True, "random_selection": True, "sample_size": 80, "defects": 0, "accept_number": 1, "reject_number": 2, "critical_defects": 0}),
        ("quantity_reconciliation", {"input": 100, "qualified": 90, "nonconforming": 5, "rework": 2, "scrapped": 1, "wip": 1, "explained_variance": 1}),
        ("escape_risk", {"sample_size": 80, "defects": 0}),
    ],
    "supplier_recovery_exit": [
        ("recovery_choice", {"options": [{"id": "A", "feasible": True, "loss": 10, "days": 2}, {"id": "B", "feasible": True, "loss": 12, "days": 1}]}),
        ("cost_of_quality", {"prevention": 1, "appraisal": 2, "internal_failure": 3, "external_failure": 4, "recall": 5}),
    ],
}


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def report(kind, index):
    mechanisms, gates, targets, alternatives = CONFIG[kind]
    calculations = []
    for offset, (model, payload) in enumerate(CALCULATIONS[kind], 1):
        cid = f"CAL-{index}-{offset}"
        evaluated = evaluate({"model": model, "input": payload})
        calculations.append(
            {
                "id": cid,
                "model": model,
                "input": payload,
                "output": evaluated["output"],
                "input_hash": evaluated["input_hash"],
                "output_hash": evaluated["output_hash"],
                "evidence_ids": [f"E-{index}-1"],
                "recomputed": True,
                "status": "complete",
            }
        )
    return {
        "runtime_version": "SPPQ-2026.07",
        "report_id": f"G-{index}",
        "decision_type": kind,
        "executive_summary": {
            "status": "validated",
            "conclusion": f"{kind} is conditionally executable within the declared controls",
        },
        "object_scope": {"object_id": f"O-{index}", "version": "v1", "effective_at": "2026-07-29T00:00:00Z"},
        "sovereignty": {"owner": "D04", "excluded": ["D01", "D03", "D05", "D06", "D07", "D13"]},
        "data_quality": {"grade": "E3", "missing": [], "conflicts": []},
        "hard_gates": [{"id": gate, "status": "passed", "evidence_id": f"E-{index}-{n}"} for n, gate in enumerate(gates, 1)],
        "alternatives": [
            {"id": alternative, "feasible": True, "tradeoff": f"controlled tradeoff for {alternative}"}
            for alternative in alternatives
        ],
        "professional_analysis": {
            "mechanisms": mechanisms,
            "calculation_ids": [row["id"] for row in calculations],
            "sensitivity": "decision reverses when any declared hard gate fails",
        },
        "counterevidence": [
            {
                "id": f"CE-{index}",
                "effect": "could reverse the recommendation if independently confirmed",
                "verification": "reconcile source timestamp, object identity, and independent evidence",
            }
        ],
        "decision": {
            "status": "validated",
            "limitations": ["synthetic evidence cannot establish production effectiveness"],
        },
        "cross_domain": [
            {"target": target, "response": "accepted", "contract_version": "1.0.0"}
            for target in targets
        ],
        "execution_controls": {
            "success": ["all declared gates remain passed through the effective window"],
            "stop": ["stop immediately when identity, critical defect, or authority state changes"],
            "rollback": ["restore the previous effective decision and invalidate downstream fields"],
            "recovery": ["contain affected objects, assign an owner, and recompute dependent decisions"],
        },
        "outcome_feedback": {
            "status": "pending_real_outcome",
            "metric": "decision-specific effectiveness and adverse-event recurrence",
        },
        "ledgers": {
            "evidence": [
                {"id": f"E-{index}-{n}", "hash": sha({"kind": kind, "gate": gate}), "supports": [f"hard_gates.{gate}"] + ([f"calculations.{row['id']}" for row in calculations] if n == 1 else [])}
                for n, gate in enumerate(gates, 1)
            ],
            "calculation": calculations,
            "decision": [{"id": f"D-{index}", "state": "validated", "version": "v1"}],
        },
        "limitations": ["Golden fixture validates semantics but does not close the L4 external-outcome gate"],
    }


def main():
    output = {
        "runtime_version": "SPPQ-2026.07",
        "reports": [report(kind, i) for i, kind in enumerate(CONFIG, 1)],
    }
    path = ROOT / "evaluations/golden-professional-reports.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
