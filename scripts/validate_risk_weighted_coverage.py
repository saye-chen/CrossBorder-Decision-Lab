#!/usr/bin/env python3
"""Validate WP0-WP5 risk-weighted coverage and honest evidence boundaries."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts/build_risk_weighted_evaluation_catalogs.py"
spec = importlib.util.spec_from_file_location("risk_builder", BUILDER_PATH)
builder = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(builder)


def validate() -> list[str]:
    errors: list[str] = []
    ledger_path = ROOT / "evaluations/risk-weighted-coverage-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    by_domain = {x["domain_id"]: x for x in ledger["domains"]}
    if set(by_domain) != set(builder.DOMAIN_PLANS):
        errors.append("coverage ledger domain scope drift")
    for domain, plan in builder.DOMAIN_PLANS.items():
        catalog = json.loads((ROOT / plan["path"]).read_text(encoding="utf-8"))
        cases = catalog.get("cases", [])
        if len(cases) < plan["target"] or len({x.get("id") for x in cases}) != len(cases):
            errors.append(f"{domain}: case target or uniqueness failed")
        generated = [x for x in cases if str(x.get("id", "")).startswith(plan["prefix"])]
        represented = {(x["name"].rsplit("-", 1)[0], x["mode"]) for x in generated}
        required_pairs = {(mechanism, mode) for mechanism in plan["mechanisms"] for mode in builder.MODES}
        if not represented <= required_pairs or {x["mode"] for x in generated} != set(builder.MODES):
            errors.append(f"{domain}: risk matrix mode binding failed")
        for case in generated:
            if case.get("evidence_binding", {}).get("l4_eligible") is not False:
                errors.append(f"{case.get('id')}: synthetic fixture may infer L4")
            if not case.get("counterevidence") or not case.get("rollback") or not case.get("mutation", {}).get("guard"):
                errors.append(f"{case.get('id')}: counterevidence rollback or specific guard missing")
            if not {"external_write", "redline_compensation", "synthetic_l4", "unknown_as_zero"} <= set(case.get("forbidden", [])):
                errors.append(f"{case.get('id')}: noncompensable guard set incomplete")
    schema = json.loads((ROOT / "legal-tax-intellectual-property-market-access-decision/schemas/professional-report.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    golden_dir = ROOT / "legal-tax-intellectual-property-market-access-decision/evaluations/golden"
    reports = [json.loads(path.read_text()) for path in sorted(golden_dir.glob("*.json"))]
    statuses = set()
    for report in reports:
        violations = list(validator.iter_errors(report))
        if violations:
            errors.append(f"D05 golden {report.get('report_id')}: {violations[0].message}")
        statuses.add(report.get("gate_status"))
        if report.get("external_write") is not False or report.get("maturity") != "controlled pilot":
            errors.append(f"D05 golden {report.get('report_id')}: authority ceiling widened")
    if not {"blocked", "evidence_required", "continue_with_conditions", "exit_required"} <= statuses:
        errors.append("D05 golden state breadth incomplete")
    chains = json.loads((ROOT / "logistics-inventory-fulfillment-decision/evaluations/decision-chain-coverage.json").read_text())
    if len(chains.get("chains", [])) != 7 or chains.get("l4_eligible") is not False:
        errors.append("D07 decision-chain coverage incomplete or maturity widened")
    for chain in chains.get("chains", []):
        for script in chain.get("scripts", []):
            if not (ROOT / "logistics-inventory-fulfillment-decision/scripts" / script).is_file():
                errors.append(f"D07 missing chain executable {script}")
        if not chain.get("hard_guard") or not chain.get("recovery"):
            errors.append(f"D07 chain guard/recovery missing: {chain.get('mechanism')}")
    index = json.loads((ROOT / "evaluations/professional-evaluation-index.json").read_text())
    oracle_hashes = [x.get("case_oracle_hash") for x in index.get("cases", [])]
    if any(not isinstance(x, str) or len(x) != 64 for x in oracle_hashes):
        errors.append("case oracle hashes missing")
    if len(set(oracle_hashes)) < 100:
        errors.append("case oracle differentiation insufficient")
    return errors


if __name__ == "__main__":
    errors = validate()
    print("RISK_WEIGHTED_COVERAGE=PASS" if not errors else "RISK_WEIGHTED_COVERAGE=FAIL\n- " + "\n- ".join(errors))
    raise SystemExit(0 if not errors else 2)
