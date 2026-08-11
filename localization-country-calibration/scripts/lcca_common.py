#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any

class LCCAError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message); self.code=code

def parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value,str) or not value: raise LCCAError("TIME_INVALID",f"{field} is required")
    try: result=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc: raise LCCAError("TIME_INVALID",f"{field} is invalid") from exc
    if result.tzinfo is None: raise LCCAError("TIMEZONE_UNRESOLVED",f"{field} requires timezone")
    return result

def decimal(value: Any, field: str) -> Decimal:
    if not isinstance(value,str): raise LCCAError("DECIMAL_STRING_REQUIRED",f"{field} must be decimal string")
    try: result=Decimal(value)
    except InvalidOperation as exc: raise LCCAError("DECIMAL_INVALID",f"{field} is invalid") from exc
    if not result.is_finite(): raise LCCAError("DECIMAL_INVALID",f"{field} must be finite")
    return result

def canonical_hash(value: Any) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    return "sha256:"+hashlib.sha256(raw).hexdigest()

def quantize(value: Decimal, precision: str) -> Decimal:
    return value.quantize(Decimal(precision),rounding=ROUND_HALF_EVEN)

def require_false(payload: dict[str,Any]) -> None:
    if payload.get("external_write") is not False: raise LCCAError("EXTERNAL_WRITE_FORBIDDEN","external_write must be false")

ACTION_RANK={"analysis_only":0,"controlled_test":1,"reversible_action":2,"human_approved_execution":3}
def narrower_action(left: str,right: str) -> str:
    if left not in ACTION_RANK or right not in ACTION_RANK: raise LCCAError("ACTION_CEILING_INVALID","unknown action ceiling")
    return min((left,right),key=ACTION_RANK.get)
