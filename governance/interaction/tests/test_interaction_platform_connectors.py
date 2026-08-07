#!/usr/bin/env python3
"""Golden, missing-data, injection, expiry and connector-failure controls."""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import unittest
from datetime import datetime, timezone
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[3]


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader; spec.loader.exec_module(module); return module


class InteractionPlatformConnectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = load(ROOT / "governance/interaction/scripts/validate_prompt_intake.py", "intake")
        cls.compiler = load(ROOT / "governance/interaction/scripts/compile_operator_playbook.py", "compiler")
        cls.playbook = load(ROOT / "governance/interaction/scripts/validate_operator_playbook.py", "playbook")
        cls.cards = load(ROOT / "governance/platform-knowledge/scripts/validate_platform_cards.py", "cards")
        cls.connectors = load(ROOT / "governance/connectors/scripts/validate_connector_contract.py", "connectors")
        cls.adapter = load(ROOT / "governance/connectors/scripts/adapt_evidence.py", "adapter")
        cls.gateway = load(ROOT / "governance/connectors/scripts/authorize_action.py", "gateway")

    def intake_fixture(self):
        return {"contract":"CBDS-INTERACTION-2026.08","request_id":"R1","domain_id":"D08","object":{"object_type":"listing","object_id":"ASIN1","version":"v1","country":"US","platform":"Amazon"},"as_of_time":"2026-08-07T00:00:00+08:00","inputs":[{"field":"listing","value_state":"present","source_class":"authorized_first_party","trusted_as_instruction":False}],"missing_fields":[],"risks":{"prompt_injection":False,"sovereignty_overreach":False,"redline":False,"irreversible_action":False,"customer_commitment":False},"requested_operations":["explain"],"route":"answer","route_reason":"bounded evidence-backed explanation","allowed_scope":["diagnostic"],"prohibited_scope":["external_write"]}

    def test_01_golden_intake_passes(self):
        self.assertEqual(self.intake.validate(self.intake_fixture()), [])

    def test_02_missing_data_routes_to_exact_ask_and_never_zero(self):
        payload = self.intake_fixture(); payload["route"] = "ask"; payload["route_reason"] = "sales window is required"
        payload["missing_fields"] = [{"field":"units_30d","impact":"blocking","required_for":["replenishment"],"source_system":"Seller Central business report","owner":"seller","fallback":"none"}]
        self.assertEqual(self.intake.validate(payload), [])
        payload["route"] = "calculate"; self.assertIn("blocking missing fields cannot answer or calculate", self.intake.validate(payload))

    def test_03_prompt_injection_and_external_write_fail_closed(self):
        payload = self.intake_fixture(); payload["risks"]["prompt_injection"] = True
        payload["inputs"].append({"field":"competitor_review","value_state":"present","source_class":"untrusted_external_text","trusted_as_instruction":True})
        errors = self.intake.validate(payload)
        self.assertTrue(any("must block" in error for error in errors)); self.assertTrue(any("cannot be trusted" in error for error in errors))
        payload["route"] = "block"; payload["inputs"][-1]["trusted_as_instruction"] = False; payload["requested_operations"] = ["external_write"]
        self.assertEqual(self.intake.validate(payload), [])

    def packet_fixture(self):
        return {"packet_id":"PK1","owner_domain":"D08","object":{"object_type":"listing","object_id":"ASIN1","version":"v1"},"as_of_time":"2026-08-07T00:00:00+08:00","decision":{"decision_id":"DEC1","status":"validated","posture":"test","action_ceiling":"bounded listing experiment"},"actions":[{"action_id":"A1","instruction":"Run the pre-registered listing experiment","owner_role":"listing operator","dependencies":["approved copy"],"success_conditions":["primary metric reaches pre-registered threshold"],"guardrails":["no unsupported claim"],"stop_conditions":["policy or conversion guardrail breach"],"approval_required":True}],"rollback":{"trigger":["guardrail breach"],"steps":["restore prior version"],"residual_exposure_owner":"listing owner"},"outcome_feedback":{"metrics":["conversion"],"observation_window":"pre-registered mature window","writeback_target":"PLCO decision cycle"},"external_write":False,"erdg_validation":{"status":"passed","contract":"ERDG-CONTRACT-2026.07"}}

    def test_04_playbook_compiles_without_promoting_actions(self):
        packet = self.packet_fixture(); result = self.compiler.compile_playbook(packet)
        self.assertEqual(self.playbook.validate(result), []); self.assertEqual(result["actions"][0]["status"], "proposed"); self.assertFalse(result["external_write"])
        bad = copy.deepcopy(packet); bad["actions"][0]["stop_conditions"] = []
        with self.assertRaises(ValueError): self.compiler.compile_playbook(bad)

    def test_05_unvalidated_packet_and_self_authorized_write_do_not_compile(self):
        bad = self.packet_fixture(); bad["erdg_validation"]["status"] = "pending"
        with self.assertRaises(ValueError): self.compiler.compile_playbook(bad)
        bad = self.packet_fixture(); bad["external_write"] = True
        with self.assertRaises(ValueError): self.compiler.compile_playbook(bad)

    def test_06_current_cards_pass_and_expired_cards_fail(self):
        for path in (ROOT / "governance/platform-knowledge/cards").glob("*.json"):
            card = json.loads(path.read_text()); self.assertEqual(self.cards.validate(card, datetime(2026, 8, 7).date()), [], path)
            self.assertIn("card is expired", self.cards.validate(card, datetime(2027, 1, 1).date()))

    def test_07_inferred_card_cannot_become_score_or_write_rule(self):
        path = ROOT / "governance/platform-knowledge/cards/plco-amazon-generative-discovery.json"; card = json.loads(path.read_text())
        card["prohibited_uses"].remove("direct_score_change")
        self.assertTrue(any("must forbid" in error for error in self.cards.validate(card, datetime(2026, 8, 7).date())))

    def test_08_all_connector_manifests_are_read_only_and_contract_valid(self):
        for path in (ROOT / "governance/connectors/manifests").glob("*.json"):
            manifest = json.loads(path.read_text()); self.assertEqual(self.connectors.validate_manifest(manifest), [], path)
            self.assertEqual(manifest["status"], "contract_only"); self.assertFalse(manifest["permissions"]["write"])

    def test_09_empty_connector_field_is_missing_not_zero(self):
        manifest = json.loads((ROOT / "governance/connectors/manifests/amazon-sp-api.json").read_text())
        fields = json.loads((ROOT / "governance/connectors/field-contracts/amazon-sp-api-inventory.json").read_text())
        context = {"tenant_id":"T1","authorization_ref":"AUTH1","raw_reference":"s3://redacted/ref","observed_at":"2026-08-07T00:00:00Z","ingested_at":"2026-08-07T00:01:00Z"}
        result = self.adapter.adapt({"sellerSku":"SKU1","snapshotTime":"2026-08-07T00:00:00Z"}, manifest, fields, context)
        missing = {item["field"]: item["semantics"] for item in result["missing"]}
        self.assertEqual(missing["available_quantity"], "unknown_not_zero"); self.assertNotIn("available_quantity", result["values"])

    def test_10_contract_only_connector_denies_even_complete_write_request(self):
        manifest = json.loads((ROOT / "governance/connectors/manifests/amazon-ads-api.json").read_text())
        target = {"campaign_id":"C1"}
        request = {"action_id":"A1","decision_id":"D1","owner_domain":"D09","target":target,"operation":"set_bid","idempotency_key":"K1","decision_binding":{"erdg_contract":"ERDG-CONTRACT-2026.07","validation_status":"passed","decision_id":"D1","owner_domain":"D09","allowed_operations":["set_bid"],"target_ref":target,"packet_hash":"a"*64},"human_approval":{"status":"approved","approver":"owner","approved_at":"2026-08-07T00:00:00Z"},"expires_at":"2026-08-08T00:00:00Z","dry_run":{"status":"passed","result_hash":"abc"},"rollback":{"steps":["restore prior bid"],"owner":"ad owner"},"audit_destination":"tenant-audit"}
        result = self.gateway.authorize(request, manifest, datetime(2026, 8, 7, tzinfo=timezone.utc))
        self.assertFalse(result["authorized"]); self.assertIn("connector is not write-eligible", result["reasons"]); self.assertIn("connector manifest is read-only", result["reasons"])

    def test_11_schemas_accept_all_golden_contract_instances(self):
        intake_schema = json.loads((ROOT / "governance/interaction/schemas/prompt-intake.schema.json").read_text())
        playbook_schema = json.loads((ROOT / "governance/interaction/schemas/operator-playbook.schema.json").read_text())
        card_schema = json.loads((ROOT / "governance/platform-knowledge/platform-knowledge-card.schema.json").read_text())
        manifest_schema = json.loads((ROOT / "governance/connectors/schemas/connector-manifest.schema.json").read_text())
        field_schema = json.loads((ROOT / "governance/connectors/schemas/field-contract.schema.json").read_text())
        for schema in (intake_schema, playbook_schema, card_schema, manifest_schema, field_schema): Draft202012Validator.check_schema(schema)
        Draft202012Validator(intake_schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(self.intake_fixture())
        Draft202012Validator(playbook_schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(self.compiler.compile_playbook(self.packet_fixture()))
        for path in (ROOT / "governance/platform-knowledge/cards").glob("*.json"): Draft202012Validator(card_schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(json.loads(path.read_text()))
        for path in (ROOT / "governance/connectors/manifests").glob("*.json"): Draft202012Validator(manifest_schema).validate(json.loads(path.read_text()))
        for path in (ROOT / "governance/connectors/field-contracts").glob("*.json"): Draft202012Validator(field_schema).validate(json.loads(path.read_text()))

    def test_12_future_write_gateway_binds_owner_operation_target_and_packet(self):
        manifest = json.loads((ROOT / "governance/connectors/manifests/amazon-ads-api.json").read_text())
        manifest["status"] = "controlled_pilot"; manifest["permissions"]["write"] = True
        target = {"campaign_id":"C1"}
        request = {"action_id":"A1","decision_id":"D1","owner_domain":"D09","target":target,"operation":"set_bid","idempotency_key":"K1","decision_binding":{"erdg_contract":"ERDG-CONTRACT-2026.07","validation_status":"passed","decision_id":"D1","owner_domain":"D08","allowed_operations":["set_budget"],"target_ref":{"campaign_id":"C2"},"packet_hash":"bad"},"human_approval":{"status":"approved","approver":"owner","approved_at":"2026-08-07T00:00:00Z"},"expires_at":"2026-08-08T00:00:00Z","dry_run":{"status":"passed","result_hash":"abc"},"rollback":{"steps":["restore prior bid"],"owner":"ad owner"},"audit_destination":"tenant-audit"}
        result = self.gateway.authorize(request, manifest, datetime(2026, 8, 7, tzinfo=timezone.utc))
        self.assertFalse(result["authorized"])
        for expected in ("decision binding identity or owner mismatch", "operation is outside the approved decision ceiling", "target does not match the approved decision binding", "decision packet hash is invalid"):
            self.assertIn(expected, result["reasons"])


if __name__ == "__main__": unittest.main()
