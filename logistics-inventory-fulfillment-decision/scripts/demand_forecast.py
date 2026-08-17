#!/usr/bin/env python3
import math
from common import main,n,num
def quantile(xs,q):
    ys=sorted(xs);pos=(len(ys)-1)*q;lo=math.floor(pos);hi=math.ceil(pos)
    return ys[lo] if lo==hi else ys[lo]+(ys[hi]-ys[lo])*(pos-lo)
def croston(hist,alpha):
    nonzero=[(i,x) for i,x in enumerate(hist) if x>0]
    if not nonzero:return 0
    z=nonzero[0][1];interval=nonzero[0][0]+1;last=nonzero[0][0]
    for i,x in nonzero[1:]: z=alpha*x+(1-alpha)*z;interval=alpha*(i-last)+(1-alpha)*interval;last=i
    return z/max(interval,1e-9)
def run(d):
    hist=[num(x,"history",0) for x in d.get("history",[])]
    if len(hist)<3: raise ValueError("history requires at least 3 observations")
    window=int(n(d,"window",min(4,len(hist)),1));window=min(window,len(hist));zero_share=sum(x==0 for x in hist)/len(hist)
    requested=d.get("method","auto")
    if requested not in ["auto","moving_average","croston"]: raise ValueError("unsupported forecast method")
    method="croston" if requested=="croston" or (requested=="auto" and zero_share>=n(d,"intermittent_zero_share",.4)) else "moving_average"
    base=croston(hist,num(d.get("croston_alpha",.2),"croston_alpha",0)) if method=="croston" else sum(hist[-window:])/window
    factor=num(d.get("causal_factor",1),"causal_factor",0);point=base*factor
    errors=[]
    for i in range(window,len(hist)):
        pred=croston(hist[:i],num(d.get("croston_alpha",.2),"croston_alpha",0)) if method=="croston" else sum(hist[i-window:i])/window;errors.append(hist[i]-pred)
    abs_errors=[abs(x) for x in errors] or [0]
    q=num(d.get("interval_quantile",.9),"interval_quantile",0)
    if not 0 <= q <= 1: raise ValueError("interval_quantile must be in [0, 1]")
    spread=quantile(abs_errors,q)
    actual=d.get("actual");metrics=None
    if actual:
        if len(actual)!=len(d.get("forecast",[])): raise ValueError("actual and forecast lengths differ")
        forecasts=[num(x,"forecast",0) for x in d["forecast"]];actuals=[num(x,"actual",0) for x in actual]
        denom=sum(actuals);metrics={"bias":round(sum(f-a for f,a in zip(forecasts,actuals))/len(actuals),6),"wape":round(sum(abs(f-a) for f,a in zip(forecasts,actuals))/denom,6) if denom else None}
    horizon=int(n(d,"horizon",1,1))
    censored=d.get("stockout_flags",[])
    if censored and len(censored)!=len(hist): raise ValueError("stockout_flags length differs from history")
    stockout_warning=bool(censored and any(censored));quality="conditional" if stockout_warning else "usable"
    return {"point_forecast":round(point,6),"forecast":[round(point,6)]*horizon,"lower":round(max(0,point-spread),6),"upper":round(point+spread,6),"intervals":[{"period":i+1,"low":round(max(0,point-spread),6),"high":round(point+spread,6)} for i in range(horizon)],"error_quantile":round(spread,6),"metrics":metrics,"method":method+"_with_empirical_error","zero_share":round(zero_share,6),"stockout_censoring_warning":stockout_warning,"decision_quality":quality}
if __name__=="__main__":main(run)
