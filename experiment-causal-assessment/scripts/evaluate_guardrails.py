#!/usr/bin/env python3
"""Evaluate preregistered harm guardrails with independent stop authority."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main


def evaluate_guardrails(value: dict) -> dict:
    guardrails = value.get("guardrails")
    if not isinstance(guardrails, list) or not guardrails:
        raise ECAEError("NO_GUARDRAILS", "At least one preregistered guardrail is required")
    results, stop = [], False
    for item in guardrails:
        required = ["guardrail_id","harm_direction","harm_threshold","interval","decision_rule","registered_before_launch"]
        if any(field not in item for field in required):
            raise ECAEError("INVALID_GUARDRAIL", "Guardrail contract is incomplete", item.get("guardrail_id"))
        if item["registered_before_launch"] is not True:
            raise ECAEError("UNREGISTERED_GUARDRAIL", "Guardrail must be registered before launch", item["guardrail_id"])
        interval = item["interval"]
        lower, upper = interval.get("lower"), interval.get("upper")
        if not isinstance(lower, (int,float)) or not isinstance(upper, (int,float)) or lower > upper:
            raise ECAEError("INVALID_INTERVAL", "Guardrail interval is invalid", item["guardrail_id"])
        threshold = float(item["harm_threshold"])
        direction, rule = item["harm_direction"], item["decision_rule"]
        if direction == "higher_is_harmful":
            confirmed = lower > threshold
            cannot_exclude = upper > threshold
        elif direction == "lower_is_harmful":
            confirmed = upper < threshold
            cannot_exclude = lower < threshold
        else:
            raise ECAEError("INVALID_HARM_DIRECTION", "harm_direction must be higher_is_harmful or lower_is_harmful")
        if rule == "stop_on_confirmed_harm":
            triggered = confirmed
        elif rule == "stop_when_harm_cannot_be_excluded":
            triggered = cannot_exclude
        else:
            raise ECAEError("INVALID_GUARDRAIL_RULE", "Unknown guardrail decision_rule")
        stop = stop or triggered
        results.append({"guardrail_id":item["guardrail_id"],"confirmed_harm":confirmed,"harm_cannot_be_excluded":cannot_exclude,"stop_triggered":triggered,"threshold":threshold,"interval":interval})
    return {"stop_for_harm":stop,"guardrails":results,"efficacy_cannot_override_harm":True,"recommended_state":"stopped_for_harm" if stop else "continue_per_protocol"}


if __name__ == "__main__":
    cli_main(evaluate_guardrails, __doc__ or "Evaluate guardrails")
