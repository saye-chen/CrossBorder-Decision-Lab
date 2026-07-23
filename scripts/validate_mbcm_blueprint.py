#!/usr/bin/env python3
"""Validate D12/MBCM blueprint traceability and evidence closure."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"governance/mbcm-blueprint-implementation-manifest.json"
SCIENCE_PATH=ROOT/"governance/mbcm-marketing-science-remediation.json"
VALID={"fixed","partial","open","controlled_external_gate"}

def main() -> None:
    data=json.loads(PATH.read_text(encoding="utf-8")); errors=[]
    blueprint=data.get("blueprint",{})
    if blueprint.get("baseline")!="Frozen-v1.0": errors.append("baseline_not_frozen_v1")
    if len(blueprint.get("sha256",""))!=64 or blueprint.get("line_count")!=5122:
        errors.append("invalid_blueprint_provenance")
    reqs=data.get("requirements",[]); ids=[r.get("id") for r in reqs]
    if len(reqs)!=22 or len(ids)!=len(set(ids)): errors.append("requirements_not_22_unique")
    if {f"D12-R{i:02d}" for i in range(1,22)}-{str(x) for x in ids}: errors.append("missing_normative_requirement")
    if "D12-L4" not in ids: errors.append("missing_l4_gate")
    for req in reqs:
        status=req.get("status")
        if status not in VALID: errors.append(f"{req.get('id')}:invalid_status")
        evidence=req.get("evidence",[]); tests=req.get("tests",[])
        if status=="fixed" and (not evidence or not tests):
            errors.append(f"{req.get('id')}:fixed_without_evidence_and_test")
        for rel in evidence+tests:
            if not (ROOT/rel).exists(): errors.append(f"{req.get('id')}:missing_path:{rel}")
    l4=next((r for r in reqs if r.get("id")=="D12-L4"),{})
    if l4.get("status")!="controlled_external_gate": errors.append("l4_must_remain_external")
    science=json.loads(SCIENCE_PATH.read_text(encoding="utf-8"))
    science_reqs=science.get("requirements",[])
    if len(science_reqs)!=10 or {x.get("id") for x in science_reqs}!={f"MS-{i:02d}" for i in range(1,11)}:
        errors.append("marketing_science_requirements_not_10_unique")
    for req in science_reqs:
        if req.get("status")!="fixed": errors.append(f"{req.get('id')}:marketing_science_not_fixed")
        if not req.get("evidence") or not req.get("tests"): errors.append(f"{req.get('id')}:missing_evidence_or_test")
        for rel in req.get("evidence",[])+req.get("tests",[]):
            if not (ROOT/rel).exists(): errors.append(f"{req.get('id')}:missing_path:{rel}")
    if errors: raise SystemExit("MBCM blueprint validation failed:\n- "+"\n- ".join(errors))
    counts={s:sum(r["status"]==s for r in reqs) for s in sorted(VALID)}
    print(f"MBCM blueprint traceability passed: {len(reqs)} blueprint requirements {counts}; 10 marketing-science remediations fixed")

if __name__=="__main__": main()
