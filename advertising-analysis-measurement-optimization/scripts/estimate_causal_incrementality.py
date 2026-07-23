#!/usr/bin/env python3
"""Estimate clustered ITT, DiD, or synthetic-control advertising incrementality."""
import argparse,json,math
from pathlib import Path
from aamo_statistics import mean,variance,ols,project_simplex,numbers

def ci(effect,se,z=1.96): return [effect-z*se,effect+z*se]

def clustered_itt(p):
    t=numbers(p.get("treatment_clusters"),"treatment_clusters",2)
    c=numbers(p.get("control_clusters"),"control_clusters",2)
    effect=mean(t)-mean(c); se=math.sqrt(variance(t)/len(t)+variance(c)/len(c))
    return {"method":"clustered_itt","estimand":"intention_to_treat_per_assignment_cluster",
            "effect":effect,"standard_error":se,"ci":ci(effect,se),
            "diagnostics":{"treatment_clusters":len(t),"control_clusters":len(c),"cluster_level_inference":True},
            "identified":True,"action_limit":"applies only to preregistered eligible assignment clusters; inspect spillover and noncompliance"}

def did(p):
    tb=numbers(p.get("treatment_pre"),"treatment_pre",3); cb=numbers(p.get("control_pre"),"control_pre",3)
    ta=numbers(p.get("treatment_post"),"treatment_post",2); ca=numbers(p.get("control_post"),"control_post",2)
    if len(tb)!=len(cb): raise ValueError("pre periods must align")
    effect=(mean(ta)-mean(tb))-(mean(ca)-mean(cb))
    gaps=[a-b for a,b in zip(tb,cb)]; trend=ols(list(range(len(gaps))),gaps,"pretrend")
    threshold=float(p.get("maximum_pretrend_slope",0.05))
    residual=trend["residuals"]; se=math.sqrt((variance(residual) if len(residual)>1 else 0)/len(gaps)+
                                             variance(ta)/len(ta)+variance(ca)/len(ca))
    parallel=abs(trend["slope"])<=threshold
    return {"method":"difference_in_differences","estimand":"average_change_difference","effect":effect,
            "standard_error":se,"ci":ci(effect,se),"identified":parallel,
            "diagnostics":{"pretrend_slope":trend["slope"],"maximum_pretrend_slope":threshold,
                           "parallel_trends_passed":parallel,"pre_periods":len(tb)},
            "action_limit":"causal use blocked when pretrend fails; concurrent shocks and spillover still require evidence"}

def synthetic(p):
    treated=numbers(p.get("treated_pre"),"treated_pre",3)
    donors=p.get("donor_pre")
    if not isinstance(donors,list) or len(donors)<2: raise ValueError("at least two donor series required")
    donors=[numbers(x,f"donor_pre[{i}]",len(treated)) for i,x in enumerate(donors)]
    if any(len(x)!=len(treated) for x in donors): raise ValueError("donor periods must align")
    weights=[1/len(donors)]*len(donors); lr=float(p.get("learning_rate",.05))
    for _ in range(int(p.get("iterations",2000))):
        pred=[sum(weights[j]*donors[j][i] for j in range(len(donors))) for i in range(len(treated))]
        grad=[2*sum((pred[i]-treated[i])*donors[j][i] for i in range(len(treated)))/len(treated) for j in range(len(donors))]
        weights=project_simplex([w-lr*g for w,g in zip(weights,grad)])
    pred=[sum(weights[j]*donors[j][i] for j in range(len(donors))) for i in range(len(treated))]
    rmse=math.sqrt(sum((a-b)**2 for a,b in zip(treated,pred))/len(treated))
    treated_post=numbers(p.get("treated_post"),"treated_post",1); donor_post=p.get("donor_post")
    if len(donor_post)!=len(donors) or any(len(x)!=len(treated_post) for x in donor_post): raise ValueError("post donor dimensions must align")
    counter=[sum(weights[j]*float(donor_post[j][i]) for j in range(len(donors))) for i in range(len(treated_post))]
    effects=[a-b for a,b in zip(treated_post,counter)]; effect=mean(effects)
    threshold=float(p.get("maximum_pre_rmse",max(1.0,.1*abs(mean(treated)))))
    return {"method":"synthetic_control","estimand":"average_post_treatment_gap","effect":effect,
            "weights":weights,"counterfactual_post":counter,"identified":rmse<=threshold,
            "diagnostics":{"pre_rmse":rmse,"maximum_pre_rmse":threshold,"weights_sum":sum(weights)},
            "action_limit":"causal use blocked when pre-fit fails; donor contamination and placebo gaps require review"}

def estimate(p):
    method=p.get("method")
    if method=="clustered_itt": return clustered_itt(p)
    if method=="did": return did(p)
    if method=="synthetic_control": return synthetic(p)
    raise ValueError("method must be clustered_itt, did, or synthetic_control")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    try: result=estimate(json.loads(a.input.read_text()))
    except (OSError,json.JSONDecodeError,ValueError,TypeError) as exc: ap.error(str(exc))
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__": main()
