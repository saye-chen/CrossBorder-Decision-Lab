#!/usr/bin/env python3
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def validate(d):
    e=[];cases=d.get("cases",[])
    if d.get("total")!=160 or len(cases)!=160:e.append("exactly_160_cases_required")
    ids=[x.get("id") for x in cases]
    if len(ids)!=len(set(ids)):e.append("duplicate_ids")
    expected={"decision":36,"calculation":36,"cross_domain":28,"multi_turn":24,"complex":20,"extreme":16}
    actual={g:sum(x.get("group")==g for x in cases) for g in expected}
    if actual!=expected:e.append(f"group_coverage:{actual}")
    if len({x.get("decision_type") for x in cases})!=6:e.append("six_decisions_required")
    if len({x.get("manufacturing_mode") for x in cases})<6:e.append("six_modes_required")
    if len({x.get("risk_route") for x in cases})<8:e.append("eight_risk_routes_required")
    if any(x["group"]=="multi_turn" and x.get("turns",0)<4 for x in cases):e.append("multiturn_four_turns_required")
    if any(not x.get("executable") or "expected" not in x["executable"] for x in cases):e.append("every_case_must_be_executable")
    signatures=[]
    for x in cases:
        executable={key:value for key,value in x.get("executable",{}).items() if key!="expected"}
        signature=hashlib.sha256(json.dumps(executable,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        signatures.append((x["group"],signature))
    if len(signatures)!=len(set(signatures)):e.append("near_duplicate_mechanisms")
    invalid_models={x.get("executable",{}).get("model") for x in cases if x.get("group")=="calculation" and x.get("executable",{}).get("expected")=="blocked"}
    valid_models={x.get("executable",{}).get("model") for x in cases if x.get("group")=="calculation" and x.get("executable",{}).get("expected")=="pass"}
    if invalid_models!=valid_models or len(valid_models)<18:e.append("every_model_requires_valid_and_invalid_case")
    if any(x.get("group") in {"complex","extreme"} and x.get("executable",{}).get("kind")!="composite" for x in cases):e.append("complex_extreme_must_execute_composite")
    response_modes={x.get("executable",{}).get("response_mode") for x in cases if x.get("group") in {"complex","extreme"}}
    if response_modes!={"rejected","partially_accepted","accepted_then_rejected","consumer_conflict"}:e.append("composite_response_breadth_required")
    return e
def main():
    d=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text());e=validate(d)
    if e:raise SystemExit("SPPQ evaluation rejected:\n- "+"\n- ".join(e))
    print("SPPQ evaluation catalog passed: 160 non-duplicate cases")
if __name__=="__main__":main()
