#!/usr/bin/env python3
"""Audit F02 L1-L4 gates while keeping real-market evidence outside L1-L3."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];F02=ROOT/'localization-country-calibration'
def load(p): return json.loads(p.read_text())
def run(cmd):
 env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1';r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=env);return r.returncode==0,(r.stdout+r.stderr)[-3000:]
def audit(run_tests=True):
 manifest=load(ROOT/'governance/f02-implementation-manifest.json');blue=ROOT/manifest['blueprint']['path'];blue_hash=hashlib.sha256(blue.read_bytes()).hexdigest()
 required=[F02/'SKILL.md',F02/'agents/openai.yaml',F02/'schemas',F02/'scripts',F02/'tests',F02/'integrations/consumer-migration.json',F02/'evaluations/development-closure.json',F02/'evaluations/controlled-pilot-review.json',F02/'evaluations/independent-review-template.json',F02/'evaluations/real-replay-template.json',ROOT/'governance/f02-requirements-traceability.json']
 missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
 test_ok,test_out=(True,'not_run') if not run_tests else run([sys.executable,'-m','unittest','discover','-s',str(F02/'tests'),'-p','test_*.py'])
 migration=load(F02/'integrations/consumer-migration.json');acceptance=load(F02/'evaluations/consumer-controlled-pilot-acceptance.json');review=load(F02/'evaluations/controlled-pilot-review.json');external=load(F02/'evaluations/independent-review-template.json');replay=load(F02/'evaluations/real-replay-template.json');closure=load(F02/'evaluations/development-closure.json')
 adapters=[ROOT/x['adapter_ref'] for x in migration['consumers']];adapters_ok=len(adapters)==13 and all(x.exists() and load(x).get('external_write') is False for x in adapters)
 l1=not missing and blue_hash==manifest['blueprint']['sha256'] and all(x['status']=='complete' for x in manifest['work_packages'])
 l2=l1 and test_ok and adapters_ok and len(acceptance['consumers'])==13 and all(x['status']=='accepted_controlled_pilot' and x['rollback_verified'] for x in acceptance['consumers']) and not acceptance['production_accepted']
 l3=l2 and review['status']=='accepted' and review['l3_controlled_pilot_gate_closed'] and closure['status']=='L3_controlled_pilot_complete'
 l4=l3 and external['l4_external_review_gate_closed'] and replay['l4_gate_closed'] and migration['completion_gate']['production_acceptance_complete']
 registry=load(ROOT/'governance/foundation-capability-registry.json');f02=next(x for x in registry['foundations'] if x['foundation_id']=='F02');expected=f02['availability']=='current' and f02['maturity']=='controlled_pilot'
 boundaries=manifest['release_boundaries'];consistent=boundaries['l1_structure']==l1 and boundaries['l2_contract']==l2 and boundaries['l3_expert']==l3 and boundaries['l4_external_assurance']==l4 and boundaries['production_ready'] is False and boundaries['external_write_authority'] is False
 result={'schema_version':'1.0.0','f02_release_audit':{'l1_structure':l1,'l2_contract':l2,'l3_expert':l3,'l4_external_assurance':l4,'availability':f02['availability'],'maturity':f02['maturity'],'manifest_consistent':consistent,'premature_promotion':not(expected and consistent and l3),'controlled_pilot_released':expected and consistent and l3,'remaining_gate_class':'L4_EXTERNAL_ONLY' if l3 and not l4 else 'L1_L3_REMAINS'},'checks':{'missing_artifacts':missing,'blueprint_hash_match':blue_hash==manifest['blueprint']['sha256'],'tests':{'pass':test_ok,'output':test_out},'consumer_adapters_13_of_13':adapters_ok},'l4_blockers':{'production_consumer_acceptance_pending':not migration['completion_gate']['production_acceptance_complete'],'independent_nonimplementer_review_pending':not external['l4_external_review_gate_closed'],'authorized_real_replay_pending':not replay['l4_gate_closed']},'policy':{'production_ready':False,'external_write':False}}
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--no-tests',action='store_true');p.add_argument('--require-l3',action='store_true');p.add_argument('--write-audit',action='store_true');a=p.parse_args();r=audit(not a.no_tests)
 if a.write_audit:(F02/'evaluations/release-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True));return 2 if r['f02_release_audit']['premature_promotion'] or (a.require_l3 and not r['f02_release_audit']['l3_expert']) else 0
if __name__=='__main__':raise SystemExit(main())
