#!/usr/bin/env python3
"""Recompute every ERDG Golden report binding from deterministic inputs."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
ERDG = ROOT / "governance/erdg"
EVAL = ROOT / "evaluations/erdg"


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ERDG / "scripts" / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


common = load_module("erdg_common", "erdg_common.py")
economic = load_module("erdg_economic_recompute", "calculate_economic_layers.py")
cash = load_module("erdg_cash_recompute", "calculate_cash_flow.py")
risk = load_module("erdg_risk_recompute", "evaluate_risk_and_redlines.py")
lineage = load_module("erdg_lineage_recompute", "compute_impact_closure.py")


def run_check(check: dict[str, Any]) -> dict[str, Any]:
    runner = check["runner"]
    payload = check["input"]
    if runner == "economic":
        result = economic.calculate(payload)
        return result["layers_exact"]
    if runner == "cash":
        return cash.calculate(payload)
    if runner == "risk":
        return risk.evaluate(payload)
    if runner == "lineage":
        return lineage.compute(payload)
    if runner == "stress":
        count = payload["cash_events"]
        entries = [
            {
                "entry_id": f"E{i}",
                "occurred_at": f"2026-07-{(i % 28) + 1:02d}T00:00:00Z",
                "direction": "inflow" if i % 2 == 0 else "outflow",
                "amount": "1.01",
            }
            for i in range(count)
        ]
        cash_result = cash.calculate({"currency": "USD", "opening_cash": "0", "entries": entries})
        node_count = payload["lineage_nodes"]
        nodes = [{"id": f"N{i:04d}"} for i in range(node_count)]
        edges = [{"from": f"N{i:04d}", "to": f"N{i+1:04d}"} for i in range(node_count - 1)]
        graph_result = lineage.compute(
            {"nodes": nodes, "edges": edges, "changed_ids": [f"N{payload['changed_node']:04d}"]}
        )
        return {
            "ending_cash": cash_result["ending_cash"],
            "affected_count": len(graph_result["affected_ids"]),
            "unaffected_count": len(graph_result["unaffected_ids"]),
        }
    raise ValueError(f"unknown runner: {runner}")


def expected_matches(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


def validate() -> list[str]:
    errors: list[str] = []
    manifest = json.loads((EVAL / "report-recomputation-manifest.json").read_text(encoding="utf-8"))
    catalog = json.loads((EVAL / "evaluation-catalog.json").read_text(encoding="utf-8"))
    catalog_ids = {case["id"] for case in catalog["cases"]}
    for check in manifest["checks"]:
        check_id = check["id"]
        unknown = set(check["case_ids"]) - catalog_ids
        if unknown:
            errors.append(f"{check_id}: unknown case ids {sorted(unknown)}")
            continue
        actual = run_check(check)
        if not expected_matches(actual, check["expected"]):
            errors.append(f"{check_id}: recomputation differs expected={check['expected']} actual={actual}")
        input_hash = common.sha256_payload(check["input"])
        output_hash = common.sha256_payload(actual)
        report = (EVAL / check["report"]).read_text(encoding="utf-8")
        pattern = (
            rf"recomputation_id:\s*`{re.escape(check_id)}`.*?"
            rf"input_hash:\s*`{input_hash}`.*?"
            rf"output_hash:\s*`{output_hash}`"
        )
        if re.search(pattern, report, re.DOTALL) is None:
            errors.append(f"{check_id}: report binding is missing or stale")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("ERDG report recomputation passed for 7 bound Golden reports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
