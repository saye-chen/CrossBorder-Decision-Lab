#!/usr/bin/env python3
"""Restate attributed orders into mature revenue and contribution profit."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

COST_FIELDS = ["discount", "refund", "chargeback", "tax", "cogs", "fulfillment", "platform_fee", "service_cost", "ad_spend"]
ALL_FIELDS = ["gross_revenue", *COST_FIELDS]


def amount(row: dict, key: str, row_number: int) -> float:
    try:
        value = float(row.get(key, 0) or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: invalid {key}") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"row {row_number}: {key} must be finite and non-negative")
    return value


def restate(rows: list[dict]) -> dict:
    totals = defaultdict(float)
    currencies = set()
    maturity_counts = defaultdict(int)
    order_ids = set()
    for row_number, row in enumerate(rows, 2):
        order_id = str(row.get("order_id", f"row-{row_number}"))
        if order_id in order_ids:
            raise ValueError(f"row {row_number}: duplicate order_id {order_id}")
        order_ids.add(order_id)
        currency = str(row.get("currency", "UNSPECIFIED"))
        currencies.add(currency)
        maturity = str(row.get("maturity", "mature"))
        if maturity not in {"mature", "immature", "excluded"}:
            raise ValueError(f"row {row_number}: invalid maturity")
        maturity_counts[maturity] += 1
        values = {key: amount(row, key, row_number) for key in ALL_FIELDS}
        if maturity == "excluded":
            continue
        for key, value in values.items():
            totals[key] += value

    if len(currencies) > 1:
        raise ValueError("multiple currencies require prior FX normalization")
    net = totals["gross_revenue"] - sum(totals[key] for key in ["discount", "refund", "chargeback", "tax"])
    pre_ad = net - sum(totals[key] for key in ["cogs", "fulfillment", "platform_fee", "service_cost"])
    post_ad = pre_ad - totals["ad_spend"]
    mature = maturity_counts["immature"] == 0
    return {
        "rows": len(rows),
        "currency": next(iter(currencies), "UNSPECIFIED"),
        "maturity_counts": dict(maturity_counts),
        **{key: round(totals[key], 6) for key in ALL_FIELDS},
        "mature_net_revenue": round(net, 6),
        "pre_ad_contribution_profit": round(pre_ad, 6),
        "ad_contribution_profit": round(post_ad, 6),
        "ad_contribution_margin_rate": round(post_ad / net, 6) if net else None,
        "status": "mature" if mature else "provisional",
        "decision_limit": None if mature else "Do not validate Scale/Stop until immature orders settle",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8-sig", newline="") as handle:
            result = restate(list(csv.DictReader(handle)))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
