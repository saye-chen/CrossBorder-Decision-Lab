#!/usr/bin/env python3
"""Validate ERDG quantity metadata and pairwise comparability."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from erdg_common import decimal_value, parse_time

TAX_BASES = {"tax_inclusive", "tax_exclusive", "tax_not_applicable"}


def validate_quantity(item: dict[str, Any], prefix: str) -> list[str]:
    errors = []
    try:
        decimal_value(item.get("value"), f"{prefix}.value")
    except ValueError as exc:
        errors.append(str(exc))
    if not item.get("unit"):
        errors.append(f"{prefix}.unit is required")
    if item.get("unit") == "currency":
        currency = item.get("currency")
        if not isinstance(currency, str) or len(currency) != 3 or currency.upper() != currency:
            errors.append(f"{prefix}.currency must be a three-letter uppercase code")
        if item.get("tax_basis") not in TAX_BASES:
            errors.append(f"{prefix}.tax_basis is invalid")
    try:
        parse_time(item.get("as_of_time"), f"{prefix}.as_of_time")
    except ValueError as exc:
        errors.append(str(exc))
    window = item.get("effective_window")
    if not isinstance(window, dict):
        errors.append(f"{prefix}.effective_window is required")
    else:
        try:
            start = parse_time(window.get("start"), f"{prefix}.effective_window.start")
            end = parse_time(window.get("end"), f"{prefix}.effective_window.end")
            if start > end:
                errors.append(f"{prefix}.effective_window start exceeds end")
        except ValueError as exc:
            errors.append(str(exc))
    if not item.get("source") or not item.get("calculation_id"):
        errors.append(f"{prefix}.source and calculation_id are required")
    return errors


def comparable(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    errors = []
    for field in ("unit", "currency", "tax_basis"):
        if left.get(field) != right.get(field):
            errors.append(f"incompatible {field}")
    if left.get("effective_window") != right.get("effective_window"):
        errors.append("incompatible effective_window")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        quantities = payload.get("quantities")
        if not isinstance(quantities, list) or not quantities:
            raise ValueError("quantities must be a non-empty list")
        errors = [error for index, item in enumerate(quantities) for error in validate_quantity(item, f"quantities[{index}]")]
        if payload.get("compare") and len(quantities) == 2:
            errors.extend(comparable(quantities[0], quantities[1]))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(f"BLOCKED: {error}" for error in errors), file=sys.stderr)
        return 1
    print("PASS: quantities are valid and comparable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
