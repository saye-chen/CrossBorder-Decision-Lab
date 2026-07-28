#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker

ROOT=Path(__file__).resolve().parents[1]
FILES={"input":"input-envelope.schema.json","evidence":"evidence-record.schema.json","claim":"claim-record.schema.json","calculation":"calculation-record.schema.json","decision":"decision-skeleton.schema.json"}

def schema_errors(name,payload):
    schema=json.loads((ROOT/"schemas"/FILES[name]).read_text())
    return [e.message for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(payload)]

def validate(package:dict)->list[str]:
    errors=[]
    for name in FILES:
        value=package.get(name)
        values=value if isinstance(value,list) else [value]
        if value is None: errors.append(f"missing:{name}");continue
        for i,item in enumerate(values):
            if not isinstance(item,dict): errors.append(f"{name}[{i}]:not_object");continue
            errors.extend(f"{name}[{i}]:{x}" for x in schema_errors(name,item))
    evidence={x.get("evidence_id") for x in package.get("evidence",[]) if isinstance(x,dict)}
    claims={x.get("claim_id") for x in package.get("claim",[]) if isinstance(x,dict)}
    calculations={x.get("calculation_id") for x in package.get("calculation",[]) if isinstance(x,dict)}
    for claim in package.get("claim",[]):
        if claim.get("state")=="validated" and not claim.get("evidence_ids"): errors.append(f"claim:{claim.get('claim_id')}:validated_without_evidence")
        if claim.get("grade")=="causal": errors.append(f"claim:{claim.get('claim_id')}:causal_blocked_until_f01")
        for ref in claim.get("evidence_ids",[]):
            if ref not in evidence: errors.append(f"claim:{claim.get('claim_id')}:unknown_evidence:{ref}")
        if set(claim.get("allowed_uses",[])) & set(claim.get("forbidden_uses",[])): errors.append(f"claim:{claim.get('claim_id')}:use_conflict")
    decision=package.get("decision",{})
    for field,known in (("evidence_ids",evidence),("claim_ids",claims),("calculation_ids",calculations)):
        for ref in decision.get(field,[]):
            if ref not in known: errors.append(f"decision:unknown_{field}:{ref}")
    unresolved=[g for g in decision.get("hard_gates",[]) if g.get("status")!="passed"]
    if unresolved and decision.get("state") not in {"blocked","inconclusive","rejected"}: errors.append("decision:unresolved_gate_must_block")
    for field in package.get("input",{}).get("fields",[]):
        state=field.get("value_state")
        if state not in {"observed","observed_zero"} and field.get("value")==0: errors.append(f"input:{field.get('field_id')}:missing_silently_zero")
    return errors

def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("input",type=Path);args=parser.parse_args()
    try: package=json.loads(args.input.read_text());errors=validate(package)
    except (OSError,json.JSONDecodeError) as exc: print(f"PIPM_WP3=BLOCKED:{exc}",file=sys.stderr);return 1
    if errors: print("PIPM_WP3=BLOCKED:"+"|".join(errors),file=sys.stderr);return 1
    print("PIPM_WP3=PASS");return 0
if __name__=="__main__": raise SystemExit(main())
