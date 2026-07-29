#!/usr/bin/env python3
"""Second implementation used only as an independent calculation oracle."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json


def d(value):
    return Decimal(str(value))


def q(value):
    return str(d(value).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def calculate(model, x):
    if model == "quote_normalization":
        total = d(x["unit_price"]) * d(x["quantity"]) + sum((d(v) for v in x["extra_costs"]), Decimal("0"))
        output = {"base_currency_unit_cost": q(total * d(x["fx_rate"]) / d(x["quantity"])), "base_currency_total": q(total * d(x["fx_rate"]))}
    elif model == "bom_rollup":
        total = sum((d(r["quantity"]) * d(r["unit_cost"]) / (Decimal("1") - d(r["scrap_rate"])) for r in x["components"]), Decimal("0"))
        output = {"bom_cost": q(total), "component_count": len(x["components"])}
    elif model == "should_cost":
        keys = ("direct_material", "direct_labor", "machine_process", "manufacturing_overhead", "packaging_testing", "risk_allowance")
        base = sum((d(x[k]) for k in keys), Decimal("0"))
        estimate = base * (Decimal("1") + d(x.get("reasonable_margin_rate", 0)))
        output = {"currency": x["currency"], "unit": x["unit"], "as_of_time": x["as_of_time"], "cost_before_margin": q(base), "should_cost": q(estimate), "low_case": q(estimate), "high_case": q(estimate), "tooling_amortization_per_unit": q(0), "depreciation_per_unit": q(0), "selected_volume_tier": None, "component_count": 8, "is_supplier_actual_cost": False}
    elif model == "total_cost_of_ownership":
        keys = ("purchase", "inspection", "quality_failure", "delay", "switch_exit")
        financing = d(x.get("financing_base", x["purchase"])) * d(x.get("annual_financing_rate", 0)) * d(x.get("payment_to_recovery_days", 0)) / Decimal("365")
        event_loss = sum((d(e["probability"]) * d(e["loss"]) for e in x.get("tail_events", [])), Decimal("0"))
        total = sum((d(x[k]) for k in keys), Decimal("0")) + d(x.get("logistics", 0)) + d(x.get("duties_taxes", 0)) + financing + event_loss - d(x.get("recoverable_value", 0))
        output = {"currency": x["currency"], "unit": x["unit"], "as_of_time": x["as_of_time"], "total_cost_of_ownership": q(total), "financing_cost": q(financing), "expected_tail_loss": q(event_loss), "tail_event_mode": x.get("tail_event_mode"), "logistics": q(x.get("logistics", 0)), "duties_taxes": q(x.get("duties_taxes", 0)), "recoverable_value": q(x.get("recoverable_value", 0)), "logistics_and_cash_require_owner_inputs": True}
    elif model == "capacity":
        effective = (d(x["available_hours"]) - d(x["changeover_hours"])) * d(x["units_per_hour"]) * d(x["yield_rate"]) * d(x["uptime_rate"])
        output = {"effective_capacity": q(effective), "capacity_gap": q(effective - d(x["demand"])), "feasible": effective >= d(x["demand"])}
    elif model == "lead_time":
        output = {"committed_lead_time_days": q(sum((d(v) for v in x["stage_days"]), Decimal("0")) + d(x.get("risk_buffer_days", 0)))}
    elif model == "concentration":
        shares = [d(v) for v in x["shares"]]
        output = {"hhi": q(sum((v * v for v in shares), Decimal("0"))), "single_source": len([v for v in shares if v > 0]) == 1}
    elif model == "measurement_system":
        ratio = d(x["study_variation"]) / d(x["tolerance"])
        ndc = int((Decimal("1.41") * d(x["process_variation"]) / d(x["study_variation"])).to_integral_value(rounding="ROUND_FLOOR")) if "process_variation" in x else None
        output = {"variation_to_tolerance": q(ratio), "ndc": ndc, "acceptable": ratio <= Decimal(".1") and (ndc is None or ndc >= 5), "conditional": Decimal(".1") < ratio <= Decimal(".3")}
    elif model == "process_stability":
        values = [d(v) for v in x["values"]]; center = sum(values, Decimal("0")) / d(len(values))
        ranges = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]; sigma = (sum(ranges, Decimal("0")) / d(len(ranges))) / Decimal("1.128")
        ucl = center + 3 * sigma; lcl = center - 3 * sigma
        outside = [i for i, value in enumerate(values) if value > ucl or value < lcl]
        trends = [[s, s + 5] for s in range(len(values) - 5) if all(values[s + i] > values[s + i - 1] for i in range(1, 6)) or all(values[s + i] < values[s + i - 1] for i in range(1, 6))]
        span = max(values) - min(values)
        output = {"center": q(center), "range": q(span), "estimated_sigma": q(sigma), "individual_ucl": q(ucl), "individual_lcl": q(lcl), "special_cause_points": outside, "trend_windows": trends, "monotonic_trend": bool(trends), "stable": span <= d(x["max_range"]) and not outside and not trends, "specification_limit_used_as_control_limit": False}
    elif model == "process_capability":
        cp=(d(x["usl"])-d(x["lsl"]))/(Decimal("6")*d(x["sigma"]))
        cpk=min((d(x["usl"])-d(x["mean"]))/(Decimal("3")*d(x["sigma"])),(d(x["mean"])-d(x["lsl"]))/(Decimal("3")*d(x["sigma"])))
        output={"cp":q(cp),"cpk":q(cpk)}
    elif model == "fmea":
        rpn=int(x["severity"])*int(x["occurrence"])*int(x["detection"])
        output={"rpn":rpn,"hard_redline":int(x["severity"])>=9,"priority":"critical" if int(x["severity"])>=9 else "high" if rpn>=200 else "controlled"}
    elif model == "sampling":
        output = {"decision": "accept" if x["critical_defects"] == 0 and x["defects"] <= x["accept_number"] else "reject", "observed_defect_rate": q(d(x["defects"]) / d(x["sample_size"])), "zero_defect_claim": False}
    elif model == "quantity_reconciliation":
        parts = sum((d(x[k]) for k in ("qualified", "nonconforming", "rework", "scrapped", "wip", "explained_variance")), Decimal("0"))
        output = {"balanced": d(x["input"]) == parts, "difference": q(d(x["input"]) - parts)}
    elif model == "escape_risk":
        upper = min(Decimal("1"), (d(x["defects"]) + 3) / d(x["sample_size"]))
        output = {"observed_rate": q(d(x["defects"]) / d(x["sample_size"])), "approximate_upper_95_rate": q(upper), "residual_risk": "nonzero", "zero_defect_claim": False}
    elif model == "recovery_choice":
        feasible = [r for r in x["options"] if r["feasible"]]
        chosen = min(feasible, key=lambda r: (d(r["loss"]), d(r["days"]), str(r["id"])))
        output = {"selected_option": chosen["id"], "residual_risk": chosen.get("residual_risk", "unknown")}
    elif model == "cost_of_quality":
        total = sum((d(x[k]) for k in ("prevention", "appraisal", "internal_failure", "external_failure", "recall")), Decimal("0"))
        output = {"total_cost_of_quality": q(total), "external_failure_included": True, "recall_included": True}
    elif model == "reliability":
        hours=d(x["test_hours"]);failures=d(x["failures"]);rate=failures/hours
        output={"observed_failure_rate_per_hour":q(rate),"approximate_upper_95_failure_rate":q((failures+3)/hours),"mtbf_observed":None if failures==0 else q(hours/failures),"zero_failure_proves_zero_risk":False}
    elif model == "delivery_reliability":
        output={"otif":q(d(x["on_time_in_full"])/d(x["orders"])),"orders":int(x["orders"])}
    else:
        raise ValueError(f"oracle_model_not_supported:{model}")
    return {"output": output, "input_hash": digest(x), "output_hash": digest(output)}
