#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

def validate_file(schema_name: str, payload: dict) -> list[str]:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(payload), key=lambda x: list(x.path))]

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("schema", choices=["canonical-product-object.schema.json","product-lifecycle-state.schema.json"])
    parser.add_argument("input", type=Path)
    args=parser.parse_args()
    try:
        payload=json.loads(args.input.read_text())
        errors=validate_file(args.schema,payload)
    except (OSError,json.JSONDecodeError) as exc:
        print(f"PIPM_WP2=BLOCKED: {exc}",file=sys.stderr);return 1
    if errors:
        print("PIPM_WP2=BLOCKED: "+"|".join(errors),file=sys.stderr);return 1
    print("PIPM_WP2=PASS");return 0

if __name__=="__main__": raise SystemExit(main())
