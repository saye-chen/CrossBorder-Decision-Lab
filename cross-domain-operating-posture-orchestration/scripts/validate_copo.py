#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; REPO = ROOT.parent
sys.path.insert(0, str(Path(__file__).parent))
from copo import SCENARIOS, topological_order  # noqa: E402

def validate() -> list[str]:
    errors=[]
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema dependency unavailable"]
    registry=json.loads((REPO/"governance/domain-architecture-registry.json").read_text())
    d14=next(x for x in registry["domains"] if x["domain_id"]=="D14")
    if d14["availability"]!="current": errors.append("D14 must be current after atomic release")
    if not (ROOT/"SKILL.md").is_file(): errors.append("callable root SKILL.md is required after atomic release")
    if d14["external_write_authority"] is not False: errors.append("D14 external write authority drift")
    required={"operating-scope","diagnostic-question","scenario-route","domain-request","domain-receipt","diagnostic-graph","cross-domain-conflict","posture-candidate","operating-posture","coordination-plan","outcome-replay","f01-consumer-receipt","f02-consumer-receipt","reproducibility-bundle","trusted-packet-ledger","decision-bundle"}
    found={p.name.removesuffix(".schema.json") for p in (ROOT/"schemas").glob("*.schema.json")} - {"common"}
    if found != required: errors.append(f"schema inventory drift missing={sorted(required-found)} extra={sorted(found-required)}")
    for path in (ROOT/"schemas").glob("*.schema.json"):
        try: jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text()))
        except Exception as exc: errors.append(f"invalid schema {path.name}: {exc}")
        if path.name not in {"common.schema.json","trusted-packet-ledger.schema.json","decision-bundle.schema.json"}:
            schema=json.loads(path.read_text())
            if "governance" not in schema.get("required",[]) or schema.get("properties",{}).get("governance",{}).get("$ref")!="common.schema.json#/$defs/governance":
                errors.append(f"schema omits shared governance metadata: {path.name}")
    for name,row in SCENARIOS.items():
        try: topological_order(row["dependencies"])
        except Exception as exc: errors.append(f"invalid dependencies {name}: {exc}")
        if not set(row["required_owners"]).issubset(set(row["dependencies"])):
            errors.append(f"required owner absent from dependency graph: {name}")
    charter=json.loads((ROOT/"contracts/charter.json").read_text())
    if charter["external_write"] is not False or charter["availability"]!="current": errors.append("charter controlled-pilot boundary drift")
    manifest=json.loads((REPO/"governance/copo-blueprint-implementation-manifest.json").read_text())
    if manifest["availability"]!="current" or manifest["release_authorized"] is not True or manifest["l4"]!="not_passed" or manifest["production_ready"] is not False: errors.append("implementation manifest release boundary drift")
    for path in list((ROOT/"integrations").glob("**/*.json"))+list((ROOT/"view-models").glob("*.json")):
        row=json.loads(path.read_text())
        if row.get("external_write") is not False: errors.append(f"write authority drift: {path.relative_to(ROOT)}")
        if path.parent.name=="view-models" and row.get("computes")!=[]: errors.append(f"view model contains second decision logic: {path.name}")
    cases=json.loads((ROOT/"evaluations/scenario-cases.json").read_text())["cases"]
    if len(cases)!=45 or len({x["id"] for x in cases})!=45: errors.append("launch scenario catalog must contain 45 unique cases")
    if any(sum(x["scenario"]==name for x in cases)!=15 for name in SCENARIOS): errors.append("each launch scenario must contain exactly 15 cases")
    mutations=json.loads((ROOT/"evaluations/mutations/contract.json").read_text())["mutations"]
    test_source=(ROOT/"tests/test_copo.py").read_text()
    if len(mutations)!=16 or len({x["id"] for x in mutations})!=16: errors.append("mutation contract must contain 16 unique mutations")
    for mutation in mutations:
        if f"def {mutation['test']}(" not in test_source: errors.append(f"mutation test is not executable: {mutation['id']}")
    catalog=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text())
    for suite in catalog["suites"]:
        if not (ROOT/suite["entrypoint"]).is_file(): errors.append(f"missing evaluation entrypoint: {suite['entrypoint']}")
    return errors

if __name__=="__main__":
    errors=validate(); print("COPO_CONTROLLED_PILOT_GATE=PASS" if not errors else "COPO_CONTROLLED_PILOT_GATE=FAIL\n- "+"\n- ".join(errors)); print("D14_AVAILABILITY=CURRENT"); print("L4_EXTERNAL_ASSURANCE=NOT_PASSED"); raise SystemExit(0 if not errors else 2)
