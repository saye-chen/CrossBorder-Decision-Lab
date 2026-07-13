#!/usr/bin/env python3
"""Calculate transparent scenario CLV and CAC payback from period margins."""
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    d=json.loads(Path(a.input).read_text()); margins=d["expected_contribution_margins"]; survival=d.get("survival",[1]*len(margins)); rate=float(d.get("discount_rate_per_period",0)); cac=float(d.get("cac",0)); future=float(d.get("expected_future_cost",0))
    if len(margins)!=len(survival): raise SystemExit("margins and survival must have equal length")
    discounted=[float(m)*float(s)/(1+rate)**(i+1) for i,(m,s) in enumerate(zip(margins,survival))]
    cumulative=0; payback=None
    for i,x in enumerate(discounted,1):
        cumulative+=x
        if payback is None and cumulative>=cac: payback=i
    out={"clv":sum(discounted)-cac-future,"discounted_contribution":discounted,"cac":cac,"payback_period":payback,"type":"scenario_not_individual_prediction"}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
