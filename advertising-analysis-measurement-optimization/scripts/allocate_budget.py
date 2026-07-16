#!/usr/bin/env python3
"""Allocate discrete budget increments by positive marginal contribution under limits."""
import argparse,json,math
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();d=json.loads(a.input.read_text());budget=float(d["budget"]);items=[]
    if not math.isfinite(budget) or budget<0:p.error("budget must be finite and non-negative")
    for x in d["candidates"]:
        step=float(x["step"]); maxb=float(x["max_budget"]); mc=float(x["marginal_contribution_per_currency"])
        if not all(math.isfinite(v) for v in (step,maxb,mc)) or step<=0 or maxb<0:p.error("invalid step/max_budget/marginal contribution")
        items.append({**x,"step":step,"max_budget":maxb,"mc":mc,"allocated":0.0})
    for x in sorted(items,key=lambda y:y["mc"],reverse=True):
        while x["mc"]>0 and budget+1e-12>=x["step"] and x["allocated"]+x["step"]<=x["max_budget"]+1e-12:
            x["allocated"]+=x["step"];budget-=x["step"]
    out={"allocations":[{"id":x["id"],"allocated":x["allocated"],"marginal_contribution_per_currency":x["mc"]} for x in items],"unallocated":budget}
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
