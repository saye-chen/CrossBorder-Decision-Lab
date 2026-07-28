#!/usr/bin/env python3
"""Validate comparable evaluation categories for PPFC and PIPM."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / "governance/evaluation-taxonomy.json").read_text())
ALLOWED = set(TAXONOMY["canonical_categories"])


def validate() -> list[str]:
    errors: list[str] = []
    catalogs = {
        "PPFC": ROOT / "pricing-profit-finance-cashflow-decision/evaluations/fixtures/evaluation-catalog.json",
        "PIPM": ROOT / "product-innovation-product-management/evaluations/fixtures/evaluation-catalog.json",
    }
    for domain, path in catalogs.items():
        cases = json.loads(path.read_text())["cases"]
        for case in cases:
            if case.get("category") not in ALLOWED:
                errors.append(f"{domain}:{case.get('id')}:category")
        if domain == "PIPM":
            if any(not case.get("mutation_class") for case in cases):
                errors.append("PIPM:mutation_class")
            if "cross_domain" not in {case["category"] for case in cases}:
                errors.append("PIPM:cross_domain")
    return errors


if __name__ == "__main__":
    found = validate()
    if found:
        raise SystemExit("EVALUATION_TAXONOMY=BLOCKED\n-" + "\n-".join(found))
    print("EVALUATION_TAXONOMY=PASS domains=2")
