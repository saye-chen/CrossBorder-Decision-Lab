#!/usr/bin/env python3
"""Demand decomposition and minimum supported campaign volume."""
from mbcm_common import finite, require, run_cli, ModelError

def calculate(d):
    require(d,"baseline_demand","incremental_demand","pull_forward_demand","uncertainty_buffer","capacities")
    demand=sum(finite(d[k],k,0) for k in ("baseline_demand","incremental_demand","pull_forward_demand","uncertainty_buffer"))
    caps={k:finite(v,f"capacities.{k}",0) for k,v in d["capacities"].items()}
    if not caps: raise ModelError("capacities:nonempty_required")
    limiting=min(caps,key=caps.get); total_supported=caps[limiting]
    non_campaign=finite(d["baseline_demand"],"baseline_demand",0)+finite(d["pull_forward_demand"],"pull_forward_demand",0)+finite(d["uncertainty_buffer"],"uncertainty_buffer",0)
    supported=max(0,total_supported-non_campaign)
    utilization={k:(demand/v if v else None) for k,v in caps.items()}
    return {"required_peak_volume":demand,"minimum_total_capacity":total_supported,
            "supported_campaign_volume":supported,
            "limiting_capacity":limiting,"utilization":utilization,
            "full_demand_supported":demand<=total_supported}
if __name__=="__main__": run_cli(calculate,"capacity_stress")
