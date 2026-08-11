#!/usr/bin/env python3
"""JSON-only weak-IV adapter; adapter existence is not backend verification."""

from __future__ import annotations

import importlib.metadata
import json
import math
import sys

EXPECTED_VERSION = "0.10.0"
BACKEND_ID = "weak_iv"
CANDIDATE_ID = "weak_iv_ivmodels"


class AdapterError(Exception):
    def __init__(self, code, message, details=None):
        super().__init__(message); self.code, self.details = code, details


def matrix(value, field, rows=None):
    if not isinstance(value, list) or not value:
        raise AdapterError("BACKEND_REQUEST_INVALID", f"{field} must be a non-empty array")
    normalized = [[x] for x in value] if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in value) else value
    if not all(isinstance(row, list) and row for row in normalized) or len({len(row) for row in normalized}) != 1:
        raise AdapterError("BACKEND_REQUEST_INVALID", f"{field} must be rectangular")
    if rows is not None and len(normalized) != rows:
        raise AdapterError("BACKEND_REQUEST_INVALID", f"{field} row count differs")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for row in normalized for x in row):
        raise AdapterError("BACKEND_REQUEST_INVALID", f"{field} must be finite numeric")
    return normalized


def quadric_payload(value):
    import numpy as np
    return {"display":str(value),"A":np.asarray(value.A,dtype=float).tolist(),"b":np.asarray(value.b,dtype=float).tolist(),"c":float(value.c),"interpretation":"acceptance_set_of_weak_robust_test; may be bounded, unbounded, empty, or disconnected"}


def run(request):
    if importlib.metadata.version("ivmodels") != EXPECTED_VERSION:
        raise AdapterError("BACKEND_VERSION_MISMATCH", "ivmodels version differs from adapter lock")
    import numpy as np
    from ivmodels import KClass, tests
    y_raw = request.get("outcome")
    if not isinstance(y_raw, list) or len(y_raw) < 20 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in y_raw):
        raise AdapterError("BACKEND_REQUEST_INVALID", "outcome must contain at least 20 finite values")
    n=len(y_raw); y=np.asarray(y_raw,dtype=float)
    x=np.asarray(matrix(request.get("endogenous"),"endogenous",n),dtype=float)
    z=np.asarray(matrix(request.get("instruments"),"instruments",n),dtype=float)
    if x.shape[1] != 1:
        raise AdapterError("IV_SCOPE_UNSUPPORTED", "Current adapter supports one endogenous regressor")
    c_raw=request.get("exogenous")
    c=None if c_raw in (None,[]) else np.asarray(matrix(c_raw,"exogenous",n),dtype=float)
    estimator=request.get("estimator")
    if estimator not in {"2SLS","LIML"}:
        raise AdapterError("IV_ESTIMATOR_INVALID", "estimator must be 2SLS or LIML")
    null=request.get("null_value",0)
    level=request.get("confidence_level",.95)
    if isinstance(null,bool) or not isinstance(null,(int,float)) or not math.isfinite(null) or isinstance(level,bool) or not isinstance(level,(int,float)) or not 0<level<1:
        raise AdapterError("BACKEND_REQUEST_INVALID", "null_value must be finite and confidence_level in (0,1)")
    requested=request.get("weak_robust_test")
    if requested not in {"anderson_rubin","conditional_likelihood_ratio","both"}:
        raise AdapterError("WEAK_IV_INFERENCE_REQUIRED", "weak_robust_test must be anderson_rubin, conditional_likelihood_ratio, or both")
    fit=KClass(kappa=1 if estimator=="2SLS" else "liml").fit(Z=z,X=x,y=y,C=c)
    effect=float(fit.coef_[0])
    rank_stat,rank_p=tests.rank_test(z,x,C=c)
    beta=np.asarray([float(null)])
    test_outputs={}; sets={}
    if requested in {"anderson_rubin","both"}:
        stat,p=tests.anderson_rubin_test(z,x,y,beta=beta,C=c)
        test_outputs["anderson_rubin"]={"statistic":float(stat),"p_value":float(p)}
        sets["anderson_rubin"]=quadric_payload(tests.inverse_anderson_rubin_test(z,x,y,alpha=1-level,C=c))
    if requested in {"conditional_likelihood_ratio","both"}:
        stat,p=tests.conditional_likelihood_ratio_test(z,x,y,beta=beta,C=c)
        test_outputs["conditional_likelihood_ratio"]={"statistic":float(stat),"p_value":float(p)}
        sets["conditional_likelihood_ratio"]=quadric_payload(tests.inverse_conditional_likelihood_ratio_test(z,x,y,alpha=1-level,C=c))
    numbers=[effect,float(rank_stat),float(rank_p)]+[v[k] for v in test_outputs.values() for k in ("statistic","p_value")]
    if any(not math.isfinite(v) for v in numbers) or not 0<=float(rank_p)<=1 or any(not 0<=v["p_value"]<=1 for v in test_outputs.values()):
        raise AdapterError("BACKEND_NUMERICAL_INVALID", "IV output failed numerical invariants")
    warnings=["weak_robust_inference_does_not_validate_instrument_assumptions","LATE_or_CACE_scope_only","external_parity_and_simulation_pending"]
    return {"effect":effect,"estimator":estimator,"first_stage_rank_test":{"statistic":float(rank_stat),"p_value":float(rank_p)},"weak_robust_test":requested,"weak_robust_results":test_outputs,"weak_robust_confidence_sets":sets,"confidence_level":level,"null_value":float(null),"warnings":warnings}


def response(ok,result=None,error=None):
    return {"schema_version":"1.0.0","backend_id":BACKEND_ID,"candidate_id":CANDIDATE_ID,"package":"ivmodels","version":EXPECTED_VERSION,"ok":ok,"result":result,"warnings":result.get("warnings",[]) if result else [],"error":error}


try:
    request=json.load(sys.stdin)
    if not isinstance(request,dict): raise AdapterError("BACKEND_REQUEST_INVALID","Request must be a JSON object")
    output=response(True,run(request))
except AdapterError as exc:
    output=response(False,error={"code":exc.code,"message":str(exc),"details":exc.details})
except Exception as exc:
    output=response(False,error={"code":"BACKEND_INTERNAL_ERROR","message":str(exc),"details":None})
json.dump(output,sys.stdout,allow_nan=False,separators=(",",":"))
