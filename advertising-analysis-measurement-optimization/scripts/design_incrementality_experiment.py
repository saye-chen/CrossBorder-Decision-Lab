#!/usr/bin/env python3
"""Design an advertising incrementality test with cluster and MDE controls."""
import argparse,json,math
from pathlib import Path
from aamo_statistics import finite

def design(p):
    baseline=finite(p.get("baseline_rate"),"baseline_rate")
    mde=finite(p.get("absolute_mde"),"absolute_mde")
    alpha=finite(p.get("alpha",.05),"alpha"); power=finite(p.get("power",.8),"power")
    cluster_size=finite(p.get("average_cluster_size",1),"average_cluster_size")
    icc=finite(p.get("icc",0),"icc"); periods=int(finite(p.get("periods",1),"periods"))
    if not 0<baseline<1 or mde<=0 or baseline+mde>=1 or not 0<alpha<.5 or not .5<power<1:
        raise ValueError("invalid baseline, MDE, alpha, or power")
    if cluster_size<1 or not 0<=icc<1 or periods<1: raise ValueError("invalid clustering or periods")
    # Stable standard critical values for the supported preregistration levels.
    z_alpha=1.96 if abs(alpha-.05)<1e-9 else 2.576 if abs(alpha-.01)<1e-9 else None
    z_power=.842 if abs(power-.8)<1e-9 else 1.282 if abs(power-.9)<1e-9 else None
    if z_alpha is None or z_power is None: raise ValueError("supported alpha: .05/.01; power: .8/.9")
    p2=baseline+mde
    individual=math.ceil(((z_alpha*math.sqrt(2*((baseline+p2)/2)*(1-(baseline+p2)/2))+
             z_power*math.sqrt(baseline*(1-baseline)+p2*(1-p2)))**2)/(mde*mde))
    design_effect=1+(cluster_size-1)*icc
    per_arm=math.ceil(individual*design_effect)
    clusters=math.ceil(per_arm/cluster_size)
    return {"estimand":"intention_to_treat","assignment_unit":p.get("assignment_unit","geo"),
            "individual_equivalent_per_arm":individual,"design_effect":design_effect,
            "required_observations_per_arm":per_arm,"required_clusters_per_arm":clusters,
            "minimum_periods":periods,"alpha":alpha,"power":power,"absolute_mde":mde,
            "preregistration_required":["eligibility","assignment_unit","primary_metric","MDE","window","guardrails","stopping_rule","spillover_check"],
            "action_limit":"design_only; do not launch until cluster availability, balance and spillover checks pass"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    try: result=design(json.loads(a.input.read_text()))
    except (OSError,json.JSONDecodeError,ValueError) as exc: ap.error(str(exc))
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__": main()
