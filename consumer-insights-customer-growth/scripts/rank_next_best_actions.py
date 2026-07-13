#!/usr/bin/env python3
"""Rank user-supplied uplift actions after eligibility and budget constraints."""
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); p.add_argument("--budget",type=float,default=float("inf")); a=p.parse_args(); rows=json.loads(Path(a.input).read_text())
    eligible=[]; rejected=[]
    for r in rows:
        reasons=[]
        for key in ("consent","not_unsubscribed","frequency_ok","inventory_ok","market_allowed"):
            if not r.get(key,False): reasons.append(key)
        niv=float(r.get("uplift",0))*float(r.get("contribution_margin",0))-sum(float(r.get(k,0)) for k in ("incentive_cost","contact_cost","fatigue_cost","risk_cost"))
        item={**r,"net_incremental_value":niv}
        if niv<=0: reasons.append("non_positive_niv")
        if reasons: item["rejection_reasons"]=reasons; rejected.append(item)
        else: eligible.append(item)
    eligible.sort(key=lambda x:x["net_incremental_value"],reverse=True); selected=[]; spent=0
    for r in eligible:
        cost=float(r.get("incentive_cost",0))+float(r.get("contact_cost",0))
        if spent+cost<=a.budget: selected.append(r); spent+=cost
        else: r["rejection_reasons"]=["budget"]; rejected.append(r)
    Path(a.output).write_text(json.dumps({"selected":selected,"not_selected":rejected,"spent":spent},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
