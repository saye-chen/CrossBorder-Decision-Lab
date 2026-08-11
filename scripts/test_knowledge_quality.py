#!/usr/bin/env python3
from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kq", ROOT / "scripts/validate_knowledge_quality.py")
KQ = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(KQ)
BASE = json.loads((ROOT / "governance/knowledge-quality/knowledge-quality-register.json").read_text())


class KnowledgeQualityTests(unittest.TestCase):
    def test_current_register_passes(self):
        self.assertEqual(KQ.validate(copy.deepcopy(BASE), dt.date(2026, 8, 11)), [])

    def test_expired_fact_fails_closed(self):
        data = copy.deepcopy(BASE); data["dynamic_facts"][0]["expires_at"] = "2026-08-10"
        self.assertTrue(any("expired but active" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_every_platform_card_requires_dynamic_fact_coverage(self):
        data = copy.deepcopy(BASE); data["dynamic_facts"] = data["dynamic_facts"][:1]
        self.assertTrue(any("lack dynamic-fact coverage" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_dynamic_fact_cannot_broaden_source_card(self):
        data = copy.deepcopy(BASE); data["dynamic_facts"][0]["allowed_uses"].append("direct_score_change")
        self.assertTrue(any("broadens allowed uses" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_dynamic_fact_metadata_must_match_source_card(self):
        data = copy.deepcopy(BASE); data["dynamic_facts"][0]["owner_domain"] = "D09"
        self.assertTrue(any("owner_domain drifted" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_unknown_constraint_reference_is_rejected(self):
        data = copy.deepcopy(BASE); data["deliveries"][0]["constraint_refs"].append("MISSING")
        self.assertTrue(any("unknown constraints" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_unknown_constraint_consumer_is_rejected(self):
        data = copy.deepcopy(BASE); data["constraints"][0]["consumers"].append("D99")
        self.assertTrue(any("unknown consumers" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_generic_duplicate_self_check_is_rejected(self):
        data = copy.deepcopy(BASE); duplicate = copy.deepcopy(data["deliveries"][0]); duplicate["check_id"] = "DUP"; duplicate["object_ref"] = "other"
        data["deliveries"].append(duplicate)
        self.assertTrue(any("duplicate generic" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_missing_data_route_requires_decision_impact(self):
        data = copy.deepcopy(BASE); data["missing_data_routes"][0]["decision_impact"] = ""
        self.assertTrue(any("decision_impact" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_scale_claim_drift_is_rejected(self):
        data = copy.deepcopy(BASE); data["scale_claims"]["registered_domains"] = 99
        self.assertTrue(any("scale claims drift" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_health_auto_close_is_rejected(self):
        data = copy.deepcopy(BASE); data["health_policy"]["auto_close"] = True
        self.assertTrue(any("must not auto-close" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))

    def test_threshold_guard_cannot_be_weakened(self):
        data = copy.deepcopy(BASE); data["anti_gaming"]["threshold_changes_require"] = ["change_impact"]
        self.assertTrue(any("threshold-change" in e for e in KQ.validate(data, dt.date(2026, 8, 11))))


if __name__ == "__main__": unittest.main()
