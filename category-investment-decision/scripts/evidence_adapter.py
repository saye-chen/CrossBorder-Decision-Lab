#!/usr/bin/env python3
"""Fail-closed external evidence normalization with deterministic lineage."""
from __future__ import annotations
import hashlib
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

class AdapterError(ValueError): pass

def _hash(value: Any) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return "sha256:"+hashlib.sha256(raw.encode()).hexdigest()

def normalize(raw: dict[str, Any], contract: dict[str, Any], *, as_of: date | None=None) -> dict[str, Any]:
    if not isinstance(raw,dict) or raw.get("error") is not None: raise AdapterError("source response missing or contains error")
    required={"source","source_family_id","raw_evidence_id","observed_at","fields"}
    if required-set(contract): raise AdapterError("adapter contract incomplete")
    if not contract["source_family_id"] or not contract["raw_evidence_id"]: raise AdapterError("lineage identity required")
    try: observed=date.fromisoformat(contract["observed_at"])
    except (TypeError,ValueError) as exc: raise AdapterError("observed_at must be ISO date") from exc
    max_age=contract.get("max_age_days")
    if max_age is not None and ((as_of or date.today())-observed).days>int(max_age): raise AdapterError("source evidence is stale")
    normalized={}; lineage=[]; warnings=[]
    for target,spec in contract["fields"].items():
        source_field=spec.get("source_field")
        if not source_field or source_field not in raw or raw[source_field] is None:
            if spec.get("required",True): raise AdapterError(f"missing required source field: {source_field}")
            normalized[target]=None; warnings.append(f"optional field missing: {source_field}"); continue
        value=raw[source_field]
        if spec.get("kind")=="ratio":
            try: value=Decimal(str(value))
            except InvalidOperation as exc: raise AdapterError(f"ratio is not numeric: {source_field}") from exc
            scale=spec.get("scale")
            if scale=="0-100": value/=Decimal("100")
            elif scale!="0-1": raise AdapterError(f"unknown ratio scale: {source_field}")
            if value<0 or value>1: raise AdapterError(f"ratio outside 0-1: {source_field}")
            value=str(value)
        normalized[target]=value
        lineage.append({"target_field":target,"source_field":source_field,"transformation":spec.get("kind","identity"),"unit":spec.get("unit"),"scale":"0-1" if spec.get("kind")=="ratio" else spec.get("scale")})
    result={"status":"normalized","source":contract["source"],"source_family_id":contract["source_family_id"],"raw_evidence_id":contract["raw_evidence_id"],"observed_at":contract["observed_at"],"normalized_fields":normalized,"transformation_lineage":lineage,"warnings":warnings,"raw_hash":_hash(raw),"contract_hash":_hash(contract)}
    result["output_hash"]=_hash(result)
    return result
