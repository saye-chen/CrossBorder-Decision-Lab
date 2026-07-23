#!/usr/bin/env python3
"""Geometric adstock, Hill saturation, interactions and pacing comparison."""
from __future__ import annotations
from mbcm_common import finite, require, run_cli, ModelError, sequence

def adstock(spend,decay):
    out=[]; carry=0.0
    for value in spend:
        carry=value+decay*carry; out.append(carry)
    return out

def hill(value,half_saturation,shape):
    if value<=0: return 0.0
    return value**shape/(value**shape+half_saturation**shape)

def _pacing(total,periods,mode):
    if mode=="continuous": return [total/periods]*periods
    if mode=="flighting":
        active=max(1,periods//2); return [total/active if i<active else 0 for i in range(periods)]
    if mode=="pulsing":
        base=total*0.4/periods; pulse_periods=max(1,periods//4); pulse=(total-base*periods)/pulse_periods
        return [base+(pulse if i%4==0 and i//4<pulse_periods else 0) for i in range(periods)]
    raise ModelError("pacing:unsupported")

def calculate(d):
    require(d,"channels","interactions","pacing")
    channels=sequence(d["channels"],"channels",False); curves={}; total_response=0.0
    for i,row in enumerate(channels):
        require(row,"id","spend","decay","half_saturation","shape","max_response")
        spend=[finite(x,f"channels[{i}].spend") for x in sequence(row["spend"],f"channels[{i}].spend",False)]
        decay=finite(row["decay"],f"channels[{i}].decay",0,0.999)
        half=finite(row["half_saturation"],f"channels[{i}].half_saturation",0)
        shape=finite(row["shape"],f"channels[{i}].shape",0)
        maximum=finite(row["max_response"],f"channels[{i}].max_response",0)
        if half<=0 or shape<=0: raise ModelError(f"channels[{i}]:positive_curve_parameters_required")
        stock=adstock(spend,decay); response=[maximum*hill(x,half,shape) for x in stock]
        curves[row["id"]]={"adstock":stock,"response":response,"total_response":sum(response)}
        total_response+=sum(response)
    interaction_value=0.0
    for i,row in enumerate(sequence(d["interactions"],"interactions")):
        require(row,"channel_a","channel_b","coefficient")
        if row["channel_a"] not in curves or row["channel_b"] not in curves: raise ModelError("interaction:unknown_channel")
        coefficient=finite(row["coefficient"],f"interactions[{i}].coefficient")
        a=curves[row["channel_a"]]["response"]; b=curves[row["channel_b"]]["response"]
        interaction_value+=coefficient*sum(x*y for x,y in zip(a,b))
    pacing=d["pacing"]; require(pacing,"total_budget","periods")
    total=finite(pacing["total_budget"],"pacing.total_budget",0)
    periods=int(finite(pacing["periods"],"pacing.periods",1))
    schedules={mode:_pacing(total,periods,mode) for mode in ("continuous","flighting","pulsing")}
    frequency_curve=[]
    for i,row in enumerate(sequence(d.get("frequency_bins",[]),"frequency_bins")):
        require(row,"frequency","exposed","conversions")
        frequency=finite(row["frequency"],f"frequency_bins[{i}].frequency",1)
        exposed=finite(row["exposed"],f"frequency_bins[{i}].exposed",1)
        conversions=finite(row["conversions"],f"frequency_bins[{i}].conversions",0)
        if conversions>exposed: raise ModelError("frequency_bins:conversions_exceed_exposed")
        frequency_curve.append({"frequency":frequency,"conversion_rate":conversions/exposed})
    frequency_curve.sort(key=lambda x:x["frequency"])
    for i,row in enumerate(frequency_curve):
        row["marginal_conversion_rate"]=row["conversion_rate"]-(frequency_curve[i-1]["conversion_rate"] if i else 0)
    window_values=d.get("attribution_window_values",{})
    if not isinstance(window_values,dict): raise ModelError("attribution_window_values:object_required")
    rankings={window:[k for k,_ in sorted(values.items(),key=lambda item:item[1],reverse=True)]
              for window,values in window_values.items()}
    window_sensitive=len({tuple(x) for x in rankings.values()})>1
    return {"method":"geometric_adstock_hill_saturation","channels":curves,
            "base_response":total_response,"interaction_value":interaction_value,
            "total_response":total_response+interaction_value,"pacing_schedules":schedules,
            "frequency_response":frequency_curve,"attribution_window_rankings":rankings,
            "window_sensitive":window_sensitive,
            "assumptions":["curve_parameters_estimated_or_explicit_scenarios","no_unmodeled_channel_confounding"],
            "action_limit":"direction_not_ad_bid"}
if __name__=="__main__": run_cli(calculate,"channel_response")
