#!/usr/bin/env python3
"""Fail-closed validator for Amazon store profiles and operating archetypes."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY_PATH = SKILL_ROOT / "references/amazon-store-operating-models.json"


def _is_unknown(value: Any) -> bool:
    if value is None or value == "" or value == "unknown" or value == "UNKNOWN":
        return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False


def _registry(registry: dict | None) -> dict:
    return registry if registry is not None else json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def validate(profile: dict, registry: dict | None = None) -> dict:
    """Return pass/conditional/fail without silently upgrading unknown fields."""

    registry = _registry(registry)
    errors: list[str] = []
    warnings: list[str] = []
    required = {item["id"]: item for item in registry.get("required_profile_fields", [])}
    archetypes = {item["id"]: item for item in registry.get("operating_archetypes", [])}
    overlays = {item["id"]: item for item in registry.get("overlays", [])}

    if profile.get("platform") != "Amazon":
        errors.append("platform_must_be_Amazon")
    if profile.get("external_write") is True:
        errors.append("external_write_must_be_false")

    archetype_id = profile.get("archetype_id")
    if archetype_id in overlays:
        errors.append("overlay_is_not_operating_profile")
    archetype = archetypes.get(archetype_id)
    if archetype is None:
        errors.append("unknown_or_missing_operating_archetype")

    def require(field: str, reason: str) -> None:
        value = profile.get(field)
        if _is_unknown(value):
            if value in (None, "", [], {}):
                errors.append(f"missing:{field}:{reason}")
            else:
                warnings.append(f"unknown:{field}:{reason}")

    for field, spec in required.items():
        scopes = set(spec.get("required_for", []))
        if "all" in scopes or "all_operating_profiles" in scopes:
            require(field, spec.get("unknown_action", "required"))

    if profile.get("selling_program") in {"seller_central_3p", "amazon_business"}:
        require("seller_id", "seller_central_identity")
    if profile.get("seller_role") == "brand_owner":
        require("brand_id", "brand_owner_identity")
        require("brand_authorization_state", "brand_authority")
    if profile.get("seller_role") == "authorized_reseller":
        require("brand_authorization_state", "reseller_authority")

    for field, spec in required.items():
        value = profile.get(field)
        allowed = spec.get("allowed")
        if allowed and value is not None and value not in allowed:
            errors.append(f"invalid_enum:{field}:{value}")

    if archetype is not None:
        for key in ("seller_role", "selling_program", "fulfillment_mode"):
            expected = archetype[key]
            actual = profile.get(key)
            if _is_unknown(actual):
                if actual in (None, ""):
                    errors.append(f"missing:{key}:archetype_match")
                else:
                    warnings.append(f"unknown:{key}:archetype_match")
            elif actual != expected:
                errors.append(f"archetype_mismatch:{key}:{actual}!={expected}")
        for field in archetype.get("required_fields", []):
            require(field, f"archetype:{archetype_id}")

    declared_overlays = profile.get("overlays", [])
    if declared_overlays is None:
        declared_overlays = []
    if not isinstance(declared_overlays, list):
        errors.append("overlays_must_be_array")
        declared_overlays = []
    for overlay_id in declared_overlays:
        overlay = overlays.get(overlay_id)
        if overlay is None:
            errors.append(f"unknown_overlay:{overlay_id}")
            continue
        if not overlay.get("not_an_independent_seller_account"):
            errors.append(f"overlay_flag_missing:{overlay_id}")
        for field in overlay.get("required_fields", []):
            value = profile.get(field)
            if _is_unknown(value):
                errors.append(f"missing:{field}:overlay:{overlay_id}")

    if not isinstance(profile.get("evidence_ids"), list) or not profile.get("evidence_ids"):
        errors.append("evidence_ids_must_be_nonempty_array")
    if not isinstance(profile.get("as_of_time"), str) or not profile.get("as_of_time"):
        errors.append("as_of_time_must_be_nonempty_string")

    if errors:
        status, action_limit = "fail", "blocked"
    elif warnings:
        status, action_limit = "conditional", "conditional_only"
    else:
        status, action_limit = "pass", "controlled_pilot_only"
    return {
        "status": status,
        "action_limit": action_limit,
        "archetype_id": archetype_id,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=pathlib.Path)
    args = parser.parse_args()
    result = validate(json.loads(args.profile.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"pass", "conditional"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
