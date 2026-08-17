#!/usr/bin/env python3
"""Calculate purchase-cohort retention with immature cells left null."""
import argparse,csv,json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def month_index(d): return d.year*12+d.month-1
def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--as-of",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    cutoff_dt=datetime.fromisoformat(a.as_of.replace("Z","+00:00"))
    if cutoff_dt.tzinfo is None: p.error("--as-of timezone required")
    cutoff=cutoff_dt.date(); purchases=defaultdict(set)
    with open(a.input,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            order_dt=datetime.fromisoformat(r["order_time"].replace("Z","+00:00"))
            if order_dt.tzinfo is None: p.error("order_time timezone required")
            d=order_dt.date()
            if d<=cutoff: purchases[r["customer_key"]].add((d.year,d.month))
    cohorts=defaultdict(list)
    for cid,months in purchases.items(): cohorts[min(months)].append((cid,months))
    result=[]; cutoff_i=month_index(cutoff)
    for cohort,members in sorted(cohorts.items()):
        base=cohort[0]*12+cohort[1]-1; cells=[]
        for age in range(cutoff_i-base+1):
            active=sum(( (base+age)//12, (base+age)%12+1 ) in months for _,months in members)
            cell_period=(base+age)//12, (base+age)%12+1
            mature=cell_period < (cutoff.year, cutoff.month)
            cells.append({"month":age,"active":active,"base":len(members),
                          "mature":mature,
                          "retention":active/len(members) if mature else None})
        result.append({"cohort":f"{cohort[0]:04d}-{cohort[1]:02d}","cells":cells})
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
