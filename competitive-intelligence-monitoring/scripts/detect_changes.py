#!/usr/bin/env python3
"""Detect numeric anomalies from a JSON snapshot history."""

import argparse
import json
import math
import statistics
from pathlib import Path
from snapshot_schema import canonicalize_many


DEFAULT_THRESHOLDS = {"price": 0.10, "rating": 0.30, "rank": 0.30, "sku_count": 10.0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSON list of chronological snapshots")
    parser.add_argument("--output", required=True)
    parser.add_argument("--baseline-periods", type=int, default=8)
    parser.add_argument("--calibration", help="Optional JSON with field thresholds and calibration metadata")
    parser.add_argument("--baseline-method", choices=["mean_std", "median_mad"], default="mean_std")
    args = parser.parse_args()
    if args.baseline_periods < 3:
        parser.error("baseline-periods must be at least 3")
    rows = canonicalize_many(json.loads(Path(args.input).read_text(encoding="utf-8")))
    if not isinstance(rows, list) or len(rows) < 2:
        raise SystemExit("input must be a JSON list with at least two snapshots")
    if any(not isinstance(row, dict) for row in rows):
        raise SystemExit("each snapshot must be an object")
    timestamps = [row.get("snapshot_at") for row in rows]
    if any(not isinstance(value, str) or not value for value in timestamps) or timestamps != sorted(timestamps):
        raise SystemExit("snapshots must contain chronological snapshot_at values")
    product_ids = {row.get("product_id") for row in rows}
    if None in product_ids or len(product_ids) != 1:
        raise SystemExit("all snapshots must belong to one product_id")
    current, previous = rows[-1], rows[-2]
    calibration = {}
    if args.calibration:
        calibration = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
    thresholds = {**DEFAULT_THRESHOLDS, **calibration.get("thresholds", {})}
    alerts = []
    ignored = {"snapshot_at", "product_id", "source", "url"}
    fields = sorted(set().union(*(row.keys() for row in rows)) - ignored)
    for field in fields:
        value, before = current.get(field), previous.get(field)
        if not isinstance(value, (int, float)) or not isinstance(before, (int, float)) or not math.isfinite(value) or not math.isfinite(before):
            continue
        absolute = value - before
        relative = None if before == 0 else absolute / abs(before)
        baseline_values = [row.get(field) for row in rows[-(args.baseline_periods + 1):-1]]
        baseline_values = [x for x in baseline_values if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)]
        zscore = None
        center = scale = None
        if len(baseline_values) >= 3:
            if args.baseline_method == "median_mad":
                center = statistics.median(baseline_values)
                scale = 1.4826 * statistics.median(abs(x - center) for x in baseline_values)
            else:
                center = statistics.mean(baseline_values)
                scale = statistics.stdev(baseline_values)
            if scale:
                zscore = (value - center) / scale
        threshold = thresholds.get(field)
        threshold_hit = False
        if threshold is not None and field in {"price", "rank"} and relative is not None:
            threshold_hit = abs(relative) >= threshold
        elif threshold is not None and field in {"rating", "sku_count"}:
            threshold_hit = abs(absolute) >= threshold
        z_hit = zscore is not None and abs(zscore) >= 1.96
        if threshold_hit or z_hit:
            severity = "red" if zscore is not None and abs(zscore) >= 3 else "yellow"
            confirmed = severity == "red"
            if len(rows) >= 3 and not confirmed:
                prior = rows[-3].get(field)
                if isinstance(prior, (int, float)):
                    previous_change = before - prior
                    confirmed = previous_change != 0 and absolute != 0 and (previous_change > 0) == (absolute > 0)
            alerts.append({
                "field": field, "before": before, "after": value,
                "absolute_change": absolute, "relative_change": relative,
                "zscore": None if zscore is None or math.isnan(zscore) else zscore,
                "baseline_mature": len(baseline_values) >= args.baseline_periods,
                "baseline_method": args.baseline_method, "baseline_center": center,
                "baseline_scale": scale, "baseline_count": len(baseline_values),
                "severity": severity, "attribution": "pending_verification",
                "confirmation_status": "confirmed" if confirmed else "candidate_waiting_next_snapshot",
            })
    result = {
        "product_id": current.get("product_id"), "snapshot_at": current.get("snapshot_at"),
        "calibration": calibration.get("metadata", {}), "alerts": alerts,
        "baseline_method": args.baseline_method,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
