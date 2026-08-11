#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,require_false
def grade(p):
    require_false(p)
    if p.get('assessment_status') in {'not_assessed','inconclusive','conflicted','expired'}: return {'status':p['assessment_status'],'grade':None,'action_ceiling':'analysis_only','external_write':False}
    if p.get('redline_conflict') or p.get('structural_incompatibility'): g=('L1','prohibited','analysis_only')
    elif not p.get('target_evidence') or p.get('conclusion_requires_reestimation'): g=('L2','rebuild_required','analysis_only')
    elif any(p.get(x) for x in ('parameter_difference','expression_difference','execution_difference')): g=('L3','calibration_required','controlled_test')
    elif p.get('same_frozen_scope') and p.get('same_version') and p.get('evidence_current'): g=('L4','direct_within_frozen_scope',p.get('source_action_ceiling','analysis_only'))
    else: g=('L2','rebuild_required','analysis_only')
    return {'status':'assessed','grade':g[0],'grade_name':g[1],'action_ceiling':g[2],'external_write':False}
def main():
    q=argparse.ArgumentParser();q.add_argument('input',type=Path);a=q.parse_args()
    try: print(json.dumps(grade(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
