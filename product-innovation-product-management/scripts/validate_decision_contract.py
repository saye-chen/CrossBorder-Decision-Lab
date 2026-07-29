#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/"governance/erdg/scripts/validate_contract.py"
SPEC=importlib.util.spec_from_file_location("erdg_contract",PATH)
CORE=importlib.util.module_from_spec(SPEC);assert SPEC and SPEC.loader;SPEC.loader.exec_module(CORE)

def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("input",type=Path);args=parser.parse_args()
    try:
        payload=json.loads(args.input.read_text())
        errors=CORE.validate(payload)
    except (OSError,json.JSONDecodeError) as exc:
        print(f"PIPM_ERDG=BLOCKED: {exc}",file=sys.stderr);return 1
    if errors:
        print("PIPM_ERDG=BLOCKED: "+"|".join(errors),file=sys.stderr);return 1
    print(json.dumps({"valid":True,"erdg_contract":"ERDG-CONTRACT-2026.07","decision_owner":payload["decision_owner"]},ensure_ascii=False))
    return 0

if __name__=="__main__": raise SystemExit(main())
