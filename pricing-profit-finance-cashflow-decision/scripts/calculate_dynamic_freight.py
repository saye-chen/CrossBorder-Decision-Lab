#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, ceil_increment, dec, exact, rate


MODES = {"land", "sea", "air", "rail", "warehouse", "last_mile", "reverse"}


def calculate_segment(segment: dict[str, Any], index: int) -> dict[str, str]:
    mode = segment.get("transport_mode")
    if mode not in MODES:
        raise PPFCError(f"segments[{index}].transport_mode invalid")
    if segment.get("eligible") is not True:
        raise PPFCError(f"segments[{index}] route is not eligible")
    actual = dec(segment.get("actual_weight"), f"segments[{index}].actual_weight", nonnegative=True)
    volume = dec(segment.get("volume"), f"segments[{index}].volume", nonnegative=True)
    divisor = dec(segment.get("volumetric_divisor"), f"segments[{index}].volumetric_divisor", nonnegative=True)
    if divisor == 0:
        raise PPFCError(f"segments[{index}].volumetric_divisor must be positive")
    increment = dec(segment.get("weight_rounding_increment"), f"segments[{index}].weight_rounding_increment", nonnegative=True)
    volumetric = volume / divisor
    chargeable = ceil_increment(max(actual, volumetric), increment)
    base = dec(segment.get("base_charge"), f"segments[{index}].base_charge", nonnegative=True)
    minimum = dec(segment.get("minimum_charge"), f"segments[{index}].minimum_charge", nonnegative=True)
    tiers = segment.get("tiers")
    if not isinstance(tiers, list) or not tiers:
        raise PPFCError(f"segments[{index}].tiers required")
    matched = []
    for tier in tiers:
        lower = dec(tier.get("from_inclusive"), "tier.from_inclusive", nonnegative=True)
        upper = dec(tier["to_exclusive"], "tier.to_exclusive", nonnegative=True) if tier.get("to_exclusive") is not None else None
        if chargeable >= lower and (upper is None or chargeable < upper):
            matched.append(tier)
    if len(matched) != 1:
        raise PPFCError(f"segments[{index}] chargeable weight must match exactly one tier")
    unit_rate = dec(matched[0].get("rate_per_weight"), "tier.rate_per_weight", nonnegative=True)
    tier_charge = chargeable * unit_rate
    surcharges = Decimal("0")
    seen_groups: set[str] = set()
    for surcharge in segment.get("surcharges", []):
        if surcharge.get("applies") is not True:
            continue
        group = surcharge.get("mutual_exclusion_group")
        if group and group in seen_groups:
            raise PPFCError(f"segments[{index}] mutually exclusive surcharge collision: {group}")
        if group:
            seen_groups.add(group)
        kind = surcharge.get("type")
        if kind == "amount":
            surcharges += dec(surcharge.get("value"), "surcharge.value", nonnegative=True)
        elif kind == "rate_on_base_and_tier":
            surcharges += (base + tier_charge) * rate(surcharge.get("value"), "surcharge.value")
        else:
            raise PPFCError(f"segments[{index}] unsupported surcharge type")
    before_tax = max(minimum, base + tier_charge + surcharges)
    tax = before_tax * rate(segment.get("tax_rate", "0"), f"segments[{index}].tax_rate")
    return {
        "segment_id": str(segment.get("segment_id")),
        "transport_mode": mode,
        "actual_weight": exact(actual),
        "volumetric_weight": exact(volumetric),
        "chargeable_weight": exact(chargeable),
        "base_charge": exact(base),
        "tier_charge": exact(tier_charge),
        "surcharges": exact(surcharges),
        "tax": exact(tax),
        "total": exact(before_tax + tax),
        "currency": str(segment.get("currency")),
    }


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    currency = payload.get("currency")
    segments = payload.get("segments")
    if not isinstance(currency, str) or not isinstance(segments, list) or not segments:
        raise PPFCError("currency and non-empty segments are required")
    if len({segment.get("segment_id") for segment in segments}) != len(segments):
        raise PPFCError("segment_id must be unique")
    if any(segment.get("currency") != currency for segment in segments):
        raise PPFCError("all segments must use payload currency or be converted before calculation")
    calculated = [calculate_segment(segment, index) for index, segment in enumerate(segments)]
    total = sum((Decimal(segment["total"]) for segment in calculated), Decimal("0"))
    return {"status": "calculated", "currency": currency, "segments": calculated, "route_total": exact(total)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(calculate(json.loads(args.input.read_text())), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, PPFCError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
