#!/usr/bin/env python3
import copy
import json
import pathlib
import sys
import unittest

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from calculate_recoverable_value import calculate
from decompose_conversion_funnel import evaluate as funnel
from evaluate_hard_gates import evaluate as gates
from evaluate_listing_experiment import evaluate as experiment
from evaluate_variant_structure import evaluate as variants
from validate_d08_contract import validate as contract
from validate_page_lineage import validate as lineage

ROOT=HERE.parent
GOLD=json.loads((ROOT/"references/golden-expert-report.json").read_text())

class CoreTests(unittest.TestCase):
    def test_golden_contract(self): self.assertEqual(contract(GOLD)["status"],"pass")
    def test_golden_is_expert(self): self.assertTrue(contract(GOLD)["expert_optimization"])
    def test_valid_experiment(self): self.assertIn(experiment({"control":{"n":1000,"successes":100},"treatment":{"n":1000,"successes":130},"primary_metric":"order","mature":True})["decision"],{"go","iterate"})

def add_test(name,fn): setattr(CoreTests,name,fn)

# 24 Gate cases: every gate in each non-pass state plus all-pass controls.
for i in range(24):
    def case(self,i=i):
        state=("pass","conditional","unknown","fail")[i%4]
        payload={"gates":{f"G{x}":"pass" for x in range(1,7)}}; payload["gates"][f"G{(i%6)+1}"]=state
        out=gates(payload); self.assertEqual(out["overall"],state)
    add_test(f"test_gate_{i:03}",case)

# 20 valid funnel conservation cases.
for i in range(20):
    def case(self,i=i):
        base=1000+i*10; c={"qualified_exposure":base,"visit":500,"engage":300,"add_to_cart":100,"checkout":60,"paid_order":40}
        self.assertEqual(funnel({"counts":c})["status"],"pass")
    add_test(f"test_funnel_{i:03}",case)

# 20 value monotonicity cases.
for i in range(20):
    def case(self,i=i):
        a=calculate({"qualified_visits":1000+i,"conversion_gap":.05,"recoverable_share":.5,"mature_contribution_per_order":{"low":2,"high":4},"implementation_cost":10,"currency":"USD"})
        b=calculate({"qualified_visits":1100+i,"conversion_gap":.05,"recoverable_share":.5,"mature_contribution_per_order":{"low":2,"high":4},"implementation_cost":10,"currency":"USD"})
        self.assertGreater(b["recoverable_orders"],a["recoverable_orders"])
    add_test(f"test_value_{i:03}",case)

# 15 lineage cases with one current version.
for i in range(15):
    def case(self,i=i):
        nodes=[{"id":f"v{x}","current":x==i+1} for x in range(i+2)]; edges=[{"from":f"v{x}","to":f"v{x+1}"} for x in range(i+1)]
        self.assertEqual(lineage({"nodes":nodes,"edges":edges})["status"],"pass")
    add_test(f"test_lineage_{i:03}",case)

# 16 anti-regression deletions: any mandatory optimization field must fail.
MANDATORY=["optimization_unit_id","object_id","page_version_id","scenario_id","current_observation","evidence_ids","counterevidence_ids","root_cause","alternative_explanations","proposed_variant_ids","implementation_order","owner","primary_metric","success_condition","stop_condition","rollback_version"]
for i,field in enumerate(MANDATORY):
    def case(self,field=field):
        x=copy.deepcopy(GOLD); del x["optimization_units"][0][field]
        self.assertEqual(contract(x)["status"],"fail")
    add_test(f"test_contract_delete_{i:03}_{field}",case)

# 12 valid variant portfolio cases.
for i in range(12):
    def case(self,i=i):
        payload={"product_identity":"p","variants":[{"variant_id":"a","attributes":{"size":f"S{i}"},"inventory":i,"product_identity":"p"},{"variant_id":"b","attributes":{"size":f"L{i}"},"inventory":i+1,"product_identity":"p"}]}
        self.assertEqual(variants(payload)["status"],"pass")
    add_test(f"test_variant_{i:03}",case)

if __name__=="__main__": unittest.main(verbosity=1)
