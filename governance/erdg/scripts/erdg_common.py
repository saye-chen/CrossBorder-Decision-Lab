#!/usr/bin/env python3
"""Shared deterministic primitives for ERDG."""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any

DECIMAL_PATTERN = "decimal string"


def decimal_value(value: Any, field: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field} must be a decimal string or integer, not binary float")
    if not isinstance(value, (str, int)):
        raise ValueError(f"{field} must be a decimal string or integer")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not a valid decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    return result


def decimal_string(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("non-finite decimal")
    normalized = value.normalize()
    text = format(normalized, "f")
    return "0" if text in {"-0", ""} else text


def quantize_money(value: Decimal, scale: int = 2) -> str:
    if not 0 <= scale <= 12:
        raise ValueError("scale must be between 0 and 12")
    quantum = Decimal(1).scaleb(-scale)
    return format(value.quantize(quantum, rounding=ROUND_HALF_EVEN), f".{scale}f")


def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be an ISO date-time string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date-time string") from exc
    if result.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return result


def canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {unicodedata.normalize("NFC", str(k)): canonical_value(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [canonical_value(item) for item in value]
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical payload cannot contain non-finite float")
        raise ValueError("canonical payload cannot contain binary float; use decimal string")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(canonical_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
