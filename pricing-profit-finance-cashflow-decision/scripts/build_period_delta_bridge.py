#!/usr/bin/env python3
"""Build an owner-signed D06 period revenue/profit delta bridge."""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import jsonschema

REVERSALS=("discounts","pass_through_tax","cancellations","refunds","other_reversals")
COSTS=("product_cogs","fulfillment","platform_payment_fees","expected_returns","variable_marketing","variable_service","avoidable_period_cost","allocated_operating_expense")

class BridgeError(ValueError): pass
SCHEMA_PATH=Path(__file__).resolve().parents[1]/"schemas/period-delta-bridge.schema.json"

def parse_time(value: str, field: str) -> datetime:
    try: parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    except (AttributeError,ValueError) as exc: raise BridgeError(f"{field}: invalid date-time") from exc
    if parsed.tzinfo is None: raise BridgeError(f"{field}: timezone offset required")
    return parsed

def validate_contract(payload: dict[str,Any]) -> None:
    schema=json.loads(SCHEMA_PATH.read_text())
    errors=sorted(jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).iter_errors(payload),key=lambda e:list(e.path))
    if errors: raise BridgeError("schema:"+"|".join(error.message for error in errors[:8]))
    try: ZoneInfo(payload["timezone"])
    except ZoneInfoNotFoundError as exc: raise BridgeError("timezone: unknown IANA timezone") from exc
    baseline_start=parse_time(payload["baseline_window"]["start"],"baseline.start");baseline_end=parse_time(payload["baseline_window"]["end"],"baseline.end")
    comparison_start=parse_time(payload["comparison_window"]["start"],"comparison.start");comparison_end=parse_time(payload["comparison_window"]["end"],"comparison.end")
    if baseline_start>=baseline_end or comparison_start>=comparison_end: raise BridgeError("PPFC_SCOPE_CONFLICT:invalid_window")
    if baseline_end>comparison_start: raise BridgeError("PPFC_SCOPE_CONFLICT:overlapping_windows")
    if baseline_start>=comparison_start: raise BridgeError("PPFC_SCOPE_CONFLICT:baseline_not_earlier")
    if baseline_end-baseline_start != comparison_end-comparison_start: raise BridgeError("PPFC_NOT_COMPARABLE:window_duration")
    records={row["evidence_id"]:row for row in payload["evidence_records"]}
    if len(records)!=len(payload["evidence_records"]): raise BridgeError("PPFC_EVIDENCE_DUPLICATE")
    if set(payload["evidence_refs"])!=set(records): raise BridgeError("PPFC_EVIDENCE_BINDING_MISMATCH")
    binding=("subject_id","subject_version","currency","tax_basis","quantity_unit","timezone")
    for evidence_id,row in records.items():
        if row["status"]!="verified": raise BridgeError(f"PPFC_EVIDENCE_NOT_CURRENT:{evidence_id}")
        if any(row[field]!=payload[field] for field in binding): raise BridgeError(f"PPFC_EVIDENCE_SCOPE_MISMATCH:{evidence_id}")
        if parse_time(row["observed_at"],"evidence.observed_at")>comparison_end or parse_time(row["valid_until"],"evidence.valid_until")<comparison_end: raise BridgeError(f"PPFC_EVIDENCE_EXPIRED:{evidence_id}")
def dec(value: Any, field: str, *, nonnegative: bool = False) -> Decimal:
    if not isinstance(value,str): raise BridgeError(f"{field}: decimal string required")
    try: result=Decimal(value)
    except InvalidOperation as exc: raise BridgeError(f"{field}: invalid decimal") from exc
    if not result.is_finite(): raise BridgeError(f"{field}: non-finite forbidden")
    if nonnegative and result < 0: raise BridgeError(f"{field}: negative value forbidden")
    return result
def exact(value: Decimal) -> str:
    if value==0:return "0"
    result=format(value.normalize(),"f"); return result.rstrip("0").rstrip(".") if "." in result else result
def canonical_hash(payload: Any)->str:return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def computed(period: dict[str,Any], label: str)->tuple[Decimal,Decimal]:
    revenue=dec(period["gross_ordered_revenue"],f"{label}.gross_ordered_revenue",nonnegative=True)-sum((dec(period[x],f"{label}.{x}",nonnegative=True) for x in REVERSALS),Decimal("0"))
    profit=revenue-sum((dec(period[x],f"{label}.{x}",nonnegative=True) for x in COSTS),Decimal("0"))
    return revenue,profit

def build(payload: dict[str,Any])->dict[str,Any]:
    if payload.get("external_write") is not False: raise BridgeError("PPFC_EXTERNAL_WRITE_FORBIDDEN")
    validate_contract(payload)
    errors=[]; values={}
    for label in ("baseline","comparison"):
        revenue,profit=computed(payload[label],label); values[label]=(revenue,profit)
        if revenue!=dec(payload[label]["recognized_net_revenue"],f"{label}.recognized_net_revenue"): errors.append(f"REVENUE_NOT_CONSERVED:{label}")
        if profit!=dec(payload[label]["operating_profit"],f"{label}.operating_profit"): errors.append(f"PROFIT_NOT_CONSERVED:{label}")
    delta={field:exact(dec(payload["comparison"][field],field)-dec(payload["baseline"][field],field)) for field in ("gross_ordered_revenue",)+REVERSALS+COSTS}
    revenue_delta=values["comparison"][0]-values["baseline"][0]; profit_delta=values["comparison"][1]-values["baseline"][1]
    revenue_bridge=dec(delta["gross_ordered_revenue"],"delta")-sum((dec(delta[x],x) for x in REVERSALS),Decimal("0"))
    profit_bridge=revenue_bridge-sum((dec(delta[x],x) for x in COSTS),Decimal("0"))
    if revenue_bridge!=revenue_delta: errors.append("REVENUE_DELTA_NOT_CONSERVED")
    if profit_bridge!=profit_delta: errors.append("PROFIT_DELTA_NOT_CONSERVED")
    result={"bridge_id":payload["bridge_id"],"subject_id":payload["subject_id"],"subject_version":payload["subject_version"],"owner":"D06","status":"blocked" if errors else "validated","action_ceiling":"analysis_only" if errors else "reconciliation_only","scope":{"currency":payload["currency"],"tax_basis":payload["tax_basis"],"quantity_unit":payload["quantity_unit"],"timezone":payload["timezone"],"baseline_window":payload["baseline_window"],"comparison_window":payload["comparison_window"]},"component_deltas":delta,"recognized_net_revenue_delta":exact(revenue_delta),"operating_profit_delta":exact(profit_delta),"blocking_errors":errors,"allowed_uses":["cross_domain_financial_reconciliation"],"forbidden_uses":["causal_claim","capital_approval","business_action_approval","external_write"],"input_hash":canonical_hash(payload),"external_write":False}
    result["result_hash"]=canonical_hash(result); return result

def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("input",type=Path);parser.add_argument("--output",type=Path);args=parser.parse_args()
    try: result=build(json.loads(args.input.read_text()))
    except (OSError,json.JSONDecodeError,BridgeError,KeyError) as exc: print(f"PPFC_PERIOD_DELTA_BRIDGE=BLOCKED: {exc}",file=sys.stderr);return 2
    rendered=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(rendered)
    else: print(rendered,end="")
    return 0 if result["status"]=="validated" else 2
if __name__=="__main__":raise SystemExit(main())
