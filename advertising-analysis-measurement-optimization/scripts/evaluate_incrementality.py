#!/usr/bin/env python3
"""Basic two-arm ITT incrementality with normal confidence interval."""
import argparse,json,math
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args();d=json.loads(a.input.read_text());t=d["treatment"];c=d["control"]
    nt=float(t["n"]);nc=float(c["n"]);yt=float(t["value"]);yc=float(c["value"])
    if not all(math.isfinite(x) for x in (nt,nc,yt,yc)) or nt<=1 or nc<=1:p.error("arms require finite values and n > 1")
    vt=float(t.get("variance",0));vc=float(c.get("variance",0));z=float(d.get("z",1.96));spend=float(d.get("incremental_spend",0));cm=float(d.get("contribution_margin_rate",1))
    if not all(math.isfinite(x) for x in (vt,vc,z,spend,cm)) or vt<0 or vc<0 or z<=0 or spend<0 or not 0<=cm<=1:p.error("invalid variance, z, spend, or margin")
    mt=yt/nt;mc=yc/nc;diff=mt-mc;se=math.sqrt(vt/nt+vc/nc)
    out={"treatment_mean":mt,"control_mean":mc,"incremental_value_per_unit":diff,"ci":[diff-z*se,diff+z*se],"incremental_contribution":diff*nt*cm-spend,"iroas":(diff*nt)/spend if spend>0 else None,"decision":"Go" if diff-z*se>0 and diff*nt*cm-spend>0 else "Stop" if diff+z*se<0 else "Inconclusive"}
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
