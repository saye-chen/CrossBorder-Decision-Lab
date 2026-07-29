#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re
import sys

import jsonschema
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/professional-report.schema.json").read_text())
HASH = re.compile(r"^[0-9a-f]{64}$")
CORE_SPEC = importlib.util.spec_from_file_location("sppq_report_core", ROOT / "scripts/sppq_core.py")
CORE = importlib.util.module_from_spec(CORE_SPEC)
CORE_SPEC.loader.exec_module(CORE)
ORACLE_SPEC = importlib.util.spec_from_file_location("sppq_independent_oracle", ROOT / "scripts/independent_oracles.py")
ORACLE = importlib.util.module_from_spec(ORACLE_SPEC)
ORACLE_SPEC.loader.exec_module(ORACLE)

REQUIREMENTS = {
    "supplier_selection": {
        "mechanisms": {"identity_chain", "supply_network", "capacity", "quality_history"},
        "gates": {"identity", "facility", "critical_redline", "segregation_of_duties"},
        "targets": {"D01", "D03"},
    },
    "procurement_commitment": {
        "mechanisms": {"quote_normalization", "bom_rollup", "total_cost", "commercial_terms"},
        "gates": {"supplier_approval", "capital_authority", "cash_constraint", "compliance"},
        "targets": {"D01", "D05", "D06"},
    },
    "sample_approval": {
        "mechanisms": {"sample_chain", "ctq_coverage", "measurement_system", "revalidation"},
        "gates": {"identity", "specification", "measurement_system"},
        "targets": {"D03", "D05"},
    },
    "production_release": {
        "mechanisms": {"approved_sample", "process_stability", "control_plan", "capacity"},
        "gates": {"sample", "specification", "bom", "capacity", "compliance"},
        "targets": {"D03", "D05", "D06", "D07"},
    },
    "batch_quality_release": {
        "mechanisms": {"batch_lineage", "sampling", "quantity_reconciliation", "escape_risk"},
        "gates": {"production_release", "lineage", "measurement_system", "critical_defect"},
        "targets": {"D05", "D07", "D13"},
    },
    "supplier_recovery_exit": {
        "mechanisms": {"containment", "root_cause", "capa_effectiveness", "switch_exit"},
        "gates": {"affected_scope", "containment", "accountable_owner"},
        "targets": {"D01", "D05", "D06", "D07", "D13"},
    },
}
GENERIC_VALUES = {"好", "不好", "建议优化", "处理", "恢复", "待定", "ok", "pass"}


def _ids(rows):
    return {str(row.get("id", "")) for row in rows if isinstance(row, dict)}


def validate(d):
    errors = []
    try:
        jsonschema.validate(d, SCHEMA)
    except jsonschema.ValidationError as exc:
        errors.append(f"schema:{exc.message}")
        return errors

    kind = d.get("decision_type")
    req = REQUIREMENTS.get(kind)
    if not req:
        errors.append("unsupported_decision_type")
        return errors

    mechanisms = set(d.get("professional_analysis", {}).get("mechanisms", []))
    missing_mechanisms = req["mechanisms"] - mechanisms
    if missing_mechanisms:
        errors.append("missing_mechanisms:" + ",".join(sorted(missing_mechanisms)))

    gate_ids = _ids(d.get("hard_gates", []))
    missing_gates = req["gates"] - gate_ids
    if missing_gates:
        errors.append("missing_hard_gates:" + ",".join(sorted(missing_gates)))
    gate_rows = {str(row.get("id", "")): row for row in d.get("hard_gates", []) if isinstance(row, dict)}
    if d.get("decision", {}).get("status") == "validated":
        failed = sorted(gate for gate in req["gates"] if gate_rows.get(gate, {}).get("status") != "passed")
        if failed:
            errors.append("validated_with_unpassed_gates:" + ",".join(failed))
        if d.get("executive_summary", {}).get("status") != "validated":
            errors.append("executive_decision_status_mismatch")
        quality = d.get("data_quality", {})
        if quality.get("missing") or quality.get("conflicts"):
            errors.append("validated_with_unresolved_data_quality")

    targets = {str(row.get("target", "")) for row in d.get("cross_domain", [])}
    missing_targets = req["targets"] - targets
    if missing_targets:
        errors.append("missing_cross_domain_targets:" + ",".join(sorted(missing_targets)))

    alternatives = d.get("alternatives", [])
    if len(alternatives) < 2 or len(_ids(alternatives)) < 2:
        errors.append("two_distinct_alternatives_required")

    analysis_ids = set(d.get("professional_analysis", {}).get("calculation_ids", []))
    calculations = d.get("ledgers", {}).get("calculation", [])
    calculation_ids = _ids(calculations)
    if not calculations or not analysis_ids or analysis_ids != calculation_ids:
        errors.append("calculation_ledger_must_match_analysis")
    for row in calculations:
        if not HASH.fullmatch(str(row.get("input_hash", ""))) or not HASH.fullmatch(str(row.get("output_hash", ""))):
            errors.append(f"invalid_calculation_hash:{row.get('id', '')}")
        if row.get("recomputed") is not True or row.get("status") != "complete":
            errors.append(f"calculation_not_recomputed:{row.get('id', '')}")
        if not row.get("evidence_ids"):errors.append(f"calculation_evidence_required:{row.get('id','')}")
        try:
            replayed = CORE.evaluate({"model": row.get("model"), "input": row.get("input")})
            independent = ORACLE.calculate(row.get("model"), row.get("input"))
        except (CORE.ModelError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"calculation_replay_failed:{row.get('id', '')}:{exc}")
            continue
        if row.get("input_hash") != replayed["input_hash"] or row.get("output_hash") != replayed["output_hash"] or row.get("output") != replayed["output"]:
            errors.append(f"calculation_replay_mismatch:{row.get('id', '')}")
        if independent != {"output": replayed["output"], "input_hash": replayed["input_hash"], "output_hash": replayed["output_hash"]}:
            errors.append(f"independent_oracle_mismatch:{row.get('id','')}")
        if d.get("decision",{}).get("status")=="validated":
            output=replayed["output"];model=row.get("model")
            adverse=(
                (model=="capacity" and output.get("feasible") is False)
                or (model=="measurement_system" and output.get("acceptable") is False)
                or (model=="process_stability" and output.get("stable") is False)
                or (model=="sampling" and output.get("decision")!="accept")
                or (model=="quantity_reconciliation" and output.get("balanced") is False)
            )
            if adverse:errors.append(f"validated_with_adverse_calculation:{row.get('id','')}")

    evidence_rows=d.get("ledgers", {}).get("evidence", [])
    evidence_by_id={str(row.get("id","")):row for row in evidence_rows}
    for row in evidence_rows:
        if not HASH.fullmatch(str(row.get("hash", ""))):
            errors.append(f"invalid_evidence_hash:{row.get('id', '')}")
    for gate,row in gate_rows.items():
        evidence=evidence_by_id.get(str(row.get("evidence_id","")))
        if not evidence or f"hard_gates.{gate}" not in evidence.get("supports",[]):errors.append(f"gate_evidence_lineage_missing:{gate}")
    for calculation in calculations:
        evidence_ids=calculation.get("evidence_ids",[])
        if any(evidence_id not in evidence_by_id for evidence_id in evidence_ids):errors.append(f"calculation_evidence_missing:{calculation.get('id','')}")
        elif not any(f"calculations.{calculation.get('id','')}" in evidence_by_id[evidence_id].get("supports",[]) for evidence_id in evidence_ids):errors.append(f"calculation_evidence_lineage_missing:{calculation.get('id','')}")

    counterevidence = d.get("counterevidence", [])
    if not all(row.get("effect") and row.get("verification") for row in counterevidence):
        errors.append("counterevidence_effect_and_verification_required")

    controls = d.get("execution_controls", {})
    for key in ("success", "stop", "rollback", "recovery"):
        values = controls.get(key, [])
        if not values or any(len(str(value).strip()) < 8 for value in values):
            errors.append(f"meaningful_{key}_controls_required")

    limitations = d.get("decision", {}).get("limitations", [])
    if not limitations:
        errors.append("decision_limitations_required")
    decision_states={str(row.get("state","")) for row in d.get("ledgers",{}).get("decision",[]) if isinstance(row,dict)}
    if d.get("decision",{}).get("status") not in decision_states:
        errors.append("decision_ledger_status_mismatch")
    if d.get("decision",{}).get("status")=="validated":
        rejected=sorted(str(row.get("target")) for row in d.get("cross_domain",[]) if row.get("response")!="accepted")
        if rejected:errors.append("validated_with_unaccepted_consumers:"+",".join(rejected))

    def walk(value):
        if isinstance(value, dict):
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)
        elif isinstance(value, str):
            yield value.strip().lower()

    found = sorted(GENERIC_VALUES.intersection(walk(d)))
    if found:
        errors.append("generic_semantics_forbidden:" + ",".join(found))
    return errors


def main():
    document = json.loads(pathlib.Path(sys.argv[1]).read_text())
    errors = validate(document)
    if errors:
        raise SystemExit("SPPQ report rejected:\n- " + "\n- ".join(errors))
    print("SPPQ professional report accepted")


if __name__ == "__main__":
    main()
