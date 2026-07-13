#!/usr/bin/env python3
"""Build deterministic RFM metrics and interpretable lifecycle segments."""
import argparse,csv,json
from collections import defaultdict
from datetime import date,datetime
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--as-of",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    cutoff=date.fromisoformat(a.as_of); customers=defaultdict(lambda:{"dates":[],"orders":set(),"margin":0.0})
    with open(a.input,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            d=datetime.fromisoformat(r["order_time"].replace("Z","+00:00")).date()
            if d>cutoff or r.get("status","completed") not in {"completed","paid","fulfilled"}: continue
            x=customers[r["customer_key"]]; x["dates"].append(d); x["orders"].add(r["order_id"]); x["margin"]+=float(r.get("contribution_margin") or 0)
    output=[]
    for cid,x in customers.items():
        recency=(cutoff-max(x["dates"])).days; frequency=len(x["orders"]); margin=round(x["margin"],2)
        if frequency==1 and recency<=30: segment="new"
        elif frequency>=3 and recency<=60 and margin>0: segment="high_value_active"
        elif recency<=60: segment="active"
        elif recency<=120: segment="dormant"
        else: segment="lapsed"
        output.append({"customer_key":cid,"as_of":a.as_of,"recency_days":recency,"frequency":frequency,"contribution_margin":margin,"segment":segment})
    Path(a.output).write_text(json.dumps(sorted(output,key=lambda x:x["customer_key"]),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
