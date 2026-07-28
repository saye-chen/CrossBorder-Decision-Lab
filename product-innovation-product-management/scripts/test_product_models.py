#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("models",ROOT/"scripts/evaluate_product_models.py")
M=importlib.util.module_from_spec(S);assert S and S.loader;S.loader.exec_module(M)

class Models(unittest.TestCase):
    def test_unmet_properties_and_float_rejection(self):
        a=M.evaluate({"model":"unmet_need","importance":"0.8","satisfaction":"0.2","support_weight":"3","conflict_weight":"1"})["result"]
        b=M.evaluate({"model":"unmet_need","importance":"0.9","satisfaction":"0.2","support_weight":"3","conflict_weight":"1"})["result"]
        self.assertGreater(M.d(b["unmet_score"],"x"),M.d(a["unmet_score"],"x"))
        with self.assertRaises(M.ModelError): M.evaluate({"model":"unmet_need","importance":0.8,"satisfaction":"0.2","support_weight":"3","conflict_weight":"1"})
    def test_interval_order(self):
        self.assertEqual(M.evaluate({"model":"opportunity_interval","low":"10","base":"20","high":"30"})["result"]["width"],"20")
        with self.assertRaises(M.ModelError): M.evaluate({"model":"opportunity_interval","low":"30","base":"20","high":"10"})
    def test_constraints_dependency_and_unit(self):
        p={"model":"constraint_feasibility","specifications":[{"id":"w","value":"1","min":"0.5","max":"2","unit":"kg"}],"selected_features":["a"],"dependencies":[["a","b"]]}
        self.assertEqual(M.evaluate(p)["result"]["status"],"blocked")
        p["selected_features"].append("b");self.assertEqual(M.evaluate(p)["result"]["status"],"proposed")
    def test_mvp_critical_coverage(self):
        p={"model":"mvp_coverage","assumptions":[{"id":"a","critical":True,"coverage":"0.8","threshold":"1"}]}
        self.assertEqual(M.evaluate(p)["result"]["status"],"blocked")
        p["assumptions"][0]["coverage"]="1";self.assertEqual(M.evaluate(p)["result"]["status"],"proposed")
    def test_variant_cannibalization_monotonic(self):
        p={"model":"variant_portfolio","incremental_demand":"100","cannibalized_demand":"20","complexity_demand_equivalent":"10"}
        a=M.evaluate(p)["result"];p["cannibalized_demand"]="30";b=M.evaluate(p)["result"]
        self.assertLess(M.d(b["net_incremental_demand"],"x"),M.d(a["net_incremental_demand"],"x"))
    def test_packaging_volume_and_protection_gate(self):
        p={"model":"packaging_impact","length_cm":"10","width_cm":"20","height_cm":"30","dimensional_divisor_cm3_per_kg":"5000","protection_score":"0.9","minimum_protection_score":"0.8"}
        self.assertEqual(M.evaluate(p)["result"]["volume_cm3"],"6000")
        p["protection_score"]="0.7";self.assertEqual(M.evaluate(p)["result"]["status"],"blocked")
    def test_roadmap_requires_approved_metadata_and_ties_are_inconclusive(self):
        meta={"value":"1","owner":"product","approved_by":"owner","scope":"US","valid_from":"2026-01-01","valid_to":"2026-12-31","source":"review"}
        p={"model":"roadmap_priority","weights":{"value":meta},"candidates":[{"id":"a","scores":{"value":"0.8"}},{"id":"b","scores":{"value":"0.8"}}]}
        self.assertEqual(M.evaluate(p)["result"]["status"],"inconclusive")
        del meta["approved_by"]
        with self.assertRaises(M.ModelError): M.evaluate(p)
    def test_traceability_blocks_orphans(self):
        p={"model":"traceability","requirements":[{"id":"r","specification_ids":["s"]}],"specifications":[{"id":"s","requirement_id":"r","verification_ids":["v"]}],"claims":[{"id":"c","specification_id":"s","verification_ids":["v"]}],"verifications":[{"id":"v"}]}
        self.assertTrue(M.evaluate(p)["result"]["freeze_eligible"])
        p["claims"][0]["verification_ids"]=[];self.assertFalse(M.evaluate(p)["result"]["freeze_eligible"])
    def test_hard_gate_is_non_compensable(self):
        p={"model":"unmet_need","importance":"1","satisfaction":"0","support_weight":"10","conflict_weight":"0","hard_gates":[{"id":"safety","status":"failed"}]}
        self.assertEqual(M.evaluate(p)["result"]["status"],"blocked")
if __name__=="__main__": unittest.main(verbosity=2)
