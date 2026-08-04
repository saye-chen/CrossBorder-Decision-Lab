#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("validate_cidm_handoff.py")

def packet() -> dict:
    return {
        "packet_version": "CIDM-PLCO-v1",
        "decision_object": {"product_concept_id": "P1", "category_node": "N1", "country": "US", "platform": "Amazon", "currency": "USD"},
        "cidm_decision_id": "D1", "product_facts": [], "proof_assets": [{"proof_id": "P1"}],
        "unsupported_claims": [], "prohibited_claims": [], "target_segments": [], "purchase_jobs": [],
        "purchase_objections": [], "keyword_clusters": [], "validated_pain_points": [],
        "differentiation_claims": [{"claim": "tested fact", "proof_id": "P1"}], "price_position": {},
        "weakest_assumption": "conversion", "experiment_hypotheses": [],
        "allowed_use": ["listing_and_store_acceptance_design"], "forbidden_use": ["investment_score_override"]
    }

class CIDMHandoffTests(unittest.TestCase):
    def run_packet(self, value: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT), str(path)], text=True, capture_output=True)

    def test_accepts_proof_bound_packet(self):
        self.assertEqual(self.run_packet(packet()).returncode, 0)

    def test_rejects_unproved_claim_and_score_override(self):
        value = packet(); value["differentiation_claims"][0]["proof_id"] = "missing"; value["invest"] = True
        result = self.run_packet(value)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("proof_id", result.stderr)
        self.assertIn("investment authority", result.stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
