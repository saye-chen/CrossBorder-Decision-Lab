#!/usr/bin/env python3
"""Deterministic cross-mode advertising economics from a JSON input."""
import argparse,json,math
from pathlib import Path

def finite(x,name):
    x=float(x)
    if not math.isfinite(x): raise ValueError(f"{name} must be finite")
    return x

def calculate(d):
    revenue=finite(d["revenue"],"revenue"); margin=finite(d["pre_ad_cm_rate"],"pre_ad_cm_rate")
    if revenue < 0 or not 0 < margin <= 1: raise ValueError("invalid revenue or pre_ad_cm_rate")
    mode=d["mode"].lower(); spend=0.0
    if mode=="cpc": spend=finite(d["clicks"],"clicks")*finite(d["cpc"],"cpc")
    elif mode=="cpm": spend=finite(d["impressions"],"impressions")/1000*finite(d["cpm"],"cpm")
    elif mode=="cpv": spend=finite(d["views"],"views")*finite(d["cpv"],"cpv")
    elif mode=="cpa": spend=finite(d["actions"],"actions")*finite(d["cpa"],"cpa")
    elif mode=="cps": spend=revenue*finite(d["cps_rate"],"cps_rate")
    elif mode=="fixed": spend=finite(d["fixed_cost"],"fixed_cost")
    elif mode=="mixed": spend=finite(d.get("fixed_cost",0),"fixed_cost")+finite(d.get("variable_spend",0),"variable_spend")+revenue*finite(d.get("cps_rate",0),"cps_rate")
    else: raise ValueError("unsupported mode")
    if spend < 0: raise ValueError("spend must be non-negative")
    contribution=revenue*margin-spend
    out={"mode":mode,"revenue":revenue,"ad_spend":round(spend,6),"pre_ad_contribution":round(revenue*margin,6),"ad_contribution_profit":round(contribution,6),"after_ad_margin":round(contribution/revenue,6) if revenue else None,"platform_roas":round(revenue/spend,6) if spend else None,"profit_roi":round(contribution/spend,6) if spend else None,"break_even_platform_roas":round(1/margin,6)}
    target_profit_roi=finite(d.get("target_profit_roi",0),"target_profit_roi")
    out["target_platform_roas"]=round((1+target_profit_roi)/margin,6)
    if all(k in d for k in ("cvr","aov")):
        cvr=finite(d["cvr"],"cvr"); aov=finite(d["aov"],"aov")
        if not 0 <= cvr <= 1 or aov < 0: raise ValueError("invalid cvr or aov")
        out["break_even_cpc"]=round(cvr*aov*margin,6); out["break_even_cpa"]=round(aov*margin,6)
    if all(k in d for k in ("ctr","cvr","aov")):
        ctr=finite(d["ctr"],"ctr")
        if not 0 <= ctr <= 1: raise ValueError("invalid ctr")
        out["break_even_cpm"]=round(1000*ctr*cvr*aov*margin,6)
    if all(k in d for k in ("view_to_click_rate","cvr","aov")):
        v=finite(d["view_to_click_rate"],"view_to_click_rate")
        if not 0 <= v <= 1: raise ValueError("invalid view_to_click_rate")
        out["break_even_cpv"]=round(v*cvr*aov*margin,6)
    out["status"]="positive" if contribution>0 else "break_even" if contribution==0 else "negative"
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    try: result=calculate(json.loads(a.input.read_text()))
    except (KeyError,ValueError,TypeError,json.JSONDecodeError) as e: p.error(str(e))
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__": main()
