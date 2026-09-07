#!/usr/bin/env python3
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('starter',ROOT/'scripts/run_starter.py');starter=importlib.util.module_from_spec(spec);spec.loader.exec_module(starter)
spec=importlib.util.spec_from_file_location('installer',ROOT/'scripts/install_skills.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)

class OperatorStarter(unittest.TestCase):
    def payload(self,task,suffix=''):
        return json.loads((ROOT/f'examples/starter/{task}{suffix}.json').read_text())
    def test_three_owned_calculators_and_independent_expected_values(self):
        ad=starter.run('ad-profit',self.payload('ad-profit'))
        self.assertEqual(ad['metrics']['ad_contribution_profit'],200)
        trial=starter.run('product-test',self.payload('product-test'))
        self.assertEqual(trial['metrics']['contribution_margin_per_unit'],12.5)
        self.assertEqual(trial['metrics']['break_even_units'],24)
        inv=starter.run('replenishment',self.payload('replenishment'))
        self.assertEqual(inv['metrics']['final_order_qty'],100)
        self.assertEqual(inv['metrics']['schedule']['available_to_sell_date'],'2026-09-18')
        for r in (ad,trial,inv):
            self.assertFalse(r['external_write']);self.assertFalse(r['production_ready'])
            self.assertEqual(r['source_class'],'synthetic_fixture')
    def test_missing_invalid_and_no_fabricated_results(self):
        for task in starter.TASKS:
            for suffix in ('-missing','-invalid'):
                r=starter.run(task,self.payload(task,suffix))
                self.assertEqual(r['status'],'inconclusive',(task,r));self.assertIsNone(r['metrics'])
    def test_mixed_currency_duplicate_and_immature(self):
        p=self.payload('ad-profit');p['data'].append(copy.deepcopy(p['data'][0]))
        self.assertEqual(starter.run('ad-profit',p)['status'],'inconclusive')
        p=self.payload('ad-profit');p['data'][0]['currency']='EUR'
        self.assertEqual(starter.run('ad-profit',p)['status'],'inconclusive')
        p=self.payload('ad-profit');p['data'][0]['maturity']='immature'
        r=starter.run('ad-profit',p);self.assertEqual(r['metrics']['status'],'provisional')
    def test_continuity_and_cross_case_rejection(self):
        p=self.payload('product-test');r=starter.run('product-test',p)
        p['data']['price']=31;new=starter.run('product-test',p,r)
        self.assertEqual(new['version'],2);self.assertEqual(new['parent_hash'],starter.digest(r))
        p['case_id']='different';self.assertEqual(starter.run('product-test',p,r)['status'],'inconclusive')
    def test_cli_preserves_sources_and_never_overwrites_outputs(self):
        source=ROOT/'examples/starter/ad-profit.json';before=source.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/'new';cmd=[sys.executable,str(ROOT/'scripts/run_starter.py'),'ad-profit',str(source),'--output-dir',str(dest)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertTrue((dest/'outcome.json').exists())
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        self.assertEqual(before,source.read_bytes())
    def test_selected_skill_link_keeps_governance_and_conflicts_safe(self):
        name='advertising-analysis-measurement-optimization'
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/'skills';self.assertEqual(installer.install(dest,[name]),[])
            real=(dest/name).resolve();self.assertTrue((real.parent/'governance/interaction/interaction-governance.md').is_file())
            self.assertEqual(installer.install(dest,[name],True),[])
            (dest/name).unlink();(dest/name).mkdir()
            self.assertTrue(installer.install(dest,[name]));self.assertTrue((dest/name).is_dir())
if __name__=='__main__':unittest.main()
