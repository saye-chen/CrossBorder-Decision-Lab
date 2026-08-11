#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
def main():
    p=argparse.ArgumentParser();p.add_argument('schema',type=Path);p.add_argument('instance',type=Path);a=p.parse_args()
    try:
        schema=json.loads(a.schema.read_text());instance=json.loads(a.instance.read_text());Draft202012Validator.check_schema(schema)
        errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(instance),key=lambda e:list(e.path))
    except Exception as e: print(f'INVALID: {e}',file=sys.stderr);return 2
    if errors:
        for e in errors: print('BLOCKED: '+'.'.join(map(str,e.path))+': '+e.message,file=sys.stderr)
        return 1
    print('PASS');return 0
if __name__=='__main__': raise SystemExit(main())
