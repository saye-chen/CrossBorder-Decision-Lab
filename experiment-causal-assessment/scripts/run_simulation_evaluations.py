#!/usr/bin/env python3
"""Run seeded Monte Carlo checks for native randomized estimators."""

from __future__ import annotations

import json
import math
import random

from evaluate_randomized_effect import evaluate_randomized_effect


def _band(target:float,repeats:int)->float:
    return max(0.005,3*math.sqrt(target*(1-target)/repeats))


def run()->dict:
    continuous_seed=20260810; binary_seed=20260811
    repeats_cont,n_cont,alpha=3000,80,0.05
    rng=random.Random(continuous_seed); null_reject=0; positive_estimates=[]; positive_reject=0; true_effect=0.45
    for _ in range(repeats_cont):
        c=[rng.gauss(0,1) for _ in range(n_cont)]
        t0=[rng.gauss(0,1) for _ in range(n_cont)]
        null=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":{"c":c,"t":t0}})["comparisons"][0]
        null_reject += null["p_value_unadjusted"]<alpha
        t=[rng.gauss(true_effect,1) for _ in range(n_cont)]
        positive=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":{"c":c,"t":t}})["comparisons"][0]
        positive_estimates.append(positive["estimate_absolute"]); positive_reject += positive["p_value_unadjusted"]<alpha
    null_rate=null_reject/repeats_cont; bias=sum(positive_estimates)/len(positive_estimates)-true_effect
    rmse=math.sqrt(sum((item-true_effect)**2 for item in positive_estimates)/len(positive_estimates))
    repeats_binary,n_binary,target_coverage=2500,60,0.95
    rng=random.Random(binary_seed); covered=0
    for _ in range(repeats_binary):
        c=[1 if rng.random()<0.08 else 0 for _ in range(n_binary)]
        t=[1 if rng.random()<0.08 else 0 for _ in range(n_binary)]
        interval=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"binary","control_arm":"c","groups":{"c":c,"t":t}})["comparisons"][0]["confidence_interval"]
        covered += interval["lower"]<=0<=interval["upper"]
    coverage=covered/repeats_binary
    checks={
        "continuous_null_type_one":{"seed":continuous_seed,"repeats":repeats_cont,"observed":null_rate,"target":alpha,"acceptance_band":_band(alpha,repeats_cont),"pass":abs(null_rate-alpha)<=_band(alpha,repeats_cont)},
        "continuous_positive_bias_rmse":{"seed":continuous_seed,"repeats":repeats_cont,"true_effect":true_effect,"bias":bias,"rmse":rmse,"power":positive_reject/repeats_cont,"pass":abs(bias)<=0.02 and rmse<0.2},
        "binary_newcombe_null_coverage":{"seed":binary_seed,"repeats":repeats_binary,"baseline":0.08,"observed":coverage,"target":target_coverage,"acceptance_lower":target_coverage-_band(target_coverage,repeats_binary),"pass":coverage>=target_coverage-_band(target_coverage,repeats_binary)}
    }
    return {"schema_version":"1.0.0","evaluation_id":"ECAE-SIMULATION-2026-08-10","simulation_policy":{"mc_band":"max(0.005, 3*MCSE)","implementation":"stdlib seeded DGP"},"checks":checks,"status":"pass" if all(item["pass"] for item in checks.values()) else "fail","limitations":["This is implementer-owned evidence, not independent parity.","Additional skewed, clustered, ratio, rare-event and small-sample grids remain required for L3."]}


if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2,sort_keys=True))
