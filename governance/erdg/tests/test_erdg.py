#!/usr/bin/env python3
"""ERDG Golden, adversarial, property, adapter and v2 architecture tests."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest
from decimal import Decimal

ROOT = pathlib.Path(__file__).resolve().parents[3]
ERDG_DIR = ROOT / "governance/erdg"
SCRIPTS = ERDG_DIR / "scripts"
FIXTURES = ERDG_DIR / "tests/fixtures"
EXPECTED_SKILLS = {
    "category-investment-decision", "competitive-intelligence-monitoring", "video-link-breakdown",
    "consumer-insights-customer-growth", "advertising-analysis-measurement-optimization",
    "logistics-inventory-fulfillment-decision", "platform-store-listing-conversion",
    "creator-affiliate-partnership-management", "marketing-brand-campaign-management",
    "pricing-profit-finance-cashflow-decision",
    "product-innovation-product-management",
    "supplier-procurement-production-quality-decision",
}
sys.path.insert(0, str(SCRIPTS))


def load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"erdg_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ERDGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.common = load("erdg_common")
        cls.economics = load("calculate_economic_layers")
        cls.cash = load("calculate_cash_flow")
        cls.risk = load("evaluate_risk_and_redlines")
        cls.states = load("validate_state_transition")
        cls.parameters = load("resolve_parameters")
        cls.units = load("validate_units_currency_tax_time")
        cls.impact = load("compute_impact_closure")
        cls.depth = load("validate_erdg_depth")
        cls.recomputation = load("validate_report_recomputation")
        cls.capacity = load("validate_erdg_capacity")
        cls.schema_validator = load("validate_schema_instance")
        cls.contract = load("validate_contract")
        cls.compat = load("validate_domain_contract")

    def test_01_contract_version_keeps_l4_closed(self):
        version = json.loads((ERDG_DIR / "contract-version.json").read_text())
        self.assertEqual(version["runtime"], "ERDG-2026.07")
        self.assertEqual(version["contract"], "ERDG-CONTRACT-2026.07")
        self.assertEqual(version["schema_version"], "2.0.0")
        self.assertFalse(version["production_ready"])
        self.assertEqual(version["l4"], "not_passed")
        self.assertEqual(version["external_write"], "forbidden")

    def test_02_all_normative_schemas_validate_their_meta_schema(self):
        schemas = sorted((ERDG_DIR / "schemas").glob("*.schema.json"))
        self.assertGreaterEqual(len(schemas), 13)
        for path in schemas:
            schema = json.loads(path.read_text())
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema", path)
            self.assertTrue(schema["$id"].startswith("erdg/"), path)
            self.assertEqual(schema["type"], "object", path)
            self.assertIsInstance(schema.get("properties"), dict, path)

    def test_03_all_registered_adapters_are_non_writing(self):
        adapters = {path.parent.name: json.loads(path.read_text()) for path in (ERDG_DIR / "adapters").glob("*/adapter.json")}
        self.assertEqual(set(adapters), EXPECTED_SKILLS)
        for skill, adapter in adapters.items():
            self.assertEqual(adapter["version"], "2.0.0", skill)
            self.assertEqual(adapter["contract"], "ERDG-CONTRACT-2026.07", skill)
            self.assertEqual(adapter["handoff_schema"], "governance/erdg/schemas/handoff-envelope.schema.json", skill)
            self.assertEqual(adapter["decision_cycle_schema"], "governance/erdg/schemas/decision-cycle.schema.json", skill)
            self.assertFalse(adapter["accepts_v1"], skill)
            self.assertFalse(adapter["external_write"], skill)
            self.assertTrue(adapter["owned_decision_types"], skill)

    def test_04_economic_golden_is_exact_and_layered(self):
        payload = json.loads((FIXTURES / "economics.json").read_text())
        result = self.economics.calculate(payload)
        self.assertEqual(result["layers_exact"], {
            "E0": "1000", "E1": "920", "E2": "600", "E3": "530",
            "E4": "430", "E5": "280", "E6": "270", "E7": "265", "E8": "165",
        })
        self.assertTrue(result["average_marginal_separated"])

    def test_05_economic_float_missing_and_unknown_fields_fail_closed(self):
        base = json.loads((FIXTURES / "economics.json").read_text())
        for mutate in (
            lambda p: p["amounts"].update(gross_sales=1.1),
            lambda p: p["amounts"].pop("gross_sales"),
            lambda p: p["amounts"].update(unknown_cost="1"),
            lambda p: p.pop("cash_bridge"),
        ):
            payload = json.loads(json.dumps(base))
            mutate(payload)
            with self.assertRaises(ValueError):
                self.economics.calculate(payload)

    def test_06_decimal_additivity_property(self):
        for gross in ("0", "1", "99.99", "1000000000000.01"):
            payload = {"currency": "USD", "tax_basis": "tax_exclusive", "economic_mode": "average", "amounts": {"gross_sales": gross}}
            result = self.economics.calculate(payload)
            self.assertTrue(all(Decimal(value) == Decimal(gross) for value in result["layers_exact"].values()))

    def test_07_cash_golden_preserves_timing_and_peak_funding(self):
        result = self.cash.calculate(json.loads((FIXTURES / "cash-flow.json").read_text()))
        self.assertEqual(result["ending_cash"], "250")
        self.assertEqual(result["minimum_cash"], "-150")
        self.assertEqual(result["peak_funding_required"], "150")

    def test_08_redline_cannot_be_compensated(self):
        result = self.risk.evaluate({"risks": [
            {"risk_id": "R1", "risk_type": "safety", "redline": True, "status": "open"},
            {"risk_id": "R2", "risk_type": "demand", "redline": False, "status": "open", "probability": "0.5", "impact": "100"},
        ]})
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["blocked_redlines"], ["R1"])
        self.assertTrue(result["redlines_not_compensated"])

    def test_09_unknown_risk_probability_is_not_zero(self):
        result = self.risk.evaluate({"risks": [{"risk_id": "R1", "risk_type": "demand", "redline": False, "status": "open", "probability": None, "impact": "100"}]})
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["unknown_probability"], ["R1"])
        with self.assertRaises(ValueError):
            self.risk.evaluate({"risks": [{"risk_id": "R2", "risk_type": "demand", "redline": False, "status": "open", "probability": "0.5", "impact": "-1"}]})

    def test_10_four_state_machines_allow_and_reject_independently(self):
        base = {"actor": "owner", "occurred_at": "2026-07-27T00:00:00Z", "reason": "review", "input_version": "v1"}
        valid = [
            {"machine": "claim", "from": "proposed", "to": "validated"},
            {"machine": "decision", "from": "review", "to": "approved"},
            {"machine": "action", "from": "planned", "to": "approved", "approved_decision_id": "D1"},
            {"machine": "replay", "from": "replayed", "to": "independently_reviewed"},
        ]
        for transition in valid:
            self.assertEqual(self.states.validate({**base, **transition}), [])
        self.assertTrue(self.states.validate({**base, "machine": "decision", "from": "draft", "to": "effective"}))
        self.assertTrue(self.states.validate({**base, "machine": "action", "from": "planned", "to": "approved"}))

    def test_11_parameter_resolution_preserves_redline_and_controls_override(self):
        base = {
            "parameter_id": "P1", "as_of_time": "2026-07-27T00:00:00+00:00",
            "context": {"country": "US", "platform": "Amazon", "category": "x", "lifecycle": "test"},
        }
        redline = {"parameter_id": "P1", "parameter_type": "redline", "owner_domain": "repo", "value_or_formula": True, "scope": "global", "effective_from": "2026-01-01T00:00:00+00:00", "version": "1.0.0", "calibration_status": "default", "approval": {"status": "approved"}}
        result = self.parameters.resolve({**base, "parameters": [redline]})
        self.assertEqual(result["reason"], "non_relaxable_global_redline")
        override = {**redline, "parameter_type": "threshold", "scope": "policy_override", "effective_to": "2026-08-01T00:00:00+00:00"}
        with self.assertRaises(ValueError):
            self.parameters.resolve({**base, "parameters": [override]})
        unqualified_specific = {**redline, "parameter_type": "threshold", "scope": "combination", "calibration_status": "synthetic", "country": "US"}
        self.assertEqual(self.parameters.resolve({**base, "parameters": [unqualified_specific]})["status"], "inconclusive")

    def test_12_canonical_hash_is_order_and_unicode_stable_and_rejects_float(self):
        left = {"b": "e\u0301", "a": ["1.00", 2]}
        right = {"a": ["1.00", 2], "b": "é"}
        self.assertEqual(self.common.sha256_payload(left), self.common.sha256_payload(right))
        with self.assertRaises(ValueError):
            self.common.sha256_payload({"amount": 0.1})

    def test_13_authoritative_validator_matches_compatibility_validator(self):
        payload = json.loads((FIXTURES / "domain-contract.json").read_text())
        self.assertEqual(self.compat.validate(payload), [])
        self.assertEqual(self.contract.validate(payload), [])
        unsafe = {**payload, "production_ready": True}
        self.assertEqual(self.compat.validate(unsafe), [])
        self.assertIn("ERDG production_ready cannot be asserted by a decision payload", self.contract.validate(unsafe))

    def test_14_root_and_legacy_entrypoints_route_to_erdg(self):
        fixture = FIXTURES / "domain-contract.json"
        for script in (ROOT / "scripts/validate_decision_contract.py", ROOT / "category-investment-decision/scripts/validate_decision_contract.py"):
            result = subprocess.run([sys.executable, str(script), str(fixture)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, (script, result.stdout, result.stderr))
            self.assertIn("ERDG decision contract", result.stdout)

    def test_15_v2_is_the_only_shared_handoff_runtime(self):
        self.assertFalse((ERDG_DIR / "migration-manifest.json").exists())
        self.assertFalse((SCRIPTS / "migrate_contract.py").exists())
        self.assertFalse((ERDG_DIR / "schemas/handoff-envelope-v2.schema.json").exists())
        schema = json.loads((ERDG_DIR / "schemas/handoff-envelope.schema.json").read_text())
        self.assertEqual(schema["properties"]["message_version"]["const"], "v2")
        self.assertEqual(schema["properties"]["contract_version"]["const"], "ERDG-CONTRACT-2026.07")

    def test_16_parameter_registry_contains_no_production_thresholds(self):
        registry = json.loads((ERDG_DIR / "parameter-registry.json").read_text())
        self.assertEqual(registry["production_thresholds"], [])
        self.assertEqual(registry["parameters"][0]["parameter_type"], "redline")

    def test_17_approved_requirements_have_evidence_tests_and_only_l4_is_external(self):
        manifest = json.loads((ERDG_DIR / "implementation-manifest.json").read_text())
        self.assertEqual([item["id"] for item in manifest["requirements"][:18]], [f"R{i:02d}" for i in range(1, 19)])
        self.assertEqual(
            [item["id"] for item in manifest["requirements"][18:]],
            [
                "ERDG-XDEPTH",
                "ERDG-XINTEGRATION",
                "ERDG-XSCHEMA",
                "ERDG-XRECOMPUTE",
                "ERDG-XCAPACITY",
                "ERDG-XREGISTRY",
                "ERDG-XHANDOFFV2",
            ],
        )
        for item in manifest["requirements"]:
            self.assertTrue(item["evidence"], item)
            self.assertTrue(item["tests"], item)
            for relative in item["evidence"] + item["tests"]:
                self.assertTrue((ROOT / relative).exists(), relative)
        external = [item["id"] for item in manifest["requirements"] if item["status"] == "controlled_external_gate"]
        self.assertEqual(external, ["R18"])
        self.assertEqual(manifest["summary"], {"fixed": 24, "controlled_external_gate": 1, "partial": 0, "missing": 0})
        self.assertFalse(manifest["production_ready"])

    def test_18_unit_currency_tax_and_time_conflicts_fail_closed(self):
        quantity = {
            "value": "10.00", "unit": "currency", "currency": "USD", "tax_basis": "tax_exclusive",
            "as_of_time": "2026-07-27T00:00:00Z",
            "effective_window": {"start": "2026-07-01T00:00:00Z", "end": "2026-07-31T00:00:00Z"},
            "source": "fixture", "calculation_id": "CAL1",
        }
        self.assertEqual(self.units.validate_quantity(quantity, "q"), [])
        other = {**quantity, "currency": "EUR"}
        self.assertEqual(self.units.comparable(quantity, other), ["incompatible currency"])
        self.assertTrue(self.units.validate_quantity({**quantity, "value": 0.1}, "q"))

    def test_19_selective_recomputation_and_cycle_rejection(self):
        base = {
            "nodes": [{"id": "evidence"}, {"id": "calculation"}, {"id": "claim"}, {"id": "decision"}, {"id": "unrelated"}],
            "edges": [{"from": "evidence", "to": "calculation"}, {"from": "calculation", "to": "claim"}, {"from": "claim", "to": "decision"}],
            "changed_ids": ["calculation"],
        }
        result = self.impact.compute(base)
        self.assertEqual(result["affected_ids"], ["calculation", "claim", "decision"])
        self.assertIn("unrelated", result["unaffected_ids"])
        with self.assertRaises(ValueError):
            self.impact.compute({**base, "edges": base["edges"] + [{"from": "decision", "to": "calculation"}]})

    def test_20_v1_contract_and_missing_contract_fail_closed(self):
        payload = json.loads((FIXTURES / "domain-contract.json").read_text())
        missing = dict(payload)
        missing.pop("erdg_contract")
        self.assertIn("erdg_contract must be ERDG-CONTRACT-2026.07", self.contract.validate(missing))
        retired = {**payload, "erdg_contract": "ERDG-CONTRACT-2025.12"}
        self.assertIn("erdg_contract must be ERDG-CONTRACT-2026.07", self.contract.validate(retired))

    def test_21_seven_execution_modes_and_reports_have_substantive_depth(self):
        self.assertEqual(self.depth.validate(), [])

    def test_22_cash_100k_event_stress_is_exact_deterministic_and_rejects_conflict(self):
        entries = [
            {"entry_id": f"E{i}", "occurred_at": f"2026-07-{(i % 28) + 1:02d}T00:00:00+00:00", "direction": "inflow" if i % 2 == 0 else "outflow", "amount": "1.01"}
            for i in range(100000)
        ]
        payload = {"currency": "USD", "opening_cash": "0", "entries": entries}
        first = self.cash.calculate(payload)
        second = self.cash.calculate({**payload, "entries": list(reversed(entries))})
        self.assertEqual(first, second)
        self.assertEqual(first["ending_cash"], "0")
        with self.assertRaises(ValueError):
            self.cash.calculate({**payload, "entries": entries + [{**entries[0], "amount": "9.99"}]})

    def test_23_thousand_node_lineage_stress_is_selective_and_cycle_safe(self):
        nodes = [{"id": f"N{i:04d}"} for i in range(1000)]
        edges = [{"from": f"N{i:04d}", "to": f"N{i+1:04d}"} for i in range(999)]
        result = self.impact.compute({"nodes": nodes, "edges": edges, "changed_ids": ["N0900"]})
        self.assertEqual(len(result["affected_ids"]), 100)
        self.assertEqual(len(result["unaffected_ids"]), 900)
        with self.assertRaises(ValueError):
            self.impact.compute({"nodes": nodes, "edges": edges + [{"from": "N0999", "to": "N0500"}], "changed_ids": ["N0900"]})

    def test_24_state_history_is_chronological_continuous_and_single_effective(self):
        events = [
            {"from": "draft", "to": "review", "actor": "a", "occurred_at": "2026-07-01T00:00:00Z", "reason": "submit", "input_version": "v1"},
            {"from": "review", "to": "approved", "actor": "b", "occurred_at": "2026-07-02T00:00:00Z", "reason": "approve", "input_version": "v1"},
            {"from": "approved", "to": "effective", "actor": "b", "occurred_at": "2026-07-03T00:00:00Z", "reason": "activate", "input_version": "v1"},
        ]
        self.assertEqual(self.states.validate_history({"machine": "decision", "events": events}), [])
        broken = events + [{"from": "approved", "to": "effective", "actor": "c", "occurred_at": "2026-07-04T00:00:00Z", "reason": "double", "input_version": "v2"}]
        errors = self.states.validate_history({"machine": "decision", "events": broken})
        self.assertTrue(any("continuity" in error for error in errors))
        self.assertTrue(any("multiple effective" in error for error in errors))

    def test_25_all_schema_families_have_executable_valid_and_invalid_assertions(self):
        instances = {
            "canonical-object.schema.json": {"object_id": "O1", "object_type": "sku", "country": "US", "platform": "Amazon"},
            "object-version.schema.json": {"object_id": "O1", "object_version": "v1", "valid_from": "2026-01-01T00:00:00Z", "as_of_time": "2026-01-01T00:00:00Z", "attributes_hash": "a"*64, "current": True},
            "evidence.schema.json": {"evidence_id": "E1", "source_type": "authorized_first_party", "processing_status": "verified", "source_ref": "fixture", "observed_at": "2026-01-01T00:00:00Z", "fingerprint": "f"},
            "claim.schema.json": {"claim_id": "C1", "owner_domain": "owner", "object_id": "O1", "state": "validated", "grade": "descriptive", "evidence_ids": ["E1"], "allowed_uses": ["support"], "forbidden_uses": []},
            "calculation.schema.json": {"calculation_id": "CAL1", "calculator": "x", "calculator_version": "1", "input_hash": "a"*64, "output_hash": "b"*64, "status": "complete"},
            "economic-ledger.schema.json": {"currency": "USD", "tax_basis": "tax_exclusive", "as_of_time": "2026-01-01T00:00:00Z", "amounts": {"gross_sales": "1.00"}},
            "cash-flow.schema.json": {"currency": "USD", "opening_cash": "0", "entries": [{"entry_id": "E1", "occurred_at": "2026-01-01T00:00:00Z", "direction": "inflow", "amount": "1"}]},
            "risk.schema.json": {"risk_id": "R1", "risk_type": "demand", "object_id": "O1", "redline": False, "status": "open", "owner": "owner"},
            "decision.schema.json": {"decision_id": "D1", "owner_domain": "owner", "object_id": "O1", "decision_question": "q", "state": "draft", "version": "v1"},
            "action.schema.json": {"action_id": "A1", "decision_id": "D1", "object_id": "O1", "owner": "owner", "state": "planned", "external_write": False},
            "handoff-envelope.schema.json": {"message_id": "M2", "message_version": "v2", "contract_version": "ERDG-CONTRACT-2026.07", "decision_cycle_id": "C1", "packet_type": "evidence", "decision_phase": "sense", "source": {"domain_id": "D02", "skill": "competitive-intelligence-monitoring", "availability": "current"}, "target": {"domain_id": "D01", "skill": "category-investment-decision", "availability": "current"}, "decision_question": "q", "object_ref": {"object_id": "O1", "object_version": "v1"}, "runtime_versions": {"D02": "CIM-2026.07"}, "authority": {"source_authority": "competitive_intelligence", "target_authority": "investment", "ownership_transfer": False}, "allowed_uses": ["support"], "forbidden_uses": [], "participant_status": "contributed", "gate_binding": {"gate_id": "G0_EVIDENCE", "gate_status": "passed"}, "impact": {"affected_domains": ["D01"], "affected_claims": [], "preserved_results": []}, "lineage": {"input_hash": "a"*64, "packet_hash": "b"*64}},
            "decision-cycle.schema.json": {"cycle_id": "C1", "cycle_version": "v2", "architecture_version": "DARCH-2026.07", "decision_object": {"object_id": "O1", "object_version": "v1", "country": "US", "platform": "Amazon", "category": "example"}, "orchestration_mode": "sequential", "current_phase": "sense", "participants": [{"domain_id": "D02", "role": "evidence_provider", "availability": "current", "status": "contributed"}], "stages": [{"stage_id": "S1", "phase": "sense", "dependencies": [], "participant_domains": ["D02"], "status": "completed", "required_packet_types": ["evidence"]}], "gates": [{"gate_id": "G0_EVIDENCE", "status": "passed", "required_stage_ids": ["S1"], "blocking_reasons": [], "recovery_requirements": []}], "current_effective_decisions": [], "lineage": {"cycle_input_hash": "a"*64, "cycle_state_hash": "b"*64}},
            "parameter.schema.json": {"parameter_id": "P1", "parameter_type": "threshold", "owner_domain": "owner", "value_or_formula": "1", "scope": "global", "effective_from": "2026-01-01T00:00:00Z", "version": "1", "calibration_status": "default", "approval": {"status": "approved"}},
            "replay.schema.json": {"replay_id": "RP1", "state": "not_started", "input_hash": "a"*64, "result_hash": "b"*64, "authorized": False, "deidentified": True, "production_ready": False},
        }
        schemas = {path.name: json.loads(path.read_text()) for path in (ERDG_DIR / "schemas").glob("*.schema.json")}
        self.assertEqual(set(instances), set(schemas))
        for name, instance in instances.items():
            self.assertEqual(self.schema_validator.validate_instance(instance, schemas[name]), [], name)
            broken = dict(instance)
            broken.pop(schemas[name]["required"][0])
            self.assertTrue(self.schema_validator.validate_instance(broken, schemas[name]), name)
            unknown = {**instance, "misspelled_field": "must fail closed"}
            self.assertTrue(
                any("Additional properties" in error for error in self.schema_validator.validate_instance(unknown, schemas[name])),
                name,
            )

    def test_26_complete_draft_2020_12_and_format_validation_fail_closed(self):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "when": {"type": "string", "format": "date-time"},
                "choice": {"oneOf": [{"const": "a"}, {"const": "b"}]},
            },
            "required": ["when", "choice"],
            "unevaluatedProperties": False,
        }
        self.assertEqual(
            self.schema_validator.validate_instance(
                {"when": "2026-07-27T00:00:00Z", "choice": "a"}, schema
            ),
            [],
        )
        errors = self.schema_validator.validate_instance(
            {"when": "not-a-date", "choice": "c", "unexpected": True}, schema
        )
        self.assertTrue(any("date-time" in error for error in errors))
        self.assertTrue(any("not valid under any" in error for error in errors))
        self.assertTrue(any("unevaluated" in error.lower() for error in errors))

    def test_27_all_seven_reports_are_bound_to_recomputed_results(self):
        self.assertEqual(self.recomputation.validate(), [])

    def test_28_reference_capacity_and_hard_limits_pass(self):
        errors, metrics = self.capacity.validate()
        self.assertEqual(errors, [], metrics)
        self.assertFalse(metrics["production_slo_claim"])
        with self.assertRaises(ValueError):
            self.cash.calculate({"currency": "USD", "entries": [{}] * 100001})
        with self.assertRaises(ValueError):
            self.impact.compute({"nodes": [{"id": str(i)} for i in range(10001)], "edges": [], "changed_ids": []})


if __name__ == "__main__":
    unittest.main(verbosity=2)
