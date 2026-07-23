#!/usr/bin/env python3
"""Deterministic bootstrap and Monte Carlo uncertainty propagation."""
from __future__ import annotations
import random
from mbcm_common import finite, require, run_cli, sequence, ModelError
from statistics_common import mean, percentile

def calculate(d):
    require(d,"method","seed","iterations")
    rng=random.Random(int(finite(d["seed"],"seed",0)))
    iterations=int(finite(d["iterations"],"iterations",100,100000))
    if d["method"]=="bootstrap_mean_difference":
        a=sequence(d["treatment"],"treatment",False); b=sequence(d["control"],"control",False)
        draws=[]
        for _ in range(iterations):
            sa=[a[rng.randrange(len(a))] for _ in a]; sb=[b[rng.randrange(len(b))] for _ in b]
            draws.append(mean(sa,"bootstrap_treatment")-mean(sb,"bootstrap_control"))
    elif d["method"]=="monte_carlo_contribution":
        require(d,"revenue","costs")
        revenue=d["revenue"]; costs=sequence(d["costs"],"costs")
        draws=[]
        for _ in range(iterations):
            rev=rng.gauss(finite(revenue["mean"],"revenue.mean"),finite(revenue["sd"],"revenue.sd",0))
            cost=sum(rng.gauss(finite(x["mean"],"cost.mean"),finite(x["sd"],"cost.sd",0)) for x in costs)
            draws.append(rev-cost)
    elif d["method"]=="beta_binomial_update":
        require(d,"prior_alpha","prior_beta","successes","trials")
        prior_alpha=finite(d["prior_alpha"],"prior_alpha",0)
        prior_beta=finite(d["prior_beta"],"prior_beta",0)
        successes=finite(d["successes"],"successes",0)
        trials=finite(d["trials"],"trials",0)
        if prior_alpha<=0 or prior_beta<=0 or successes>trials:
            raise ModelError("beta_binomial:valid_positive_prior_and_counts_required")
        posterior_alpha=prior_alpha+successes; posterior_beta=prior_beta+trials-successes
        draws=[rng.betavariate(posterior_alpha,posterior_beta) for _ in range(iterations)]
    else: raise ModelError("method:unsupported")
    draws.sort(); probability_positive=sum(x>0 for x in draws)/iterations
    result={"method":d["method"],"iterations":iterations,"seed":int(d["seed"]),
            "mean":sum(draws)/iterations,"p05":percentile(draws,0.05),
            "p50":percentile(draws,0.5),"p95":percentile(draws,0.95),
            "probability_positive":probability_positive,
            "action_limit":"scenario_not_guarantee"}
    if d["method"]=="beta_binomial_update":
        result["posterior_alpha"]=posterior_alpha; result["posterior_beta"]=posterior_beta
    return result
if __name__=="__main__": run_cli(calculate,"uncertainty_engine")
