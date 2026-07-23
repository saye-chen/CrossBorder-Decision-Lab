#!/usr/bin/env python3
"""Transparent statistical primitives for MBCM estimators."""
from __future__ import annotations
import math
from mbcm_common import ModelError, finite, sequence

STATISTICS_CONTRACT_VERSION="CBSTAT-2026.01"

def mean(values,name="values"):
    xs=[finite(x,f"{name}[{i}]") for i,x in enumerate(sequence(values,name,allow_empty=False))]
    return sum(xs)/len(xs)

def variance(values,name="values",sample=True):
    xs=[finite(x,f"{name}[{i}]") for i,x in enumerate(sequence(values,name,allow_empty=False))]
    if sample and len(xs)<2: raise ModelError(f"{name}:at_least_two_required")
    m=sum(xs)/len(xs); denom=len(xs)-1 if sample else len(xs)
    return sum((x-m)**2 for x in xs)/denom

def covariance(x,y,name="values"):
    if len(x)!=len(y) or len(x)<2: raise ModelError(f"{name}:aligned_two_or_more_required")
    mx=mean(x,f"{name}.x"); my=mean(y,f"{name}.y")
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/(len(x)-1)

def ols(x,y,name="ols"):
    if len(x)!=len(y) or len(x)<3: raise ModelError(f"{name}:aligned_three_or_more_required")
    vx=variance(x,f"{name}.x")
    if vx<=0: raise ModelError(f"{name}:zero_predictor_variance")
    slope=covariance(x,y,name)/vx; intercept=mean(y,f"{name}.y")-slope*mean(x,f"{name}.x")
    fitted=[intercept+slope*a for a in x]; residuals=[b-f for b,f in zip(y,fitted)]
    sse=sum(r*r for r in residuals); sst=sum((b-mean(y,f"{name}.y"))**2 for b in y)
    se=math.sqrt((sse/(len(x)-2))/sum((a-mean(x,f"{name}.x"))**2 for a in x))
    return {"intercept":intercept,"slope":slope,"slope_se":se,
            "r_squared":1-sse/sst if sst>0 else None,"fitted":fitted,"residuals":residuals}

def percentile(sorted_values,p):
    if not sorted_values: raise ModelError("percentile:nonempty_required")
    position=(len(sorted_values)-1)*p; low=math.floor(position); high=math.ceil(position)
    if low==high: return sorted_values[low]
    return sorted_values[low]*(high-position)+sorted_values[high]*(position-low)

def project_simplex(values):
    """Euclidean projection onto non-negative weights summing to one."""
    u=sorted(values,reverse=True); cumulative=0.0; rho=-1
    for j,value in enumerate(u):
        cumulative+=value
        if value-(cumulative-1)/(j+1)>0: rho=j
    if rho<0: return [1/len(values)]*len(values)
    theta=(sum(u[:rho+1])-1)/(rho+1)
    return [max(v-theta,0.0) for v in values]
