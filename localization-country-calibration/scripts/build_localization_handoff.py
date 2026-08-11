#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,canonical_hash,narrower_action,require_false
def build(p):
    require_false(p)
    required=('handoff_id','source_domain','target_domain','scope_ref','comparability_status','transfer_status','source_action_ceiling')
    if any(not p.get(x) for x in required): raise LCCAError('HANDOFF_INCOMPLETE','required handoff fields missing')
    ceiling=narrower_action(p['source_action_ceiling'],p.get('f02_action_ceiling','analysis_only'))
    out={k:p.get(k) for k in required};out.update({'schema_version':'1.0.0','contract':'LCCA-HANDOFF-1.0','action_ceiling':ceiling,'claim_upgrade_allowed':False,'external_write':False,'limitations':p.get('limitations',[])})
    out['content_hash']=canonical_hash(out);return out
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(build(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
