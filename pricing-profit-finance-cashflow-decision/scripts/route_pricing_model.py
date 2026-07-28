#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FAMILIES = {
    "P01": "cost_plus", "P02": "target_margin_contribution", "P03": "break_even_survival",
    "P04": "competitive_reference", "P05": "value_wtp", "P06": "elasticity_profit_optimization",
    "P07": "penetration", "P08": "skimming_premium", "P09": "psychological_price_point",
    "P10": "version_good_better_best", "P11": "tier_contract", "P12": "channel_waterfall",
    "P13": "subscription_consumable", "P14": "inventory_time_dynamic", "P15": "clearance_recovery",
    "P16": "preorder_custom", "P17": "bundle_cross_subsidy", "P18": "auction_usage_capacity",
}

ROUTES = {
    "marketplace_standard": ("P02", ["P04", "P12"]),
    "content_commerce": ("P02", ["P07", "P17"]),
    "dtc_brand": ("P05", ["P02", "P09", "P13"]),
    "wholesale_distribution": ("P11", ["P12", "P01"]),
    "subscription": ("P13", ["P17", "P05"]),
    "custom_preorder": ("P16", ["P05", "P01"]),
    "seasonal_inventory": ("P14", ["P15", "P06"]),
    "premium_innovation": ("P08", ["P05", "P10"]),
    "low_price_volume": ("P07", ["P03", "P06"]),
    "refurbished_secondhand": ("P15", ["P04", "P05"]),
    "usage_capacity": ("P18", ["P11", "P06"]),
}


def route(payload: dict) -> dict:
    archetype = payload.get("merchant_archetype")
    evidence = set(payload.get("evidence_capabilities", []))
    objective = payload.get("objective")
    if archetype not in ROUTES:
        return {
            "status": "inconclusive", "reason": "UNKNOWN_MODEL_ROUTE",
            "primary_family": None, "supporting_families": [],
            "floor_required": True, "evidence_ceiling": "hypothesis",
            "missing": ["recognized merchant_archetype"],
        }
    primary, supporting = ROUTES[archetype]
    missing = []
    if primary in {"P05", "P08"} and "wtp" not in evidence:
        missing.append("validated_wtp")
    if primary in {"P06", "P14"} and not ({"historical_response", "experiment"} & evidence):
        missing.append("price_demand_response")
    if primary == "P13" and "retention" not in evidence:
        missing.append("retention")
    if primary == "P17" and "incrementality" not in evidence:
        missing.append("incremental_attachment")
    if not objective:
        missing.append("pricing_objective")
    ceiling = "validated_candidate" if not missing else "hypothesis"
    return {
        "status": "routed" if not missing else "proposed",
        "primary_family": primary,
        "primary_name": FAMILIES[primary],
        "supporting_families": supporting,
        "supporting_names": [FAMILIES[item] for item in supporting],
        "floor_required": True,
        "evidence_ceiling": ceiling,
        "missing": missing,
        "reprice_triggers": ["cost", "fee", "tax", "fx", "inventory", "competition", "lifecycle", "evidence"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(route(json.loads(args.input.read_text())), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
