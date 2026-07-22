#!/usr/bin/env python3
"""Compute a conservative CAPM outreach funnel."""
import argparse
import math
from capm_common import emit, load_json, require_number, sha256_json


def calculate(data: dict) -> dict:
    target = math.ceil(require_number(data.get("target_deliveries"), "target_deliveries", minimum=1))
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        raise ValueError("stages must be a non-empty list")
    required = target
    trace = []
    for stage in reversed(stages):
        name = str(stage.get("name", "")).strip()
        rate = require_number(stage.get("rate"), f"stage[{name}].rate", minimum=1e-12, maximum=1.0)
        downstream = required
        required = math.ceil(required / rate)
        trace.append({"stage": name, "rate": rate, "required_inputs": required, "required_outputs": downstream})
    return {"target_deliveries": target, "required_candidates": required, "trace": list(reversed(trace)),
            "input_hash": sha256_json(data)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); emit(calculate(load_json(a.input)))
