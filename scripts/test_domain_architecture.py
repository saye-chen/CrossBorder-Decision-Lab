#!/usr/bin/env python3
"""Executable tests for the registry-driven modular architecture and v2 handoffs."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


architecture = load_module("domain_architecture", ROOT / "scripts/validate_domain_architecture.py")
handoff = load_module("handoff", ROOT / "governance/erdg/scripts/validate_handoff.py")
cycle = load_module("decision_cycle", ROOT / "governance/erdg/scripts/validate_decision_cycle.py")


def endpoint(domain_id: str, skill: str, availability: str) -> dict:
    return {"domain_id": domain_id, "skill": skill, "availability": availability}


def evidence_packet() -> dict:
    return {
        "message_id": "M-1",
        "message_version": "v2",
        "contract_version": "ERDG-CONTRACT-2026.07",
        "decision_cycle_id": "CYCLE-1",
        "packet_type": "evidence",
        "decision_phase": "sense",
        "source": endpoint("D02", "competitive-intelligence-monitoring", "current"),
        "target": endpoint("D01", "category-investment-decision", "current"),
        "decision_question": "Does the confirmed competitive change affect the capital posture?",
        "object_ref": {"object_id": "O-1", "object_version": "v1"},
        "runtime_versions": {
            "competitive-intelligence-monitoring": "CIM-2026.07",
            "category-investment-decision": "CIDM-2026.07"
        },
        "authority": {
            "source_authority": "competitive_intelligence",
            "target_authority": "investment",
            "ownership_transfer": False,
            "requested_response": "accept"
        },
        "evidence_refs": ["E-1"],
        "allowed_uses": ["capital_decision_support"],
        "forbidden_uses": ["rewrite_capital_decision"],
        "participant_status": "contributed",
        "gate_binding": {
            "gate_id": "G0_EVIDENCE",
            "gate_status": "passed",
            "blocking_reasons": [],
            "recovery_requirements": []
        },
        "impact": {
            "affected_domains": ["D01"],
            "affected_claims": ["C-1"],
            "preserved_results": ["C-0"],
            "recompute_scope": ["capital_posture"]
        },
        "lineage": {"input_hash": "a" * 64, "packet_hash": "b" * 64}
    }


def decision_cycle() -> dict:
    return {
        "cycle_id": "CYCLE-1",
        "cycle_version": "v2",
        "architecture_version": "CBDS-ARCH-2026.07",
        "decision_object": {
            "object_id": "O-1", "object_version": "v1", "country": "US",
            "platform": "Amazon", "category": "example"
        },
        "orchestration_mode": "sequential",
        "current_phase": "invest",
        "participants": [
            {"domain_id": "D02", "role": "evidence_provider", "availability": "current", "status": "completed"},
            {"domain_id": "D01", "role": "decision_owner", "availability": "current", "status": "completed"}
        ],
        "stages": [
            {"stage_id": "SENSE", "phase": "sense", "dependencies": [], "participant_domains": ["D02"], "status": "completed", "required_packet_types": ["evidence"]},
            {"stage_id": "INVEST", "phase": "invest", "dependencies": ["SENSE"], "participant_domains": ["D01"], "status": "completed", "required_packet_types": ["decision"]}
        ],
        "gates": [
            {"gate_id": "G0_EVIDENCE", "status": "passed", "required_stage_ids": ["SENSE"], "blocking_reasons": [], "recovery_requirements": []},
            {"gate_id": "G1_CAPITAL", "status": "passed", "required_stage_ids": ["INVEST"], "blocking_reasons": [], "recovery_requirements": []}
        ],
        "current_effective_decisions": [
            {"decision_id": "DEC-1", "owner_domain_id": "D01", "decision_type": "investment", "state": "validated", "version": "v1"}
        ],
        "lineage": {"cycle_input_hash": "a" * 64, "cycle_state_hash": "b" * 64}
    }


class DomainArchitectureTest(unittest.TestCase):
    def test_registry_schema_semantics_and_current_coverage(self):
        self.assertEqual(architecture.validate(), [])

    def test_d14_is_constrained_to_orchestration_and_owner_approved_synthesis(self):
        registry = json.loads(
            (ROOT / "governance/domain-architecture-registry.json").read_text(encoding="utf-8")
        )
        d14 = next(item for item in registry["domains"] if item["domain_id"] == "D14")
        self.assertEqual(d14["architecture_roles"], ["orchestration"])
        self.assertIn("operating_posture_synthesis", d14["owned_decision_types"])
        self.assertNotIn("company_operating_posture", d14["owned_decision_types"])
        self.assertNotIn("capital_portfolio", d14["owned_decision_types"])
        self.assertIn("accept_only_owner_approved_decisions", d14["orchestration_constraints"])
        self.assertIn("sequence_only_within_approved_envelopes", d14["orchestration_constraints"])
        self.assertIn(
            "escalate_conflicts_without_adjudicating_professional_conclusions",
            d14["orchestration_constraints"],
        )
        self.assertFalse(d14["external_write_authority"])

    def test_current_v2_evidence_handoff_is_accepted(self):
        self.assertEqual(handoff.validate(evidence_packet()), [])

    def test_planned_domain_cannot_execute(self):
        payload = evidence_packet()
        payload["target"] = endpoint(
            "D14", "cross-domain-operating-posture-orchestration", "planned"
        )
        payload["authority"]["target_authority"] = "task_orchestration"
        failures = handoff.validate(payload)
        self.assertTrue(any("planned" in failure and "cannot execute" in failure for failure in failures), failures)

    def test_next_build_domain_cannot_execute(self):
        plan = ROOT / "governance/next-build/d05-ltma.md"
        self.assertTrue(plan.is_file())
        plan_text = plan.read_text(encoding="utf-8")
        for marker in ("next_build", "fail closed", "不得把本文件注册为可调用 Skill"):
            self.assertIn(marker, plan_text)
        payload = evidence_packet()
        payload["target"] = endpoint(
            "D05", "legal-tax-intellectual-property-market-access-decision", "next_build"
        )
        payload["authority"]["target_authority"] = "legal_access"
        failures = handoff.validate(payload)
        self.assertTrue(any("next_build" in failure and "cannot execute" in failure for failure in failures), failures)

    def test_action_request_requires_passed_g4(self):
        payload = evidence_packet()
        payload["packet_type"] = "action_request"
        payload["decision_phase"] = "launch"
        payload["source"] = endpoint("D08", "platform-store-listing-conversion", "current")
        payload["target"] = endpoint("D09", "advertising-analysis-measurement-optimization", "current")
        payload["authority"] = {
            "source_authority": "listing_conversion",
            "target_authority": "advertising",
            "ownership_transfer": False,
            "requested_response": "accept"
        }
        payload["gate_binding"] = {
            "gate_id": "G4_ACTION_QUALIFICATION",
            "gate_status": "not_evaluated",
            "blocking_reasons": [],
            "recovery_requirements": []
        }
        failures = handoff.validate(payload)
        self.assertIn("action_request requires passed G4_ACTION_QUALIFICATION", failures)

    def test_handoff_rejects_missing_runtime_overlap_and_self_dependency(self):
        payload = evidence_packet()
        payload["runtime_versions"].pop("category-investment-decision")
        payload["forbidden_uses"] = ["capital_decision_support"]
        payload["prerequisite_message_ids"] = ["M-1"]
        errors = handoff.validate(payload)
        self.assertTrue(any("missing or invalid runtime version" in error for error in errors), errors)
        self.assertIn("allowed and forbidden uses overlap", errors)
        self.assertIn("handoff cannot depend on itself", errors)

    def test_decision_cycle_semantics_are_registry_driven(self):
        self.assertEqual(cycle.validate(decision_cycle()), [])

    def test_decision_cycle_rejects_wrong_owner_and_false_gate_completion(self):
        payload = decision_cycle()
        payload["current_effective_decisions"][0]["owner_domain_id"] = "D02"
        payload["stages"][1]["status"] = "running"
        errors = cycle.validate(payload)
        self.assertTrue(any("owner must be D01" in error for error in errors), errors)
        self.assertTrue(any("passed gate has incomplete stages" in error for error in errors), errors)

    def test_decision_cycle_blocks_planned_domain_execution(self):
        payload = decision_cycle()
        payload["participants"].append(
            {"domain_id": "D05", "role": "constraint_provider", "availability": "planned", "status": "running"}
        )
        payload["stages"].append(
            {"stage_id": "ACCESS", "phase": "qualify", "dependencies": ["INVEST"], "participant_domains": ["D05"], "status": "running", "required_packet_types": ["constraint"]}
        )
        errors = cycle.validate(payload)
        self.assertTrue(any("unavailable domain cannot execute" in error for error in errors), errors)
        self.assertTrue(any("stage cannot execute unavailable domains" in error for error in errors), errors)

    def test_registry_is_source_for_owner_and_version_maps(self):
        compat = load_module(
            "domain_contract",
            ROOT / "governance/erdg/scripts/validate_domain_contract.py"
        )
        registry = json.loads(
            (ROOT / "governance/domain-architecture-registry.json").read_text(encoding="utf-8")
        )
        current = {item["skill"] for item in registry["domains"] if item["availability"] == "current"}
        self.assertEqual(compat.SKILLS, current)
        self.assertEqual(compat.OWNERS["investment"], "category-investment-decision")
        self.assertEqual(compat.VERSION_PREFIX["product-innovation-product-management"], "PIPM")
        self.assertEqual(
            compat.OWNERS["supplier_selection"],
            "supplier-procurement-production-quality-decision"
        )
        self.assertNotIn("legal_access", compat.OWNERS)
        self.assertEqual(
            compat.REGISTERED_OWNERS["supplier_selection"],
            "supplier-procurement-production-quality-decision"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
