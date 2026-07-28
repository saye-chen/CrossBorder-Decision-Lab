#!/usr/bin/env python3
"""Fail closed unless the WP8 catalog and generated artifacts satisfy expert coverage."""
from __future__ import annotations
import importlib.util,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MIN={"standard":10,"boundary":12,"failure":15,"adversarial":12,"property":12,"cross_skill":16,"multi_turn":12,"extreme":12}
EXECUTABLES={"evaluate_product_models.py","validate_wp3_package.py","validate_cross_domain_envelope.py","compute_product_change_impact.py","validate_wp6_contracts.py","evaluate_temporary_contract_migration.py","update_continuous_product_decision.py","compute_decision_impact_closure.py","validate_professional_report.py"}
def validate():
    errors=[];cat=json.loads((ROOT/"evaluations/fixtures/evaluation-catalog.json").read_text());cases=cat["cases"];counts=Counter(x["mode"] for x in cases)
    if cat.get("count")!=len(cases) or len(cases)!=101:errors.append("catalog_count")
    for mode,n in MIN.items():
        if counts[mode]<n:errors.append(f"mode:{mode}")
    if len({x["id"] for x in cases})!=len(cases):errors.append("duplicate_id")
    if len({x["scenario_signature"] for x in cases})!=len(cases):errors.append("duplicate_signature")
    allowed={"standard","boundary","failure","adversarial","property","cross_domain","multi_turn","extreme"}
    if {x.get("category") for x in cases}!=allowed:errors.append("coverage:category")
    if any(not x.get("mutation_class") for x in cases):errors.append("coverage:mutation_class")
    checks={"archetype":8,"plc":9,"platform":4,"region":4,"report_type":9,"event_type":12,"risk":10}
    for field,n in checks.items():
        if len({x[field] for x in cases})<n:errors.append(f"coverage:{field}")
    if len({p for x in cases for p in x["participants"]})<13:errors.append("coverage:participants")
    if {x.get("exercised_script") for x in cases}!=EXECUTABLES:errors.append("coverage:executable_scripts")
    for script in EXECUTABLES:
        if not (ROOT/"scripts"/script).is_file():errors.append(f"missing_script:{script}")
    multi=json.loads((ROOT/"evaluations/multiturn-challenges.json").read_text())
    if len(multi)!=12 or any(len(x["turns"])<4 for x in multi):errors.append("multiturn")
    extreme=json.loads((ROOT/"evaluations/extreme-scenarios.json").read_text())
    if len(extreme)!=12 or any(len(x["must"])<4 or len(x["forbidden"])<2 or not x["failure_injection"] for x in extreme):errors.append("extreme")
    spec=importlib.util.spec_from_file_location("rv",ROOT/"scripts/validate_professional_report.py");rv=importlib.util.module_from_spec(spec);spec.loader.exec_module(rv)
    for report in sorted((ROOT/"evaluations/golden").glob("*-report.json")):
        errors.extend(f"{report.name}:{e}" for e in rv.validate(json.loads(report.read_text())))
    if len(list((ROOT/"evaluations/golden").glob("*-fixture.json")))!=10 or len(list((ROOT/"evaluations/golden").glob("*-report.json")))!=10 or len(list((ROOT/"evaluations/golden").glob("*-oracle.json")))!=10:errors.append("golden_count")
    gs=importlib.util.spec_from_file_location("golden_runner",ROOT/"scripts/run_golden_evaluations.py");gr=importlib.util.module_from_spec(gs);gs.loader.exec_module(gr)
    execution_path=ROOT/"evaluations/golden-execution-results.json"
    if not execution_path.is_file():errors.append("golden_execution_missing")
    else:errors.extend(gr.validate(json.loads(execution_path.read_text())))
    bs=importlib.util.spec_from_file_location("binding_validator",ROOT/"scripts/validate_wp8_execution_bindings.py");bv=importlib.util.module_from_spec(bs);bs.loader.exec_module(bv)
    execution_map=json.loads((ROOT/"evaluations/fixtures/evaluation-execution-map.json").read_text())
    binding_result=bv.validate_and_run(cat,execution_map)
    if not binding_result["valid"] or binding_result["total_assertions"]!=404:errors.extend("execution_binding:"+x for x in binding_result["errors"] or ["assertion_count"])
    return errors
if __name__=="__main__":
    e=validate()
    if e:raise SystemExit("PIPM_WP8_COVERAGE=BLOCKED\n-"+"\n-".join(e))
    print("PIPM_WP8_COVERAGE=PASS cases=101 golden=10 multiturn=12 extreme=12")
