#!/usr/bin/env python3
from common import main,n,num
def run(d):
    paths=[]
    for p in d.get("paths",[]):
        if not p.get("compliance_pass",False) or not p.get("title_clear",False):
            paths.append({"id":p.get("id"),"eligible":False,"reason":"compliance_or_title"});continue
        proceeds=n(p,"cash_proceeds")*num(p.get("collection_probability",1),"collection_probability",0)
        if not 0 <= p.get("collection_probability",1) <= 1: raise ValueError("collection_probability must be in [0, 1]")
        costs=sum(n(p,k) for k in ["preparation_rework","transfer_freight","duties_taxes_fees","commission","brand_deidentification","claims_liability","termination_closeout","downside_reserve"])
        rate=num(p.get("annual_discount_rate",d.get("annual_discount_rate",0)),"annual_discount_rate",0)
        cash_days=n(p,"cash_days");discounted=(proceeds-costs)/((1+rate)**(cash_days/365))
        if p.get("deadline") and p.get("execution_days") is not None:
            from datetime import date,timedelta
            deadline=date.fromisoformat(p["deadline"]);latest=(deadline-timedelta(days=int(n(p,"execution_days")+n(p,"risk_buffer_days")))).isoformat()
        else: latest=None
        paths.append({"id":p.get("id"),"eligible":True,"risk_adjusted_value":round(discounted,6),"cash_days":cash_days,"latest_decision_date":latest})
    eligible=[x for x in paths if x.get("eligible")];eligible.sort(key=lambda x:(-x["risk_adjusted_value"],x["cash_days"],str(x["id"])))
    hold=n(d,"expected_net_sales_proceeds")-sum(n(d,k) for k in ["additional_storage_handling","financing","markdown_loss","obsolescence_damage","compliance_channel_risk","future_exit_cost"])
    best=eligible[0] if eligible else None
    decision="dispose" if best and best["risk_adjusted_value"]>hold else "hold" if d else "blocked"
    return {"hold_value":round(hold,6),"paths":paths,"recommended":best if decision=="dispose" else {"id":"hold","risk_adjusted_value":round(hold,6)},"decision":decision}
if __name__=="__main__":main(run)
