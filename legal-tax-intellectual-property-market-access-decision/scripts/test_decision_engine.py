#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location("engine",ROOT/"scripts/decision_engine.py"); engine=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(engine)

class DecisionEngineTest(unittest.TestCase):
    def test_redline_is_non_compensatory(self):
        result=engine.evaluate_gate(redlines=["major_safety_risk"],evidence_gaps=[],professional_reviews=[],requested_action="external_commercial_action")
        self.assertEqual(result["status"],"blocked"); self.assertEqual(result["action_ceiling"],"collect_evidence")
    def test_gaps_and_professional_review_cap_actions(self):
        self.assertEqual(engine.evaluate_gate(redlines=[],evidence_gaps=["certificate"],professional_reviews=[],requested_action="external_commercial_action")["status"],"evidence_required")
        self.assertEqual(engine.evaluate_gate(redlines=[],evidence_gaps=[],professional_reviews=["tax"],requested_action="external_commercial_action")["status"],"professional_review")
    def test_staging_never_allows_external_action(self):
        result=engine.evaluate_gate(redlines=[],evidence_gaps=[],professional_reviews=[],requested_action="external_commercial_action",staging=True)
        self.assertEqual(result["action_ceiling"],"reversible_preparation")
    def test_impact_closure_is_selective(self):
        graph={"material":["certificate","claim"],"certificate":["market_gate"],"price":["margin"]}
        result=engine.impact_closure(["material"],graph)
        self.assertEqual(result["affected"],["certificate","claim","market_gate","material"]); self.assertEqual(result["preserved"],["margin","price"])
    def test_incident_requires_freeze_and_recheck(self):
        self.assertTrue(engine.validate_incident_transition("detected","triaged",affected_actions=["sale"],frozen_actions=[]))
        self.assertEqual(engine.validate_incident_transition("detected","triaged",affected_actions=["sale"],frozen_actions=["sale"]),[])
        errors=engine.validate_incident_transition("recovery_review","recovered",affected_actions=[],frozen_actions=[],root_cause="expired cert",recovery_conditions=["new cert"],professional_recheck=[])
        self.assertTrue(errors)

if __name__=="__main__": unittest.main(verbosity=2)
