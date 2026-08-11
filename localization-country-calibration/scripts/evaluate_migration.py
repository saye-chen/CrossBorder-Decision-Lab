#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,canonical_hash,require_false
CONSUMERS={f'D{i:02d}' for i in range(1,14)}
def evaluate(p):
    require_false(p)
    mappings=p.get('field_mappings',[]); critical=[m for m in mappings if m.get('criticality') in {'major','safety_critical'} and m.get('loss') in {'material','unmapped'}]
    dual=p.get('dual_run',{}); same=dual.get('same_input_hash') and dual.get('source_input_hash')==dual.get('target_input_hash')==dual.get('same_input_hash')
    accepted={x.get('consumer_id') for x in p.get('consumer_acceptance',[]) if x.get('status')=='accepted_controlled_pilot' and x.get('rollback_verified') is True and x.get('production_accepted') is False}
    differences=p.get('differences',[]); unexplained=[x for x in differences if not x.get('explanation') or x.get('severity') in {'P0','P1'} and not x.get('accepted_by_owner')]
    ready=not critical and bool(same) and accepted==CONSUMERS and not unexplained and p.get('rollback',{}).get('supported') is True and p.get('rollback',{}).get('source_readable') is True
    result={'status':'cutover_ready' if ready else 'blocked','critical_mapping_failures':len(critical),'same_input_verified':bool(same),'accepted_consumers':len(accepted),'unexplained_differences':len(unexplained),'production_accepted':False,'external_write':False}
    result['result_hash']=canonical_hash(result);return result
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(evaluate(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
