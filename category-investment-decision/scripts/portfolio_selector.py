#!/usr/bin/env python3
"""Select a constrained candidate portfolio without changing base model scores."""

import itertools
import json
import math
import sys
from collections import Counter


CONFIDENCE = {"high": 1.0, "medium": 0.9, "low": 0.75}


def load_input(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate(data):
    if not isinstance(data.get("candidates"), list) or not data["candidates"]:
        raise ValueError("candidates must be a non-empty list")
    constraints = data.get("constraints", {})
    desired = int(constraints.get("desired_items", 3))
    if desired < 1 or desired > 5:
        raise ValueError("desired_items must be between 1 and 5")
    if len(data["candidates"]) > 60:
        raise ValueError("at most 60 candidates are supported per run")
    seen = set()
    for candidate in data["candidates"]:
        for field in ("id", "name", "score", "investment"):
            if field not in candidate:
                raise ValueError(f"candidate missing required field: {field}")
        if candidate["id"] in seen:
            raise ValueError(f"duplicate candidate id: {candidate['id']}")
        seen.add(candidate["id"])
        if not 0 <= float(candidate["score"]) <= 100:
            raise ValueError(f"score out of range for {candidate['id']}")
        if float(candidate["investment"]) < 0:
            raise ValueError(f"investment must be non-negative for {candidate['id']}")
        confidence = candidate.get("confidence", "medium")
        if confidence not in CONFIDENCE:
            raise ValueError(f"invalid confidence for {candidate['id']}")
    return constraints, desired


def concentration_penalty(combo, constraints):
    penalty = 0.0
    rates = {
        "category": float(constraints.get("penalty_same_category", 4.0)),
        "platform": float(constraints.get("penalty_same_platform", 2.0)),
        "supplier": float(constraints.get("penalty_same_supplier", 3.0)),
    }
    for field, rate in rates.items():
        counts = Counter(item.get(field) for item in combo if item.get(field))
        penalty += sum(math.comb(count, 2) * rate for count in counts.values() if count > 1)
    return penalty


def feasible(combo, constraints):
    budget = float(constraints.get("budget", math.inf))
    max_load = float(constraints.get("max_operational_load", math.inf))
    if sum(float(item["investment"]) for item in combo) > budget:
        return False
    if sum(float(item.get("operational_load", 0)) for item in combo) > max_load:
        return False
    for field, key in (("category", "max_per_category"), ("platform", "max_per_platform")):
        limit = int(constraints.get(key, len(combo)))
        counts = Counter(item.get(field) for item in combo if item.get(field))
        if counts and max(counts.values()) > limit:
            return False
    return True


def utility(combo, constraints):
    adjusted = sum(float(item["score"]) * CONFIDENCE[item.get("confidence", "medium")] for item in combo)
    penalty = concentration_penalty(combo, constraints)
    return adjusted - penalty, adjusted, penalty


def select(data):
    constraints, desired = validate(data)
    redlines = [item for item in data["candidates"] if item.get("redline", False)]
    eligible = [item for item in data["candidates"] if not item.get("redline", False)]
    best = None
    selected_size = 0
    for size in range(min(desired, len(eligible)), 0, -1):
        options = []
        for combo in itertools.combinations(eligible, size):
            if feasible(combo, constraints):
                score, adjusted, penalty = utility(combo, constraints)
                investment = sum(float(item["investment"]) for item in combo)
                load = sum(float(item.get("operational_load", 0)) for item in combo)
                tie_break = (score, adjusted, -investment, -load, tuple(item["id"] for item in combo))
                options.append((tie_break, combo, score, adjusted, penalty))
        if options:
            _, combo, score, adjusted, penalty = max(options, key=lambda row: row[0])
            best = (combo, score, adjusted, penalty)
            selected_size = size
            break
    if best is None:
        raise ValueError("no feasible portfolio under the supplied constraints")

    combo, score, adjusted, penalty = best
    selected_ids = {item["id"] for item in combo}
    selected = []
    for item in combo:
        selected.append({
            **item,
            "confidence_adjusted_score": round(
                float(item["score"]) * CONFIDENCE[item.get("confidence", "medium")], 2
            ),
        })
    return {
        "desired_items": desired,
        "selected_count": selected_size,
        "exact_count_feasible": selected_size == desired,
        "total_investment": round(sum(float(item["investment"]) for item in combo), 2),
        "total_operational_load": round(sum(float(item.get("operational_load", 0)) for item in combo), 2),
        "base_score_sum": round(sum(float(item["score"]) for item in combo), 2),
        "confidence_adjusted_score_sum": round(adjusted, 2),
        "concentration_penalty": round(penalty, 2),
        "portfolio_selection_utility": round(score, 2),
        "selected": selected,
        "excluded_redline": [{"id": item["id"], "name": item["name"]} for item in redlines],
        "eligible_not_selected": [
            {"id": item["id"], "name": item["name"]}
            for item in eligible if item["id"] not in selected_ids
        ],
        "note": "Portfolio utility is a selection aid, not a replacement for the 100-point base score.",
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: portfolio_selector.py input.json")
    try:
        result = select(load_input(sys.argv[1]))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
