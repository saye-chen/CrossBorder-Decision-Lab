#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from decimal import Decimal,InvalidOperation
from pathlib import Path

class ModelError(ValueError): pass
def d(v,name):
    if isinstance(v,(float,bool)): raise ModelError(f"{name}:decimal_string_required")
    try: x=Decimal(str(v))
    except InvalidOperation as exc: raise ModelError(f"{name}:invalid_decimal") from exc
    if not x.is_finite(): raise ModelError(f"{name}:non_finite")
    return x
def out(x): return format(x.normalize(),"f") if x else "0"
def gates(p):
    failed=[g["id"] for g in p.get("hard_gates",[]) if g.get("status")!="passed"]
    return failed

def unmet(p):
    i=d(p["importance"],"importance");s=d(p["satisfaction"],"satisfaction")
    support=d(p["support_weight"],"support_weight");conflict=d(p["conflict_weight"],"conflict_weight")
    if not (0<=i<=1 and 0<=s<=1 and support>=0 and conflict>=0): raise ModelError("range")
    score=i*(Decimal(1)-s)
    evidence= support/(support+conflict) if support+conflict else Decimal(0)
    return {"unmet_score":out(score),"evidence_consistency":out(evidence),"status":"blocked" if gates(p) else ("inconclusive" if evidence<Decimal("0.5") else "proposed"),"failed_gates":gates(p)}
def interval(p):
    low,base,high=(d(p[x],x) for x in ("low","base","high"))
    if low<0 or not low<=base<=high: raise ModelError("interval_order")
    return {"low":out(low),"base":out(base),"high":out(high),"width":out(high-low),"status":"blocked" if gates(p) else "proposed","failed_gates":gates(p)}
def constraints(p):
    violations=[]
    for x in p["specifications"]:
        value=d(x["value"],x["id"]);minimum=d(x["min"],x["id"]);maximum=d(x["max"],x["id"])
        if minimum>maximum or value<minimum or value>maximum: violations.append(x["id"])
        if not x.get("unit"): violations.append(x["id"]+":unit")
    selected=set(p.get("selected_features",[]))
    for a,b in p.get("mutually_exclusive",[]):
        if a in selected and b in selected: violations.append(f"exclusive:{a}:{b}")
    for feature,dependency in p.get("dependencies",[]):
        if feature in selected and dependency not in selected: violations.append(f"dependency:{feature}:{dependency}")
    failed=gates(p)
    return {"feasible":not violations and not failed,"violations":sorted(set(violations)),"failed_gates":failed,"status":"proposed" if not violations and not failed else "blocked"}
def mvp(p):
    critical=[x for x in p["assumptions"] if x.get("critical")]
    uncovered=[x["id"] for x in critical if d(x.get("coverage","0"),x["id"])<d(x.get("threshold","1"),x["id"])]
    failed=gates(p);ratio=Decimal(len(critical)-len(uncovered))/Decimal(len(critical)) if critical else Decimal(0)
    return {"critical_coverage":out(ratio),"uncovered_critical":uncovered,"status":"proposed" if critical and not uncovered and not failed else "blocked","failed_gates":failed}
def variants(p):
    demand=d(p["incremental_demand"],"incremental_demand");cann=d(p["cannibalized_demand"],"cannibalized_demand");complexity=d(p["complexity_demand_equivalent"],"complexity")
    if min(demand,cann,complexity)<0: raise ModelError("negative")
    net=demand-cann-complexity
    return {"net_incremental_demand":out(net),"cannibalization_rate":out(cann/demand) if demand else None,"status":"blocked" if gates(p) else ("proposed" if net>0 else "rejected"),"failed_gates":gates(p)}
def packaging(p):
    l,w,h=(d(p[x],x) for x in ("length_cm","width_cm","height_cm"));div=d(p["dimensional_divisor_cm3_per_kg"],"divisor")
    if min(l,w,h,div)<=0: raise ModelError("positive_required")
    volume=l*w*h;dim=volume/div;failed=gates(p)
    if d(p["protection_score"],"protection")<d(p["minimum_protection_score"],"minimum_protection"): failed.append("packaging_protection")
    return {"volume_cm3":out(volume),"dimensional_weight_kg":out(dim),"status":"blocked" if failed else "proposed","failed_gates":sorted(set(failed))}
def roadmap(p):
    required={"owner","approved_by","scope","valid_from","valid_to","source"}
    weights=p["weights"]
    for key,meta in weights.items():
        if not required<=set(meta): raise ModelError(f"weight:{key}:metadata")
    total=sum((d(v["value"],f"weight:{k}") for k,v in weights.items()),Decimal(0))
    if total!=1: raise ModelError("weights_must_sum_1")
    failed=gates(p)
    rows=[]
    for c in p["candidates"]:
        score=sum((d(c["scores"][k],f"{c['id']}:{k}")*d(meta["value"],f"weight:{k}") for k,meta in weights.items()),Decimal(0))
        rows.append((score,c["id"]))
    rows.sort(key=lambda x:(-x[0],x[1]))
    tied=len(rows)>1 and rows[0][0]==rows[1][0]
    return {"ranking":[{"id":i,"score":out(s)} for s,i in rows],"status":"blocked" if failed else ("inconclusive" if tied else "proposed"),"failed_gates":failed}
def trace(p):
    req={x["id"] for x in p["requirements"]};spec={x["id"] for x in p["specifications"]};claims={x["id"] for x in p["claims"]};ver={x["id"] for x in p["verifications"]}
    missing=[]
    for x in p["requirements"]:
        if not set(x.get("specification_ids",[])) & spec: missing.append("requirement:"+x["id"])
    for x in p["specifications"]:
        if x.get("requirement_id") not in req or not set(x.get("verification_ids",[]))&ver: missing.append("specification:"+x["id"])
    for x in p["claims"]:
        if x.get("specification_id") not in spec or not set(x.get("verification_ids",[]))&ver: missing.append("claim:"+x["id"])
    failed=gates(p)
    return {"freeze_eligible":not missing and not failed,"untraced":sorted(missing),"status":"proposed" if not missing and not failed else "blocked","failed_gates":failed}
MODELS={"unmet_need":unmet,"opportunity_interval":interval,"constraint_feasibility":constraints,"mvp_coverage":mvp,"variant_portfolio":variants,"packaging_impact":packaging,"roadmap_priority":roadmap,"traceability":trace}
def evaluate(p):
    if p.get("model") not in MODELS: raise ModelError("unknown_model")
    return {"model":p["model"],"model_version":"PIPM-MODELS-2026.01","result":MODELS[p["model"]](p)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("input",type=Path);a=ap.parse_args()
    try: result=evaluate(json.loads(a.input.read_text()))
    except (OSError,json.JSONDecodeError,KeyError,ModelError) as exc: print(f"PIPM_MODEL=BLOCKED:{exc}",file=sys.stderr);return 1
    print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
if __name__=="__main__": raise SystemExit(main())
