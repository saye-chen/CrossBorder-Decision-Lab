#!/usr/bin/env python3
"""Adversarial regression tests for unbounded progressive report evolution."""
from __future__ import annotations
import copy, importlib.util, json, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
def load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py"); mod = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod
lineage = load("validate_report_lineage"); impact = load("analyze_report_delta"); state_builder = load("build_current_decision_state")

DEPTH = {"decisive_modules":10,"evidence_count":5,"counterevidence_count":2,"assumption_count":3,"calculation_count":1,"action_contract_count":1}

def action(status="planned", aid="A1"):
    return {"action_id":aid,"status":status,"owner":"owner","deadline":"2026-08-01","success":"pass","stop":"stop","rollback":"rollback"}

def report(rid="R1", status="current", parents=None, change="Revision", obj="O1"):
    return {"report_id":rid,"report_version":"v1","object_id":obj,"parent_report_ids":parents or [],"runtime_version":"CIDM-2026.07",
            "evidence_cutoff":"2026-07-17","information_state":f"hash-{rid}","status":status,"change_class":change,
            "impact_set":{"recalculate":[],"review":["risk"],"inherit":["market"],"unaffected":[]},
            "transition_matrix":[{"item":"conclusion","state":"confirmed"}],"modules":{"market":"complete"},
            "actions":[action()],"calculations":[],"changed_inputs":[],"required_calculation_ids":[],"depth_metrics":dict(DEPTH),
            "effective_conclusion":"Test"}

def bundle():
    return {"objects":[{"object_id":"O1","kind":"product-market"}],"reports":[report()],
            "current_states":[{"object_id":"O1","current_report_id":"R1","active_action_ids":["A1"],"pending_gate_ids":["G1"],"missing_data":["cost"],"stop_conditions":["redline"]}]}

class LineageAdversarialTests(unittest.TestCase):
    def assertBlocked(self, data, phrase): self.assertTrue(any(phrase in e for e in lineage.validate(data)), lineage.validate(data))
    def test_valid_single_object(self): self.assertEqual(lineage.validate(bundle()), [])
    def test_two_current_reports_same_object_blocked(self):
        b=bundle(); b["reports"].append(report("R2")); self.assertBlocked(b,"exactly one current")
    def test_parent_cycle_blocked(self):
        b=bundle(); b["reports"][0]["parent_report_ids"]=["R2"]; b["reports"].append(report("R2","historical",["R1"])); b["reports"][1]["actions"]=[]; self.assertBlocked(b,"cycle")
    def test_unknown_parent_blocked(self):
        b=bundle(); b["reports"][0]["parent_report_ids"]=["missing"]; self.assertBlocked(b,"unknown parent")
    def test_merge_without_conflict_resolution_blocked(self):
        b=bundle(); b["reports"]=[report("P1","historical"),report("P2","historical"),report("R3","current",["P1","P2"],"Consolidation")]
        b["reports"][0]["actions"]=[]; b["reports"][1]["actions"]=[]; b["current_states"][0]["current_report_id"]="R3"; self.assertBlocked(b,"conflict_resolution")
    def test_new_object_cannot_inherit_conclusion(self):
        b=bundle(); b["objects"].append({"object_id":"O2","kind":"country","parent_object_id":"O1"}); r=report("R2","current",["R1"],"New Decision Object","O2"); r["inherited_conclusion_ids"]=["C1"]; b["reports"].append(r); b["current_states"].append({"object_id":"O2","current_report_id":"R2","active_action_ids":["A1"],"pending_gate_ids":[],"missing_data":[],"stop_conditions":["stop"]}); self.assertBlocked(b,"cannot inherit conclusions")
    def test_changed_input_without_recalculation_blocked(self):
        b=bundle(); r=b["reports"][0]; r["change_class"]="Recalculation"; r["changed_inputs"]=["price.sale"]; self.assertBlocked(b,"lack complete required calculations")
    def test_fake_artifact_hash_blocked(self):
        b=bundle(); r=b["reports"][0]; r["change_class"]="Recalculation"; r["changed_inputs"]=["price.sale"]; r["required_calculation_ids"]=["C1"]; r["calculations"]=[{"id":"C1","calculator":"x","input_hash":"deadbeef","output_hash":"deadbeef","status":"complete","input_file":"in.json","output_file":"out.json"}]
        with tempfile.TemporaryDirectory() as td:
            Path(td,"in.json").write_text("{}",encoding="utf-8"); Path(td,"out.json").write_text("{}",encoding="utf-8"); self.assertTrue(any("hash mismatch" in e for e in lineage.validate(b,Path(td))))
    def test_committed_revocation_requires_recovery_economics(self):
        b=bundle(); a=b["reports"][0]["actions"][0]; a.update(status="revoked",previous_status="committed"); b["current_states"][0]["active_action_ids"]=[]; self.assertBlocked(b,"recovery_plan")
    def test_irreversible_action_recovery_can_pass(self):
        b=bundle(); a=b["reports"][0]["actions"][0]; a.update(status="recovery_required",previous_status="irreversible",recovery_plan="liquidate",recoverable_cost=10,sunk_cost=5); self.assertEqual(lineage.validate(b),[])
    def test_superseded_active_action_without_transition_blocked(self):
        b=bundle(); old=report("R0","superseded"); new=report("R1","current",["R0"],"Rebase"); new["actions"]=[]; b["reports"]=[old,new]; b["current_states"][0]["active_action_ids"]=[]; self.assertBlocked(b,"leaves active actions")
    def test_depth_regression_blocked(self):
        b=bundle(); old=report("R0","historical"); old["actions"]=[]; new=report("R1","current",["R0"],"Rebase"); new["depth_metrics"]["counterevidence_count"]=1; b["reports"]=[old,new]; self.assertBlocked(b,"regresses depth")
    def test_depth_reduction_requires_explicit_justification(self):
        b=bundle(); old=report("R0","historical"); old["actions"]=[]; new=report("R1","current",["R0"],"Rebase"); new["depth_metrics"]["counterevidence_count"]=1; new["depth_reduction_justifications"]={"counterevidence_count":"duplicate evidence removed with lineage"}; b["reports"]=[old,new]; self.assertEqual(lineage.validate(b),[])
    def test_state_pointer_mismatch_blocked(self):
        b=bundle(); b["current_states"][0]["current_report_id"]="missing"; self.assertBlocked(b,"wrong report")
    def test_old_version_cannot_be_restored_directly(self):
        b=bundle(); old=report("R0","current"); new=report("R1","historical",["R0"],"Rebase"); old["actions"]=[]; new["actions"]=[]; b["reports"]=[old,new]; b["current_states"][0]["current_report_id"]="R0"; b["current_states"][0]["active_action_ids"]=[]; self.assertBlocked(b,"cannot be restored")
    def test_active_action_state_mismatch_blocked(self):
        b=bundle(); b["current_states"][0]["active_action_ids"]=[]; self.assertBlocked(b,"active actions")
    def test_conflicting_user_update_is_not_auto_confirmed(self):
        b=bundle(); b["reports"][0]["evidence_deltas"]=[{"state":"conflicting","effective_now":True}]
        self.assertBlocked(b,"non-confirmed evidence delta")
    def test_expired_dynamic_fact_cannot_support_current(self):
        b=bundle(); b["reports"][0]["dynamic_facts"]=[{"fact_id":"F1","verified_at":"2026-01-01","valid_until":"2026-02-01","supports_current":True}]
        self.assertBlocked(b,"expired dynamic fact")
    def test_resource_loss_requires_current_recalculation(self):
        b=bundle(); r=b["reports"][0]; r["change_class"]="Rebase"; r["changed_inputs"]=["seller.resources"]; self.assertBlocked(b,"lack complete required calculations")
    def test_three_incremental_deltas_require_consolidation(self):
        b=bundle(); b["reports"][0]["information_deltas"]=[{"class":"Addendum"},{"class":"Revision"},{"class":"Addendum"}]; self.assertBlocked(b,"requires Consolidation")
    def test_multiple_objects_each_may_have_one_current(self):
        b=bundle(); b["objects"].append({"object_id":"O2","kind":"country","parent_object_id":"O1"}); b["reports"].append(report("R2","current",change="New Decision Object",obj="O2")); b["current_states"].append({"object_id":"O2","current_report_id":"R2","active_action_ids":["A1"],"pending_gate_ids":[],"missing_data":[],"stop_conditions":["stop"]}); self.assertEqual(lineage.validate(b),[])
    def test_state_builder_returns_authoritative_snapshot(self):
        result=state_builder.build(bundle(),Path.cwd()); self.assertEqual(result["status"],"PASS"); self.assertEqual(result["current_states"][0]["effective_conclusion"],"Test")

class ImpactGraphTests(unittest.TestCase):
    def test_packaging_change_reaches_profit_and_action(self):
        result=impact.analyze(["packaging.dimensions"]); self.assertEqual(result["status"],"PASS"); self.assertIn("economics",result["required_modules"]); self.assertIn("action_plan",result["required_modules"])
    def test_unknown_delta_field_blocks(self): self.assertEqual(impact.analyze(["strange.new.logic"])["status"],"BLOCKED")
    def test_country_change_creates_object_and_localization_review(self):
        result=impact.analyze(["country.target"]); self.assertIn("object_boundary",result["required_modules"]); self.assertIn("localization",result["required_modules"])
    def test_supplier_change_reaches_cash_profit_inventory_and_actions(self):
        result=impact.analyze(["supplier.identity"]); self.assertIn("economics",result["required_modules"]); self.assertIn("capital_and_inventory",result["required_modules"]); self.assertIn("action_plan",result["required_modules"])
    def test_strategy_change_rebuilds_object_metrics_and_actions(self):
        result=impact.analyze(["strategic.objective"]); self.assertIn("object_boundary",result["required_modules"]); self.assertIn("action_plan",result["required_modules"])
    def test_account_change_reaches_gates_and_capital(self):
        result=impact.analyze(["account.status"]); self.assertIn("capital_and_inventory",result["required_modules"]); self.assertIn("action_plan",result["required_modules"])
    def test_lifecycle_change_reaches_capital_and_actions(self):
        result=impact.analyze(["lifecycle.stage"]); self.assertIn("capital_and_inventory",result["required_modules"]); self.assertIn("action_plan",result["required_modules"])
    def test_customer_value_change_reaches_advertising_and_capital(self):
        result=impact.analyze(["customer.clv"]); self.assertIn("capital_and_inventory",result["required_modules"]); self.assertIn("economics",result["required_modules"])

if __name__ == "__main__": unittest.main(verbosity=2)
