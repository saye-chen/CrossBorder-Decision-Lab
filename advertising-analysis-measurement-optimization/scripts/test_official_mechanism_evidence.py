#!/usr/bin/env python3
"""Validate official-mechanism scope, provenance and anti-hallucination gates."""

from __future__ import annotations

import json
import pathlib
import unittest
from urllib.parse import urlparse


ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "references/platforms/official-mechanism-evidence.json"
EXPECTED = {
    "amazon", "google-search", "google-shopping-pmax", "meta-ads", "tiktok-shop",
    "tiktok-ads-dtc", "shopee", "shein", "temu", "mercado-libre",
}
OFFICIAL_HOST_SUFFIXES = (
    "advertising.amazon.com",
    "support.google.com",
    "facebook.com",
    "ads.tiktok.com",
    "newsroom.tiktok.com",
)


class OfficialMechanismEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.records = {item["platform_id"]: item for item in cls.data["records"]}

    def test_all_platform_cards_have_one_evidence_record(self):
        self.assertEqual(set(self.records), EXPECTED)
        self.assertEqual(len(self.records), len(self.data["records"]))

    def test_contract_separates_published_unknown_and_refresh(self):
        self.assertEqual(self.data["contract"], "AAMO-OFFICIAL-MECHANISM-EVIDENCE-1.0")
        self.assertRegex(self.data["snapshot_date"], r"^\d{4}-\d{2}-\d{2}$")
        for platform, record in self.records.items():
            self.assertIn(record["evidence_status"], {"official_public_mechanism", "current_interface_required"})
            self.assertTrue(record["scope"], platform)
            self.assertTrue(record["undisclosed"], platform)
            self.assertTrue(record["forbidden_inferences"], platform)
            self.assertTrue(record["execution_refresh"], platform)
            if record["evidence_status"] == "official_public_mechanism":
                self.assertTrue(record["official_sources"], platform)
                self.assertTrue(record["published_mechanism"], platform)

    def test_registered_sources_are_first_party(self):
        for platform, record in self.records.items():
            for source in record["official_sources"]:
                parsed = urlparse(source)
                self.assertEqual(parsed.scheme, "https", (platform, source))
                self.assertTrue(
                    any(parsed.hostname == suffix or parsed.hostname.endswith("." + suffix)
                        for suffix in OFFICIAL_HOST_SUFFIXES),
                    (platform, source),
                )

    def test_google_quality_score_is_not_falsely_used_as_formula(self):
        record = self.records["google-search"]
        joined = " ".join(record["published_mechanism"] + record["forbidden_inferences"])
        self.assertIn("not an auction input", joined)
        self.assertIn("Do not state Ad Rank = bid x Quality Score x ad format impact", joined)
        self.assertNotIn("Ad Rank = bid × Quality Score", " ".join(record["published_mechanism"]))

    def test_tiktok_organic_and_paid_scopes_cannot_be_merged(self):
        paid = self.records["tiktok-ads-dtc"]
        shop = self.records["tiktok-shop"]
        self.assertEqual(paid["scope"], "paid_social_ad_auction")
        self.assertIn("not a paid-ad auction formula", " ".join(paid["undisclosed"]))
        self.assertIn("adjacent context", " ".join(shop["published_mechanism"]))
        self.assertTrue(any("Do not transfer organic For You" in item for item in shop["forbidden_inferences"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
