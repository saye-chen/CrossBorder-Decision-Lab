#!/usr/bin/env python3
from __future__ import annotations
import argparse,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PATH=ROOT/'governance/erdg/scripts/validate_contract.py';SPEC=importlib.util.spec_from_file_location('erdg_contract',PATH);CORE=importlib.util.module_from_spec(SPEC);assert SPEC and SPEC.loader;SPEC.loader.exec_module(CORE)
def main():
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);a=p.parse_args()
 try: payload=json.loads(a.input.read_text());errors=CORE.validate(payload)
 except (OSError,json.JSONDecodeError) as e: print(f'LCCA_ERDG=BLOCKED: {e}',file=sys.stderr);return 1
 if errors: print('LCCA_ERDG=BLOCKED: '+'|'.join(errors),file=sys.stderr);return 1
 print(json.dumps({'valid':True,'erdg_contract':'ERDG-CONTRACT-2026.07','decision_owner':payload['decision_owner'],'external_write':False},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
