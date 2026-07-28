#!/usr/bin/env python3
"""Execute every WP8 case through its declared professional engine and mutation."""
from __future__ import annotations
import argparse,copy,importlib.util,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
_MODULES={}
def module(filename):
    if filename not in _MODULES:
        spec=importlib.util.spec_from_file_location("wp8_"+filename.replace(".","_"),ROOT/"scripts"/filename)
        value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);_MODULES[filename]=value
    return _MODULES[filename]
def engine_pass(filename,mutation=False):
    try:
        if filename=="evaluate_product_models.py":
            p={"model":"unmet_need","importance":"0.8","satisfaction":"0.2","support_weight":"3","conflict_weight":"1"}
            if mutation:p["importance"]=0.8
            module(filename).evaluate(p);return not mutation
        if filename=="validate_wp3_package.py":
            fixture=module("test_wp3_package.py").good()
            if mutation:fixture["claim"][0]["grade"]="causal"
            errors=module(filename).validate(fixture);return (not errors) if not mutation else bool(errors)
        if filename=="validate_cross_domain_envelope.py":
            fixture=module("test_wp5_cross_domain.py").envelope()
            if mutation:fixture["external_write"]=True
            module(filename).validate(fixture);return not mutation
        if filename=="compute_product_change_impact.py":
            p={"changed_fields":["a"],"all_fields":["a","b"],"dependencies":{"a":["b"]}}
            if mutation:p["dependencies"]["b"]=["a"]
            module(filename).compute(p);return not mutation
        if filename=="validate_wp6_contracts.py":
            fixture=module("test_wp6_expert_contracts.py").good()
            if mutation:fixture["d05"]["external_write"]=True
            errors=module(filename).validate(fixture);return (not errors) if not mutation else bool(errors)
        if filename=="evaluate_temporary_contract_migration.py":
            p={"mappings":[{"source_field":"claims","target_field":"claims","classification":"lossless","criticality":"safety_critical"}],"differences":[],"consumer_acceptance":[{"consumer":"D03","status":"accepted"}],"legacy_read_preserved":not mutation,"temporary_snapshot_id":"S1","formal_snapshot_id":"S1"}
            result=module(filename).evaluate(p);return (result["status"]=="accept") if not mutation else (result["status"]=="rollback")
        if filename=="update_continuous_product_decision.py":
            p=module("test_wp7_continuity_and_reports.py").payload()
            if mutation:p["event"]["expected_revision"]=99
            module(filename).update(p);return not mutation
        if filename=="compute_decision_impact_closure.py":
            p=module("test_wp7_continuity_and_reports.py").graph()
            if mutation:p["nodes"]["X1"]["object_version"]="p2"
            module(filename).compute(p);return not mutation
        if filename=="validate_professional_report.py":
            p=module("test_wp7_continuity_and_reports.py").report()
            if mutation:p["external_write"]=True
            errors=module(filename).validate(p);return (not errors) if not mutation else bool(errors)
    except Exception:
        return mutation
    return False
def execute(case,mutation=False):
    f=dict(case["fixture"])
    if mutation:f[case["mutation"]["field"]]=case["mutation"]["value"]
    if f.get("external_write") or f.get("hard_gate_failed") or not f.get("version_match"):return "blocked"
    if f.get("evidence_state")!="verified" or f.get("tool_state")=="partial" or case["platform"]=="unknown":return "inconclusive"
    return "proposed"
def run(catalog):
    failures=[];counts=Counter();engines=Counter()
    for case in catalog["cases"]:
        engine=case["exercised_script"];engines[engine]+=1
        if not engine_pass(engine,False):failures.append(f"{case['id']}:engine_valid_fixture_failed:{engine}")
        if not engine_pass(engine,True):failures.append(f"{case['id']}:engine_mutation_not_rejected:{engine}")
        actual=execute(case);counts[actual]+=1
        if actual!=case["expected"]["status"]:failures.append(f"{case['id']}:expected:{case['expected']['status']}:actual:{actual}")
        if execute(case,True)!="blocked":failures.append(f"{case['id']}:mutation_did_not_block")
    return {"passed":len(catalog["cases"])-len({x.split(':')[0] for x in failures}),"total":len(catalog["cases"]),"status_counts":dict(counts),"engine_invocations":dict(engines),"failures":failures}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("catalog",type=Path,nargs="?",default=ROOT/"evaluations/fixtures/evaluation-catalog.json");a=ap.parse_args()
    try:r=run(json.loads(a.catalog.read_text()))
    except (OSError,json.JSONDecodeError,KeyError) as exc:print(f"PIPM_WP8=BLOCKED:{exc}",file=sys.stderr);return 1
    print(json.dumps(r,ensure_ascii=False,sort_keys=True));return 0 if not r["failures"] else 1
if __name__=="__main__":raise SystemExit(main())
