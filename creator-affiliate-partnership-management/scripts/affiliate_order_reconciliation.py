#!/usr/bin/env python3
"""Reconcile mutually exclusive affiliate-order buckets and causal labels."""
import argparse
from capm_common import emit, load_json, require_number, sha256_json
from validate_ecae_handoff import qualified_receipt_from


BUCKETS = ("duplicate", "confirmed_fraud", "mature_refund_chargeback", "mature_valid", "pending")


def reconcile(data: dict) -> dict:
    raw = int(require_number(data.get("raw_attributed"), "raw_attributed"))
    buckets = {k: int(require_number(data.get(k, 0), k)) for k in BUCKETS}
    if any(float(data.get(k, 0)) != buckets[k] for k in BUCKETS) or float(data.get("raw_attributed")) != raw:
        raise ValueError("order counts must be integers")
    total = sum(buckets.values())
    if total != raw:
        raise ValueError(f"order conservation failed: raw={raw}, buckets={total}")
    legacy_causal = data.get("causal_evidence_level", "C0")
    receipt = qualified_receipt_from(data)
    incremental_qualified = bool(receipt and receipt["incremental_claim_allowed"])
    return {"status": "validated", "raw_attributed": raw, **buckets, "conservation": True,
            "causal_status": "f01_incremental_eligible" if incremental_qualified else ("legacy_c_label_non_equivalent" if legacy_causal in {"C2", "C3"} else "inconclusive"),
            "incremental_claim_allowed": incremental_qualified,
            "ecae_consumer_receipt": receipt,
            "mature_valid_label": "mature_valid_attributed_orders", "input_hash": sha256_json(data)}


def reconcile_touchpoints(data: dict) -> dict:
    result = reconcile(data)
    touchpoints = data.get("touchpoints", [])
    if not isinstance(touchpoints, list): raise ValueError("touchpoints must be an array")
    seen = set(); duplicated = []
    for index, item in enumerate(touchpoints):
        key = (item.get("order_id"), item.get("partner_id"), item.get("touch_type"))
        if None in key: raise ValueError(f"touchpoints[{index}] missing identity")
        if key in seen: duplicated.append({"order_id":key[0], "partner_id":key[1], "touch_type":key[2]})
        seen.add(key)
    result.update({"touchpoint_duplicates": duplicated, "touchpoint_status":"blocked" if duplicated else "validated",
                   "incremental_orders": data.get("incremental_orders") if result["incremental_claim_allowed"] else None})
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("input", nargs="?"); a = p.parse_args(); emit(reconcile(load_json(a.input)))
