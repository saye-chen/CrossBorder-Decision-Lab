#!/usr/bin/env python3
"""Validate ERDG reference capacity, memory, determinism and hard input limits."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
ERDG = ROOT / "governance/erdg"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ERDG / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


load_module("erdg_common", "erdg_common.py")
cash = load_module("erdg_capacity_cash", "calculate_cash_flow.py")
lineage = load_module("erdg_capacity_lineage", "compute_impact_closure.py")


def percentile95(samples: list[float]) -> float:
    return sorted(samples)[max(0, int(len(samples) * 0.95 + 0.999999) - 1)]


def measure(fn: Callable[[], Any], samples: int) -> tuple[Any, float, float]:
    durations: list[float] = []
    outputs: list[Any] = []
    peak_bytes = 0
    for _ in range(samples):
        tracemalloc.start()
        start = time.perf_counter()
        output = fn()
        durations.append(time.perf_counter() - start)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_bytes = max(peak_bytes, peak)
        outputs.append(output)
    if any(output != outputs[0] for output in outputs[1:]):
        raise ValueError("capacity workload is not deterministic")
    return outputs[0], percentile95(durations), peak_bytes / (1024 * 1024)


def cash_payload(count: int) -> dict[str, Any]:
    return {
        "currency": "USD",
        "opening_cash": "0",
        "entries": [
            {
                "entry_id": f"E{i}",
                "occurred_at": f"2026-07-{(i % 28) + 1:02d}T00:00:00Z",
                "direction": "inflow" if i % 2 == 0 else "outflow",
                "amount": "1.01",
            }
            for i in range(count)
        ],
    }


def lineage_payload(count: int, changed: int) -> dict[str, Any]:
    return {
        "nodes": [{"id": f"N{i:05d}"} for i in range(count)],
        "edges": [{"from": f"N{i:05d}", "to": f"N{i+1:05d}"} for i in range(count - 1)],
        "changed_ids": [f"N{changed:05d}"],
    }


def must_reject(fn: Callable[[], Any], label: str, errors: list[str]) -> None:
    try:
        fn()
    except ValueError:
        return
    errors.append(f"{label}: capacity overflow was not rejected")


def validate() -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    contract = json.loads((ERDG / "capacity-contract.json").read_text(encoding="utf-8"))
    cash_spec = contract["cash"]
    lineage_spec = contract["lineage"]
    cash_input = cash_payload(cash_spec["accepted_events"])
    cash_result, cash_p95, cash_memory = measure(
        lambda: cash.calculate(cash_input), cash_spec["samples"]
    )
    graph_input = lineage_payload(lineage_spec["accepted_nodes"], 900)
    graph_result, graph_p95, graph_memory = measure(
        lambda: lineage.compute(graph_input), lineage_spec["samples"]
    )
    if cash_result["ending_cash"] != "0":
        errors.append("cash: conservation mismatch")
    if len(graph_result["affected_ids"]) != 100:
        errors.append("lineage: selective closure mismatch")
    if cash_p95 > cash_spec["p95_seconds_max"]:
        errors.append(f"cash: p95 {cash_p95:.4f}s exceeds {cash_spec['p95_seconds_max']}s")
    if cash_memory > cash_spec["peak_memory_mib_max"]:
        errors.append(f"cash: peak {cash_memory:.2f}MiB exceeds {cash_spec['peak_memory_mib_max']}MiB")
    if graph_p95 > lineage_spec["p95_seconds_max"]:
        errors.append(f"lineage: p95 {graph_p95:.4f}s exceeds {lineage_spec['p95_seconds_max']}s")
    if graph_memory > lineage_spec["peak_memory_mib_max"]:
        errors.append(f"lineage: peak {graph_memory:.2f}MiB exceeds {lineage_spec['peak_memory_mib_max']}MiB")
    must_reject(
        lambda: cash.calculate({"currency": "USD", "opening_cash": "0", "entries": [{}] * (cash_spec["hard_event_limit"] + 1)}),
        "cash",
        errors,
    )
    must_reject(
        lambda: lineage.compute({"nodes": [{"id": str(i)} for i in range(lineage_spec["hard_node_limit"] + 1)], "edges": [], "changed_ids": []}),
        "lineage nodes",
        errors,
    )
    metrics = {
        "cash": {"p95_seconds": round(cash_p95, 6), "peak_memory_mib": round(cash_memory, 3)},
        "lineage": {"p95_seconds": round(graph_p95, 6), "peak_memory_mib": round(graph_memory, 3)},
        "production_slo_claim": False,
    }
    return errors, metrics


def main() -> int:
    errors, metrics = validate()
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("ERDG reference capacity gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
