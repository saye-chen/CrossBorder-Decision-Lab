#!/usr/bin/env python3
"""Execute every locked development adapter on deterministic non-production fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
from pathlib import Path

from verify_backend_runtime import verify


ROOT = Path(__file__).resolve().parents[1]


def _rows(seed: int, count: int, effect) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for index in range(count):
        x1, x2 = rng.gauss(0, 1), rng.gauss(0, 1)
        treatment = index % 2
        group = "high" if x1 >= 0 else "low"
        treatment_effect = effect(x1) if callable(effect) else effect
        outcome = 2 + 0.7 * x1 - 0.3 * x2 + treatment_effect * treatment + rng.gauss(0, 0.6)
        rows.append({"y": outcome, "w": treatment, "x1": x1, "x2": x2, "group": group, "partition": "development" if index < count // 2 else "evaluation", "current": index % 3 == 0})
    return rows


def fixtures() -> dict[str, dict]:
    cluster_rows = []
    cluster_means = [-1.5, -0.5, 0.5, 1.5, 1.0, 2.0, 3.0, 4.0]
    for cluster, mean in enumerate(cluster_means):
        treatment = 0 if cluster < 4 else 1
        for offset in (-0.1, 0.1):
            cluster_rows.append({"y": mean + offset, "t": treatment, "cluster": f"c{cluster + 1}"})
    information = [0.33, 0.67, 1.0]
    allowed = [[0,0,1,1],[0,1,0,1],[0,1,1,0],[1,0,0,1],[1,0,1,0],[1,1,0,0]]
    rdd_running = [(-100 + index) / 100 for index in range(100)] + [(index + 1) / 100 for index in range(100)]
    rdd_outcome = [1 + 2 * x + (3 if x >= 0 else 0) + 0.03 * math.sin(13 * x) for x in rdd_running]
    rng = random.Random(20260810)
    instruments, endogenous, outcomes = [], [], []
    for _ in range(300):
        z = rng.gauss(0, 1); v = rng.gauss(0, 0.5); epsilon = rng.gauss(0, 0.5)
        x = 0.9 * z + v
        instruments.append([z]); endogenous.append([x]); outcomes.append(2 * x + epsilon)
    dml_rows = _rows(20260811, 400, 1.5)
    hte_rows = _rows(20260812, 400, lambda x: 1 if x < 0 else 3)
    did_rows = []
    for unit in range(30):
        first = 0 if unit < 15 else 5
        for period in range(1, 9):
            did_rows.append({"unit": unit + 1, "time": period, "g": first, "y": unit * 0.07 + period * 0.15 + (2 if first and period >= first else 0) + 0.02 * math.sin(unit + period)})
    scm_rows = []
    for unit in range(1, 6):
        for period in range(1, 11):
            donor = unit * 0.4 + period * 0.3 + 0.05 * math.sin(unit * period)
            outcome = donor
            if unit == 1:
                outcome = 0.5 * (2 * 0.4 + period * 0.3 + 0.05 * math.sin(2 * period)) + 0.5 * (3 * 0.4 + period * 0.3 + 0.05 * math.sin(3 * period)) + (2 if period >= 7 else 0)
            scm_rows.append({"unit": unit, "time": period, "y": outcome, "predictor": unit * 0.2 + period * 0.01})
    matrix = []
    for unit in range(10):
        matrix.append([unit * 0.1 + period * 0.2 + (2 if unit >= 8 and period >= 6 else 0) + 0.01 * math.sin(unit + period) for period in range(10)])
    observational = _rows(20260813, 400, 1.5)
    return {
        "cluster_cr2_clubsandwich": {"rows": cluster_rows, "outcome_column": "y", "treatment_column": "t", "cluster_column": "cluster", "confidence_level": 0.95, "null_value": 0},
        "group_sequential_gsdesign": {"sided": 1, "alpha": 0.025, "power": 0.8, "information_fractions": information, "effect_scale": "z_statistic", "futility_binding": True, "efficacy_spending": "obrien_fleming", "futility_spending": "hwang_shih_decani", "futility_parameters": {"gamma": -2}, "observed_z_statistics": [0.2, 0.5, 2.2]},
        "switchback_randomization_ri2": {"randomization_scheme": "custom_sequence", "period_id": ["p1","p2","p3","p4"], "period_start": ["2026-01-01T00:00:00Z","2026-01-01T01:00:00Z","2026-01-01T02:00:00Z","2026-01-01T03:00:00Z"], "period_end": ["2026-01-01T01:00:00Z","2026-01-01T02:00:00Z","2026-01-01T03:00:00Z","2026-01-01T04:00:00Z"], "observed_sequence": [0,1,0,1], "arm": [0,1,0,1], "outcome": [1,4,2,5], "washout_excluded": [True,True,True,True], "test_statistic": "difference_in_period_means", "sharp_null": 0, "allowed_sequences": allowed, "maximum_enumerations": 100, "seed_contract": {"mode": "exact_enumeration", "seed": None}, "periodicity_terms": ["hour_of_day"], "lagged_treatment_terms": ["lag_1"]},
        "staggered_did_callaway_santanna": {"rows": did_rows, "outcome_column": "y", "time_column": "time", "unit_column": "unit", "first_treatment_time_column": "g", "control_group": "never_treated", "anticipation_periods": 0, "confidence_level": 0.95, "bootstrap_iterations": 999, "cluster_column": None, "panel_structure": "panel", "allow_unbalanced_panel": False},
        "synthetic_control_synth": {"rows": scm_rows, "unit_column": "unit", "time_column": "time", "outcome_column": "y", "predictor_columns": ["predictor"], "treated_unit": 1, "donor_pool": [2,3,4,5], "pre_periods": [1,2,3,4,5,6], "post_periods": [7,8,9,10], "time_placebo_pre_periods": [1,2,3,4], "time_placebo_post_periods": [5,6]},
        "synthetic_did_synthdid": {"outcome_matrix": matrix, "control_unit_count": 8, "pre_period_count": 6, "uncertainty_method": "placebo", "replications": 200, "seed": 20260810, "confidence_level": 0.95},
        "rdd_local_rdrobust": {"outcome": rdd_outcome, "running": rdd_running, "cutoff": 0, "assignment_type": "sharp", "polynomial_order": 1, "bias_order": 2, "kernel": "triangular", "bandwidth_rule": "mserd", "confidence_level": 0.95},
        "weak_iv_ivmodels": {"outcome": outcomes, "endogenous": endogenous, "instruments": instruments, "exogenous": None, "estimator": "LIML", "null_value": 2, "confidence_level": 0.95, "weak_robust_test": "both"},
        "observational_aipw_r": {"outcome": [row["y"] for row in observational], "treatment": [row["w"] for row in observational], "covariates": [[row["x1"],row["x2"]] for row in observational], "estimand": "ATE", "folds": 2, "seed": 20260810, "outcome_learners": ["SL.mean","SL.glm"], "propensity_learners": ["SL.mean","SL.glm"], "propensity_bounds": [0.05,0.95], "confidence_level": 0.95},
        "observational_dml_doubleml": {"rows": dml_rows, "outcome_column": "y", "treatment_column": "w", "covariate_columns": ["x1","x2"], "score": "ATE", "folds": 2, "repetitions": 1, "seed": 20260810, "propensity_bounds": [0.05,0.95], "outcome_learner": "linear", "propensity_learner": "logistic", "confidence_level": 0.95},
        "hte_uplift_econml": {"rows": hte_rows, "outcome_column": "y", "treatment_column": "w", "group_column": "group", "partition_column": "partition", "baseline_policy_column": "current", "covariate_columns": ["x1","x2"], "source_design": "randomized", "known_treatment_probability": 0.5, "folds": 2, "seed": 20260810, "n_estimators": 100, "min_samples_leaf": 10, "calibration_groups": 3, "bootstrap_repetitions": 100, "confidence_level": 0.95, "propensity_bounds": [0.05,0.95], "policy_threshold": 0, "acceptance_policy": {"minimum_calibration_r_squared": 0, "minimum_blp_lower_bound": 0, "minimum_Qini_lower_bound": 0, "minimum_AUTOC_lower_bound": 0, "ranking_rule": "any_positive_ranking_metric", "primary_policy_baseline": "treat_all", "minimum_policy_value_improvement": 0}},
        "hte_uplift_grf": {"rows": hte_rows, "outcome_column": "y", "treatment_column": "w", "group_column": "group", "partition_column": "partition", "covariate_columns": ["x1","x2"], "known_treatment_probability": 0.5, "num_trees": 500, "seed": 20260810, "confidence_level": 0.95},
    }


ADAPTERS = {
    "cluster_cr2_clubsandwich": ("r", "backends/adapters/cluster_clubsandwich.R"),
    "group_sequential_gsdesign": ("r", "backends/adapters/group_sequential_gsdesign.R"),
    "switchback_randomization_ri2": ("r", "backends/adapters/switchback_ri2.R"),
    "staggered_did_callaway_santanna": ("r", "backends/adapters/staggered_did_callaway_santanna.R"),
    "synthetic_control_synth": ("r", "backends/adapters/synthetic_control_synth.R"),
    "synthetic_did_synthdid": ("r", "backends/adapters/synthetic_did_synthdid.R"),
    "rdd_local_rdrobust": ("python", "backends/adapters/rdd_rdrobust.py"),
    "weak_iv_ivmodels": ("python", "backends/adapters/weak_iv_ivmodels.py"),
    "observational_aipw_r": ("r", "backends/adapters/observational_aipw.R"),
    "observational_dml_doubleml": ("python", "backends/adapters/observational_dml_doubleml.py"),
    "hte_uplift_econml": ("python", "backends/adapters/hte_uplift_econml.py"),
    "hte_uplift_grf": ("r", "backends/adapters/hte_uplift_grf.R"),
}


def _execute(executable: str, relative: str, request: dict, kind: str) -> dict:
    command = [executable, "--vanilla", str(ROOT / relative)] if kind == "r" else [executable, str(ROOT / relative)]
    result = subprocess.run(command, input=json.dumps(request, separators=(",", ":")), text=True, capture_output=True, timeout=600, check=False)
    if result.returncode:
        return {"status": "process_failed", "returncode": result.returncode, "stderr": result.stderr[-1500:]}
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "invalid_json", "stdout": result.stdout[-1500:], "stderr": result.stderr[-1500:]}
    digest = hashlib.sha256(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return {"status": "pass" if output.get("ok") is True else "adapter_failed", "output_sha256": digest, "error": output.get("error"), "warnings": output.get("warnings", [])}


def run(python_executable: str, rscript_executable: str, selected: set[str] | None = None) -> dict:
    runtime = verify(python_executable, rscript_executable)
    frozen = fixtures()
    results = {}
    for candidate, (kind, relative) in ADAPTERS.items():
        if selected and candidate not in selected:
            continue
        executable = rscript_executable if kind == "r" else python_executable
        results[candidate] = _execute(executable, relative, frozen[candidate], kind)
    return {
        "schema_version": "1.0.0",
        "report_id": "ECAE-PERSISTENT-BACKEND-DEVELOPMENT-QUALIFICATION-2026-08-10",
        "qualification": "implementer_owned_fixed_vectors_not_external_parity_or_independent_review",
        "runtime": runtime,
        "adapter_results": results,
        "all_adapters_pass": bool(results) and all(item["status"] == "pass" for item in results.values()),
        "registry_promotion_authorized": False,
        "business_action_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=os.environ.get("ECAE_PYTHON_BACKEND"))
    parser.add_argument("--rscript", default=os.environ.get("ECAE_RSCRIPT_BACKEND"))
    parser.add_argument("--candidate", action="append", choices=sorted(ADAPTERS))
    args = parser.parse_args()
    if not args.python or not args.rscript:
        parser.error("--python and --rscript or their ECAE environment variables are required")
    report = run(args.python, args.rscript, set(args.candidate or []))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["all_adapters_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
