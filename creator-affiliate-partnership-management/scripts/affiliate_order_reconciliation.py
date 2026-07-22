#!/usr/bin/env python3
"""Reconcile mutually exclusive affiliate-order buckets and causal labels."""
import argparse
from capm_common import emit, load_json, require_number, sha256_json


BUCKETS = ("duplicate", "confirmed_fraud", "mature_refund_chargeback", "mature_valid", "pending")


def reconcile(data: dict) -> dict:
    raw = int(require_number(data.get("raw_attributed"), "raw_attributed"))
    buckets = {k: int(require_number(data.get(k, 0), k)) for k in BUCKETS}
    if any(float(data.get(k, 0)) != buckets[k] for k in BUCKETS) or float(data.get("raw_attributed")) != raw:
        raise ValueError("order counts must be integers")
    total = sum(buckets.values())
    if total != raw:
        raise ValueError(f"order conservation failed: raw={raw}, buckets={total}")
    causal = data.get("causal_evidence_level", "C0")
    return {"status": "validated", "raw_attributed": raw, **buckets, "conservation": True,
            "causal_status": "incremental_eligible" if causal in {"C2", "C3"} else "inconclusive",
            "mature_valid_label": "mature_valid_attributed_orders", "input_hash": sha256_json(data)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); emit(reconcile(load_json(a.input)))
