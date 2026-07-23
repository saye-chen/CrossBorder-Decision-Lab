#!/usr/bin/env python3
"""Fit a transparent adstock-Hill media response with a time holdout."""
import argparse,json,math
from pathlib import Path
from aamo_statistics import numbers,ols,mean

def adstock(xs,decay):
    out=[]; state=0
    for x in xs: state=x+decay*state; out.append(state)
    return out
def hill(xs,half,slope): return [(x**slope)/(x**slope+half**slope) if x>0 else 0 for x in xs]
def fit(p):
    spend=numbers(p.get("spend"),"spend",10); outcome=numbers(p.get("outcome"),"outcome",10)
    if len(spend)!=len(outcome): raise ValueError("spend and outcome must align")
    holdout=int(p.get("holdout_periods",max(2,len(spend)//5)))
    if holdout<2 or len(spend)-holdout<6: raise ValueError("need at least six train and two holdout periods")
    decays=p.get("decay_grid",[0,.3,.6,.8]); halves=p.get("half_saturation_grid")
    if halves is None:
        positive=sorted(x for x in spend if x>0); base=positive[len(positive)//2] if positive else 1
        halves=[base*.5,base,base*2]
    slopes=p.get("hill_slope_grid",[.7,1,1.5])
    best=None
    for d in decays:
      if not 0<=float(d)<1: raise ValueError("decay must be in [0,1)")
      stocked=adstock(spend,float(d))
      for h in halves:
       for s in slopes:
        feature=hill(stocked,float(h),float(s)); model=ols(feature[:-holdout],outcome[:-holdout],"media_response")
        pred=[model["intercept"]+model["slope"]*x for x in feature[-holdout:]]
        rmse=math.sqrt(sum((a-b)**2 for a,b in zip(outcome[-holdout:],pred))/holdout)
        candidate=(rmse,float(d),float(h),float(s),model,feature,pred)
        if best is None or rmse<best[0]: best=candidate
    rmse,d,h,s,model,feature,pred=best
    baseline_rmse=math.sqrt(sum((x-mean(outcome[:-holdout]))**2 for x in outcome[-holdout:])/holdout)
    return {"method":"adstock_hill_time_holdout","decay":d,"half_saturation":h,"hill_slope":s,
            "coefficient":model["slope"],"intercept":model["intercept"],"training_r_squared":model["r_squared"],
            "holdout_rmse":rmse,"holdout_baseline_rmse":baseline_rmse,
            "holdout_improvement":1-rmse/baseline_rmse if baseline_rmse else None,
            "identified":model["slope"]>0 and rmse<baseline_rmse,
            "response_index":feature,"holdout_predictions":pred,
            "action_limit":"directional budget-response evidence only; not causal MMM without controls, calibration and residual diagnostics"}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    try: result=fit(json.loads(a.input.read_text()))
    except (OSError,json.JSONDecodeError,ValueError,TypeError) as exc: ap.error(str(exc))
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__": main()
