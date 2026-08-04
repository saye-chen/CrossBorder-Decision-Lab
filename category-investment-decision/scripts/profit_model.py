#!/usr/bin/env python3
"""Deterministic unit and batch economics calculator for category reports."""

import argparse
import json
import math
from pathlib import Path


def parser():
    p = argparse.ArgumentParser(description="Calculate per-unit profit, break-even ad rate, and optional batch break-even.")
    p.add_argument("--input-json", type=Path, help="JSON object containing the same inputs as the command line.")
    p.add_argument("--price", type=float)
    for name in ("product", "packaging", "duty", "inbound", "fulfillment", "storage", "quality", "payment", "other"):
        p.add_argument(f"--{name}", type=float, default=0.0)
    for name in ("commission_rate", "ad_rate", "promo_rate", "return_rate", "return_loss_rate"):
        p.add_argument(f"--{name.replace('_', '-')}", dest=name, type=float, default=0.0,
                       help="Decimal rate, e.g. 0.15 for 15%%")
    p.add_argument("--batch-fixed-costs", type=float, default=0.0,
                   help="Total fixed costs for one test/batch, separate from per-unit costs.")
    p.add_argument("--batch-fixed-costs-json", type=Path,
                   help="JSON object or list of fixed cost items for one test/batch.")
    return p


def load_batch_fixed_costs(path):
    if path is None:
        return 0.0, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid batch fixed cost JSON: {exc}") from exc
    if isinstance(data, dict):
        items = data
    elif isinstance(data, list):
        items = {}
        for index, item in enumerate(data):
            if not isinstance(item, dict) or "name" not in item or "amount" not in item:
                raise SystemExit("batch fixed cost list items must contain name and amount")
            items[str(item["name"])] = item["amount"]
    else:
        raise SystemExit("batch fixed cost JSON must be an object or list")
    total = 0.0
    cleaned = {}
    for name, value in items.items():
        try:
            amount = float(value)
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"batch fixed cost must be numeric: {name}") from exc
        if not math.isfinite(amount) or amount < 0:
            raise SystemExit(f"batch fixed cost must be non-negative: {name}")
        cleaned[str(name)] = round(amount, 2)
        total += amount
    return total, cleaned


def main():
    a = parser().parse_args()
    if a.input_json:
        try:
            payload = json.loads(a.input_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"invalid input JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise SystemExit("input JSON must be an object")
        allowed = set(vars(a)) - {"input_json", "batch_fixed_costs_json"}
        unknown = set(payload) - allowed
        if unknown:
            raise SystemExit(f"unknown input JSON fields: {sorted(unknown)}")
        for key, value in payload.items():
            setattr(a, key, value)
    if a.price is None:
        raise SystemExit("price is required")
    if not math.isfinite(a.price) or a.price <= 0:
        raise SystemExit("price must be greater than zero")
    rates = (a.commission_rate, a.ad_rate, a.promo_rate, a.return_rate, a.return_loss_rate)
    if any(not math.isfinite(rate) or rate < 0 or rate > 1 for rate in rates):
        raise SystemExit("rates must be between 0 and 1")
    unit_costs = (a.product, a.packaging, a.duty, a.inbound, a.fulfillment,
                  a.storage, a.quality, a.payment, a.other)
    if any(not math.isfinite(cost) or cost < 0 for cost in unit_costs):
        raise SystemExit("unit costs must be non-negative")
    if not math.isfinite(a.batch_fixed_costs) or a.batch_fixed_costs < 0:
        raise SystemExit("batch fixed costs must be non-negative")

    unit_cost_total = sum(unit_costs)
    json_batch_fixed, batch_fixed_items = load_batch_fixed_costs(a.batch_fixed_costs_json)
    batch_fixed_costs = a.batch_fixed_costs + json_batch_fixed
    commission = a.price * a.commission_rate
    advertising = a.price * a.ad_rate
    promotion = a.price * a.promo_rate
    return_reserve = a.price * a.return_rate * a.return_loss_rate
    profit_before_ads = a.price - unit_cost_total - commission - promotion - return_reserve
    net_profit = profit_before_ads - advertising
    contribution_margin = profit_before_ads
    if contribution_margin > 0:
        break_even_units = math.ceil(batch_fixed_costs / contribution_margin) if batch_fixed_costs else 0
        break_even_revenue = break_even_units * a.price
        batch_status = "viable_under_current_assumptions"
    else:
        break_even_units = None
        break_even_revenue = None
        batch_status = "not_viable_under_current_assumptions"
    result = {
        "price": round(a.price, 2),
        "fixed_costs": round(unit_cost_total, 2),
        "unit_costs": round(unit_cost_total, 2),
        "commission": round(commission, 2),
        "advertising": round(advertising, 2),
        "promotion_affiliate": round(promotion, 2),
        "return_reserve": round(return_reserve, 2),
        "profit_before_ads": round(profit_before_ads, 2),
        "net_profit": round(net_profit, 2),
        "net_margin_pct": round(net_profit / a.price * 100, 1),
        "break_even_ad_rate_pct": round(max(profit_before_ads / a.price, 0) * 100, 1),
        "contribution_margin_per_unit": round(contribution_margin, 2),
        "contribution_margin_pct": round(contribution_margin / a.price * 100, 1),
        "batch_fixed_costs": round(batch_fixed_costs, 2),
        "batch_fixed_cost_items": batch_fixed_items,
        "break_even_units": break_even_units,
        "break_even_revenue": round(break_even_revenue, 2) if break_even_revenue is not None else None,
        "batch_break_even_status": batch_status,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
