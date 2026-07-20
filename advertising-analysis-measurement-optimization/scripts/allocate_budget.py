#!/usr/bin/env python3
"""Allocate discrete advertising budget under marginal, risk and group constraints."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def number(value: object, name: str, *, minimum: float | None = None) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(result) or (minimum is not None and result < minimum):
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return result


def normalize_candidate(raw: dict) -> dict:
    candidate_id = str(raw.get("id", "")).strip()
    if not candidate_id:
        raise ValueError("candidate id is required")
    step = number(raw.get("step"), f"{candidate_id}.step", minimum=0)
    if step == 0:
        raise ValueError(f"{candidate_id}.step must be positive")
    minimum = number(raw.get("min_budget", 0), f"{candidate_id}.min_budget", minimum=0)
    maximum = number(raw.get("max_budget"), f"{candidate_id}.max_budget", minimum=0)
    if minimum > maximum:
        raise ValueError(f"{candidate_id}: min_budget exceeds max_budget")
    if minimum % step > 1e-9:
        raise ValueError(f"{candidate_id}: min_budget must align to step")
    marginal = number(raw.get("marginal_contribution_per_currency"), f"{candidate_id}.marginal")
    uncertainty = number(raw.get("uncertainty_penalty", 0), f"{candidate_id}.uncertainty", minimum=0)
    risk = number(raw.get("risk_penalty", 0), f"{candidate_id}.risk", minimum=0)
    return {
        **raw,
        "id": candidate_id,
        "step": step,
        "min_budget": minimum,
        "max_budget": maximum,
        "raw_marginal": marginal,
        "risk_adjusted_marginal": marginal - uncertainty - risk,
        "allocated": 0.0,
        "group": str(raw.get("group", "ungrouped")),
    }


def allocate(payload: dict) -> dict:
    budget = number(payload.get("budget"), "budget", minimum=0)
    reserve = number(payload.get("reserve", 0), "reserve", minimum=0)
    if reserve > budget:
        raise ValueError("reserve cannot exceed budget")
    spendable = budget - reserve
    candidates = [normalize_candidate(item) for item in payload.get("candidates", [])]
    if not candidates:
        raise ValueError("at least one candidate is required")
    if len({item["id"] for item in candidates}) != len(candidates):
        raise ValueError("candidate ids must be unique")

    group_caps = {
        str(key): number(value, f"group_cap.{key}", minimum=0)
        for key, value in payload.get("group_caps", {}).items()
    }
    group_spend: dict[str, float] = {}

    # Minimums are commitments: reject the whole plan if they do not fit.
    minimum_total = sum(item["min_budget"] for item in candidates)
    if minimum_total > spendable + 1e-9:
        raise ValueError("candidate minimum budgets exceed spendable budget")
    for item in candidates:
        cap = group_caps.get(item["group"], math.inf)
        next_group = group_spend.get(item["group"], 0) + item["min_budget"]
        if next_group > cap + 1e-9:
            raise ValueError(f"minimum budgets exceed group cap for {item['group']}")
        item["allocated"] = item["min_budget"]
        group_spend[item["group"]] = next_group
        spendable -= item["min_budget"]

    rejected = []
    ranked = sorted(candidates, key=lambda item: (-item["risk_adjusted_marginal"], item["id"]))
    for item in ranked:
        if item["risk_adjusted_marginal"] <= 0:
            rejected.append({"id": item["id"], "reason": "non_positive_risk_adjusted_marginal"})
            continue
        group_cap = group_caps.get(item["group"], math.inf)
        while (
            spendable + 1e-9 >= item["step"]
            and item["allocated"] + item["step"] <= item["max_budget"] + 1e-9
            and group_spend.get(item["group"], 0) + item["step"] <= group_cap + 1e-9
        ):
            item["allocated"] += item["step"]
            group_spend[item["group"]] = group_spend.get(item["group"], 0) + item["step"]
            spendable -= item["step"]

    return {
        "allocations": [
            {
                "id": item["id"],
                "group": item["group"],
                "allocated": round(item["allocated"], 8),
                "marginal_contribution_per_currency": item["raw_marginal"],
                "risk_adjusted_marginal": item["risk_adjusted_marginal"],
            }
            for item in candidates
        ],
        "group_spend": group_spend,
        "reserve": reserve,
        "unallocated": round(spendable, 8),
        "rejected": rejected,
        "decision": "Allocate" if any(item["allocated"] > 0 for item in candidates) else "Hold",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = allocate(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
