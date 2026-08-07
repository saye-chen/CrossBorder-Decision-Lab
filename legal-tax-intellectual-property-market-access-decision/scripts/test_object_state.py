#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_object_state.py")
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

import jsonschema


def state(previous, current, blocked=None, allowed=None):
    return {
        "contract": "D05-STATE-DRAFT-1",
        "decision_id": "D-1",
        "decision_version": "v1",
        "object_ref": "O-1@v1",
        "lifecycle_stage": "qualify",
        "state": current,
        "previous_state": previous,
        "supersedes_decision_ref": None,
        "scope_hash": "a" * 64,
        "blocked_actions": blocked or [],
        "allowed_actions": allowed or [],
        "external_write": False,
        "history_refs": [],
    }


def minimal_object(**overrides):
    obj = {
        "contract": "D05-OBJECT-DRAFT-1",
        "subject_ref": {"object_id": "OBJ-1", "object_type": "product_listing", "object_version": "v1"},
        "product_ref": {"product_id": "PROD-1", "product_version": "v1"},
        "scope_ref": {
            "jurisdiction": "US", "country": "US", "platform": "amazon",
            "sales_model": "FBA", "legal_entity_role": "seller_of_record",
            "business_time": "2026-08-01T00:00:00Z",
        },
        "use_ref": {
            "intended_use": "household cleaning", "foreseeable_misuse": ["ingestion by child"],
            "age_scope": "adult", "contact_scenarios": ["skin contact"],
        },
        "as_of_time": "2026-08-01T00:00:00Z",
    }
    obj.update(overrides)
    return obj


class TransitionCoverageTest(unittest.TestCase):
    """Every valid transition must pass; every invalid transition must fail."""

    def test_all_states_reachable_from_intake(self):
        paths = {
            "intake": [None],
            "screening": [None, "intake"],
            "evidence_required": [None, "intake"],
            "professional_review": [None, "intake", "screening"],
            "conditionally_cleared": [None, "intake", "screening"],
            "blocked": [None, "intake", "screening"],
            "withdrawn": [None, "intake"],
            "cleared_for_named_use": [None, "intake", "screening", "conditionally_cleared"],
            "suspended": [None, "intake", "screening", "conditionally_cleared", "cleared_for_named_use"],
            "remediation": [None, "intake", "screening", "blocked"],
            "expired": [None, "intake", "evidence_required"],
            "superseded": [None, "intake", "screening", "conditionally_cleared", "cleared_for_named_use"],
            "closed": [None, "intake", "screening", "blocked", "cleared_for_named_use"],
        }
        for target, path in paths.items():
            for i in range(1, len(path)):
                errors = validator.validate_transition(state(path[i - 1], path[i] if i < len(path) - 1 else target))
            final = state(path[-1], target)
            if target in {"blocked", "suspended", "expired"}:
                final["blocked_actions"] = ["some_action"]
            errors = validator.validate_transition(final)
            self.assertEqual(errors, [], f"failed to reach {target} via {path}: {errors}")

    def test_all_declared_transitions_pass(self):
        for previous, targets in validator.TRANSITIONS.items():
            for target in targets:
                s = state(previous, target)
                if target in {"blocked", "suspended", "expired"}:
                    s["blocked_actions"] = ["launch"]
                errors = validator.validate_transition(s)
                self.assertEqual(errors, [], f"valid transition {previous!r} → {target!r} rejected: {errors}")

    def test_undeclared_transitions_rejected(self):
        all_states = validator.STATES | {None}
        for previous in all_states:
            allowed = validator.TRANSITIONS.get(previous, set())
            for target in validator.STATES:
                if target in allowed:
                    continue
                s = state(previous, target)
                errors = validator.validate_transition(s)
                self.assertTrue(errors, f"undeclared transition {previous!r} → {target!r} should be rejected")

    def test_closed_is_terminal(self):
        for target in validator.STATES:
            s = state("closed", target)
            errors = validator.validate_transition(s)
            self.assertTrue(errors, f"closed → {target} should be forbidden")


class InvariantTest(unittest.TestCase):
    """State invariants: blocked_actions, overlap, staging guards."""

    def test_blocked_requires_blocked_actions(self):
        for s_name in ("blocked", "suspended", "expired"):
            prev = next(iter(validator.TRANSITIONS))
            for prev_state, targets in validator.TRANSITIONS.items():
                if s_name in targets:
                    prev = prev_state
                    break
            errors = validator.validate_transition(state(prev, s_name))
            self.assertTrue(errors, f"{s_name} without blocked_actions should fail")

    def test_allowed_blocked_overlap_rejected(self):
        errors = validator.validate_transition(state("screening", "blocked", ["launch"], ["launch"]))
        self.assertIn("allowed_actions and blocked_actions overlap", errors)

    def test_staging_guard(self):
        errors = validator.validate_transition(
            state("conditionally_cleared", "cleared_for_named_use"), staging=True)
        self.assertIn("controlled staging cannot emit cleared_for_named_use", errors)

    def test_unknown_state_rejected(self):
        s = state(None, "intake")
        s["state"] = "nonexistent_state"
        errors = validator.validate_transition(s)
        self.assertTrue(errors)


class OriginalBehaviorTest(unittest.TestCase):
    """Preserve original test intent."""

    def test_valid_fail_closed_path(self):
        self.assertEqual(validator.validate_transition(state(None, "intake")), [])
        self.assertEqual(validator.validate_transition(state("screening", "blocked", ["launch"])), [])
        self.assertEqual(validator.validate_transition(state("blocked", "remediation", ["launch"], ["collect_evidence"])), [])

    def test_direct_clearance_is_forbidden(self):
        errors = validator.validate_transition(state("screening", "cleared_for_named_use"))
        self.assertTrue(any("forbidden transition" in item for item in errors), errors)


class ObjectIdentitySchemaTest(unittest.TestCase):
    """9-dimensional object identity per blueprint §3."""

    def _validate_object(self, obj):
        schema = json.loads((ROOT / "schemas/canonical-access-object.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        try:
            jsonschema.validate(obj, schema, format_checker=jsonschema.FormatChecker())
            return []
        except jsonschema.ValidationError as exc:
            return [exc.message]

    def test_minimal_object_validates(self):
        self.assertEqual(self._validate_object(minimal_object()), [])

    def test_missing_subject_ref_rejected(self):
        obj = minimal_object()
        del obj["subject_ref"]
        self.assertTrue(self._validate_object(obj))

    def test_missing_scope_country_rejected(self):
        obj = minimal_object()
        del obj["scope_ref"]["country"]
        self.assertTrue(self._validate_object(obj))

    def test_claim_ref_validates_when_present(self):
        obj = minimal_object(claim_ref={
            "claim_text": "removes 99% bacteria", "language": "en",
            "medium": "product_listing", "object_version": "v1",
            "audience": "adult_consumers", "allowed_uses": ["product_detail_page"],
        })
        self.assertEqual(self._validate_object(obj), [])

    def test_claim_ref_missing_required_field_rejected(self):
        obj = minimal_object(claim_ref={
            "claim_text": "removes 99% bacteria", "language": "en",
        })
        self.assertTrue(self._validate_object(obj))

    def test_rule_ref_validates_when_present(self):
        obj = minimal_object(rule_ref={
            "issuer": "FDA", "source": "21_CFR", "rule_version": "2026.1",
            "scope": "food_contact_materials", "effective_date": "2026-01-01",
            "verified_date": "2026-07-15",
        })
        self.assertEqual(self._validate_object(obj), [])

    def test_opinion_ref_validates_when_present(self):
        obj = minimal_object(opinion_ref={
            "professional_id": "PRO-LAW-001", "qualification": "licensed_attorney",
            "authorization_scope": "US_patent_litigation", "jurisdiction": "US",
            "basis": "claim_construction_analysis", "issued_date": "2026-06-01",
        })
        self.assertEqual(self._validate_object(obj), [])

    def test_certificate_ref_validates_when_present(self):
        obj = minimal_object(certificate_ref={
            "issuer": "TUV", "holder": "Factory_ABC", "model": "Model_X",
            "standard": "CE_EN_71", "scope": "toy_safety", "status": "valid",
            "valid_until": "2027-12-31",
        })
        self.assertEqual(self._validate_object(obj), [])

    def test_certificate_ref_invalid_status_rejected(self):
        obj = minimal_object(certificate_ref={
            "issuer": "TUV", "holder": "Factory_ABC", "model": "Model_X",
            "standard": "CE_EN_71", "scope": "toy_safety", "status": "pending",
            "valid_until": "2027-12-31",
        })
        self.assertTrue(self._validate_object(obj))

    def test_null_optional_refs_valid(self):
        obj = minimal_object(claim_ref=None, rule_ref=None, opinion_ref=None, certificate_ref=None)
        self.assertEqual(self._validate_object(obj), [])

    def test_invalid_country_code_rejected(self):
        obj = minimal_object()
        obj["scope_ref"]["country"] = "usa"
        self.assertTrue(self._validate_object(obj))


class StateMachineSchemaTest(unittest.TestCase):
    """State machine schema is well-formed and covers all transitions."""

    def test_state_machine_schema_loads(self):
        sm = json.loads((ROOT / "schemas/state-machine.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(len(sm["states"]), 13)
        self.assertIn("closed", sm["states"])
        self.assertTrue(sm["states"]["closed"]["terminal"])

    def test_state_machine_transitions_match_validator(self):
        sm = json.loads((ROOT / "schemas/state-machine.schema.json").read_text(encoding="utf-8"))
        for key in sm["transitions"]:
            parts = key.split(" → ")
            prev_str, target = parts[0], parts[1]
            prev = None if prev_str == "null" else prev_str
            self.assertIn(target, validator.TRANSITIONS.get(prev, set()),
                          f"schema transition {key} not in validator TRANSITIONS")

    def test_validator_transitions_covered_in_schema(self):
        sm = json.loads((ROOT / "schemas/state-machine.schema.json").read_text(encoding="utf-8"))
        schema_keys = set()
        for key in sm["transitions"]:
            parts = key.split(" → ")
            prev_str, target = parts[0], parts[1]
            prev = None if prev_str == "null" else prev_str
            schema_keys.add((prev, target))
        for prev, targets in validator.TRANSITIONS.items():
            for target in targets:
                self.assertIn((prev, target), schema_keys,
                              f"validator transition {prev!r} → {target!r} not in schema")


if __name__ == "__main__":
    unittest.main(verbosity=2)
