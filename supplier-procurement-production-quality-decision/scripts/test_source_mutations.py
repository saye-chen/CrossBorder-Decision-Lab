#!/usr/bin/env python3
"""Small, deterministic source-mutation suite for D04's release-critical guards."""
from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def mutant(filename, old, new):
    path = ROOT / "scripts" / filename
    source = path.read_text()
    if source.count(old) != 1:
        raise AssertionError(f"mutation target must occur exactly once: {filename}:{old}")
    namespace = {"__file__": str(path), "__name__": f"mutant_{filename}"}
    exec(compile(source.replace(old, new), str(path), "exec"), namespace)
    return namespace


def decision():
    return {
        "runtime_version": "SPPQ-2026.07",
        "erdg_contract": "ERDG-CONTRACT-2026.07",
        "decision_id": "D1",
        "decision_type": "production_release",
        "decision_owner": "supplier-procurement-production-quality-decision",
        "object": {"object_id": "O", "object_version": "v1", "as_of_time": "2026-07-29T00:00:00+08:00"},
        "status": "validated",
        "evidence": [{"id": "E"}],
        "calculations": [],
        "gates": {"identity": True, "sovereignty": True, "version": True, "evidence": True, "segregation": True, "external_action": False, "compliance": "passed"},
        "lineage": {"input_hash": "a" * 64, "output_hash": "b" * 64},
        "external_write": False,
        "production_ready": False,
    }


class SourceMutations(unittest.TestCase):
    def test_owner_guard_mutant_is_killed(self):
        module = mutant("validate_decision_contract.py", 'errors.append("decision_owner_mismatch")', 'errors.append("decision_owner_mismatch") if False else None')
        row = {**decision(), "mode": "single", "professional_core": {}, "runtime_versions": {"supplier-procurement-production-quality-decision": "SPPQ-2026.07"}}
        row["decision_owner"] = "D03"
        self.assertNotIn("decision_owner_mismatch", module["validate"](row))

    def test_compliance_guard_mutant_is_killed(self):
        module = mutant("validate_decision_contract.py", 'if d.get("decision_type") in COMPLIANCE_REQUIRED and', 'if False and d.get("decision_type") in COMPLIANCE_REQUIRED and')
        row = decision()
        row["gates"]["compliance"] = "blocked"
        self.assertNotIn("compliance_gate_required", module["validate"](row))

    def test_segregation_guard_mutant_is_killed(self):
        module = mutant("validate_decision_contract.py", '("identity","sovereignty","version","evidence","segregation")', '("identity","sovereignty","version","evidence")')
        row = decision()
        row["gates"]["segregation"] = False
        self.assertNotIn("validated_requires_segregation", module["validate"](row))

    def test_critical_defect_mutant_is_killed(self):
        module = mutant("sppq_core.py", 'if int(d.get("critical_defects",0))>0:', 'if False and int(d.get("critical_defects",0))>0:')
        self.assertNotIn("critical_defect", module["scenario_gate"]({"critical_defects": 1})["failures"])

    def test_correlated_source_mutant_is_killed(self):
        module = mutant("sppq_core.py", '("sources_independent","correlated_supply_sources"),', '')
        self.assertNotIn("correlated_supply_sources", module["scenario_gate"]({"sources_independent": False})["failures"])

    def test_reality_recovery_mutant_is_killed(self):
        module = mutant("update_continuous_decision.py", 'if affected_actions:', 'if False and affected_actions:')
        state = {"object_id":"O","current_version": "v1", "current_effective_decision": {"id": "old"}, "history": [], "open_gates": [], "active_actions": [{"action_id": "A", "status": "shipped", "depends_on": ["spec"]}],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
        result = module["update"]({"object_id":"O","expected_version":"v1","delta_type": "Rebase", "state": state, "new_version": "v2", "new_decision": {"id": "new"}, "changed_fields": ["spec"], "all_fields": ["spec"], "impact_map": {}})
        self.assertNotIn("REALITY_RECOVERY", result["open_gates"])

    def test_executable_binding_mutant_is_killed(self):
        module = mutant("validate_evaluation_catalog.py", 'if any(not x.get("executable")', 'if False and any(not x.get("executable")')
        import json
        catalog = json.loads((ROOT / "evaluations/evaluation-catalog.json").read_text())
        catalog["cases"][0].pop("executable")
        self.assertNotIn("every_case_must_be_executable", module["validate"](catalog))

    def test_report_gate_consistency_mutant_is_killed(self):
        module=mutant("validate_professional_report.py","if failed:","if False and failed:")
        row=json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"][0]
        for gate in row["hard_gates"]:gate["status"]="blocked"
        self.assertFalse(any("validated_with_unpassed_gates" in error for error in module["validate"](row)))

    def test_local_trend_mutant_is_killed(self):
        module=mutant("sppq_core.py","trend=bool(trend_windows)","trend=False")
        values=[10,10.1,9.9,10,10,10.01,10.02,10.03,10.04,10.05,10,10.1,9.9,10]
        self.assertTrue(module["process_stability"]({"values":values,"max_range":.3})["stable"])

    def test_tail_probability_mutant_is_killed(self):
        module=mutant("sppq_core.py",'if mode=="mutually_exclusive":require(all(total<=1 for total in probability_by_group.values()),"mutually_exclusive_probability_exceeds_one")','if False and mode=="mutually_exclusive":require(all(total<=1 for total in probability_by_group.values()),"mutually_exclusive_probability_exceeds_one")')
        payload={"currency":"USD","unit":"piece","as_of_time":"2026-07-29T00:00:00Z","d06_inputs_accepted":True,"d07_inputs_accepted":True,"purchase":100,"inspection":1,"quality_failure":1,"delay":1,"switch_exit":1,"tail_event_mode":"mutually_exclusive","tail_events":[{"event_id":"a","group":"incident","probability":.8,"loss":10},{"event_id":"b","group":"incident","probability":.8,"loss":10}]}
        self.assertGreater(module["total_cost_of_ownership"](payload)["expected_tail_loss"],"0")

    def test_required_model_mutant_is_killed(self):
        module=mutant("decision_engines.py","if model not in inputs:","if False and model not in inputs:")
        result=module["decide"]("supplier_selection",{"evidence_bindings":[]})
        self.assertNotIn("missing_model_input:capacity",result["failures"])

    def test_cross_field_subset_mutant_is_killed(self):
        module=mutant("validate_cross_domain_envelope.py","if not accepted.issubset(requested):","if False and not accepted.issubset(requested):")
        payload={"message_id":"M","source_domain":"D04","target_domain":"D07","object_id":"O","object_version":"v1","as_of_time":"2026-07-29T00:00:00Z","authority":"supplier_quality","allowed_uses":["support"],"forbidden_uses":["rewrite"],"requested_fields":["a"],"consumer_response":"partially_accepted","accepted_fields":["b"],"rejection_reasons":[],"lineage":{"input_hash":"a"*64,"packet_hash":"b"*64}}
        self.assertNotIn("accepted_fields_not_requested",module["validate"](payload))

    def test_expected_version_mutant_is_killed(self):
        module=mutant("update_continuous_decision.py",'if d.get("expected_version")!=state.get("current_version"):raise ValueError("stale_or_concurrent_version")','if False and d.get("expected_version")!=state.get("current_version"):raise ValueError("stale_or_concurrent_version")')
        state={"object_id":"O","current_version":"v2","current_effective_decision":{"id":"old"},"history":[],"open_gates":[],"active_actions":[],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
        result=module["update"]({"object_id":"O","expected_version":"v1","delta_type":"Revision","state":state,"new_version":"v3","new_decision":{"id":"new"},"changed_fields":[],"all_fields":[],"impact_map":{}})
        self.assertEqual(result["current_version"],"v3")


if __name__ == "__main__":
    unittest.main(verbosity=2)
