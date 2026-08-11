#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,parse_time,require_false

REQUIRED=("country_code","jurisdiction_id","platform_id","platform_site_id","locale","decision_time")
def validate(payload):
    require_false(payload)
    missing=[f for f in REQUIRED if not payload.get(f)]
    if missing: raise LCCAError("SCOPE_INCOMPLETE",",".join(missing))
    if len(payload["country_code"])!=2 or payload["country_code"]!=payload["country_code"].upper(): raise LCCAError("SCOPE_INCOMPLETE","country_code must be ISO alpha-2")
    parse_time(payload["decision_time"],"decision_time")
    return {"status":"qualified","scope_id":payload.get("object_id"),"external_write":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=Path);a=p.parse_args()
    try: print(json.dumps(validate(json.loads(a.input.read_text())),ensure_ascii=False,sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=="__main__": raise SystemExit(main())
