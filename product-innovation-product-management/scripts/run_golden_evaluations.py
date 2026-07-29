#!/usr/bin/env python3
"""Execute every Golden's own business fixture and bind its mechanism output."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "evaluations/golden"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def run(write: bool = False) -> dict[str, Any]:
    chains = load("golden_chains_runtime", "execute_golden_professional_chains.py")
    report_validator = load("golden_report_validator", "validate_professional_report.py")
    results = []
    for fixture_path in sorted(GOLDEN.glob("*-fixture.json")):
        stem = fixture_path.name.removesuffix("-fixture.json")
        report_path = GOLDEN / f"{stem}-report.json"
        oracle_path = GOLDEN / f"{stem}-oracle.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
        actual = chains.execute(fixture["execution"])
        mutated = chains.execute(fixture["execution"], True)
        binding = report.get("specific_content", {}).get("execution_binding", {})
        checks = {
            "scenario_owned_input": fixture["input_hash"] == digest(fixture["execution"]).removeprefix("sha256:"),
            "professional_engine_executed": actual["execution_state"] in {"completed", "blocked"},
            "expected_output_matches": digest(actual) == oracle["expected_output_hash"],
            "mutation_output_matches": digest(mutated) == oracle["mutation"]["expected_output_hash"],
            "mutation_changes_result": actual != mutated and oracle["mutation"]["must_differ"] is True,
            "report_mechanism_bound": (
                binding.get("engine") == fixture["execution"]["engine"]
                and binding.get("input_hash") == digest(fixture["execution"])
                and binding.get("mechanism_output_hash") == digest(actual)
                and binding.get("decision_status") == actual["decision_status"]
            ),
            "report_contract_valid": not report_validator.validate(report),
        }
        passed = all(checks.values())
        trace = {
            "golden_id": fixture["id"], "golden_name": stem,
            "engine": fixture["execution"]["engine"], "operation": fixture["execution"]["operation"],
            "passed": passed, "checks": checks,
            "decision_status": actual["decision_status"],
            "mutation_decision_status": mutated["decision_status"],
            "actual_output": actual, "mutation_output": mutated,
            "fixture_hash": digest(fixture), "report_hash": digest(report), "oracle_hash": digest(oracle),
            "execution_source": "scenario_owned_fixture",
        }
        trace["execution_hash"] = digest(trace)
        results.append(trace)
    payload = {
        "version": "PIPM-GOLDEN-EXEC-2026.07",
        "artifact_role": "executed_result_not_registry",
        "actual_professional_engine_execution": True,
        "executed_at": datetime.now(timezone.utc).isoformat() if write else None,
        "passed": all(row["passed"] for row in results),
        "results": results,
    }
    if write:
        (ROOT / "evaluations/golden-execution-results.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return payload


def validate(recorded: dict[str, Any]) -> list[str]:
    actual = run(False)
    errors: list[str] = []
    comparable = {**recorded, "executed_at": None}
    if comparable != actual:
        errors.append("GOLDEN_EXECUTION_EVIDENCE_DRIFT")
    if len(recorded.get("results", [])) != 10:
        errors.append("GOLDEN_EXECUTION_COUNT")
    if recorded.get("passed") is not True:
        errors.append("GOLDEN_EXECUTION_NOT_PASSED")
    for row in recorded.get("results", []):
        if row.get("passed") is not True:
            errors.append(f"{row.get('golden_id')}:FAILED")
        if not all(row.get("checks", {}).values()):
            errors.append(f"{row.get('golden_id')}:CHECK_FAILED")
    return errors


if __name__ == "__main__":
    result = run(True)
    print(json.dumps({"golden": len(result["results"]), "passed": result["passed"]}, sort_keys=True))
