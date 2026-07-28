#!/usr/bin/env python3
"""Execute every positive and counterexample binding in the PPFC 55-case catalog."""
from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def validate_and_run(
    catalog: dict[str, Any],
    execution_map: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    catalog_ids = [item["id"] for item in catalog.get("cases", [])]
    bindings = execution_map.get("bindings", [])
    binding_ids = [item.get("id") for item in bindings]
    if binding_ids != catalog_ids:
        errors.append("EXECUTION_BINDINGS_MUST_MATCH_CATALOG_ORDER")
    if len(set(binding_ids)) != len(binding_ids):
        errors.append("DUPLICATE_EXECUTION_BINDING")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    reference_count = 0
    for binding in bindings:
        positive = binding.get("positive")
        counterexample = binding.get("counterexample")
        if not positive or not counterexample or positive == counterexample:
            errors.append(f"{binding.get('id')}:POSITIVE_AND_COUNTEREXAMPLE_REQUIRED")
            continue
        for reference in (positive, counterexample):
            loaded = loader.loadTestsFromName(reference)
            if loaded.countTestCases() != 1:
                errors.append(f"{binding.get('id')}:INVALID_TEST_REFERENCE:{reference}")
                continue
            suite.addTests(loaded)
            reference_count += 1

    if errors:
        return {
            "valid": False,
            "catalog_cases": len(catalog_ids),
            "executed_assertions": 0,
            "errors": errors,
        }
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    if not result.wasSuccessful():
        errors.append("BOUND_EXECUTION_FAILED")
        errors.extend(str(item[1]) for item in result.failures + result.errors)
    return {
        "valid": not errors,
        "catalog_cases": len(catalog_ids),
        "executed_assertions": reference_count,
        "errors": errors,
    }


def main() -> int:
    catalog = json.loads(
        (ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text(encoding="utf-8")
    )
    execution_map = json.loads(
        (ROOT / "evaluations/fixtures/evaluation-execution-map.json").read_text(encoding="utf-8")
    )
    result = validate_and_run(catalog, execution_map)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
