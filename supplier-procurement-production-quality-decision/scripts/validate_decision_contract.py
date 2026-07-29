#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib,sys
import jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"schemas/decision.schema.json").read_text())
COMPLIANCE_REQUIRED={"procurement_commitment","production_release","batch_quality_release"}
def validate(d):
    errors=[]
    if d.get("mode") in {"single","cross_skill"} and "professional_core" in d:
        if d.get("erdg_contract")!="ERDG-CONTRACT-2026.07":errors.append("ERDG contract mismatch")
        if d.get("decision_owner")!="supplier-procurement-production-quality-decision":errors.append("decision_owner_mismatch")
        if d.get("decision_type") not in {"supplier_selection","procurement_commitment","sample_approval","production_release","batch_quality_release","supplier_recovery_exit"}:errors.append("decision_type_not_owned")
        if d.get("runtime_versions",{}).get("supplier-procurement-production-quality-decision")!="SPPQ-2026.07":errors.append("runtime_version_mismatch")
        if d.get("external_write") is True:errors.append("ERDG forbids external write")
        if d.get("production_ready") is True:errors.append("ERDG forbids production_ready without L4")
        return errors
    try: jsonschema.Draft202012Validator(SCHEMA,format_checker=jsonschema.FormatChecker()).validate(d)
    except jsonschema.ValidationError as e: errors.append(f"schema:{e.message}")
    if d.get("decision_type") in COMPLIANCE_REQUIRED and d.get("gates",{}).get("compliance")!="passed":
        errors.append("compliance_gate_required")
    if d.get("status")=="validated":
        if not d.get("calculations"):errors.append("validated_requires_calculations")
        for gate in ("identity","sovereignty","version","evidence","segregation"):
            if d.get("gates",{}).get(gate) is not True: errors.append(f"validated_requires_{gate}")
    if d.get("external_write") is not False: errors.append("ERDG forbids external write")
    if d.get("production_ready") is not False: errors.append("ERDG forbids production_ready without L4")
    return errors
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: validate_decision_contract.py decision.json")
    try:d=json.loads(pathlib.Path(sys.argv[1]).read_text())
    except Exception as e:raise SystemExit(f"SPPQ contract invalid:{e}")
    errors=validate(d)
    if errors:raise SystemExit("SPPQ ERDG contract rejected:\n- "+"\n- ".join(errors))
    print("SPPQ decision contract accepted");return 0
if __name__=="__main__":raise SystemExit(main())
