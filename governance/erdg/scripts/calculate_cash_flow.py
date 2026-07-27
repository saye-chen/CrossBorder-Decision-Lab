#!/usr/bin/env python3
"""Calculate dated ERDG cash flow and peak funding requirement."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from erdg_common import decimal_string, decimal_value, parse_time

MAX_CASH_EVENTS = 100000


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    currency = payload.get("currency")
    if not isinstance(currency, str) or len(currency) != 3 or currency.upper() != currency:
        raise ValueError("currency must be a three-letter uppercase code")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("entries must be a non-empty list")
    if len(entries) > MAX_CASH_EVENTS:
        raise ValueError(f"entries exceeds capacity limit {MAX_CASH_EVENTS}")
    daily: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entries[{index}] must be an object")
        entry_id = entry.get("entry_id")
        if not isinstance(entry_id, str) or not entry_id or entry_id in seen:
            raise ValueError(f"entries[{index}].entry_id must be unique")
        seen.add(entry_id)
        when = parse_time(entry.get("occurred_at"), f"entries[{index}].occurred_at")
        direction = entry.get("direction")
        if direction not in {"inflow", "outflow"}:
            raise ValueError(f"entries[{index}].direction is invalid")
        amount = decimal_value(entry.get("amount"), f"entries[{index}].amount")
        if amount < 0:
            raise ValueError(f"entries[{index}].amount must be non-negative")
        daily[when.date().isoformat()] += amount if direction == "inflow" else -amount
    opening = decimal_value(payload.get("opening_cash", "0"), "opening_cash")
    balance = opening
    minimum = opening
    timeline = []
    for day in sorted(daily):
        balance += daily[day]
        minimum = min(minimum, balance)
        timeline.append({"date": day, "net_cash": decimal_string(daily[day]), "closing_cash": decimal_string(balance)})
    return {
        "contract": "ERDG-CONTRACT-2026.01",
        "currency": currency,
        "timeline": timeline,
        "ending_cash": decimal_string(balance),
        "minimum_cash": decimal_string(minimum),
        "peak_funding_required": decimal_string(max(Decimal("0"), -minimum)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(calculate(payload), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
