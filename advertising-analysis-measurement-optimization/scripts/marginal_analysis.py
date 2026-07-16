#!/usr/bin/env python3
"""Compute adjacent-budget average and marginal performance."""
import argparse,json,math
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args(); rows=json.loads(a.input.read_text())
    if not isinstance(rows,list) or not rows:p.error("input must be a non-empty list")
    try: rows=sorted(rows,key=lambda x:float(x["spend"]))
    except (KeyError,TypeError,ValueError):p.error("each row requires numeric spend")
    out=[];seen=set()
    for i,r in enumerate(rows):
        try:s=float(r["spend"]);rev=float(r["mature_revenue"]);profit=float(r["contribution_profit"])
        except (KeyError,TypeError,ValueError):p.error(f"row {i+1} requires numeric fields")
        if not all(math.isfinite(x) for x in (s,rev,profit)) or s<0:p.error(f"row {i+1} invalid numeric value")
        if s in seen:p.error("spend stages must be unique")
        seen.add(s)
        x={"spend":s,"mature_revenue":rev,"contribution_profit":profit,"average_roas":rev/s if s else None}
        if i:
            ds=s-float(rows[i-1]["spend"]); x["marginal_roas"]=(rev-float(rows[i-1]["mature_revenue"]))/ds if ds>0 else None;x["marginal_contribution"]=(profit-float(rows[i-1]["contribution_profit"]))/ds if ds>0 else None
        out.append(x)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
