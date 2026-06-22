#!/usr/bin/env python3
"""Deterministic unit-economics calculator for category reports."""

import argparse
import json


def parser():
    p = argparse.ArgumentParser(description="Calculate per-unit profit and break-even ad rate.")
    p.add_argument("--price", type=float, required=True)
    for name in ("product", "packaging", "duty", "inbound", "fulfillment", "storage", "quality", "payment", "other"):
        p.add_argument(f"--{name}", type=float, default=0.0)
    for name in ("commission_rate", "ad_rate", "promo_rate", "return_rate", "return_loss_rate"):
        p.add_argument(f"--{name.replace('_', '-')}", dest=name, type=float, default=0.0,
                       help="Decimal rate, e.g. 0.15 for 15%%")
    return p


def main():
    a = parser().parse_args()
    if a.price <= 0:
        raise SystemExit("price must be greater than zero")
    rates = (a.commission_rate, a.ad_rate, a.promo_rate, a.return_rate, a.return_loss_rate)
    if any(rate < 0 or rate > 1 for rate in rates):
        raise SystemExit("rates must be between 0 and 1")

    fixed = sum((a.product, a.packaging, a.duty, a.inbound, a.fulfillment,
                 a.storage, a.quality, a.payment, a.other))
    commission = a.price * a.commission_rate
    advertising = a.price * a.ad_rate
    promotion = a.price * a.promo_rate
    return_reserve = a.price * a.return_rate * a.return_loss_rate
    profit_before_ads = a.price - fixed - commission - promotion - return_reserve
    net_profit = profit_before_ads - advertising
    result = {
        "price": round(a.price, 2),
        "fixed_costs": round(fixed, 2),
        "commission": round(commission, 2),
        "advertising": round(advertising, 2),
        "promotion_affiliate": round(promotion, 2),
        "return_reserve": round(return_reserve, 2),
        "profit_before_ads": round(profit_before_ads, 2),
        "net_profit": round(net_profit, 2),
        "net_margin_pct": round(net_profit / a.price * 100, 1),
        "break_even_ad_rate_pct": round(max(profit_before_ads / a.price, 0) * 100, 1),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
