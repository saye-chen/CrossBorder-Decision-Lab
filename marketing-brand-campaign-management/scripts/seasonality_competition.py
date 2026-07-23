#!/usr/bin/env python3
"""Seasonal indices, event ramp/depletion and competition-adjusted effect."""
from __future__ import annotations
import math
from mbcm_common import finite, require, run_cli, ModelError, sequence
from statistics_common import mean, ols

def calculate(d):
    require(d,"monthly_history","event_window","own_outcome","competitor_pressure","own_sov","own_som")
    years=sequence(d["monthly_history"],"monthly_history",False)
    if any(len(year)!=12 for year in years): raise ModelError("monthly_history:twelve_months_per_year_required")
    normalized=[]
    for y,row in enumerate(years):
        values=[finite(x,f"monthly_history[{y}]",0) for x in row]; annual=mean(values,f"year[{y}]")
        if annual<=0: raise ModelError("monthly_history:positive_annual_mean_required")
        normalized.append([x/annual for x in values])
    indices=[mean([year[m] for year in normalized],f"month[{m}]") for m in range(12)]
    event=[finite(x,f"event_window[{i}]",0) for i,x in enumerate(sequence(d["event_window"],"event_window",False))]
    peak=max(event); peak_index=event.index(peak)
    pre_base=mean(event[:max(1,peak_index)],"event_pre")
    post=event[peak_index+1:]
    post_average=mean(post,"event_post") if post else peak
    pull_forward=max(0,pre_base-post_average)
    outcome=[finite(x,f"own_outcome[{i}]",0) for i,x in enumerate(sequence(d["own_outcome"],"own_outcome",False))]
    pressure=[finite(x,f"competitor_pressure[{i}]") for i,x in enumerate(sequence(d["competitor_pressure"],"competitor_pressure",False))]
    if len(outcome)!=len(pressure): raise ModelError("competition:aligned_required")
    fit=ols(pressure,outcome,"competition")
    own_sov=finite(d["own_sov"],"own_sov",0,1); own_som=finite(d["own_som"],"own_som",0,1)
    sov_gap=own_sov-own_som
    interval=[fit["slope"]-1.96*fit["slope_se"],fit["slope"]+1.96*fit["slope_se"]]
    uncertain=interval[0]<=0<=interval[1]
    posture="inconclusive" if uncertain else "counter" if fit["slope"]<0 and sov_gap<0 else "avoid" if fit["slope"]<0 else "ignore_or_test"
    return {"method":"ratio_to_annual_mean_and_competition_ols","seasonal_indices":indices,
            "event_peak_index":peak_index,"post_event_depletion_per_period":pull_forward,
            "competitor_pressure_slope":fit["slope"],"slope_se":fit["slope_se"],
            "competitor_pressure_interval_95":interval,
            "competition_r_squared":fit["r_squared"],"excess_share_of_voice":sov_gap,
            "recommended_competitive_posture":posture,
            "action_limit":"current_competitor_facts_required"}
if __name__=="__main__": run_cli(calculate,"seasonality_competition")
