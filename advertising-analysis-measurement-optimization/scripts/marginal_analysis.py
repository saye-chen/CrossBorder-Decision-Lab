#!/usr/bin/env python3
"""Compute adjacent-budget average, marginal, uncertainty and action states."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def numeric(row: dict, key: str, index: int, *, default: float | None = None) -> float:
    value = row.get(key, default)
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {index}: {key} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"row {index}: {key} must be finite")
    return result


def analyze(rows: list[dict]) -> dict:
    if not isinstance(rows, list) or not rows:
        raise ValueError("input must be a non-empty list")
    normalized = []
    for index, row in enumerate(rows, 1):
        spend = numeric(row, "spend", index)
        revenue = numeric(row, "mature_revenue", index)
        profit = numeric(row, "contribution_profit", index)
        revenue_low = numeric(row, "mature_revenue_low", index, default=revenue)
        profit_low = numeric(row, "contribution_profit_low", index, default=profit)
        if spend < 0 or revenue < 0 or revenue_low < 0:
            raise ValueError(f"row {index}: spend and revenue must be non-negative")
        if revenue_low > revenue or profit_low > profit:
            raise ValueError(f"row {index}: lower bounds cannot exceed point estimates")
        normalized.append({
            "spend": spend,
            "mature_revenue": revenue,
            "contribution_profit": profit,
            "mature_revenue_low": revenue_low,
            "contribution_profit_low": profit_low,
            "maturity": row.get("maturity", "mature"),
        })
    normalized.sort(key=lambda row: row["spend"])
    if len({row["spend"] for row in normalized}) != len(normalized):
        raise ValueError("spend stages must be unique")

    stages = []
    for index, row in enumerate(normalized):
        result = {
            **row,
            "average_roas": row["mature_revenue"] / row["spend"] if row["spend"] else None,
            "average_contribution_per_spend": row["contribution_profit"] / row["spend"] if row["spend"] else None,
            "marginal_roas": None,
            "marginal_roas_low": None,
            "marginal_contribution": None,
            "marginal_contribution_low": None,
            "decision": "Baseline",
        }
        if index:
            previous = normalized[index - 1]
            delta_spend = row["spend"] - previous["spend"]
            if delta_spend <= 0:
                raise ValueError("spend stages must increase")
            result["marginal_roas"] = (row["mature_revenue"] - previous["mature_revenue"]) / delta_spend
            result["marginal_roas_low"] = (row["mature_revenue_low"] - previous["mature_revenue_low"]) / delta_spend
            result["marginal_contribution"] = (row["contribution_profit"] - previous["contribution_profit"]) / delta_spend
            result["marginal_contribution_low"] = (row["contribution_profit_low"] - previous["contribution_profit_low"]) / delta_spend
            if row["maturity"] != "mature":
                result["decision"] = "Inconclusive"
            elif result["marginal_contribution_low"] > 0:
                result["decision"] = "Eligible to scale"
            elif result["marginal_contribution"] < 0:
                result["decision"] = "Reduce"
            else:
                result["decision"] = "Hold/Test"
        stages.append(result)

    eligible = [row["spend"] for row in stages if row["decision"] == "Eligible to scale"]
    return {
        "stages": stages,
        "highest_supported_spend": max(eligible) if eligible else normalized[0]["spend"],
        "warning": "Adjacent stages describe marginal performance; they do not by themselves prove causal incrementality.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        rows = json.loads(args.input.read_text(encoding="utf-8"))
        result = analyze(rows)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
