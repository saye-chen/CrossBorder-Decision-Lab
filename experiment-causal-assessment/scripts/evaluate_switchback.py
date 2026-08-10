#!/usr/bin/env python3
"""Validate Switchback design/carryover contracts and route verified inference."""

from __future__ import annotations

import re

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main, parse_time, require_positive

HASH_RE = re.compile(r"^[a-f0-9]{64}$")


def evaluate_switchback(value: dict) -> dict:
    periods = value.get("periods")
    if not isinstance(periods, list) or len(periods) < 4:
        raise ECAEError("INSUFFICIENT_PERIODS", "Switchback requires at least four periods before backend-specific adequacy review")
    required = ["period_id","arm","start","end","outcome_summary","washout_excluded"]
    if any(not all(field in period for field in required) for period in periods):
        raise ECAEError("INVALID_PERIOD_RECORD", "Each period needs design, timing, outcome and washout fields")
    period_ids = [period["period_id"] for period in periods]
    if any(not isinstance(item, str) or not item for item in period_ids) or len(period_ids) != len(set(period_ids)):
        raise ECAEError("INVALID_PERIOD_ID", "Switchback period ids must be non-empty and unique")
    period_length = require_positive(value.get("period_length_seconds"), "period_length_seconds")
    response_lag = require_positive(value.get("max_response_lag_seconds"), "max_response_lag_seconds", allow_zero=True)
    washout = require_positive(value.get("washout_seconds"), "washout_seconds", allow_zero=True)
    if period_length <= response_lag and value.get("carryover_model") in (None, "none"):
        raise ECAEError("CARRYOVER_UNCONTROLLED", "Period length does not exceed response lag and no carryover model is registered")
    if washout < response_lag and value.get("carryover_sensitivity") is not True:
        raise ECAEError("WASHOUT_INADEQUATE", "Washout shorter than response lag requires carryover sensitivity")
    if value.get("randomization_scheme") not in {"complete_sequence", "blocked_sequence", "custom_sequence"}:
        raise ECAEError("SEQUENCE_NOT_REGISTERED", "A supported switchback randomization scheme must be frozen")
    if not isinstance(value.get("allowed_sequences_hash"), str) or not HASH_RE.fullmatch(value["allowed_sequences_hash"]):
        raise ECAEError("SEQUENCE_NOT_REGISTERED", "Allowed switchback sequences require a SHA-256 commitment")
    if value.get("observed_sequence_registered") is not True or value.get("test_statistic_registered") is not True:
        raise ECAEError("SEQUENCE_NOT_REGISTERED", "Observed sequence and test statistic must be registered before outcomes")
    if not isinstance(value.get("timezone"), str) or not value["timezone"]:
        raise ECAEError("TIMEZONE_NOT_FROZEN", "Switchback timezone must be frozen")
    if value.get("serial_dependence_plan") not in {"randomization_inference", "newey_west_period", "verified_block_bootstrap"}:
        raise ECAEError("SERIAL_DEPENDENCE_UNRESOLVED", "A period-compatible serial dependence plan is required")
    controls = value.get("periodicity_controls")
    if not isinstance(controls, list) or not controls or any(not isinstance(item, str) or not item for item in controls):
        raise ECAEError("PERIODICITY_CONFOUNDED", "At least one frozen periodicity control is required")
    max_carryover = value.get("max_carryover_periods")
    if not isinstance(max_carryover, int) or isinstance(max_carryover, bool) or max_carryover < 0:
        raise ECAEError("CARRYOVER_ORDER_INVALID", "max_carryover_periods must be a non-negative integer")
    if any(period["washout_excluded"] is not True for period in periods):
        raise ECAEError("WASHOUT_REINTRODUCED", "Primary period records must certify washout exclusion")
    parsed = []
    for period in periods:
        start = parse_time(period["start"], f"period[{period['period_id']}].start")
        end = parse_time(period["end"], f"period[{period['period_id']}].end")
        if end <= start:
            raise ECAEError("PERIOD_TIME_INVALID", "Each switchback period must end after it starts")
        observed_length = (end - start).total_seconds()
        if abs(observed_length - period_length) > 1e-6:
            raise ECAEError("PERIOD_LENGTH_MISMATCH", "Observed period duration differs from the frozen duration", {"period_id": period["period_id"], "observed": observed_length, "registered": period_length})
        parsed.append((start, end))
    if any(parsed[index][0] < parsed[index - 1][1] for index in range(1, len(parsed))):
        raise ECAEError("PERIOD_OVERLAP", "Switchback periods cannot overlap")
    arms = [period["arm"] for period in periods]
    if len(set(arms)) != 2 or all(arms[index] == arms[index-1] for index in range(1,len(arms))):
        raise ECAEError("NO_EFFECTIVE_SWITCHES", "Switchback needs at least two arms and effective switches")
    backend = require_verified_backend("switchback_inference")
    return {"status":"ready_for_backend_execution","backend":backend,"period_count":len(periods),"effective_switches":sum(arms[index] != arms[index-1] for index in range(1,len(arms))),"randomization_scheme":value["randomization_scheme"],"required_outputs":["randomization_compatible_effect","serial_dependence_interval","lag_sensitivity","periodicity_diagnostic","carryover_diagnostic"]}


if __name__ == "__main__":
    cli_main(evaluate_switchback, __doc__ or "Evaluate switchback")
