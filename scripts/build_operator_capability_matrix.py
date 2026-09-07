#!/usr/bin/env python3
"""Inventory evidence levels without equating platform routing with validation."""
import argparse
import json
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]

def build(as_of):
    domains=json.loads((ROOT/'governance/domain-architecture-registry.json').read_text())['domains']
    maturity={d['skill']:d for d in json.loads((ROOT/'governance/domain-maturity-status.json').read_text())['domains']}
    cards=[json.loads(p.read_text()) for p in (ROOT/'governance/platform-knowledge/cards').glob('*.json')]
    rows=[]
    for d in domains:
        if d['availability']!='current':continue
        matching=[c for c in cards if c['owner_domain']==d['domain_id']]
        rows.append({'domain':d['domain_id'],'skill':d['skill'],'country':'requires_task_scope','platform':'requires_task_scope','operating_mode':'requires_task_scope','task':d['owned_decision_types'],
          'method_entry':d['skill']+'/SKILL.md','calculator_scripts_present':any((ROOT/d['skill']/'scripts').glob('*.py')),
          'task_calculation_qualified':False,'current_task_evidence':'not_verified',
          'registered_real_cases':maturity[d['skill']]['authorized_real_cases'],
          'shared_cards':[{'id':c['card_id'],'platform':c['platform'],'evidence_status':c['evidence_status'],'within_recorded_validity':date.fromisoformat(c['valid_from'])<=as_of<=date.fromisoformat(c['expires_at']),'source_reverified_this_run':False} for c in matching]})
    return {'as_of':as_of.isoformat(),'scope':'repository_inventory_not_platform_readiness','production_ready':False,'rows':rows}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--as-of',default=date.today().isoformat());a=p.parse_args()
    print(json.dumps(build(date.fromisoformat(a.as_of)),ensure_ascii=False,indent=2))
