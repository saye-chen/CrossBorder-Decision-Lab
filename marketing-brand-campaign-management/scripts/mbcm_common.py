#!/usr/bin/env python3
"""Shared deterministic validation and CLI helpers for MBCM."""
from __future__ import annotations
import datetime, hashlib, json, math, pathlib, sys

RUNTIME="MBCM-2026.01"

class ModelError(ValueError): pass

def finite(value,name,minimum=None,maximum=None):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ModelError(f"{name}:finite_number_required")
    value=float(value)
    if minimum is not None and value < minimum: raise ModelError(f"{name}:below_minimum")
    if maximum is not None and value > maximum: raise ModelError(f"{name}:above_maximum")
    return value

def text(value,name):
    if not isinstance(value,str) or not value.strip(): raise ModelError(f"{name}:nonempty_string_required")
    return value.strip()

def boolean(value,name):
    if not isinstance(value,bool): raise ModelError(f"{name}:boolean_required")
    return value

def sequence(value,name,allow_empty=True):
    if not isinstance(value,list): raise ModelError(f"{name}:list_required")
    if not allow_empty and not value: raise ModelError(f"{name}:nonempty_required")
    return value

def iso_datetime(value,name):
    value=text(value,name)
    try:
        normalized=value[:-1]+"+00:00" if value.endswith("Z") else value
        return datetime.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ModelError(f"{name}:iso_datetime_required") from exc

def require(data,*names):
    if not isinstance(data,dict): raise ModelError("input:object_required")
    missing=[x for x in names if x not in data]
    if missing: raise ModelError("missing:"+",".join(missing))

def sha(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return "sha256:"+hashlib.sha256(raw).hexdigest()

def envelope(model,data,result,warnings=None):
    return {"runtime":RUNTIME,"model":model,"model_version":"1.0","status":"complete",
            "input_hash":sha(data),"output_hash":sha(result),"result":result,
            "warnings":warnings or [],"production_claim":False}

def read_input(path=None):
    if path: return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)

def run_cli(fn,model):
    try:
        data=read_input(sys.argv[1] if len(sys.argv)>1 else None)
        print(json.dumps(envelope(model,data,fn(data)),ensure_ascii=False,sort_keys=True))
    except (ModelError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"runtime":RUNTIME,"model":model,"status":"invalid","errors":[str(exc)],
                          "production_claim":False},ensure_ascii=False,sort_keys=True))
        raise SystemExit(2)
