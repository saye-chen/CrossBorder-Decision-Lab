#!/usr/bin/env python3
"""Fail closed when GitHub Actions permissions, timeouts, pins, or D14 release gates drift."""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORKFLOWS=[ROOT/".github/workflows/expert-release.yml",ROOT/".github/workflows/knowledge-health.yml"]
SHA_USE=re.compile(r"uses:\s+[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@([0-9a-f]{40})(?:\s+#.*)?$")
def validate()->list[str]:
 errors=[]
 for path in WORKFLOWS:
  text=path.read_text()
  if "permissions:\n  contents: read" not in text:errors.append(f"{path.name}: missing read-only permissions")
  if "timeout-minutes:" not in text:errors.append(f"{path.name}: missing timeout")
  for line in text.splitlines():
   if "uses:" in line and not SHA_USE.search(line.strip()):errors.append(f"{path.name}: unpinned action: {line.strip()}")
 expert=WORKFLOWS[0].read_text()
 for entry in ("validate_copo.py","test_scenario_catalog.py","test_behavior_mutations.py","test_period_delta_bridge.py"):
  if entry not in expert:errors.append(f"expert-release.yml: missing D14 gate {entry}")
 if "D14 controlled-pilot release gate (L4 remains separate)" not in expert:errors.append("D14 gate lacks controlled-pilot/L4 disclaimer")
 return errors
if __name__=="__main__":
 errors=validate();print("CI_WORKFLOW_SECURITY=PASS" if not errors else "CI_WORKFLOW_SECURITY=FAIL\n- "+"\n- ".join(errors));raise SystemExit(0 if not errors else 2)
