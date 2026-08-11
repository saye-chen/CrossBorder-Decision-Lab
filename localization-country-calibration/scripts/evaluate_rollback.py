#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,canonical_hash,require_false
def evaluate(p):
    require_false(p)
    if p.get('state') not in {'cutover','blocked'} or not p.get('source_readable') or not p.get('source_snapshot_hash'): raise LCCAError('BLOCKED_ROLLBACK_UNRESOLVED','source snapshot unavailable')
    invalidated=sorted(set(p.get('target_current_refs',[])));result={'state':'rolled_back','restored_contract':'F02-temporary-localization-contract-v1','restored_current_hash':p['source_snapshot_hash'],'invalidated_target_refs':invalidated,'recompute_scope':sorted(set(p.get('dependent_refs',[]))),'external_write':False};result['rollback_hash']=canonical_hash(result);return result
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(evaluate(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
