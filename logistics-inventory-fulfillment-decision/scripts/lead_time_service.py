#!/usr/bin/env python3
import math
from common import main,num,n
def qtile(xs,q):
    ys=sorted(xs);p=(len(ys)-1)*q;lo=math.floor(p);hi=math.ceil(p);return ys[lo] if lo==hi else ys[lo]+(ys[hi]-ys[lo])*(p-lo)
def run(d):
    samples=[num(x,"lead_time",0) for x in d.get("lead_time_samples",[])]
    if len(samples)<3: raise ValueError("lead_time_samples requires at least 3 values")
    stats={f"p{int(q*100)}":round(qtile(samples,q),6) for q in [.5,.75,.9,.95]}
    promise=n(d,"promise_days");prob=sum(x<=promise for x in samples)/len(samples)
    target=num(d.get("target_probability",.9),"target_probability",0)
    if not 0 <= target <= 1: raise ValueError("target_probability must be in [0, 1]")
    return {**stats,"promise_probability":round(prob,6),"target_probability":target,"decision":"pass" if prob>=target else "blocked","buffer_to_p90":round(promise-stats["p90"],6)}
if __name__=="__main__":main(run)
