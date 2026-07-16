#!/usr/bin/env python3
"""Restate attributed orders into mature net revenue and contribution profit."""
import argparse,csv,json,math
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    rows=list(csv.DictReader(a.input.open(encoding="utf-8-sig"))); total={k:0.0 for k in ["gross_revenue","discount","refund","chargeback","tax","cogs","fulfillment","platform_fee","service_cost","ad_spend"]}
    for i,r in enumerate(rows,2):
        for k in total:
            try: v=float(r.get(k,0) or 0)
            except ValueError: p.error(f"row {i} invalid {k}")
            if not math.isfinite(v):p.error(f"row {i} non-finite {k}")
            if v<0:p.error(f"row {i} negative {k}")
            total[k]+=v
    net=total["gross_revenue"]-total["discount"]-total["refund"]-total["chargeback"]-total["tax"]
    pre=net-total["cogs"]-total["fulfillment"]-total["platform_fee"]-total["service_cost"]
    out={"rows":len(rows),**{k:round(v,6) for k,v in total.items()},"mature_net_revenue":round(net,6),"pre_ad_contribution_profit":round(pre,6),"ad_contribution_profit":round(pre-total["ad_spend"],6)}
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
