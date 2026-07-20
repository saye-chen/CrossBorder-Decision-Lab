#!/usr/bin/env python3
from d08_common import number, run_cli

def rank(data):
    actions=[]
    for a in data.get("actions",[]):
        blocked=bool(a.get("gate_blocked")) or bool(a.get("unmet_dependencies")) or bool(a.get("out_of_scope"))
        score=number(a.get("severity",0),"severity")*number(a.get("impact",0),"impact")*number(a.get("confidence",0),"confidence")
        denom=1+number(a.get("cost",0),"cost")+number(a.get("risk",0),"risk")
        actions.append({**a,"blocked":blocked,"priority_score":score/denom})
    actions.sort(key=lambda x:(x["blocked"],-x["priority_score"],str(x.get("action_id",""))))
    return {"status":"ok","ranked_actions":actions,"action_order":[a.get("action_id") for a in actions if not a["blocked"]],"blocked_actions":[a.get("action_id") for a in actions if a["blocked"]]}
if __name__ == "__main__": run_cli(rank,"D08-rank-1")
