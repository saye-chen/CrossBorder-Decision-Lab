#!/usr/bin/env python3
"""Standalone statistical primitives for AAMO causal estimators."""
from __future__ import annotations
import math

STATISTICS_CONTRACT_VERSION="CBSTAT-2026.01"

def finite(value,name="value"):
    try: out=float(value)
    except (TypeError,ValueError) as exc: raise ValueError(f"{name}:numeric_required") from exc
    if not math.isfinite(out): raise ValueError(f"{name}:finite_required")
    return out

def numbers(values,name="values",minimum=1):
    if not isinstance(values,list) or len(values)<minimum: raise ValueError(f"{name}:at_least_{minimum}_required")
    return [finite(v,f"{name}[{i}]") for i,v in enumerate(values)]

def mean(values,name="values"):
    xs=numbers(values,name); return sum(xs)/len(xs)

def variance(values,name="values",sample=True):
    xs=numbers(values,name,2 if sample else 1); m=sum(xs)/len(xs)
    return sum((x-m)**2 for x in xs)/(len(xs)-1 if sample else len(xs))

def covariance(x,y,name="values"):
    xs=numbers(x,f"{name}.x",2); ys=numbers(y,f"{name}.y",2)
    if len(xs)!=len(ys): raise ValueError(f"{name}:aligned_required")
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    return sum((a-mx)*(b-my) for a,b in zip(xs,ys))/(len(xs)-1)

def ols(x,y,name="ols"):
    xs=numbers(x,f"{name}.x",3); ys=numbers(y,f"{name}.y",3)
    if len(xs)!=len(ys): raise ValueError(f"{name}:aligned_required")
    vx=variance(xs,f"{name}.x")
    if vx<=0: raise ValueError(f"{name}:zero_predictor_variance")
    slope=covariance(xs,ys,name)/vx; intercept=mean(ys)-slope*mean(xs)
    fitted=[intercept+slope*a for a in xs]; residuals=[b-f for b,f in zip(ys,fitted)]
    sse=sum(r*r for r in residuals); ym=mean(ys); sst=sum((b-ym)**2 for b in ys)
    se=math.sqrt((sse/(len(xs)-2))/sum((a-mean(xs))**2 for a in xs))
    return {"intercept":intercept,"slope":slope,"slope_se":se,
            "r_squared":1-sse/sst if sst>0 else None,"fitted":fitted,"residuals":residuals}

def project_simplex(values):
    xs=numbers(values,"simplex",1); u=sorted(xs,reverse=True); cumulative=0.0; rho=-1
    for j,value in enumerate(u):
        cumulative+=value
        if value-(cumulative-1)/(j+1)>0: rho=j
    if rho<0: return [1/len(xs)]*len(xs)
    theta=(sum(u[:rho+1])-1)/(rho+1)
    return [max(v-theta,0.0) for v in xs]

def normal_cdf(x):
    return .5*(1+math.erf(finite(x)/math.sqrt(2)))
