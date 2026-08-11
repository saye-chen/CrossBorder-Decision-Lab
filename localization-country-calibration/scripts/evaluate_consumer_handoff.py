#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,ACTION_RANK,require_false
VALID={f'D{i:02d}' for i in range(1,14)}
def evaluate(p):
    require_false(p); cid=p.get('consumer_id');h=p.get('handoff',{});adapter=p.get('adapter',{})
    if cid not in VALID or adapter.get('consumer_id')!=cid: raise LCCAError('CONSUMER_INVALID','consumer mismatch')
    if h.get('contract')!='LCCA-HANDOFF-1.0' or h.get('target_domain')!=cid: raise LCCAError('HANDOFF_INCOMPLETE','contract or target mismatch')
    if h.get('claim_upgrade_allowed') is not False: raise LCCAError('ACTION_CEILING_EXCEEDED','claim upgrade forbidden')
    if ACTION_RANK.get(h.get('action_ceiling'),99)>ACTION_RANK.get(h.get('source_action_ceiling'),-1): raise LCCAError('ACTION_CEILING_EXCEEDED','action ceiling upgraded')
    if h.get('comparability_status') in {'not_assessed','conflicted','expired','not_comparable'} and h.get('action_ceiling')!='analysis_only': raise LCCAError('ACTION_CEILING_EXCEEDED','failed qualification must be analysis only')
    return {'consumer_id':cid,'status':'accepted_controlled_pilot','rollback_verified':adapter.get('rollback_supported') is True,'production_accepted':False,'external_write':False}
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(evaluate(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
