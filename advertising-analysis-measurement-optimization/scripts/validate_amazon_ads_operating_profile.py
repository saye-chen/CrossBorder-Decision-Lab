#!/usr/bin/env python3
"""Fail-closed validator for Amazon Ads operating records and decision scope."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = SKILL_ROOT / "references/amazon-ads-operating-model.json"


def _unknown(value: Any) -> bool:
    return value is None or value == "" or (isinstance(value, str) and value in {"unknown", "UNKNOWN", "not_observed"})


def _model(model: dict | None) -> dict:
    return model if model is not None else json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def validate(profile: dict, model: dict | None = None) -> dict:
    """Return pass/conditional/fail and never upgrade missing evidence to a pass."""

    model = _model(model)
    errors: list[str] = []
    warnings: list[str] = []
    required = (
        "store_profile_id", "ads_profile_id", "seller_account_id", "marketplace_id",
        "ad_type", "campaign_id", "date", "as_of_time",
    )

    if profile.get("platform") != "Amazon":
        errors.append("platform_must_be_Amazon")
    if profile.get("external_write") is True:
        errors.append("external_write_must_be_false")
    if not isinstance(profile.get("evidence_ids"), list) or not profile.get("evidence_ids"):
        errors.append("evidence_ids_must_be_nonempty_array")

    for field in required:
        if _unknown(profile.get(field)):
            errors.append(f"missing:{field}")

    ad_types = {item["id"]: item for item in model.get("ad_types", [])}
    ad_type = profile.get("ad_type")
    ad_spec = ad_types.get(ad_type)
    if ad_spec is None and not _unknown(ad_type):
        errors.append(f"unknown:ad_type:{ad_type}")

    hierarchy = {item["level"]: item for item in model.get("campaign_hierarchy", [])}
    for level, spec in hierarchy.items():
        if level in {"ads_profile", "campaign"}:
            for field in spec.get("required", []):
                if _unknown(profile.get(field)):
                    warnings.append(f"unknown:{level}:{field}")

    if ad_spec is not None:
        target_family = profile.get("targeting_family") or profile.get("target_type")
        declared_families = set(ad_spec.get("targeting_families", []))
        if _unknown(target_family):
            errors.append("missing:targeting_family_or_target_type")
        elif target_family not in declared_families:
            errors.append(f"ad_type_targeting_mismatch:{ad_type}:{target_family}")

        if ad_type == "sponsored_products":
            for field in ("target_id", "promoted_asin"):
                if _unknown(profile.get(field)):
                    errors.append(f"missing:{field}:sponsored_products")
        elif ad_type == "sponsored_brands":
            for field in ("brand_authorization_state", "brand_asset_version", "destination_version"):
                if _unknown(profile.get(field)):
                    errors.append(f"missing:{field}:sponsored_brands")
            if profile.get("brand_authorization_state") in {"unconfirmed", "rejected", "expired"}:
                errors.append("brand_authorization_not_eligible")
        elif ad_type == "sponsored_display":
            if _unknown(profile.get("target_id")) and _unknown(profile.get("audience_id")):
                errors.append("missing:target_id_or_audience_id:sponsored_display")
        elif ad_type == "dsp":
            for field in ("audience_id", "audience_rule", "measurement_design"):
                if _unknown(profile.get(field)):
                    errors.append(f"missing:{field}:dsp")

    if _unknown(profile.get("attribution_type")):
        warnings.append("unknown:attribution_type")
    if _unknown(profile.get("maturity_state")):
        warnings.append("unknown:maturity_state")
    if _unknown(profile.get("retail_readiness_state")):
        errors.append("missing:retail_readiness_state")

    for field in ("target_id", "query_or_search_term", "placement", "promoted_asin"):
        if field in profile and _unknown(profile.get(field)):
            warnings.append(f"unknown:{field}")

    if errors:
        status, action_limit = "fail", "blocked"
    elif warnings:
        status, action_limit = "conditional", "conditional_only"
    else:
        status, action_limit = "pass", "controlled_pilot_only"
    return {
        "status": status,
        "action_limit": action_limit,
        "ad_type": ad_type,
        "workflow_hint": "AMZ-ADS-01-PROFILE-ELIGIBILITY" if status != "pass" else "AMZ-ADS-04-BID-BUDGET",
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
