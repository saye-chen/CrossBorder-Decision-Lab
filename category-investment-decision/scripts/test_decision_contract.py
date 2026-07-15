#!/usr/bin/env python3
"""Regression and adversarial tests for the decision contract gate."""

from __future__ import annotations

import copy
import itertools
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_decision_contract.py")
CIDM = "category-investment-decision"
VLB = "video-link-breakdown"


def valid_payload() -> dict:
    return {
        "mode": "multi",
        "decision_type": "investment",
        "decision_owner": CIDM,
        "participating_skills": [CIDM, VLB],
        "runtime_versions": {CIDM: "CIDM-2026.09", VLB: "VLB-2026.08"},
        "professional_core": {
            "object_boundary": "US Amazon indoor electronic pet fountain, LC-2",
            "conclusion": "Only content testing is authorized before gates pass.",
            "evidence_summary": ["E1", "E2"],
            "counterevidence": ["Single-video evidence cannot prove repeatability."],
            "commercial_constraints": ["Complete fulfillment cost is required."],
            "risks_and_redlines": ["FTO remains unresolved."],
            "actions": ["Run target-product content test."],
            "success_conditions": ["Pass pre-registered content and profit gates."],
            "stop_conditions": ["Stop if compliance or contribution gate fails."],
            "limitations_and_missing_data": ["No target-product conversion data."],
        },
        "objects": [{
            "canonical_id": "pet-fountain-us-amazon",
            "country": "US",
            "platform": "Amazon",
            "category": "pet-water-fountain",
            "subtype": "indoor-electronic",
            "price_band": "40-60 USD",
            "lifecycle": "LC-2",
        }],
        "evidence": [
            {"id": "E1", "source_skill": CIDM, "evidence_type": "official_page", "source_ref": "source-1", "observed_at": "2026-07-15", "fingerprint": "fp-1"},
            {"id": "E2", "source_skill": VLB, "evidence_type": "video_metadata", "source_ref": "source-2", "observed_at": "2026-07-15", "fingerprint": "fp-2"},
        ],
        "claims": [{
            "id": "C1",
            "producer_skill": VLB,
            "claim_domain": "content",
            "state": "proposed",
            "object_id": "pet-fountain-us-amazon",
            "evidence_ids": ["E2"],
            "allowed_uses": ["content_test_design"],
            "forbidden_uses": ["confirmed_profit", "final_investment_decision"],
            "effective_now": False,
        }],
        "calculations": [
            {"id": "score", "calculator": "score_model", "input_hash": "in-1", "output_hash": "out-1", "status": "complete"},
            {"id": "profit", "calculator": "profit_model.py", "input_hash": "in-2", "output_hash": "out-2", "status": "complete"},
        ],
        "required_calculation_ids": ["score", "profit"],
        "unresolved_redlines": [],
        "adjustments": [{
            "id": "A1",
            "proposer_skill": VLB,
            "target_skill": CIDM,
            "target_dimension": "content_communication",
            "status": "proposed",
            "original_score": 7,
            "proposed_score": 8,
            "evidence_ids": ["E2"],
            "transferability": "similar_product",
            "effective_now": False,
            "crosses_threshold": False,
        }],
    }


def run(payload: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "contract.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )


class ProfessionalCompletenessTests(unittest.TestCase):
    def test_valid_contract_passes(self):
        result = run(valid_payload())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_professional_module_is_required(self):
        fields = list(valid_payload()["professional_core"])
        for field in fields:
            with self.subTest(field=field):
                payload = valid_payload()
                payload["professional_core"][field] = []
                result = run(payload)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field, result.stderr)

    def test_missing_data_does_not_authorize_missing_stop_conditions(self):
        payload = valid_payload()
        payload["professional_core"]["stop_conditions"] = ""
        self.assertNotEqual(run(payload).returncode, 0)


class OwnershipAndWriteBackTests(unittest.TestCase):
    def test_wrong_decision_owner_is_blocked(self):
        payload = valid_payload()
        payload["decision_owner"] = VLB
        self.assertIn("decision_owner", run(payload).stderr)

    def test_proposed_adjustment_cannot_be_effective(self):
        payload = valid_payload()
        payload["adjustments"][0]["effective_now"] = True
        self.assertIn("cannot be effective", run(payload).stderr)

    def test_hypothesis_claim_cannot_be_effective(self):
        payload = valid_payload()
        payload["claims"][0]["state"] = "hypothesis"
        payload["claims"][0]["effective_now"] = True
        self.assertIn("cannot be effective", run(payload).stderr)

    def test_cross_category_adjustment_cannot_be_effective(self):
        payload = valid_payload()
        adjustment = payload["adjustments"][0]
        adjustment.update({
            "status": "validated",
            "effective_now": True,
            "accepted_by": CIDM,
            "recomputed_by": CIDM,
            "transferability": "cross_category",
            "validation_ids": ["T1"],
        })
        self.assertIn("cross_category", run(payload).stderr)

    def test_similar_product_validation_requires_experiment(self):
        payload = valid_payload()
        adjustment = payload["adjustments"][0]
        adjustment.update({"status": "validated", "effective_now": True, "accepted_by": CIDM, "recomputed_by": CIDM})
        self.assertIn("validation_ids", run(payload).stderr)


class ThresholdAndEvidenceTests(unittest.TestCase):
    def threshold_payload(self) -> dict:
        payload = valid_payload()
        adjustment = payload["adjustments"][0]
        adjustment.update({
            "status": "validated",
            "effective_now": True,
            "accepted_by": CIDM,
            "recomputed_by": CIDM,
            "validation_ids": ["T1"],
            "evidence_ids": ["E1", "E2"],
            "crosses_threshold": True,
            "target_object_direct_evidence": True,
            "required_calculation_ids": ["score", "profit"],
            "original_confidence": "medium",
            "proposed_confidence": "medium",
        })
        return payload

    def test_safe_threshold_crossing_passes(self):
        result = run(self.threshold_payload())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_source_fingerprints_do_not_count_as_independent(self):
        payload = self.threshold_payload()
        payload["evidence"][1]["fingerprint"] = payload["evidence"][0]["fingerprint"]
        self.assertIn("independent evidence", run(payload).stderr)

    def test_threshold_crossing_with_redline_is_blocked(self):
        payload = self.threshold_payload()
        payload["unresolved_redlines"] = ["FTO"]
        self.assertIn("unresolved redlines", run(payload).stderr)

    def test_threshold_crossing_requires_calculations(self):
        payload = self.threshold_payload()
        payload["adjustments"][0]["required_calculation_ids"] = ["missing"]
        self.assertIn("required calculations", run(payload).stderr)

    def test_threshold_crossing_cannot_lower_confidence(self):
        payload = self.threshold_payload()
        payload["adjustments"][0]["proposed_confidence"] = "low"
        self.assertIn("cannot lower confidence", run(payload).stderr)

    def test_reordering_evidence_does_not_change_result(self):
        first = run(self.threshold_payload())
        payload = self.threshold_payload()
        payload["evidence"] = list(reversed(payload["evidence"]))
        second = run(payload)
        self.assertEqual(first.returncode, second.returncode)

    def test_irrelevant_evidence_does_not_authorize_proposed_adjustment(self):
        payload = valid_payload()
        payload["evidence"].append({
            "id": "E3", "source_skill": VLB, "evidence_type": "irrelevant",
            "source_ref": "source-3", "observed_at": "2026-07-15", "fingerprint": "fp-3",
        })
        result = run(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(payload["adjustments"][0]["effective_now"])


class CalculationAndReferenceTests(unittest.TestCase):
    def test_incomplete_calculation_is_blocked(self):
        payload = valid_payload()
        payload["calculations"][0]["status"] = "failed"
        self.assertIn("not complete", run(payload).stderr)

    def test_unknown_evidence_reference_is_blocked(self):
        payload = valid_payload()
        payload["claims"][0]["evidence_ids"] = ["missing"]
        self.assertIn("unknown evidence", run(payload).stderr)

    def test_nonfinite_score_is_blocked(self):
        payload = valid_payload()
        payload["adjustments"][0]["proposed_score"] = float("nan")
        self.assertIn("must be finite", run(payload).stderr)

    def test_cross_domain_claim_is_blocked(self):
        payload = valid_payload()
        payload["claims"][0]["claim_domain"] = "investment"
        self.assertIn("crosses domain authority", run(payload).stderr)

    def test_overlapping_allowed_and_forbidden_uses_are_blocked(self):
        payload = valid_payload()
        payload["claims"][0]["allowed_uses"].append("confirmed_profit")
        self.assertIn("overlapping", run(payload).stderr)

    def test_cyclic_claim_lineage_is_blocked(self):
        payload = valid_payload()
        first = payload["claims"][0]
        first["derived_from_claim_ids"] = ["C2"]
        second = copy.deepcopy(first)
        second.update({"id": "C2", "derived_from_claim_ids": ["C1"]})
        payload["claims"].append(second)
        self.assertIn("cyclic claim dependency", run(payload).stderr)


class InvocationTopologyTests(unittest.TestCase):
    """All four singles plus every pair/triple/quad topology must be representable."""

    def test_all_fifteen_skill_topologies(self):
        skills = [
            "category-investment-decision",
            "competitive-intelligence-monitoring",
            "video-link-breakdown",
            "consumer-insights-customer-growth",
        ]
        owner_to_type = {
            "category-investment-decision": "investment",
            "competitive-intelligence-monitoring": "competition",
            "video-link-breakdown": "content",
            "consumer-insights-customer-growth": "customer_growth",
        }
        tested = 0
        for size in range(1, 5):
            for participants in itertools.combinations(skills, size):
                payload = valid_payload()
                owner = participants[0]
                payload.update({
                    "mode": "single" if size == 1 else "multi",
                    "decision_type": owner_to_type[owner],
                    "decision_owner": owner,
                    "participating_skills": list(participants),
                    "runtime_versions": {skill: "TEST-2026.01" for skill in participants},
                    "evidence": [],
                    "claims": [],
                    "adjustments": [],
                    "unresolved_redlines": [],
                })
                if owner == "category-investment-decision":
                    payload["calculations"] = valid_payload()["calculations"]
                    payload["required_calculation_ids"] = ["score", "profit"]
                else:
                    payload["calculations"] = []
                    payload["required_calculation_ids"] = []
                with self.subTest(participants=participants, owner=owner):
                    result = run(payload)
                    self.assertEqual(result.returncode, 0, result.stderr)
                tested += 1
        self.assertEqual(tested, 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
