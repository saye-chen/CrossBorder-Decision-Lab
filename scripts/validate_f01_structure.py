#!/usr/bin/env python3
"""Portable L1 structure audit for the ECAE shared foundation."""
from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema.validators import validator_for

ROOT=Path(__file__).resolve().parents[1]
F01=ROOT/"experiment-causal-assessment"
LINK_RE=re.compile(r"\[[^]]+\]\(([^)]+)\)")


def validate()->list[str]:
    errors=[]
    skill=F01/"SKILL.md"
    if not skill.is_file(): return ["F01 SKILL.md missing"]
    text=skill.read_text(encoding="utf-8")
    front=re.match(r"^---\n(.*?)\n---\n",text,re.DOTALL)
    if not front or "name: experiment-causal-assessment" not in front.group(1): errors.append("F01 skill frontmatter/name invalid")
    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith("#"): continue
        if not (F01/target.split("#",1)[0]).exists(): errors.append(f"broken F01 Skill link: {target}")
    all_refs=list((F01/"references").rglob("*.md"))
    for path in all_refs:
        if path.name not in text and path.relative_to(F01).as_posix() not in text:
            errors.append(f"unrouted F01 reference: {path.relative_to(F01)}")
    schema_paths=list((F01/"schemas").glob("*.json"))
    if len(schema_paths)<20: errors.append("F01 requires at least 20 schema documents including common/state contracts")
    for path in schema_paths:
        try:
            schema=json.loads(path.read_text(encoding="utf-8")); validator_for(schema).check_schema(schema)
        except Exception as exc: errors.append(f"invalid F01 schema {path.name}: {exc}")
    required_dirs=["scripts","schemas","backends","tests","evaluations","integrations","references/method-cards","references/output-protocols","agents"]
    for relative in required_dirs:
        if not (F01/relative).is_dir(): errors.append(f"missing F01 directory: {relative}")
    required_files=["agents/openai.yaml","backends/backend-registry.json","integrations/consumer-migration.json","evaluations/method-evidence-registry.json","evaluations/independent-review-template.json","evaluations/real-replay-template.json"]
    for relative in required_files:
        if not (F01/relative).is_file(): errors.append(f"missing F01 file: {relative}")
    for path in F01.rglob("*"):
        if path.name=="__pycache__" or path.suffix==".pyc": errors.append(f"generated artifact present: {path.relative_to(ROOT)}")
        if path.is_file():
            try: content=path.read_text(encoding="utf-8")
            except UnicodeDecodeError: continue
            if "/Users/" in content or "C:\\Users\\" in content: errors.append(f"unnecessary local absolute path: {path.relative_to(ROOT)}")
    return sorted(set(errors))


if __name__=="__main__":
    failures=validate(); print("F01_STRUCTURE=PASS" if not failures else "F01_STRUCTURE=FAIL\n- "+"\n- ".join(failures)); raise SystemExit(0 if not failures else 2)
