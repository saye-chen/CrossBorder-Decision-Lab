#!/usr/bin/env python3
"""Shared deterministic helpers for CAPM scripts."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def require_number(value: Any, name: str, *, minimum: float | None = 0.0, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: expected finite number")
    result = float(value)
    if minimum is not None and result < minimum:
        raise ValueError(f"{name}: must be >= {minimum}")
    if maximum is not None and result > maximum:
        raise ValueError(f"{name}: must be <= {maximum}")
    return result


def load_json(path: str | None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.load(__import__("sys").stdin)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
