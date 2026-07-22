#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from handoff_contracts import validate_brief_seed, validate_selection_handoff


def handoff() -> dict:
    return {"selection_handoff_package": {
        "meta": {"cidm_version": "CIDM-2026.14", "assessment_date": "2026-07-22", "confidence_level": "medium", "lifecycle_stage": "LC-3"},
        "product_identity": {"name": "Test product", "category_path": "Home > Test", "price_band": "$10-20", "key_variants": []},
        "selling_points_ranked": [
            {"point": "Rare proof", "differentiation": "rare", "evidence": "E1"},
            {"point": "Common proof", "differentiation": "common", "evidence": "E2"},
        ],
        "target_segment": {"primary_persona": "Authorized target segment"},
        "competitive_creative_gap": {"gap_opportunity": "Visible proof gap"},
        "entry_constraint": {"budget_level": "small", "production_capability": "self_shot", "platform_compliance_notes": [], "timeline": "2 weeks"},
        "strategic_intent": {"content_role": "unspecified", "funnel_position": "unconfirmed", "success_metric": "confirm before execution"},
    }}


def brief() -> dict:
    return {"production_ready_brief_seed": {
        "meta": {"source_video_id": "v1", "source_video_url": "https://example.test/v1", "vlb_confidence": "medium", "usage": "validate_before_scale", "platform": "TikTok", "category": "Test", "handoff_aligned": None},
        "layer_1_product_proof": {"primary_proof_point": "Demonstrate proof", "secondary_proof_points": [], "evidence_format": {"type": "live_test", "detail": "controlled demonstration"}, "proof_duration_ratio": 0.4},
        "layer_2_creative_blueprint": {"archetype": "test", "compliance_risk": "low", "narrative_structure": {"hook": {"type": "question", "content": "Does it work?", "duration_sec": 2}, "development": {"pattern": "problem_solution", "beats": [{"timestamp": "0-2s", "content": "problem", "function": "frame"}]}, "conversion_node": {"type": "product_reveal", "timing": "8s", "content": "reveal"}}, "rhythm_template": {"total_duration_sec": 10, "cut_frequency": "2s", "info_density": "medium", "energy_curve": "rise"}},
        "layer_3_execution_params": {"camera_language": {"shots": ["close-up"], "movement": "fixed", "angle": "front"}, "lighting_tone": "natural", "talent_requirement": {"type": "real_person", "persona": "operator"}, "audio": {"music_style": "none", "voiceover": "real_voice", "sound_effects": []}, "text_overlay": {"strategy": "key_points", "style": "plain"}, "ai_generation_notes": {"recommended_model": None, "prompt_skeleton": None, "limitations": "physical proof must be filmed"}},
    }}


class SelectionHandoffContract(unittest.TestCase):
    def test_valid_handoff_passes(self):
        self.assertEqual(validate_selection_handoff(handoff()), [])

    def test_missing_required_field_fails(self):
        payload = handoff(); del payload["selection_handoff_package"]["product_identity"]["name"]
        self.assertTrue(validate_selection_handoff(payload))

    def test_invalid_enum_and_duplicate_points_fail(self):
        payload = handoff(); root = payload["selection_handoff_package"]
        root["entry_constraint"]["budget_level"] = "unlimited"
        root["selling_points_ranked"][1]["point"] = "Rare proof"
        errors = validate_selection_handoff(payload)
        self.assertTrue(any("budget_level" in item for item in errors))
        self.assertTrue(any("duplicate selling point" in item for item in errors))

    def test_unspecified_is_valid_without_defaulting_to_conversion(self):
        payload = handoff()
        self.assertEqual(payload["selection_handoff_package"]["strategic_intent"]["content_role"], "unspecified")
        self.assertEqual(validate_selection_handoff(payload), [])


class BriefSeedContract(unittest.TestCase):
    def test_valid_brief_passes(self):
        self.assertEqual(validate_brief_seed(brief()), [])

    def test_low_confidence_cannot_scale(self):
        payload = brief(); meta = payload["production_ready_brief_seed"]["meta"]
        meta["vlb_confidence"] = "low"; meta["usage"] = "production_ready"
        self.assertTrue(any("low confidence" in item for item in validate_brief_seed(payload)))

    def test_medium_confidence_cannot_be_production_ready(self):
        payload = brief(); payload["production_ready_brief_seed"]["meta"]["usage"] = "production_ready"
        self.assertTrue(any("medium confidence" in item for item in validate_brief_seed(payload)))

    def test_invalid_ratio_and_timing_fail(self):
        payload = brief(); root = payload["production_ready_brief_seed"]
        root["layer_1_product_proof"]["proof_duration_ratio"] = 1.5
        root["layer_2_creative_blueprint"]["narrative_structure"]["hook"]["duration_sec"] = 11
        errors = validate_brief_seed(payload)
        self.assertTrue(any("proof_duration_ratio" in item for item in errors))
        self.assertTrue(any("cannot exceed" in item for item in errors))

    def test_ai_talent_requires_model(self):
        payload = brief(); root = payload["production_ready_brief_seed"]["layer_3_execution_params"]
        root["talent_requirement"]["type"] = "ai_avatar"
        self.assertTrue(any("recommended_model" in item for item in validate_brief_seed(payload)))

    def test_input_is_not_mutated(self):
        payload = brief(); before = copy.deepcopy(payload)
        validate_brief_seed(payload)
        self.assertEqual(payload, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
