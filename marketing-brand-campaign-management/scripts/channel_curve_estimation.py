#!/usr/bin/env python3
"""Grid-estimate adstock/Hill channel response parameters from aggregate history."""
from __future__ import annotations
from mbcm_common import finite, require, run_cli, ModelError, sequence
from channel_response import adstock, hill

def calculate(d):
    require(d,"spend","response","decay_candidates","half_saturation_candidates","shape_candidates")
    spend=[finite(x,f"spend[{i}]",0) for i,x in enumerate(sequence(d["spend"],"spend",False))]
    response=[finite(x,f"response[{i}]") for i,x in enumerate(sequence(d["response"],"response",False))]
    if len(spend)!=len(response) or len(spend)<6: raise ModelError("history:aligned_six_or_more_required")
    best=None
    for decay in sequence(d["decay_candidates"],"decay_candidates",False):
        decay=finite(decay,"decay",0,0.999); stock=adstock(spend,decay)
        for half in sequence(d["half_saturation_candidates"],"half_saturation_candidates",False):
            half=finite(half,"half_saturation",0)
            for shape in sequence(d["shape_candidates"],"shape_candidates",False):
                shape=finite(shape,"shape",0)
                if half<=0 or shape<=0: raise ModelError("curve:positive_half_and_shape_required")
                basis=[hill(x,half,shape) for x in stock]
                denom=sum(x*x for x in basis)
                maximum=max(0,sum(x*y for x,y in zip(basis,response))/denom) if denom else 0
                fitted=[maximum*x for x in basis]; sse=sum((y-f)**2 for y,f in zip(response,fitted))
                candidate=(sse,decay,half,shape,maximum,fitted)
                if best is None or candidate[0]<best[0]: best=candidate
    sse,decay,half,shape,maximum,fitted=best
    average=sum(response)/len(response); sst=sum((x-average)**2 for x in response)
    return {"method":"adstock_hill_grid_estimation","decay":decay,"half_saturation":half,
            "shape":shape,"max_response":maximum,"r_squared":1-sse/sst if sst else None,
            "fitted":fitted,"candidate_count":len(d["decay_candidates"])*len(d["half_saturation_candidates"])*len(d["shape_candidates"]),
            "action_limit":"scenario_or_test" if sst==0 or 1-sse/sst<0.5 else "bounded_curve"}
if __name__=="__main__": run_cli(calculate,"channel_curve_estimation")
