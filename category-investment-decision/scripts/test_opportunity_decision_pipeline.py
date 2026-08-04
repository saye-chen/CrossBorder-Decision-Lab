#!/usr/bin/env python3
import copy, json, unittest
from pathlib import Path
from opportunity_decision_pipeline import run

class PipelineTests(unittest.TestCase):
    def test_capability_matrix_is_complete_and_honest(self):
        root=Path(__file__).resolve().parents[1]
        matrix=json.loads((root/"references/opportunity-tactic-capability-matrix.json").read_text())
        self.assertEqual(len(matrix["tactics"]),17); self.assertEqual(len({x["id"] for x in matrix["tactics"]}),17)
        local=next(x for x in matrix["tactics"] if x["signal"]=="REPLICABLE_LOCAL_PREMIUM")
        self.assertEqual((local["implementation"],local["runtime_model"]),("configured_only",None))
        self.assertTrue(all(x["highest_verified_status"]!="externally_validated" for x in matrix["tactics"]))

    def test_external_templates_cannot_claim_completion(self):
        root=Path(__file__).resolve().parents[1]
        readiness=json.loads((root/"evaluations/external-validation-readiness.json").read_text())
        self.assertFalse(readiness["production_ready"]); self.assertEqual({x["status"] for x in readiness["gates"]},{"controlled_external_gate"})
    def payload(self):
        obj={"product_concept_id":"P1","category_node":"C1","country":"US","platform":"Amazon","currency":"USD"}
        data={"weekly_sales":[60]*8,"parent_first_seen":"2026-06-01","child_first_seen":"2026-07-01","parent_age_days":30,"promotion_sales":0}
        return {"raw_evidence":{"growth_pct":25},"adapter_contract":{"source":"fixture","source_family_id":"F1","raw_evidence_id":"E1","observed_at":"2026-08-01","max_age_days":3650,"fields":{"growth":{"source_field":"growth_pct","kind":"ratio","scale":"0-100"}}},"model":{"signal_type":"NEW_PRODUCT_BREAKOUT","data":data,"calibration":{"max_parent_age_days":90,"weekly_sales_floor":50,"max_promotion_contamination":"0.4","min_persistence":"0.75"}},"signal_card":{"signal_id":"S1","signal_version":"OSL-v1","decision_object":obj,"signal_type":"NEW_PRODUCT_BREAKOUT","observation_window":{"start":"2026-06-01","end":"2026-08-01"},"source_evidence_ids":["E1"],"observed_facts":["weekly continuity"],"derived_metrics":{},"assumptions":["proxy sales"],"counter_evidence":["promotion alternative"],"alternative_explanations":["brand traffic"],"quality":{"completeness":0.8},"confidence":"low","allowed_use":["candidate_generation"],"forbidden_use":["automatic_score_override","automatic_investment_action"],"validation_actions":["verify demand"],"expiry_date":"2030-01-01","status":"candidate"},"score":{"scores":{"market_demand":8,"competitive_entry":8,"profit_space":8,"content_communication":8,"supply_control":8,"risk_control":8,"opportunity_window":8}},"playbook_id":"PB-NEW-PRODUCT-01","lifecycle":"LC-1","confidence":"low","weakest_assumption":"nonbrand demand","priority_actions":["verify identity","verify demand","recompute profit"],"do_not_do_yet":["bulk order"],"minimum_credible_validation":"time-frozen test","go":["independent demand"],"stop":["negative contribution"]}
    def test_complete_chain_and_lineage(self):
        out=run(self.payload()); self.assertEqual(out["execution_completion"],"complete"); self.assertEqual(out["model"]["metrics"],out["oracle"]["metrics"]); self.assertEqual(out["decision_card"]["decision"],"建议进入"); self.assertEqual(out["maturity"],"controlled pilot")
    def test_redline_and_veto_cannot_be_compensated(self):
        p=self.payload(); p["score"]["hard_redlines"]=["compliance_ip_redline"]; self.assertEqual(run(p)["decision_card"]["decision"],"不建议进入")
        p=self.payload(); p["active_vetoes"]=["negative_contribution_profit"]; self.assertEqual(run(p)["composition"]["composition_status"],"blocked")
    def test_adapter_failure_stops_chain(self):
        p=copy.deepcopy(self.payload()); p["raw_evidence"]={}
        with self.assertRaises(ValueError): run(p)
if __name__=="__main__": unittest.main(verbosity=2)
