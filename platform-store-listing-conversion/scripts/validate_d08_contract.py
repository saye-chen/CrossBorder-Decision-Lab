#!/usr/bin/env python3
from d08_common import GATES, fail, required, run_cli

CORE=("object_id","page_version_id","as_of_time","evidence","counterevidence","root_cause","alternative_explanations","actions","success_condition","stop_condition","rollback_version")
OPT=("optimization_unit_id","object_id","page_version_id","scenario_id","surface_type","current_observation","evidence_ids","counterevidence_ids","root_cause","alternative_explanations","proposed_variant_ids","implementation_order","owner","approval","primary_metric","guardrails","success_condition","stop_condition","rollback_version","confidence","unresolved_exposure")
SPEC={"title":"exact_copy","image_set":"production_brief","detail":"module_spec","landing_page":"module_spec"}

def validate(data):
    errors=[]
    try: required(data,CORE)
    except ValueError as exc: errors.append(str(exc))
    gates=data.get("gates",{})
    for g in GATES:
        if g not in gates: errors.append(f"missing gate {g}")
    units=data.get("optimization_units",[]); applicable=set(data.get("applicable_surfaces",[])); delivered=set()
    for i,u in enumerate(units):
        try:
            missing=[f for f in OPT if f not in u or u[f] is None or u[f]==""]
            if missing: fail(f"optimization_units[{i}] missing required fields: {', '.join(missing)}")
            surface=u.get("surface_type"); delivered.add(surface)
            if surface not in SPEC: fail(f"optimization_units[{i}] invalid surface_type")
            required(u,(SPEC[surface],),f"optimization_units[{i}] ")
            if surface=="title" and len(u.get("proposed_variant_ids",[]))<3: fail("title requires three candidate variants")
        except ValueError as exc: errors.append(str(exc))
    na=data.get("not_applicable",{})
    for surface in applicable-delivered:
        item=na.get(surface,{})
        if not item.get("evidence") or not item.get("alternative_surface"): errors.append(f"applicable surface {surface} lacks optimization or justified not_applicable")
    expert=not errors and bool(applicable)
    return {"status":"pass" if not errors else "fail","expert_optimization":expert,"label":"Expert optimization report" if expert else "Diagnostic only / Incomplete","errors":errors,"delivered_surfaces":sorted(delivered)}
if __name__ == "__main__": run_cli(validate,"D08-contract-1")
