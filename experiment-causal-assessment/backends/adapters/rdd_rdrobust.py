#!/usr/bin/env python3
"""JSON-only rdrobust adapter; adapter existence is not backend verification."""

from __future__ import annotations

import importlib.metadata
import json
import math
import sys

EXPECTED_VERSION = "2.0.0"
BACKEND_ID = "rdd_local"
CANDIDATE_ID = "rdd_local_rdrobust"


class AdapterError(Exception):
    def __init__(self, code: str, message: str, details=None):
        super().__init__(message)
        self.code, self.details = code, details


def finite_vector(value, field: str, minimum: int = 1):
    if not isinstance(value, list) or len(value) < minimum or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in value):
        raise AdapterError("BACKEND_REQUEST_INVALID", f"{field} must contain at least {minimum} finite numbers")
    return value


def scalar(frame, row: str, column: str) -> float:
    value = float(frame.loc[row, column])
    if not math.isfinite(value):
        raise AdapterError("BACKEND_NUMERICAL_INVALID", f"Non-finite rdrobust output at {row}.{column}")
    return value


def run(request: dict) -> dict:
    if importlib.metadata.version("rdrobust") != EXPECTED_VERSION:
        raise AdapterError("BACKEND_VERSION_MISMATCH", "rdrobust version differs from adapter lock")
    from rdrobust import rdrobust

    outcome = finite_vector(request.get("outcome"), "outcome", 20)
    running = finite_vector(request.get("running"), "running", 20)
    if len(outcome) != len(running):
        raise AdapterError("BACKEND_REQUEST_INVALID", "outcome and running must have equal length")
    cutoff = request.get("cutoff")
    if isinstance(cutoff, bool) or not isinstance(cutoff, (int, float)) or not math.isfinite(cutoff):
        raise AdapterError("BACKEND_REQUEST_INVALID", "cutoff must be finite numeric")
    if not any(x < cutoff for x in running) or not any(x >= cutoff for x in running):
        raise AdapterError("RDD_SUPPORT_INADEQUATE", "Running variable requires observations on both sides of cutoff")
    assignment = request.get("assignment_type")
    if assignment not in {"sharp", "fuzzy"}:
        raise AdapterError("INVALID_RDD_TYPE", "assignment_type must be sharp or fuzzy")
    treatment = None
    if assignment == "fuzzy":
        treatment = finite_vector(request.get("treatment"), "treatment", 20)
        if len(treatment) != len(outcome) or not set(treatment).issubset({0, 1}) or len(set(treatment)) != 2:
            raise AdapterError("FUZZY_RDD_TREATMENT_MISSING", "Fuzzy treatment must be aligned binary 0/1")
    p, q = request.get("polynomial_order"), request.get("bias_order")
    if p != 1 or q != 2:
        raise AdapterError("RDD_PRIMARY_ORDER_INVALID", "Primary adapter requires p=1 and q=2")
    kernel_map = {"triangular": "tri", "uniform": "uni", "epanechnikov": "epa"}
    kernel, bwselect = request.get("kernel"), request.get("bandwidth_rule")
    if kernel not in kernel_map or bwselect not in {"mserd", "msetwo", "cerrd", "certwo"}:
        raise AdapterError("RDD_SPECIFICATION_INVALID", "Unsupported kernel or bandwidth selector")
    level = request.get("confidence_level", 0.95)
    if isinstance(level, bool) or not isinstance(level, (int, float)) or not 0 < level < 1:
        raise AdapterError("BACKEND_CONFIDENCE_LEVEL_INVALID", "confidence_level must be in (0,1)")
    result = rdrobust(y=outcome, x=running, c=cutoff, fuzzy=treatment, p=p, q=q, kernel=kernel_map[kernel], bwselect=bwselect, level=100 * level)
    conventional = scalar(result.coef, "Conventional", "Coeff")
    corrected = scalar(result.coef, "Bias-Corrected", "Coeff")
    robust_se = scalar(result.se, "Robust", "Std. Err.")
    lower = scalar(result.ci, "Robust", "CI Lower")
    upper = scalar(result.ci, "Robust", "CI Upper")
    p_value = scalar(result.pv, "Robust", "P>|z|")
    h_left, h_right = scalar(result.bws, "h", "left"), scalar(result.bws, "h", "right")
    b_left, b_right = scalar(result.bws, "b", "left"), scalar(result.bws, "b", "right")
    effective = [int(x) for x in result.N_h]
    if robust_se < 0 or lower > upper or not 0 <= p_value <= 1 or min(effective) < 2:
        raise AdapterError("BACKEND_NUMERICAL_INVALID", "RDD output failed numerical invariants")
    warnings = ["local_cutoff_estimand_only", "density_covariate_donut_placebo_diagnostics_required_outside_adapter", "external_parity_and_simulation_pending"]
    return {"conventional_effect":conventional,"bias_corrected_effect":corrected,"robust_standard_error":robust_se,"robust_confidence_interval":{"level":level,"lower":lower,"upper":upper},"robust_p_value":p_value,"bandwidths":{"estimation":{"left":h_left,"right":h_right},"bias":{"left":b_left,"right":b_right},"selector":bwselect},"effective_sample":{"left":effective[0],"right":effective[1]},"polynomial_order":p,"bias_order":q,"kernel":kernel,"assignment_type":assignment,"warnings":warnings}


def response(ok, result=None, error=None):
    return {"schema_version":"1.0.0","backend_id":BACKEND_ID,"candidate_id":CANDIDATE_ID,"package":"rdrobust","version":EXPECTED_VERSION,"ok":ok,"result":result,"warnings":result.get("warnings", []) if result else [],"error":error}


try:
    request = json.load(sys.stdin)
    if not isinstance(request, dict):
        raise AdapterError("BACKEND_REQUEST_INVALID", "Request must be a JSON object")
    output = response(True, run(request))
except AdapterError as exc:
    output = response(False, error={"code":exc.code,"message":str(exc),"details":exc.details})
except Exception as exc:
    output = response(False, error={"code":"BACKEND_INTERNAL_ERROR","message":str(exc),"details":None})
json.dump(output, sys.stdout, allow_nan=False, separators=(",", ":"))
