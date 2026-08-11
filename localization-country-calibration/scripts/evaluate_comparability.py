#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,require_false
FIELDS=('metric_id','unit','currency','tax_basis','time_window','object_granularity')
def evaluate(p):
    require_false(p); left=p.get('left',{});right=p.get('right',{});differences=[f for f in FIELDS if left.get(f)!=right.get(f)]
    converted=set(p.get('converted_fields',[])); unresolved=[f for f in differences if f not in converted]
    if not differences: status='comparable'
    elif not unresolved: status='comparable_after_conversion'
    elif len(unresolved)<len(FIELDS): status='partially_comparable'
    else: status='not_comparable'
    return {'status':status,'differences':differences,'unresolved':unresolved,'aggregation_allowed':status in {'comparable','comparable_after_conversion'},'causal_claim':False,'external_write':False}
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(evaluate(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
