#!/usr/bin/env python3
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
import pathlib
import re
import sys


class NormalizationError(ValueError):
    pass


NUMBER = re.compile(r"^\s*\(?\s*([+-]?[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?|[+-]?[0-9]+(?:\.[0-9]+)?)\s*\)?\s*([A-Za-z%]*)\s*$")
MISSING = {"", "n/a", "na", "null", "none", "-", "—"}


def normalize_number(value, *, unit=None, percent=False):
    if value is None or (isinstance(value, str) and value.strip().lower() in MISSING):
        raise NormalizationError("missing_is_not_zero")
    if isinstance(value, (int, float, Decimal)):
        number = Decimal(str(value))
        suffix = ""
        negative = number < 0
    else:
        text = str(value)
        match = NUMBER.fullmatch(text)
        if not match:
            raise NormalizationError(f"ambiguous_number:{value}")
        number = Decimal(match.group(1).replace(",", ""))
        suffix = match.group(2).lower()
        negative = text.strip().startswith("(") and text.strip().endswith(")")
        if negative:
            number = -number
    if suffix == "k":
        number *= Decimal("1000")
    elif suffix == "%":
        if not percent:
            raise NormalizationError("unexpected_percent")
        number /= Decimal("100")
    elif suffix and unit and suffix not in {unit.lower(), unit.lower().rstrip("s")}:
        raise NormalizationError(f"unit_mismatch:{suffix}!={unit}")
    elif suffix and not unit:
        raise NormalizationError(f"undeclared_unit:{suffix}")
    if percent and suffix != "%" and abs(number) > 1:
        raise NormalizationError("ambiguous_percent_scale")
    return number


def normalize_record(payload):
    specs = payload.get("field_specs", {})
    raw = payload.get("record", {})
    normalized = {}
    errors = {}
    for field, spec in specs.items():
        try:
            normalized[field] = str(
                normalize_number(
                    raw.get(field),
                    unit=spec.get("unit"),
                    percent=spec.get("type") == "percent",
                )
            )
        except (NormalizationError, InvalidOperation) as exc:
            errors[field] = str(exc)
    unknown_fields = sorted(set(raw) - set(specs))
    return {
        "status": "blocked" if errors or unknown_fields else "normalized",
        "normalized": normalized,
        "errors": errors,
        "unknown_fields": unknown_fields,
        "raw_preserved": raw,
    }


def main():
    payload = json.loads(pathlib.Path(sys.argv[1]).read_text())
    output = normalize_record(payload)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if output["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
