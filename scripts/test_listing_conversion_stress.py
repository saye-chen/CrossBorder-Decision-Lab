#!/usr/bin/env python3
import importlib.util
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SKILL=ROOT/"platform-store-listing-conversion"
SCRIPTS=SKILL/"scripts"
sys.path.insert(0,str(SCRIPTS))

from validate_d08_contract import validate as validate_contract
from evaluate_hard_gates import evaluate as evaluate_gates
from decompose_conversion_funnel import evaluate as evaluate_funnel
from validate_page_lineage import validate as validate_lineage

def text(path): return path.read_text(encoding="utf-8")

class ListingConversionStress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill=text(SKILL/"SKILL.md")
        cls.scenes=text(SKILL/"references/scenario-lifecycle-and-routing.md")
        cls.platforms=text(SKILL/"references/platform-expert-cards.md")
        cls.optimization=text(SKILL/"references/concrete-optimization-contract.md")
        cls.acceptance=text(SKILL/"references/professional-report-and-acceptance.md")
        cls.golden=json.loads(text(SKILL/"references/golden-expert-report.json"))
        cls.outputs=json.loads(text(SKILL/"references/output-contracts.json"))

    def test_runtime_and_sovereignty(self):
        self.assertIn("D08-2026.07",self.skill)
        for owner in ("D01","D05","D06","D07","D09","D11","D12","D13"):
            self.assertIn(owner,self.skill)

    def test_six_gates_are_noncompensatory(self):
        for i in range(1,7): self.assertIn(f"G{i}",self.skill)
        payload={"gates":{f"G{i}":"pass" for i in range(1,7)}}; payload["gates"]["G5"]="fail"
        self.assertEqual(evaluate_gates(payload)["action_limit"],"blocked")

    def test_four_surfaces_require_concrete_output(self):
        for term in ("强制输出三版","逐张输出","逐模块输出","每个断点给"):
            self.assertIn(term,self.optimization)
        self.assertEqual(validate_contract(self.golden)["label"],"Expert optimization report")

    def test_deleting_each_surface_fails(self):
        for surface in ("title","image_set","detail","landing_page"):
            case=json.loads(json.dumps(self.golden)); case["optimization_units"]=[u for u in case["optimization_units"] if u["surface_type"]!=surface]
            self.assertEqual(validate_contract(case)["status"],"fail")

    def test_fourteen_scenarios_and_nine_lifecycle_states(self):
        for i in range(1,15): self.assertIn(f"{i}. ",self.scenes)
        for i in range(9): self.assertIn(f"L{i}",self.scenes)

    def test_twelve_platform_cards_and_unknown_route(self):
        platforms=("Amazon","Walmart Marketplace","eBay","Etsy","TikTok Shop","Temu","SHEIN Marketplace","AliExpress","Shopee","Lazada","Mercado Libre","Shopify/DTC")
        for p in platforms: self.assertIn(f"| {p} |",self.platforms)
        self.assertIn("未知平台",self.platforms)

    def test_dynamic_platform_rules_require_recheck(self):
        self.assertIn("当前官方/授权资料重验",self.platforms)
        self.assertIn("不固化易变数字",self.platforms)

    def test_thirteen_deterministic_tools_exist_and_are_routed(self):
        expected=("validate_d08_contract.py","validate_object_version.py","validate_evidence_ledger.py","evaluate_hard_gates.py","compare_page_versions.py","check_cross_layer_consistency.py","evaluate_task_coverage.py","evaluate_variant_structure.py","decompose_conversion_funnel.py","evaluate_listing_experiment.py","calculate_recoverable_value.py","rank_repair_actions.py","validate_page_lineage.py")
        for name in expected:
            self.assertTrue((SCRIPTS/name).is_file(),name); self.assertIn(name,self.skill)

    def test_funnel_rejects_impossible_counts(self):
        out=evaluate_funnel({"counts":{"qualified_exposure":10,"visit":20,"engage":1,"add_to_cart":1,"checkout":1,"paid_order":1}})
        self.assertEqual(out["status"],"invalid")

    def test_lineage_rejects_cycle_and_multiple_current(self):
        out=validate_lineage({"nodes":[{"id":"a","current":True},{"id":"b","current":True}],"edges":[{"from":"a","to":"b"},{"from":"b","to":"a"}]})
        self.assertEqual(out["status"],"fail"); self.assertEqual(len(out["errors"]),2)

    def test_acceptance_is_100_and_no_redline_compensation(self):
        self.assertIn("必须100/100且无P0/P1",self.acceptance)
        self.assertIn("不得平均抵消",self.acceptance)

    def test_real_replay_gate_blocks_production_ready(self):
        self.assertIn("3个授权真实回放未完成前不得标 production ready",self.acceptance)
        self.assertIn("controlled pilot",self.skill)

    def test_eight_output_contracts_are_unique_and_actionable(self):
        contracts=self.outputs["contracts"]
        self.assertEqual(len(contracts),8)
        self.assertEqual(len({x["type"] for x in contracts}),8)
        for item in contracts:
            self.assertGreaterEqual(len(item["required"]),5)

if __name__=="__main__": unittest.main(verbosity=2)
