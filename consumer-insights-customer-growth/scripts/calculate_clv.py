#!/usr/bin/env python3
"""Calculate transparent scenario CLV and CAC payback from period margins."""
import argparse,json,math
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    d=json.loads(Path(a.input).read_text()); margins=d["expected_contribution_margins"]; survival=d.get("survival",[1]*len(margins)); rate=float(d.get("discount_rate_per_period",0)); cac=float(d.get("cac",0)); future=float(d.get("expected_future_cost",0))
    if not margins or len(margins)!=len(survival): raise SystemExit("margins and survival must be non-empty and equal length")
    values=[*map(float,margins),*map(float,survival),rate,cac,future]
    if not all(math.isfinite(x) for x in values): raise SystemExit("all numeric inputs must be finite")
    if rate<=-1 or cac<0 or future<0 or any(not 0<=float(s)<=1 for s in survival): raise SystemExit("invalid rate, cost, or survival")
    discounted=[float(m)*float(s)/(1+rate)**(i+1) for i,(m,s) in enumerate(zip(margins,survival))]
    cumulative=0; payback=None
    for i,x in enumerate(discounted,1):
        cumulative+=x
        if payback is None and cumulative>=cac: payback=i
    gross=sum(discounted);net=gross-cac-future
    intervals={}
    for label,values in d.get("contribution_margin_scenarios",{}).items():
        if len(values)!=len(survival): raise SystemExit("scenario margins and survival must have equal length")
        g=sum(float(m)*float(s)/(1+rate)**(i+1) for i,(m,s) in enumerate(zip(values,survival)))
        intervals[label]={"gross_customer_value":g,"net_clv":g-cac-future}
    out={"gross_customer_value":gross,"net_clv":net,"clv":net,"value_basis":"contribution_margin","discounted_contribution":discounted,"cac":cac,"expected_future_cost":future,"payback_period":payback,"scenarios":intervals,"type":"scenario_not_individual_prediction"}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
