#!/usr/bin/env python3
"""Execute all 101 PIPM positive/counterexample bindings independently."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "pipm_wp8_binding_runner", ROOT / "scripts/run_wp8_evaluations.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_and_run(
    catalog: dict[str, Any], execution_map: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    cases = catalog.get("cases", [])
    bindings = execution_map.get("bindings", [])
    case_ids = [case.get("id") for case in cases]
    binding_ids = [binding.get("id") for binding in bindings]
    if binding_ids != case_ids:
        errors.append("EXECUTION_BINDINGS_MUST_MATCH_CATALOG_ORDER")
    if len(set(binding_ids)) != len(binding_ids):
        errors.append("DUPLICATE_EXECUTION_BINDING")
    if len(bindings) != 101:
        errors.append("EXECUTION_BINDING_COUNT")
    runner = load_runner()
    engine_assertions = 0
    decision_assertions = 0
    for case, binding in zip(cases, bindings):
        prefix = case["id"]
        if binding.get("engine") != case.get("exercised_script"):
            errors.append(f"{prefix}:ENGINE_BINDING_MISMATCH")
        positive = binding.get("positive")
        counterexample = binding.get("counterexample")
        if not isinstance(positive, dict) or not isinstance(counterexample, dict):
            errors.append(f"{prefix}:POSITIVE_AND_COUNTEREXAMPLE_REQUIRED")
            continue
        if positive == counterexample:
            errors.append(f"{prefix}:POSITIVE_EQUALS_COUNTEREXAMPLE")
            continue
        if counterexample.get("mutation") != case.get("mutation"):
            errors.append(f"{prefix}:MUTATION_BINDING_MISMATCH")
        if positive.get("expected_decision_status") != case["expected"]["status"]:
            errors.append(f"{prefix}:POSITIVE_EXPECTATION_MISMATCH")
        if counterexample.get("expected_decision_status") != "blocked":
            errors.append(f"{prefix}:COUNTEREXAMPLE_MUST_BLOCK")
        if not runner.engine_pass(case["exercised_script"], False):
            errors.append(f"{prefix}:POSITIVE_ENGINE_FAILED")
        engine_assertions += 1
        if not runner.engine_pass(case["exercised_script"], True):
            errors.append(f"{prefix}:COUNTEREXAMPLE_ENGINE_ESCAPED")
        engine_assertions += 1
        if runner.execute(case, False) != positive.get("expected_decision_status"):
            errors.append(f"{prefix}:POSITIVE_DECISION_FAILED")
        decision_assertions += 1
        if runner.execute(case, True) != counterexample.get("expected_decision_status"):
            errors.append(f"{prefix}:COUNTEREXAMPLE_DECISION_ESCAPED")
        decision_assertions += 1
    return {
        "valid": not errors,
        "catalog_cases": len(cases),
        "bindings": len(bindings),
        "professional_engine_assertions": engine_assertions,
        "decision_assertions": decision_assertions,
        "total_assertions": engine_assertions + decision_assertions,
        "errors": errors,
    }


def main() -> int:
    catalog = json.loads(
        (ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text()
    )
    execution_map = json.loads(
        (ROOT / "evaluations/fixtures/evaluation-execution-map.json").read_text()
    )
    result = validate_and_run(catalog, execution_map)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
