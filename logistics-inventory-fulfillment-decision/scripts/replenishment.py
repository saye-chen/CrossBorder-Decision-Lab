#!/usr/bin/env python3
import math
from datetime import date,timedelta
from common import main,n
def ceil_step(x,step): return math.ceil(max(0,x)/step)*step
def run(d):
    required={"expected_protection_demand","target_demand_quantile",
              "target_inventory_position","current_inventory_position",
              "opening_available"}
    missing=sorted(key for key in required if key not in d)
    if missing: raise ValueError(f"missing required inventory inputs: {', '.join(missing)}")
    expected=n(d,"expected_protection_demand");quantile=n(d,"target_demand_quantile");
    if quantile<expected: raise ValueError("target quantile must be >= expected demand")
    safety=quantile-expected;rop=quantile
    raw=n(d,"target_inventory_position")-n(d,"current_inventory_position")
    step=n(d,"case_pack",1);qty=max(n(d,"moq"),ceil_step(raw,step)) if raw>0 else 0
    for k in ["supplier_capacity","cash_capacity_units","warehouse_capacity_units","lifecycle_cap","shelf_life_cap"]:
        if k in d: qty=min(qty,n(d,k))
    qty=math.floor(qty/step)*step if qty else 0
    if raw>0 and qty<n(d,"moq"): raise ValueError("constraints make MOQ infeasible")
    projected=[];available=n(d,"opening_available")
    for i,row in enumerate(d.get("timeline",[])):
        available+=n(row,"eligible_arrival")-n(row,"demand")-n(row,"reservation")-n(row,"expected_loss")
        floor=n(row,"protection_floor");projected.append({"period":row.get("period",i),"projected_available":round(available,6),"protection_floor":floor,"gap":round(available-floor,6)})
    breaks=[x for x in projected if x["gap"]<0]
    schedule=None
    if "order_date" in d:
        start=date.fromisoformat(d["order_date"])
        stages=[("supplier_confirmation_days","confirmed_date"),("production_days","production_complete_date"),("quality_release_days","latest_release_date"),("origin_handling_days","latest_ship_date"),("main_haul_days","main_haul_arrival_date"),("customs_days","customs_clear_date"),("inbound_days","warehouse_arrival_date"),("receiving_putaway_days","available_to_sell_date")]
        schedule={"order_date":start.isoformat()};cursor=start
        for key,label in stages:
            cursor+=timedelta(days=int(n(d,key)));schedule[label]=cursor.isoformat()
    return {"safety_stock":round(safety,6),"reorder_point":round(rop,6),"raw_order_qty":round(max(0,raw),6),"final_order_qty":round(qty,6),"timeline":projected,"continuity":"fail" if breaks else "pass","first_break":breaks[0] if breaks else None,"schedule":schedule}
if __name__=="__main__":main(run)
