#!/usr/bin/env python3
"""Validate PIPM professional report envelope, specialized depth and canonical hash."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
"product_opportunity_brief":{"unmet_need","user_job","opportunity_interval","weakest_assumption","evidence_plan"},
"product_definition":{"target_user","use_context","value_proposition","requirements","non_goals"},
"mvp_decision":{"learning_goal","minimum_scope","excluded_scope","validation_design","thresholds"},
"product_specification_decision":{"traceability","units_and_tolerances","ctqs","interfaces","verification_methods"},
"variant_packaging_decision":{"variant_roles","complexity","cannibalization","packaging_levels","exit_rules"},
"product_validation_report":{"protocol","sample","bias","heterogeneity","failure_modes","applicability"},
"product_change_impact_report":{"old_new_values","effective_time","impact_closure","expired","preserved","reacceptance"},
"product_roadmap":{"dependencies","resource_constraints","stage_gates","option_value","delay_cost","exit_rules"},
"product_stop_retire_decision":{"stop_reason","customer_commitments","substitutes","inventory_dependencies","support_dependencies","reactivation_rule"},
}

def report_hash(report:dict)->str:
    value=copy.deepcopy(report); value["lineage"]["report_hash"]="sha256:"
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return "sha256:"+hashlib.sha256(raw).hexdigest()

def validate(report:dict)->list[str]:
    schema=json.loads((ROOT/"schemas/professional-report.schema.json").read_text())
    errors=[f"schema:{e.message}" for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(report)]
    if errors:return errors
    missing=REQUIRED[report["report_type"]]-set(report["specific_content"])
    if missing:errors.append("missing_specialized:"+",".join(sorted(missing)))
    if set(report["allowed_uses"]) & set(report["forbidden_uses"]):errors.append("use_conflict")
    if report["decision_state"]=="validated" and (report["conflicts"] or report["missing_and_expired"]):errors.append("validated_with_open_conflict")
    if report["lineage"]["report_hash"]!=report_hash(report):errors.append("report_hash_mismatch")
    if report["external_write"] is not False:errors.append("external_write")
    return errors

def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("input",type=Path);args=parser.parse_args()
    try:errors=validate(json.loads(args.input.read_text()))
    except (OSError,json.JSONDecodeError) as exc:print(f"PIPM_REPORT=BLOCKED:{exc}",file=sys.stderr);return 1
    if errors:print("PIPM_REPORT=BLOCKED:"+"|".join(errors),file=sys.stderr);return 1
    print("PIPM_REPORT=PASS");return 0
if __name__=="__main__":raise SystemExit(main())
