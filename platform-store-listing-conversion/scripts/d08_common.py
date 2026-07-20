#!/usr/bin/env python3
import hashlib
import json
import math
import sys

GATES = ("G1", "G2", "G3", "G4", "G5", "G6")

def fail(message):
    raise ValueError(message)

def number(value, name, nonnegative=True):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail(f"{name} must be a finite number")
    if nonnegative and value < 0:
        fail(f"{name} must be nonnegative")
    return float(value)

def integer(value, name):
    v = number(value, name)
    if not v.is_integer():
        fail(f"{name} must be an integer")
    return int(v)

def required(obj, fields, prefix=""):
    missing = [f for f in fields if f not in obj or obj[f] in (None, "", [])]
    if missing:
        fail(f"{prefix}missing required fields: {', '.join(missing)}")

def fingerprint(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def stable_result(result, input_value, model):
    return {"model": model, "input_fingerprint": fingerprint(input_value), **result,
            "output_fingerprint": fingerprint(result)}

def run_cli(fn, model):
    try:
        data = json.load(sys.stdin)
        print(json.dumps(stable_result(fn(data), data, model), ensure_ascii=False, sort_keys=True))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc), "model": model}, ensure_ascii=False))
        raise SystemExit(2)
