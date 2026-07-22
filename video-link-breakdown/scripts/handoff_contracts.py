#!/usr/bin/env python3
"""Deterministic validators for CIDM handoffs and VLB Brief Seeds."""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def obj(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def required(data: dict[str, Any], fields: tuple[str, ...], path: str, errors: list[str]) -> None:
    for field in fields:
        if not nonempty(data.get(field)):
            errors.append(f"{path}.{field} must not be empty")


def enum(value: Any, allowed: set[str], path: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{path} must be one of {sorted(allowed)}")


def load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("document root must be an object")
    return data


def validate_selection_handoff(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    root = obj(payload.get("selection_handoff_package"), "selection_handoff_package", errors)

    meta = obj(root.get("meta"), "selection_handoff_package.meta", errors)
    required(meta, ("cidm_version", "assessment_date", "confidence_level", "lifecycle_stage"), "selection_handoff_package.meta", errors)
    if nonempty(meta.get("cidm_version")) and not re.fullmatch(r"CIDM-20\d{2}\.\d{2}", str(meta["cidm_version"])):
        errors.append("selection_handoff_package.meta.cidm_version has invalid format")
    if nonempty(meta.get("assessment_date")):
        try:
            date.fromisoformat(str(meta["assessment_date"]))
        except ValueError:
            errors.append("selection_handoff_package.meta.assessment_date must be YYYY-MM-DD")
    enum(meta.get("confidence_level"), {"high", "medium", "low"}, "selection_handoff_package.meta.confidence_level", errors)
    enum(meta.get("lifecycle_stage"), {f"LC-{i}" for i in range(1, 7)}, "selection_handoff_package.meta.lifecycle_stage", errors)

    identity = obj(root.get("product_identity"), "selection_handoff_package.product_identity", errors)
    required(identity, ("name", "category_path", "price_band"), "selection_handoff_package.product_identity", errors)
    if "key_variants" in identity and not isinstance(identity["key_variants"], list):
        errors.append("selection_handoff_package.product_identity.key_variants must be a list")

    points = root.get("selling_points_ranked")
    if not isinstance(points, list) or not 2 <= len(points) <= 5:
        errors.append("selection_handoff_package.selling_points_ranked must contain 2 to 5 items")
        points = []
    seen: set[str] = set()
    for index, raw in enumerate(points):
        point = obj(raw, f"selection_handoff_package.selling_points_ranked[{index}]", errors)
        required(point, ("point", "differentiation", "evidence"), f"selection_handoff_package.selling_points_ranked[{index}]", errors)
        enum(point.get("differentiation"), {"unique", "rare", "common"}, f"selection_handoff_package.selling_points_ranked[{index}].differentiation", errors)
        name = str(point.get("point", "")).strip()
        if name in seen:
            errors.append(f"duplicate selling point: {name}")
        seen.add(name)

    segment = obj(root.get("target_segment"), "selection_handoff_package.target_segment", errors)
    required(segment, ("primary_persona",), "selection_handoff_package.target_segment", errors)
    gap = obj(root.get("competitive_creative_gap"), "selection_handoff_package.competitive_creative_gap", errors)
    required(gap, ("gap_opportunity",), "selection_handoff_package.competitive_creative_gap", errors)

    constraint = obj(root.get("entry_constraint"), "selection_handoff_package.entry_constraint", errors)
    required(constraint, ("budget_level", "production_capability", "timeline"), "selection_handoff_package.entry_constraint", errors)
    enum(constraint.get("budget_level"), {"micro", "small", "medium", "large"}, "selection_handoff_package.entry_constraint.budget_level", errors)
    enum(constraint.get("production_capability"), {"self_shot", "outsource", "ai_generate", "mixed"}, "selection_handoff_package.entry_constraint.production_capability", errors)
    if not isinstance(constraint.get("platform_compliance_notes"), list):
        errors.append("selection_handoff_package.entry_constraint.platform_compliance_notes must be a list")

    intent = obj(root.get("strategic_intent"), "selection_handoff_package.strategic_intent", errors)
    required(intent, ("content_role", "funnel_position", "success_metric"), "selection_handoff_package.strategic_intent", errors)
    enum(intent.get("content_role"), {"awareness", "conversion", "retargeting", "brand_building", "unspecified"}, "selection_handoff_package.strategic_intent.content_role", errors)
    return errors


def validate_brief_seed(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    root = obj(payload.get("production_ready_brief_seed"), "production_ready_brief_seed", errors)
    meta = obj(root.get("meta"), "production_ready_brief_seed.meta", errors)
    required(meta, ("source_video_id", "source_video_url", "vlb_confidence", "usage", "platform", "category"), "production_ready_brief_seed.meta", errors)
    enum(meta.get("vlb_confidence"), {"high", "medium", "low"}, "production_ready_brief_seed.meta.vlb_confidence", errors)
    enum(meta.get("usage"), {"production_ready", "validate_before_scale", "hypothesis_only"}, "production_ready_brief_seed.meta.usage", errors)
    if meta.get("handoff_aligned") not in {True, False, None}:
        errors.append("production_ready_brief_seed.meta.handoff_aligned must be true, false, or null")
    confidence = meta.get("vlb_confidence")
    usage = meta.get("usage")
    if confidence == "low" and usage != "hypothesis_only":
        errors.append("low confidence requires hypothesis_only usage")
    if confidence == "medium" and usage == "production_ready":
        errors.append("medium confidence cannot be production_ready")

    layer1 = obj(root.get("layer_1_product_proof"), "production_ready_brief_seed.layer_1_product_proof", errors)
    required(layer1, ("primary_proof_point", "evidence_format", "proof_duration_ratio"), "production_ready_brief_seed.layer_1_product_proof", errors)
    secondary = layer1.get("secondary_proof_points", [])
    if not isinstance(secondary, list) or len(secondary) > 2:
        errors.append("production_ready_brief_seed.layer_1_product_proof.secondary_proof_points must contain at most 2 items")
    evidence_format = obj(layer1.get("evidence_format"), "production_ready_brief_seed.layer_1_product_proof.evidence_format", errors)
    required(evidence_format, ("type", "detail"), "production_ready_brief_seed.layer_1_product_proof.evidence_format", errors)
    enum(evidence_format.get("type"), {"live_test", "comparison", "data_overlay", "scenario_immersion", "testimonial", "unboxing", "before_after"}, "production_ready_brief_seed.layer_1_product_proof.evidence_format.type", errors)
    ratio = layer1.get("proof_duration_ratio")
    if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or not math.isfinite(ratio) or not 0 <= ratio <= 1:
        errors.append("production_ready_brief_seed.layer_1_product_proof.proof_duration_ratio must be between 0 and 1")

    layer2 = obj(root.get("layer_2_creative_blueprint"), "production_ready_brief_seed.layer_2_creative_blueprint", errors)
    required(layer2, ("archetype", "compliance_risk", "narrative_structure", "rhythm_template"), "production_ready_brief_seed.layer_2_creative_blueprint", errors)
    enum(layer2.get("compliance_risk"), {"low", "medium", "high"}, "production_ready_brief_seed.layer_2_creative_blueprint.compliance_risk", errors)
    narrative = obj(layer2.get("narrative_structure"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure", errors)
    hook = obj(narrative.get("hook"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.hook", errors)
    required(hook, ("type", "content", "duration_sec"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.hook", errors)
    enum(hook.get("type"), {"question", "shock", "pain_point", "curiosity_gap", "direct_callout", "trend_ride"}, "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.hook.type", errors)
    development = obj(narrative.get("development"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.development", errors)
    required(development, ("pattern", "beats"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.development", errors)
    enum(development.get("pattern"), {"linear_escalation", "problem_solution", "before_after", "listicle", "story_arc"}, "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.development.pattern", errors)
    beats = development.get("beats")
    if not isinstance(beats, list) or not beats:
        errors.append("production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.development.beats must be non-empty")
    else:
        for index, beat in enumerate(beats):
            beat_obj = obj(beat, f"beats[{index}]", errors)
            required(beat_obj, ("timestamp", "content", "function"), f"beats[{index}]", errors)
    conversion = obj(narrative.get("conversion_node"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.conversion_node", errors)
    required(conversion, ("type", "timing", "content"), "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.conversion_node", errors)
    enum(conversion.get("type"), {"cta_verbal", "cta_text", "product_reveal", "urgency_trigger", "social_proof_cascade"}, "production_ready_brief_seed.layer_2_creative_blueprint.narrative_structure.conversion_node.type", errors)
    rhythm = obj(layer2.get("rhythm_template"), "production_ready_brief_seed.layer_2_creative_blueprint.rhythm_template", errors)
    required(rhythm, ("total_duration_sec", "cut_frequency", "info_density", "energy_curve"), "production_ready_brief_seed.layer_2_creative_blueprint.rhythm_template", errors)
    enum(rhythm.get("info_density"), {"high", "medium", "low"}, "production_ready_brief_seed.layer_2_creative_blueprint.rhythm_template.info_density", errors)
    total = rhythm.get("total_duration_sec")
    hook_duration = hook.get("duration_sec")
    if not isinstance(total, (int, float)) or isinstance(total, bool) or total <= 0:
        errors.append("total_duration_sec must be positive")
    if not isinstance(hook_duration, (int, float)) or isinstance(hook_duration, bool) or hook_duration <= 0:
        errors.append("hook.duration_sec must be positive")
    elif isinstance(total, (int, float)) and hook_duration > total:
        errors.append("hook.duration_sec cannot exceed total_duration_sec")

    layer3 = obj(root.get("layer_3_execution_params"), "production_ready_brief_seed.layer_3_execution_params", errors)
    required(layer3, ("camera_language", "lighting_tone", "talent_requirement", "audio", "text_overlay", "ai_generation_notes"), "production_ready_brief_seed.layer_3_execution_params", errors)
    camera = obj(layer3.get("camera_language"), "production_ready_brief_seed.layer_3_execution_params.camera_language", errors)
    required(camera, ("shots", "movement", "angle"), "production_ready_brief_seed.layer_3_execution_params.camera_language", errors)
    if not isinstance(camera.get("shots"), list) or not camera.get("shots"):
        errors.append("camera_language.shots must be a non-empty list")
    talent = obj(layer3.get("talent_requirement"), "production_ready_brief_seed.layer_3_execution_params.talent_requirement", errors)
    required(talent, ("type", "persona"), "production_ready_brief_seed.layer_3_execution_params.talent_requirement", errors)
    enum(talent.get("type"), {"real_person", "ai_avatar", "product_only", "mixed"}, "production_ready_brief_seed.layer_3_execution_params.talent_requirement.type", errors)
    audio = obj(layer3.get("audio"), "production_ready_brief_seed.layer_3_execution_params.audio", errors)
    required(audio, ("music_style", "voiceover"), "production_ready_brief_seed.layer_3_execution_params.audio", errors)
    enum(audio.get("voiceover"), {"none", "ai_tts", "real_voice", "trending_sound"}, "production_ready_brief_seed.layer_3_execution_params.audio.voiceover", errors)
    if not isinstance(audio.get("sound_effects"), list):
        errors.append("audio.sound_effects must be a list")
    overlay = obj(layer3.get("text_overlay"), "production_ready_brief_seed.layer_3_execution_params.text_overlay", errors)
    required(overlay, ("strategy", "style"), "production_ready_brief_seed.layer_3_execution_params.text_overlay", errors)
    enum(overlay.get("strategy"), {"minimal", "key_points", "full_subtitle"}, "production_ready_brief_seed.layer_3_execution_params.text_overlay.strategy", errors)
    notes = obj(layer3.get("ai_generation_notes"), "production_ready_brief_seed.layer_3_execution_params.ai_generation_notes", errors)
    if not all(field in notes for field in ("recommended_model", "prompt_skeleton", "limitations")):
        errors.append("ai_generation_notes requires recommended_model, prompt_skeleton, and limitations fields")
    if talent.get("type") in {"ai_avatar", "mixed"} and not nonempty(notes.get("recommended_model")):
        errors.append("AI or mixed talent requires ai_generation_notes.recommended_model")
    return errors


def cli(kind: str) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = load_payload(args.input)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_selection_handoff(payload) if kind == "selection" else validate_brief_seed(payload)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"{kind} contract valid")
    return 0
