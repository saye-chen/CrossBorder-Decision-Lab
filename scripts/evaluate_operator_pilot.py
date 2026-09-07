#!/usr/bin/env python3
"""Summarize observed blinded reviews; never certify independence or L4."""
import argparse
import json
import math
from pathlib import Path

FIELDS=('completed','understood_next_action','elapsed_seconds','clarification_rounds','human_interventions','fact_errors','calculation_errors','critical_omissions')

def evaluate(payload):
    if payload.get('production_ready') is not False: raise ValueError('production_ready must remain false')
    records=payload.get('records',[])
    if not records: raise ValueError('no observed reviews; a blank template is not evidence')
    groups={};seen=set();case_scopes={}
    for r in records:
        for key in ('case_id','candidate_id','reviewer_ref','evidence_ref','input_hash','evidence_cutoff','source_class',*FIELDS):
            if key not in r or r[key] is None or r[key]=='': raise ValueError(f'missing observed field: {key}')
        if r['source_class'] not in {'synthetic_fixture','authorized_historical'}:raise ValueError('unsupported source class')
        key=(r['case_id'],r['candidate_id'],r['reviewer_ref'])
        if key in seen: raise ValueError('duplicate reviewer record')
        seen.add(key)
        scope=(r['input_hash'],r['evidence_cutoff'])
        if r['case_id'] in case_scopes and case_scopes[r['case_id']]!=scope:raise ValueError('candidate inputs or evidence cutoffs are not comparable')
        case_scopes[r['case_id']]=scope
        for f in FIELDS[:2]:
            if not isinstance(r[f],bool):raise ValueError(f'{f} must be boolean')
        for f in FIELDS[2:]:
            if isinstance(r[f],bool) or not isinstance(r[f],(int,float)) or not math.isfinite(r[f]) or r[f]<0: raise ValueError(f'{f} must be observed nonnegative number')
        g=groups.setdefault(r['candidate_id'],{'reviews':0,'completed':0,'understood':0,'seconds':0,'clarifications':0,'human_interventions':0,'fact_errors':0,'calculation_errors':0,'critical_omissions':0})
        g['reviews']+=1;g['completed']+=int(r['completed']);g['understood']+=int(r['understood_next_action']);g['seconds']+=r['elapsed_seconds'];g['clarifications']+=r['clarification_rounds']
        for f in ('human_interventions','fact_errors','calculation_errors','critical_omissions'):g[f]+=r[f]
    for g in groups.values():
        g['completion_rate']=g['completed']/g['reviews'];g['mean_seconds']=g['seconds']/g['reviews']
    return {'candidate_summaries':groups,'case_count':len(case_scopes),'recorded_historical_reviews':sum(r['source_class']=='authorized_historical' for r in records),'independence':'requires_external_verification','business_effectiveness':'not_established','production_ready':False,'l4_status':'not_changed','ranking':None}

def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);a=p.parse_args()
    try: result=evaluate(json.loads(a.input.read_text()))
    except (OSError,ValueError,TypeError,KeyError) as exc:print(json.dumps({'valid':False,'error':str(exc)},ensure_ascii=False));return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
