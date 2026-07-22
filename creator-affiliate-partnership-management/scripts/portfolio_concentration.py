#!/usr/bin/env python3
"""Calculate HHI, Shannon entropy and top shares for CAPM portfolios."""
import argparse
import math
from capm_common import emit, load_json, require_number, sha256_json


def calculate(data: dict) -> dict:
    raw = data.get("values")
    if not isinstance(raw, dict) or not raw:
        raise ValueError("values must be a non-empty object")
    values = {str(k): require_number(v, f"values.{k}") for k, v in raw.items()}
    total = sum(values.values())
    if total <= 0:
        raise ValueError("portfolio total must be positive")
    shares = {k: v / total for k, v in values.items()}
    ordered = sorted(shares.values(), reverse=True)
    hhi = sum(s * s for s in ordered)
    entropy = -sum(s * math.log(s) for s in ordered if s > 0)
    maximum = math.log(len(ordered)) if len(ordered) > 1 else 0.0
    return {"basis": data.get("basis", "unspecified"), "shares": shares, "hhi": hhi,
            "shannon_entropy": entropy, "evenness": entropy / maximum if maximum else 1.0,
            "top1_share": ordered[0], "top3_share": sum(ordered[:3]), "input_hash": sha256_json(data)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); emit(calculate(load_json(a.input)))
