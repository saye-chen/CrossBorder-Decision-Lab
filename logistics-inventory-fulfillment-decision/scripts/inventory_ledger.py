#!/usr/bin/env python3
from common import main,n,num
def run(d):
    inbound=0
    for i,x in enumerate(d.get("inbound",[])):
        inbound+=n(x,"qty")*num(x.get("eligibility",0),f"eligibility[{i}]",0)
        if not 0 <= x.get("eligibility",0) <= 1: raise ValueError("eligibility must be in [0, 1]")
    pos=n(d,"sellable")+inbound+n(d,"released_production")-n(d,"allocated")-n(d,"backorders")-n(d,"expected_quarantine_loss")
    if pos<0 and not d.get("allow_negative_position",False): raise ValueError("inventory position is negative")
    opening=n(d,"opening_physical");left=opening+n(d,"receipts")+n(d,"returns_received")+n(d,"positive_adjustments")
    right=n(d,"sales_shipments")+n(d,"supplier_returns")+n(d,"transfers_out")+n(d,"damage_disposal")+n(d,"negative_adjustments")+n(d,"closing_physical")
    diff=left-right;tol=n(d,"tolerance",0)
    return {"eligible_inbound":round(inbound,6),"inventory_position":round(pos,6),"ledger_difference":round(diff,6),"balanced":abs(diff)<=tol,"decision_gate":"pass" if abs(diff)<=tol else "blocked"}
if __name__=="__main__":main(run)
