#!/usr/bin/env python3
"""Shared deterministic utilities for ECAE command-line tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from statistics import NormalDist
from typing import Any, Iterable

SCHEMA_VERSION = "1.0.0"
RUNTIME = "ECAE"


class ECAEError(Exception):
    def __init__(self, code: str, message: str, details: Any | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def load_json(path: str | Path) -> Any:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ECAEError("INPUT_NOT_FOUND", f"Input not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ECAEError("INVALID_JSON", f"Invalid JSON at line {exc.lineno}: {path}") from exc
    ensure_finite(value)
    return value


def ensure_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ECAEError("NON_FINITE_NUMBER", f"NaN or infinity is forbidden at {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            ensure_finite(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            ensure_finite(item, f"{path}[{index}]")


def require_fields(value: dict[str, Any], fields: Iterable[str], path: str = "$") -> None:
    missing = [field for field in fields if field not in value]
    if missing:
        raise ECAEError("MISSING_REQUIRED_FIELD", f"Missing required fields at {path}", missing)


def require_probability(value: Any, name: str, *, allow_zero: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ECAEError("INVALID_PROBABILITY", f"{name} must be numeric")
    lower_ok = value >= 0 if allow_zero else value > 0
    if not lower_ok or value >= 1:
        raise ECAEError("INVALID_PROBABILITY", f"{name} must be {'[0,1)' if allow_zero else '(0,1)'}")
    return float(value)


def require_positive(value: Any, name: str, *, allow_zero: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ECAEError("INVALID_NUMBER", f"{name} must be numeric")
    if (value < 0 if allow_zero else value <= 0):
        raise ECAEError("INVALID_NUMBER", f"{name} must be {'non-negative' if allow_zero else 'positive'}")
    return float(value)


def parse_time(value: str, name: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ECAEError("INVALID_TIME", f"{name} must be RFC3339/ISO-8601") from exc


def canonical_json(value: Any) -> str:
    ensure_finite(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(value: Any, *, omit_keys: Iterable[str] = ("content_hash",)) -> str:
    if isinstance(value, dict):
        value = {key: item for key, item in value.items() if key not in set(omit_keys)}
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def z_quantile(probability: float) -> float:
    require_probability(probability, "probability")
    return NormalDist().inv_cdf(probability)


def normal_cdf(value: float) -> float:
    return NormalDist().cdf(value)


def two_sided_p_from_z(z_value: float) -> float:
    return min(1.0, 2.0 * (1.0 - normal_cdf(abs(z_value))))


def confidence_interval(estimate: float, standard_error: float, level: float) -> tuple[float, float]:
    require_probability(level, "confidence_level")
    require_positive(standard_error, "standard_error", allow_zero=True)
    critical = z_quantile(0.5 + level / 2.0)
    return estimate - critical * standard_error, estimate + critical * standard_error


def success(payload: dict[str, Any], *, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "runtime": RUNTIME,
        "ok": True,
        "result": payload,
        "warnings": warnings or [],
    }


def failure(error: ECAEError) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "runtime": RUNTIME,
        "ok": False,
        "error": {"code": error.code, "message": error.message, "details": error.details},
        "claim_ceiling": "CE0",
    }


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


def input_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input", help="Path to UTF-8 JSON input")
    return parser


def cli_main(run_function, description: str) -> None:
    parser = input_parser(description)
    args = parser.parse_args()
    try:
        emit(success(run_function(load_json(args.input))))
    except ECAEError as exc:
        emit(failure(exc))
        sys.exit(2)


def schema_root() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas"


def backend_registry_path() -> Path:
    return Path(__file__).resolve().parents[1] / "backends" / "backend-registry.json"
