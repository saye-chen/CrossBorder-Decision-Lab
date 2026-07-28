from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from typing import Any


class PPFCError(ValueError):
    pass


def dec(value: Any, field: str, *, nonnegative: bool = False) -> Decimal:
    if not isinstance(value, str):
        raise PPFCError(f"{field}: must be a decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise PPFCError(f"{field}: invalid decimal") from exc
    if not result.is_finite():
        raise PPFCError(f"{field}: non-finite value")
    if nonnegative and result < 0:
        raise PPFCError(f"{field}: must be non-negative")
    return result


def rate(value: Any, field: str) -> Decimal:
    result = dec(value, field, nonnegative=True)
    if result > 1:
        raise PPFCError(f"{field}: rate must be between 0 and 1")
    return result


def exact(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value.normalize(), "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise PPFCError(f"{field}: ISO date-time is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PPFCError(f"{field}: invalid ISO date-time") from exc
    if parsed.tzinfo is None:
        raise PPFCError(f"{field}: timezone is required")
    return parsed.astimezone(timezone.utc)


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def ceil_increment(value: Decimal, increment: Decimal) -> Decimal:
    if increment <= 0:
        raise PPFCError("rounding increment must be positive")
    return (value / increment).to_integral_value(rounding=ROUND_CEILING) * increment
