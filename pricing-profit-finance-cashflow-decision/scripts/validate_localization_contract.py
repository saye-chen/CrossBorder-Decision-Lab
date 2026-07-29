#!/usr/bin/env python3
"""Validate temporary F02 localization contracts and migration packages."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ppfc_common import PPFCError, dec, parse_time

CEILING_RANK = {"analysis_only": 0, "controlled_test": 1, "reversible_action": 2, "human_approved_execution": 3}
LOW_EVIDENCE = {"E0", "E1"}


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PPFCError(message)


def validate_localization(payload: dict[str, Any], as_of: str | None = None) -> dict[str, Any]:
    required = {"contract", "localization_id", "version", "country_code", "platform_id", "currency_code", "fx", "tax", "unit_system", "time_zone", "settlement_calendar", "dynamic_rule", "localization_status", "evidence_grade", "action_ceiling", "validity", "lineage", "external_write"}
    require(not (required - set(payload)), f"missing required fields: {sorted(required-set(payload))}")
    require(payload["contract"] == "F02-temporary-localization-contract-v1", "unsupported contract")
    require(payload["external_write"] is False, "localization contract cannot authorize external write")
    require(len(payload["country_code"]) == 2 and payload["country_code"].isupper(), "country_code must be ISO alpha-2")
    require(len(payload["currency_code"]) == 3 and payload["currency_code"].isupper(), "currency_code must be ISO 4217 style")
    try:
        ZoneInfo(payload["time_zone"])
    except ZoneInfoNotFoundError as exc:
        raise PPFCError("time_zone must be a valid IANA zone") from exc
    fx = payload["fx"]
    require(dec(fx["rate"], "fx.rate", nonnegative=True) > 0, "fx.rate must be positive")
    require(fx["quote_currency"] == payload["currency_code"], "fx quote currency must equal localization currency")
    fx_verified = parse_time(fx["verified_at"], "fx.verified_at")
    fx_until = parse_time(fx["valid_until"], "fx.valid_until")
    require(fx_until > fx_verified, "fx validity must follow verification")
    tax = payload["tax"]
    tax_verified = parse_time(tax["verified_at"], "tax.verified_at")
    tax_until = parse_time(tax["valid_until"], "tax.valid_until")
    require(tax_until > tax_verified, "tax validity must follow verification")
    require(not (tax["basis"] == "tax_inclusive_revenue" and tax["inclusive"] is False), "tax basis conflicts with inclusive flag")
    require(not (tax["basis"] == "tax_exclusive_revenue" and tax["inclusive"] is True), "tax basis conflicts with inclusive flag")
    dynamic = payload["dynamic_rule"]
    effective = parse_time(dynamic["effective_at"], "dynamic_rule.effective_at")
    expires = parse_time(dynamic["expires_at"], "dynamic_rule.expires_at")
    require(expires > effective, "dynamic rule expiry must follow effective time")
    validity = payload["validity"]
    valid_from = parse_time(validity["valid_from"], "validity.valid_from")
    valid_until = parse_time(validity["valid_until"], "validity.valid_until")
    recorded = parse_time(validity["recorded_at"], "validity.recorded_at")
    require(valid_until > valid_from and recorded >= valid_from, "invalid bitemporal validity")
    require(payload["lineage"]["runtime_version"] == "PPFC-2026.07", "runtime version mismatch")
    require(str(payload["lineage"]["input_hash"]).startswith("sha256:"), "input hash required")
    status = payload["localization_status"]
    require(status in {"proposed", "validated", "inconclusive", "blocked", "expired", "superseded", "retired"}, "invalid status")
    decision_time = parse_time(as_of, "as_of") if as_of else recorded
    expired_components = []
    if decision_time > fx_until: expired_components.append("fx")
    if decision_time > tax_until: expired_components.append("tax")
    if decision_time > expires or decision_time > valid_until: expired_components.append("dynamic_rule")
    effective_status = "expired" if expired_components else status
    ceiling = payload["action_ceiling"]
    if effective_status in {"expired", "inconclusive", "blocked", "superseded", "retired"}:
        require(ceiling == "analysis_only", "non-current localization must be analysis_only")
    if payload["evidence_grade"] in LOW_EVIDENCE:
        require(CEILING_RANK[ceiling] <= CEILING_RANK["analysis_only"], "low evidence cannot exceed analysis_only")
    if tax["basis"] == "unknown":
        require(effective_status in {"inconclusive", "blocked", "expired"}, "unknown tax basis cannot be current")
    return {"valid": True, "effective_status": effective_status, "expired_components": expired_components, "action_ceiling": "analysis_only" if expired_components else ceiling, "requires_recompute": bool(expired_components)}


def validate_migration(payload: dict[str, Any]) -> dict[str, Any]:
    required = {"migration_id", "source_contract", "target_contract", "state", "field_mappings", "dual_run", "differences", "acceptance", "rollback", "lineage"}
    require(not (required - set(payload)), f"missing migration fields: {sorted(required-set(payload))}")
    require(payload["source_contract"] == "F02-temporary-localization-contract-v1", "wrong migration source")
    require(payload["target_contract"] != payload["source_contract"], "target must be a distinct F02 contract")
    mappings = payload["field_mappings"]
    require(isinstance(mappings, list) and mappings, "field mappings required")
    losses = {item.get("loss") for item in mappings}
    state = payload["state"]
    acceptance = payload["acceptance"]
    rollback = payload["rollback"]
    require(rollback.get("supported") is True and rollback.get("source_readable") is True, "migration must be rollback-safe")
    parse_time(rollback["deadline"], "rollback.deadline")
    require(payload["dual_run"]["same_input_hash"] == payload["lineage"]["input_hash"], "dual run and lineage input hashes differ")
    blockers = []
    if losses & {"material", "unmapped"}: blockers.append("material_or_unmapped_field")
    if payload["dual_run"]["source_result_hash"] != payload["dual_run"]["target_result_hash"] and not payload["differences"]:
        blockers.append("unexplained_dual_run_difference")
    if state in {"cutover_ready", "cutover"}:
        if blockers: raise PPFCError("cutover blocked: " + ",".join(blockers))
        require(acceptance.get("accepted") is True and acceptance.get("accepted_by") and acceptance.get("accepted_at"), "cutover requires explicit acceptance")
        parse_time(acceptance["accepted_at"], "acceptance.accepted_at")
    return {"valid": True, "state": state, "cutover_allowed": not blockers and acceptance.get("accepted") is True, "blockers": blockers}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--as-of")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        require(isinstance(payload, dict), "root must be object")
        result = validate_localization(payload, args.as_of) if payload.get("contract") else validate_migration(payload)
    except (OSError, json.JSONDecodeError, KeyError, PPFCError) as exc:
        print(f"PPFC_LOCALIZATION=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
