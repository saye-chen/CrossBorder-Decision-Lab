#!/usr/bin/env python3
"""Evaluate a two-arm binary growth experiment with Wald interval and guardrails."""
import argparse,json,math
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args(); d=json.loads(Path(a.input).read_text())
    t,c=d["treatment"],d["control"]
    nums=[float(t["n"]),float(c["n"]),float(t["successes"]),float(c["successes"])]
    if not all(math.isfinite(x) for x in nums) or t["n"]<=0 or c["n"]<=0 or not 0<=t["successes"]<=t["n"] or not 0<=c["successes"]<=c["n"]: raise SystemExit("arms require finite n and successes within [0,n]")
    pt=t["successes"]/t["n"]; pc=c["successes"]/c["n"]; effect=pt-pc; se=math.sqrt(pt*(1-pt)/t["n"]+pc*(1-pc)/c["n"]); z=1.96
    total=t["n"]+c["n"]; expected=float(d.get("expected_treatment_share",.5))
    if not math.isfinite(expected) or not 0<expected<1: raise SystemExit("expected_treatment_share must be within (0,1)")
    srm_z=(t["n"]-total*expected)/math.sqrt(total*expected*(1-expected)); srm=abs(srm_z)>=3.29
    guardrails=[]
    for g in d.get("guardrails",[]):
        harmed=(g["direction"]=="max" and g["treatment"]>g["limit"]) or (g["direction"]=="min" and g["treatment"]<g["limit"])
        guardrails.append({**g,"passed":not harmed})
    margin=float(d.get("contribution_margin_per_incremental_success",0)); cost=float(d.get("incremental_cost_per_assigned",0)); net=effect*margin-cost
    decision="Stop" if srm or any(not g["passed"] for g in guardrails) or net<0 else ("Go" if effect-z*se>0 else "Iterate")
    out={"treatment_rate":pt,"control_rate":pc,"absolute_effect":effect,"ci95":[effect-z*se,effect+z*se],"net_incremental_value_per_assigned":net,"guardrails":guardrails,"srm":{"zscore":srm_z,"detected":srm,"expected_treatment_share":expected},"exposure_logging":d.get("exposure_logging","not_provided"),"decision":decision,"analysis":"ITT_binary_wald_basic_calculator","limitations":["binary_two_arm_only","wald_interval","does_not_replace_full_experiment_governance"]}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
