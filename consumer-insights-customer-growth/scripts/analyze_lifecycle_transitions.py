#!/usr/bin/env python3
"""Build lifecycle transition counts and probabilities from ordered snapshots."""
import argparse,csv,json
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);a=p.parse_args();hist=defaultdict(list)
    with open(a.input,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            observed=datetime.fromisoformat(r["snapshot_at"].replace("Z","+00:00"))
            if observed.tzinfo is None: raise ValueError("snapshot_at timezone required")
            hist[r["customer_key"]].append((observed,r["state"]))
    counts=Counter()
    for rows in hist.values():
        rows.sort()
        for (_,before),(_,after) in zip(rows,rows[1:]):counts[(before,after)]+=1
    totals=Counter(before for (before,_),n in counts.items() for _ in range(n))
    out=[{"from":b,"to":t,"count":n,"from_total":totals[b],"probability":n/totals[b]} for (b,t),n in sorted(counts.items())]
    Path(a.output).write_text(json.dumps({"customers":len(hist),"transitions":out},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
