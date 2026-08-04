#!/usr/bin/env python3
"""Validate blind, time-frozen OSL starter replay selection and label contracts."""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from typing import Any

TYPES = {"regular_success", "regular_failure", "surprise_success", "surprise_failure", "boundary_conflict"}

class ReplayError(ValueError):
    pass

def _time(value: Any) -> datetime:
    try: return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc: raise ReplayError("invalid replay timestamp") from exc

def validate(payload: dict[str, Any]) -> dict[str, Any]:
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        raise ReplayError("starter replay requires exactly 20 cases")
    counts = Counter(case.get("sample_type") for case in cases)
    if set(counts) != TYPES or any(counts[name] != 4 for name in TYPES):
        raise ReplayError("starter replay requires four cases in each of five sample types")
    ids = [case.get("case_id") for case in cases]
    if any(not value for value in ids) or len(set(ids)) != len(ids):
        raise ReplayError("case_id must be unique and nonempty")
    for case in cases:
        if case.get("selector_role") == case.get("implementation_owner_role"):
            raise ReplayError("implementer cannot be the sole sample selector")
        if not case.get("model_hash") or not case.get("input_hash") or not case.get("sample_list_hash"):
            raise ReplayError("model, input and locked sample hashes are required")
        decision = _time(case.get("decision_cutoff")); input_cutoff = _time(case.get("input_evidence_cutoff"))
        if input_cutoff > decision:
            raise ReplayError("future evidence leaked past decision cutoff")
        label = case.get("label_contract", {})
        required = {"contract_version", "evaluation_horizon_days", "primary_outcome", "success_threshold", "failure_threshold", "counterfactual_baseline", "label_source_ids", "label_confidence", "locked_at", "result_revealed_at", "censored"}
        if not required.issubset(label):
            raise ReplayError("label contract incomplete")
        if _time(label["locked_at"]) >= _time(label["result_revealed_at"]):
            raise ReplayError("label contract must be locked before result reveal")
        if label["censored"] and not label.get("censor_reason"):
            raise ReplayError("censored label requires reason")
        if label["label_confidence"] not in {"low", "medium", "high"}:
            raise ReplayError("invalid label confidence")
    return {"status": "valid_starter_replay_contract", "case_count": 20, "coverage": dict(sorted(counts.items())), "production_validity_proven": False}
