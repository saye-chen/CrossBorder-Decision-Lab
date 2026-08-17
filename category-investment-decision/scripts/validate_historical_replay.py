#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess, sys
ROOT = Path(__file__).resolve().parents[2]
if sys.argv[1:]:
    command = [sys.executable, str(ROOT / "scripts/validate_domain_maturity.py"), *sys.argv[1:], "category-investment-decision"]
else:
    status = json.loads((ROOT / "governance/domain-maturity-status.json").read_text())
    manifest = next(item["replay_manifest"] for item in status["domains"] if item["skill"] == "category-investment-decision")
    command = [sys.executable, str(ROOT / "scripts/validate_domain_maturity.py"), str(ROOT / manifest), "category-investment-decision"]
raise SystemExit(subprocess.run(command).returncode)
