#!/usr/bin/env python3
"""Deterministic video commerce unit economics calculator.

Tailored for VLB's video commerce decision context. Computes:
- Contribution margin per unit
- Maximum sustainable CPA
- Break-even ad rate
- Batch break-even orders
- ROI (when content + promotion investment is provided)

Usage:
    # Basic unit economics
    python3 unit_economics.py --price 29.99 \
        --product 5.0 --packaging 1.0 --shipping 3.5 \
        --commission-rate 0.15 --payment-rate 0.03 \
        --return-rate 0.08 --return-loss-rate 0.5

    # With CPA and content investment for ROI
    python3 unit_economics.py --price 29.99 \
        --product 5.0 --packaging 1.0 --shipping 3.5 \
        --commission-rate 0.15 --payment-rate 0.03 \
        --return-rate 0.08 --return-loss-rate 0.5 \
        --cpa 4.0 --target-margin-rate 0.10 \
        --content-cost 500 --promotion-cost 1000 \
        --orders 300

    # Reverse: given CPA, what price do I need?
    python3 unit_economics.py --reverse --cpa 5.0 \
        --product 5.0 --packaging 1.0 --shipping 3.5 \
        --commission-rate 0.15 --payment-rate 0.03 \
        --return-rate 0.08 --return-loss-rate 0.5 \
        --target-margin-rate 0.10

    # Batch break-even with fixed costs
    python3 unit_economics.py --price 29.99 \
        --product 5.0 --packaging 1.0 --shipping 3.5 \
        --commission-rate 0.15 --payment-rate 0.03 \
        --return-rate 0.08 --return-loss-rate 0.5 \
        --batch-fixed-costs 2000
"""

import argparse
import json
import math


def build_parser():
    p = argparse.ArgumentParser(
        description="Calculate video commerce unit economics: "
        "contribution margin, max CPA, break-even ad rate, ROI."
    )

    # Revenue
    p.add_argument("--price", type=float, help="Selling price per unit.")

    # Per-unit costs
    for name in ("product", "packaging", "shipping", "duty", "fulfillment",
                 "storage", "quality", "other"):
        p.add_argument(f"--{name}", type=float, default=0.0,
                       help=f"Per-unit cost: {name} (default: 0)")

    # Rates
    for name in ("commission-rate", "payment-rate", "return-rate",
                 "return-loss-rate", "promo-rate"):
        p.add_argument(f"--{name}", dest=name.replace("-", "_"),
                       type=float, default=0.0,
                       help="Decimal rate, e.g. 0.15 for 15%%")

    # Video commerce specific
    p.add_argument("--cpa", type=float, default=None,
                   help="Actual cost per acquisition (ad spend / orders).")
    p.add_argument("--target-margin-rate", type=float, default=0.0,
                   help="Target net margin rate (decimal), e.g. 0.10 for 10%%.")

    # Batch / ROI
    p.add_argument("--batch-fixed-costs", type=float, default=0.0,
                   help="Total fixed costs for content production + creator fees + initial ad spend.")
    p.add_argument("--content-cost", type=float, default=None,
                   help="Content production cost (video, creator, editing).")
    p.add_argument("--promotion-cost", type=float, default=None,
                   help="Promotion / ad spend for this batch.")
    p.add_argument("--orders", type=int, default=None,
                   help="Number of orders attributed to this content batch.")

    # Reverse mode
    p.add_argument("--reverse", action="store_true",
                   help="Reverse mode: given CPA and costs, calculate required price.")

    return p


def compute_unit_economics(args):
    """Compute unit economics from parsed arguments."""
    # Validate
    if not args.reverse and (args.price is None or args.price <= 0):
        raise SystemExit("price must be greater than zero (or use --reverse)")
    if args.reverse and (args.cpa is None or args.cpa < 0):
        raise SystemExit("--reverse mode requires --cpa")

    rates = {
        "commission_rate": args.commission_rate,
        "payment_rate": args.payment_rate,
        "return_rate": args.return_rate,
        "return_loss_rate": args.return_loss_rate,
        "promo_rate": args.promo_rate,
    }
    for name, value in rates.items():
        if value < 0 or value > 1:
            raise SystemExit(f"{name} must be between 0 and 1, got {value}")

    # Per-unit variable costs (excluding rates)
    unit_costs = {
        "product": args.product,
        "packaging": args.packaging,
        "shipping": args.shipping,
        "duty": args.duty,
        "fulfillment": args.fulfillment,
        "storage": args.storage,
        "quality": args.quality,
        "other": args.other,
    }
    for name, value in unit_costs.items():
        if value < 0:
            raise SystemExit(f"{name} cost must be non-negative, got {value}")
    unit_cost_total = sum(unit_costs.values())

    if args.reverse:
        # Reverse mode: find minimum price given CPA
        # price - unit_cost - price*commission - price*payment - price*promo
        #   - price*return*return_loss - CPA - price*target_margin >= 0
        # price * (1 - commission - payment - promo - return*return_loss - target_margin)
        #   >= unit_cost + CPA
        total_rate = (args.commission_rate + args.payment_rate + args.promo_rate
                      + args.return_rate * args.return_loss_rate + args.target_margin_rate)
        if total_rate >= 1:
            raise SystemExit(
                f"total rate ({total_rate:.2%}) >= 100%%, no viable price exists"
            )
        min_price = (unit_cost_total + args.cpa) / (1 - total_rate)
        return {
            "mode": "reverse",
            "cpa": round(args.cpa, 2),
            "unit_costs": round(unit_cost_total, 2),
            "total_rate_pct": round(total_rate * 100, 1),
            "minimum_price": round(min_price, 2),
            "recommended_price": round(math.ceil(min_price * 20) / 20, 2),  # round up to nearest $0.05
        }

    # Forward mode
    price = args.price
    commission = price * args.commission_rate
    payment = price * args.payment_rate
    promo = price * args.promo_rate
    return_reserve = price * args.return_rate * args.return_loss_rate

    # Contribution margin = price - all variable costs (before ad/CPA)
    contribution_margin = price - unit_cost_total - commission - payment - promo - return_reserve

    # Max CPA = contribution margin - target profit
    target_profit = price * args.target_margin_rate
    max_cpa = contribution_margin - target_profit

    # Break-even ad rate = contribution margin / price
    break_even_ad_rate = contribution_margin / price if price > 0 else 0

    # Net profit after CPA
    net_profit = None
    net_margin_pct = None
    if args.cpa is not None:
        net_profit = contribution_margin - args.cpa
        net_margin_pct = net_profit / price * 100 if price > 0 else 0

    # Batch break-even
    batch_fixed = args.batch_fixed_costs or 0.0
    if args.content_cost is not None:
        batch_fixed += args.content_cost
    if args.promotion_cost is not None:
        batch_fixed += args.promotion_cost

    break_even_orders = None
    if batch_fixed > 0 and net_profit is not None and net_profit > 0:
        break_even_orders = math.ceil(batch_fixed / net_profit)
    elif batch_fixed > 0 and contribution_margin > 0:
        # Without CPA, use contribution margin as upper bound
        break_even_orders = math.ceil(batch_fixed / contribution_margin)

    # ROI
    roi = None
    total_investment = batch_fixed if batch_fixed > 0 else None
    if total_investment and args.orders and args.orders > 0:
        if args.cpa is not None and net_profit is not None:
            total_revenue = price * args.orders
            total_net = net_profit * args.orders
            roi = (total_net - total_investment) / total_investment * 100
        else:
            total_revenue = price * args.orders
            total_contribution = contribution_margin * args.orders
            roi = (total_contribution - total_investment) / total_investment * 100

    result = {
        "price": round(price, 2),
        "unit_costs": {k: round(v, 2) for k, v in unit_costs.items() if v > 0},
        "unit_cost_total": round(unit_cost_total, 2),
        "commission": round(commission, 2),
        "payment": round(payment, 2),
        "promotion_affiliate": round(promo, 2),
        "return_reserve": round(return_reserve, 2),
        "contribution_margin": round(contribution_margin, 2),
        "contribution_margin_pct": round(contribution_margin / price * 100, 1),
        "max_cpa": round(max_cpa, 2),
        "break_even_ad_rate_pct": round(break_even_ad_rate * 100, 1),
        "batch_fixed_costs": round(batch_fixed, 2),
    }

    if args.cpa is not None:
        result["actual_cpa"] = round(args.cpa, 2)
        result["net_profit"] = round(net_profit, 2)
        result["net_margin_pct"] = round(net_margin_pct, 1)
        result["cpa_headroom"] = round(max_cpa - args.cpa, 2)
        result["cpa_utilization_pct"] = round(args.cpa / max_cpa * 100, 1) if max_cpa > 0 else None

    if break_even_orders is not None:
        result["break_even_orders"] = break_even_orders

    if roi is not None:
        result["roi_pct"] = round(roi, 1)
        result["total_investment"] = round(total_investment, 2)
        result["total_revenue"] = round(price * args.orders, 2)
        result["orders"] = args.orders

    # Decision hint
    if contribution_margin <= 0:
        result["unit_economics_status"] = "negative_contribution"
    elif args.cpa is not None and net_profit is not None:
        if args.cpa > max_cpa:
            result["unit_economics_status"] = "cpa_exceeds_max"
        elif net_profit < 0:
            result["unit_economics_status"] = "negative_net_profit"
        else:
            result["unit_economics_status"] = "viable"
    else:
        result["unit_economics_status"] = "positive_contribution_no_cpa"

    return result


def main():
    args = build_parser().parse_args()
    result = compute_unit_economics(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
