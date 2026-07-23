#!/usr/bin/env python3
"""DiD, parallel-trend, ITT/CACE and synthetic-control estimators."""
from __future__ import annotations
import math
from statistics import NormalDist
from mbcm_common import finite, require, run_cli, ModelError, sequence
from statistics_common import mean, variance, ols, project_simplex

def _did(d):
    for key in ("treatment_pre","treatment_post","control_pre","control_post"): sequence(d[key],key,allow_empty=False)
    if len(d["treatment_pre"])!=len(d["treatment_post"]) or len(d["control_pre"])!=len(d["control_post"]):
        raise ModelError("did:paired_periods_required")
    t_changes=[b-a for a,b in zip(d["treatment_pre"],d["treatment_post"])]
    c_changes=[b-a for a,b in zip(d["control_pre"],d["control_post"])]
    effect=mean(t_changes,"treatment_changes")-mean(c_changes,"control_changes")
    se=math.sqrt(variance(t_changes,"treatment_changes")/len(t_changes)+variance(c_changes,"control_changes")/len(c_changes))
    z=NormalDist().inv_cdf(1-finite(d.get("alpha",0.05),"alpha",0,0.5)/2)
    return effect,se,[effect-z*se,effect+z*se]

def _synthetic(d):
    treated=[finite(x,f"treated_pre[{i}]") for i,x in enumerate(sequence(d["treated_pre"],"treated_pre",False))]
    donors=sequence(d["donor_pre"],"donor_pre",False)
    if any(len(row)!=len(treated) for row in donors): raise ModelError("synthetic:aligned_pre_periods_required")
    if len(d["donor_post"])!=len(donors): raise ModelError("synthetic:one_post_per_donor_required")
    matrix=[[finite(x,f"donor_pre[{j}][{i}]") for i,x in enumerate(row)] for j,row in enumerate(donors)]
    weights=[1/len(matrix)]*len(matrix); lr=finite(d.get("learning_rate",0.01),"learning_rate",0)
    for _ in range(int(finite(d.get("iterations",2000),"iterations",1,100000))):
        fitted=[sum(weights[j]*matrix[j][i] for j in range(len(matrix))) for i in range(len(treated))]
        gradients=[2*sum((fitted[i]-treated[i])*matrix[j][i] for i in range(len(treated)))/len(treated) for j in range(len(matrix))]
        weights=project_simplex([w-lr*g for w,g in zip(weights,gradients)])
    fitted=[sum(weights[j]*matrix[j][i] for j in range(len(matrix))) for i in range(len(treated))]
    pre_rmse=math.sqrt(sum((a-b)**2 for a,b in zip(treated,fitted))/len(treated))
    synthetic_post=sum(weights[j]*finite(d["donor_post"][j],f"donor_post[{j}]") for j in range(len(weights)))
    effect=finite(d["treated_post"],"treated_post")-synthetic_post
    return effect,weights,pre_rmse,synthetic_post

def calculate(d):
    require(d,"method")
    method=d["method"]
    if method=="did":
        require(d,"treatment_pre","treatment_post","control_pre","control_post")
        effect,se,interval=_did(d)
        pre_t=ols(list(range(len(d["treatment_pre"]))),d["treatment_pre"],"pre_treatment")["slope"] if len(d["treatment_pre"])>=3 else None
        pre_c=ols(list(range(len(d["control_pre"]))),d["control_pre"],"pre_control")["slope"] if len(d["control_pre"])>=3 else None
        tolerance=finite(d.get("parallel_trend_tolerance",0.1),"parallel_trend_tolerance",0)
        parallel=None if pre_t is None else abs(pre_t-pre_c)<=tolerance
        return {"method":"difference_in_differences","effect":effect,"standard_error":se,
                "confidence_interval":interval,"parallel_trend_passed":parallel,
                "pretrend_slope_difference":None if pre_t is None else pre_t-pre_c,
                "action_limit":"causal_claim_blocked" if parallel is False or interval[0]<=0<=interval[1] else "qualified_causal_claim"}
    if method=="itt_cace":
        require(d,"assigned_treatment_mean","assigned_control_mean","treatment_compliance","control_compliance")
        itt=finite(d["assigned_treatment_mean"],"assigned_treatment_mean")-finite(d["assigned_control_mean"],"assigned_control_mean")
        compliance=finite(d["treatment_compliance"],"treatment_compliance",0,1)-finite(d["control_compliance"],"control_compliance",0,1)
        if compliance<=0: raise ModelError("cace:positive_compliance_difference_required")
        return {"method":"itt_cace","itt":itt,"compliance_difference":compliance,"cace":itt/compliance,
                "assumptions":["exclusion_restriction","monotonicity","random_assignment"]}
    if method=="synthetic_control":
        require(d,"treated_pre","donor_pre","treated_post","donor_post")
        effect,weights,rmse,counter=_synthetic(d)
        threshold=finite(d.get("maximum_pre_rmse",1e308),"maximum_pre_rmse",0)
        return {"method":"synthetic_control","effect":effect,"counterfactual_post":counter,
                "donor_weights":weights,"pre_rmse":rmse,"fit_passed":rmse<=threshold,
                "action_limit":"inconclusive" if rmse>threshold else "qualified_estimate"}
    if method=="geo_match":
        require(d,"treated_geos","control_geos","metric_weights","maximum_distance")
        treated=sequence(d["treated_geos"],"treated_geos",False); controls=sequence(d["control_geos"],"control_geos",False)
        weights=d["metric_weights"]
        if not isinstance(weights,dict) or not weights: raise ModelError("metric_weights:object_required")
        maximum=finite(d["maximum_distance"],"maximum_distance",0)
        available=set(range(len(controls))); pairs=[]
        for ti,t in enumerate(treated):
            require(t,"id","metrics"); best=None
            for ci in available:
                c=controls[ci]; require(c,"id","metrics")
                distance=math.sqrt(sum(finite(weight,f"metric_weights.{metric}",0)*
                    (finite(t["metrics"][metric],f"treated.{metric}")-finite(c["metrics"][metric],f"control.{metric}"))**2
                    for metric,weight in weights.items()))
                if best is None or distance<best[0]: best=(distance,ci)
            if best is None: raise ModelError("geo_match:not_enough_controls")
            distance,ci=best; available.remove(ci)
            pairs.append({"treated_id":t["id"],"control_id":controls[ci]["id"],"distance":distance,
                          "balance_passed":distance<=maximum})
        return {"method":"geo_match","pairs":pairs,
                "all_pairs_balanced":all(x["balance_passed"] for x in pairs),
                "action_limit":"design_ready" if all(x["balance_passed"] for x in pairs) else "repair_match"}
    raise ModelError("method:did_itt_cace_synthetic_control_or_geo_match_required")
if __name__=="__main__": run_cli(calculate,"causal_effects")
