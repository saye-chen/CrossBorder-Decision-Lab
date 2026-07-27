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
    requested_incremental=finite(d["incremental_demand"],"incremental_demand",0)
    incremental_gap=max(0,requested_incremental-supported)
    utilization={k:(demand/v if v else None) for k,v in caps.items()}
    return {"required_peak_volume":demand,"minimum_total_capacity":total_supported,
            "supported_campaign_volume":supported,"incremental_capacity_gap":incremental_gap,
            "supported_incremental_fraction":None if requested_incremental==0 else min(1,supported/requested_incremental),
            "limiting_capacity":limiting,"utilization":utilization,
            "over_capacity_stages":[k for k,v in utilization.items() if v is not None and v>1],
            "action_limit":"full" if demand<=total_supported else "reduced" if supported>0 else "stop",
            "full_demand_supported":demand<=total_supported}
if __name__=="__main__": run_cli(calculate,"capacity_stress")
