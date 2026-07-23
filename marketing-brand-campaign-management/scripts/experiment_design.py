#!/usr/bin/env python3
"""Power, MDE, cluster design effect and duration planning."""
from __future__ import annotations
import math
from statistics import NormalDist
from mbcm_common import finite, require, run_cli, ModelError

def calculate(d):
    require(d,"baseline_mean","baseline_sd","relative_mde","alpha","power",
            "cluster_size","intracluster_correlation","weekly_observations_per_cluster")
    mean=finite(d["baseline_mean"],"baseline_mean",0)
    sd=finite(d["baseline_sd"],"baseline_sd",0)
    rel=finite(d["relative_mde"],"relative_mde",0)
    alpha=finite(d["alpha"],"alpha",0,0.5); power=finite(d["power"],"power",0.5,0.9999)
    cluster=finite(d["cluster_size"],"cluster_size",1)
    icc=finite(d["intracluster_correlation"],"intracluster_correlation",0,1)
    weekly=finite(d["weekly_observations_per_cluster"],"weekly_observations_per_cluster",0)
    absolute_mde=mean*rel
    if absolute_mde<=0 or sd<=0 or weekly<=0 or alpha<=0:
        raise ModelError("design:positive_mean_sd_mde_alpha_and_volume_required")
    z_alpha=NormalDist().inv_cdf(1-alpha/2); z_power=NormalDist().inv_cdf(power)
    individual_per_arm=2*((z_alpha+z_power)*sd/absolute_mde)**2
    design_effect=1+(cluster-1)*icc
    adjusted_per_arm=math.ceil(individual_per_arm*design_effect)
    clusters_per_arm=math.ceil(adjusted_per_arm/cluster)
    weeks=math.ceil(adjusted_per_arm/(clusters_per_arm*weekly))
    achieved_mde=(z_alpha+z_power)*sd*math.sqrt(2*design_effect/adjusted_per_arm)
    return {"method":"two_sided_normal_cluster_design","individual_sample_per_arm":math.ceil(individual_per_arm),
            "design_effect":design_effect,"adjusted_sample_per_arm":adjusted_per_arm,
            "clusters_per_arm":clusters_per_arm,"minimum_weeks":weeks,
            "absolute_mde":absolute_mde,"relative_mde":rel,
            "achieved_absolute_mde":achieved_mde,
            "assumptions":["independent_clusters","stable_variance","no_cross_cluster_spillover"],
            "action_limit":"design_only_not_causal_result"}
if __name__=="__main__": run_cli(calculate,"experiment_design")
