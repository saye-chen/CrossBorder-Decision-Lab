#!/usr/bin/env python3
"""JSON-only honest HTE/uplift adapter; existence is not backend verification."""

from __future__ import annotations

import importlib.metadata
import json
import math
import re
import statistics
import sys


EXPECTED_VERSION = "0.16.0"
BACKEND_ID = "hte_uplift"
CANDIDATE_ID = "hte_uplift_econml"
SAFE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class AdapterError(Exception):
    def __init__(self, code: str, message: str, details=None):
        super().__init__(message)
        self.code, self.details = code, details


def finite(value, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AdapterError("BACKEND_REQUEST_INVALID", f"{field} must be finite numeric")
    return float(value)


def integer(value, field: str, lower: int, upper: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not lower <= value <= upper:
        raise AdapterError("HTE_CONFIGURATION_INVALID", f"{field} must be an integer from {lower} through {upper}")
    return value


def safe_name(value, field: str) -> str:
    if not isinstance(value, str) or not SAFE_NAME.fullmatch(value):
        raise AdapterError("BACKEND_COLUMN_INVALID", f"{field} must be a safe column name")
    return value


def interval(values, level: float, *, multiplier: float | None = None) -> dict:
    import numpy as np

    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise AdapterError("BACKEND_NUMERICAL_INVALID", "Interval input is invalid")
    estimate = float(np.mean(values))
    standard_error = float(np.std(values, ddof=1) / math.sqrt(len(values)))
    z = multiplier if multiplier is not None else statistics.NormalDist().inv_cdf((1 + level) / 2)
    lower, upper = estimate - z * standard_error, estimate + z * standard_error
    if not all(math.isfinite(x) for x in (estimate, standard_error, lower, upper)) or standard_error < 0 or lower > upper:
        raise AdapterError("BACKEND_NUMERICAL_INVALID", "Interval output failed numerical invariants")
    return {"estimate": estimate, "standard_error": standard_error, "confidence_interval": {"level": level, "lower": lower, "upper": upper}, "sample_size": int(len(values))}


def run(request: dict) -> dict:
    if importlib.metadata.version("econml") != EXPECTED_VERSION:
        raise AdapterError("BACKEND_VERSION_MISMATCH", "econml version differs from adapter lock")

    import numpy as np
    import pandas as pd
    from econml.dml import CausalForestDML
    from econml.validate import DRTester
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

    rows = request.get("rows")
    if not isinstance(rows, list) or len(rows) < 200 or not all(isinstance(row, dict) for row in rows):
        raise AdapterError("BACKEND_REQUEST_INVALID", "rows must contain at least 200 objects")
    names = {field: safe_name(request.get(field), field) for field in ("outcome_column", "treatment_column", "group_column", "partition_column", "baseline_policy_column")}
    covariates = request.get("covariate_columns")
    if not isinstance(covariates, list) or not covariates or len(covariates) != len(set(covariates)) or any(not isinstance(name, str) or not SAFE_NAME.fullmatch(name) for name in covariates):
        raise AdapterError("BACKEND_COLUMN_INVALID", "covariate_columns must contain distinct safe names")
    required = set(names.values()) | set(covariates)
    if any(set(row) < required for row in rows):
        raise AdapterError("BACKEND_COLUMN_MISSING", "Every row requires outcome treatment group partition baseline policy and covariates")
    data = pd.DataFrame(rows)
    numeric = [names["outcome_column"], names["treatment_column"], names["baseline_policy_column"], *covariates]
    try:
        data[numeric] = data[numeric].astype(float)
    except Exception as exc:
        raise AdapterError("BACKEND_REQUEST_INVALID", "Outcome treatment baseline policy and covariates must be numeric") from exc
    if not np.isfinite(data[numeric].to_numpy()).all():
        raise AdapterError("BACKEND_REQUEST_INVALID", "Analysis values must be finite")

    partition = names["partition_column"]
    observed_partitions = set(data[partition].astype(str))
    if observed_partitions != {"development", "evaluation"}:
        raise AdapterError("HTE_PARTITION_INVALID", "partition must contain exactly development and evaluation")
    development = data[data[partition].astype(str) == "development"].copy()
    evaluation = data[data[partition].astype(str) == "evaluation"].copy()
    if len(development) < 100 or len(evaluation) < 100:
        raise AdapterError("HTE_PARTITION_INVALID", "Both partitions require at least 100 rows")
    treatment = names["treatment_column"]
    baseline = names["baseline_policy_column"]
    if set(data[treatment].unique()) != {0.0, 1.0} or any(set(frame[treatment].unique()) != {0.0, 1.0} for frame in (development, evaluation)):
        raise AdapterError("HTE_TREATMENT_INVALID", "Both partitions require binary treatment arms 0 and 1")
    if not set(data[baseline].unique()).issubset({0.0, 1.0}):
        raise AdapterError("BACKEND_REQUEST_INVALID", "baseline policy must be binary 0/1")

    source_design = request.get("source_design")
    if source_design not in {"randomized", "observational_unconfounded"}:
        raise AdapterError("BACKEND_REQUEST_INVALID", "source_design is invalid")
    known_probability = request.get("known_treatment_probability")
    if source_design == "randomized":
        known_probability = finite(known_probability, "known_treatment_probability")
        if not 0 < known_probability < 1:
            raise AdapterError("BACKEND_REQUEST_INVALID", "known treatment probability must be in (0,1)")

    folds = integer(request.get("folds"), "folds", 2, 10)
    seed = integer(request.get("seed"), "seed", 0, 2**32 - 1)
    trees = integer(request.get("n_estimators"), "n_estimators", 100, 4000)
    if trees % 4:
        raise AdapterError("HTE_CONFIGURATION_INVALID", "n_estimators must be divisible by four for forest inference")
    leaf = integer(request.get("min_samples_leaf"), "min_samples_leaf", 5, 500)
    groups = integer(request.get("calibration_groups"), "calibration_groups", 3, 10)
    bootstrap = integer(request.get("bootstrap_repetitions"), "bootstrap_repetitions", 100, 10000)
    level = finite(request.get("confidence_level"), "confidence_level")
    if not 0 < level < 1:
        raise AdapterError("BACKEND_CONFIDENCE_LEVEL_INVALID", "confidence_level must be in (0,1)")
    propensity_bounds = request.get("propensity_bounds")
    if not isinstance(propensity_bounds, list) or len(propensity_bounds) != 2:
        raise AdapterError("HTE_CONFIGURATION_INVALID", "propensity_bounds requires [lower,upper]")
    lower_bound, upper_bound = (finite(item, "propensity_bounds") for item in propensity_bounds)
    if not 0 < lower_bound < upper_bound < 1:
        raise AdapterError("HTE_CONFIGURATION_INVALID", "propensity bounds must be ordered inside (0,1)")
    threshold = finite(request.get("policy_threshold"), "policy_threshold")
    acceptance = request.get("acceptance_policy")
    if not isinstance(acceptance, dict):
        raise AdapterError("HTE_CONFIGURATION_INVALID", "acceptance_policy must be an object")
    required_acceptance = {"minimum_calibration_r_squared", "minimum_blp_lower_bound", "minimum_Qini_lower_bound", "minimum_AUTOC_lower_bound", "ranking_rule", "primary_policy_baseline", "minimum_policy_value_improvement"}
    if set(acceptance) < required_acceptance:
        raise AdapterError("HTE_CONFIGURATION_INVALID", "acceptance_policy is incomplete", sorted(required_acceptance - set(acceptance)))
    acceptance_values = {field: finite(acceptance[field], f"acceptance_policy.{field}") for field in ("minimum_calibration_r_squared", "minimum_blp_lower_bound", "minimum_Qini_lower_bound", "minimum_AUTOC_lower_bound", "minimum_policy_value_improvement")}
    if acceptance["ranking_rule"] not in {"any_positive_ranking_metric", "all_ranking_metrics"}:
        raise AdapterError("HTE_CONFIGURATION_INVALID", "ranking_rule is invalid")
    if acceptance["primary_policy_baseline"] not in {"treat_all", "treat_none", "current_policy"}:
        raise AdapterError("HTE_CONFIGURATION_INVALID", "primary_policy_baseline is invalid")

    X_development = development[covariates].to_numpy()
    X_evaluation = evaluation[covariates].to_numpy()
    T_development = development[treatment].astype(int).to_numpy()
    T_evaluation = evaluation[treatment].astype(int).to_numpy()
    Y_development = development[names["outcome_column"]].to_numpy()
    Y_evaluation = evaluation[names["outcome_column"]].to_numpy()
    outcome_model = RandomForestRegressor(n_estimators=200, min_samples_leaf=leaf, max_depth=12, random_state=seed, n_jobs=1)
    propensity_model = RandomForestClassifier(n_estimators=200, min_samples_leaf=leaf, max_depth=12, random_state=seed, n_jobs=1)
    forest = CausalForestDML(
        model_y=outcome_model,
        model_t=propensity_model,
        discrete_treatment=True,
        cv=folds,
        n_estimators=trees,
        min_samples_leaf=leaf,
        honest=True,
        inference=True,
        random_state=seed,
        n_jobs=1,
    )
    forest.fit(Y_development, T_development, X=X_development)
    tester = DRTester(model_regression=outcome_model, model_propensity=propensity_model, cate=forest, cv=folds)
    tester.fit_nuisance(X_evaluation, T_evaluation, Y_evaluation, Xtrain=X_development, Dtrain=T_development, ytrain=Y_development)
    validation = tester.evaluate_all(Xval=X_evaluation, Xtrain=X_development, n_groups=groups, n_bootstrap=bootstrap)
    cate_predictions = np.asarray(tester.cate_preds_val_, dtype=float).reshape(-1)
    dr_scores = np.asarray(tester.dr_val_, dtype=float).reshape(len(evaluation), -1)[:, 0]
    if not np.isfinite(cate_predictions).all() or not np.isfinite(dr_scores).all():
        raise AdapterError("BACKEND_NUMERICAL_INVALID", "HTE predictions or doubly robust scores are non-finite")

    if source_design == "randomized":
        propensities = np.full(len(evaluation), known_probability, dtype=float)
    else:
        diagnostic_propensity = RandomForestClassifier(n_estimators=200, min_samples_leaf=leaf, max_depth=12, random_state=seed, n_jobs=1)
        diagnostic_propensity.fit(X_development, T_development)
        propensities = diagnostic_propensity.predict_proba(X_evaluation)[:, 1]
    if not np.isfinite(propensities).all() or np.min(propensities) < lower_bound or np.max(propensities) > upper_bound:
        raise AdapterError("HTE_OVERLAP_NOT_ESTABLISHED", "Evaluation propensity support violates frozen bounds")

    group_name = names["group_column"]
    labels = evaluation[group_name].astype(str)
    unique_groups = sorted(labels.unique())
    if len(unique_groups) < 2 or any(int((labels == label).sum()) < 20 for label in unique_groups):
        raise AdapterError("HTE_GROUP_INADEQUATE", "At least two groups with 20 evaluation rows each are required")
    simultaneous_alpha = (1 - level) / len(unique_groups)
    simultaneous_z = statistics.NormalDist().inv_cdf(1 - simultaneous_alpha / 2)
    gate = []
    for label in unique_groups:
        item = interval(dr_scores[(labels == label).to_numpy()], level, multiplier=simultaneous_z)
        item["group"] = label
        gate.append(item)

    candidate_policy = (cate_predictions >= threshold).astype(float)
    current_policy = evaluation[baseline].to_numpy()
    policies = {"candidate": candidate_policy, "treat_all": np.ones(len(evaluation)), "treat_none": np.zeros(len(evaluation)), "current_policy": current_policy}
    policy_values = {name: interval(rule * dr_scores, level) for name, rule in policies.items()}
    contrasts = {name: interval((candidate_policy - rule) * dr_scores, level) for name, rule in policies.items() if name != "candidate"}

    def one_result(obj) -> dict:
        estimate, standard_error, p_value = float(obj.params[0]), float(obj.errs[0]), float(obj.pvals[0])
        if not all(math.isfinite(x) for x in (estimate, standard_error, p_value)) or standard_error < 0 or not 0 <= p_value <= 1:
            raise AdapterError("BACKEND_NUMERICAL_INVALID", "Validation statistic failed numerical invariants")
        return {"estimate": estimate, "standard_error": standard_error, "p_value": p_value}

    blp = one_result(validation.blp)
    qini = one_result(validation.qini)
    autoc = one_result(validation.toc)
    calibration = float(validation.cal.cal_r_squared[0])
    if not math.isfinite(calibration):
        raise AdapterError("BACKEND_NUMERICAL_INVALID", "Calibration is non-finite")
    quantiles = np.quantile(cate_predictions, [0, .1, .25, .5, .75, .9, 1]).tolist()
    decision_z = statistics.NormalDist().inv_cdf((1 + level) / 2)
    lower_bounds = {
        "BLP": blp["estimate"] - decision_z * blp["standard_error"],
        "Qini": qini["estimate"] - decision_z * qini["standard_error"],
        "AUTOC": autoc["estimate"] - decision_z * autoc["standard_error"],
    }
    ranking_checks = {
        "Qini": lower_bounds["Qini"] >= acceptance_values["minimum_Qini_lower_bound"],
        "AUTOC": lower_bounds["AUTOC"] >= acceptance_values["minimum_AUTOC_lower_bound"],
    }
    ranking_pass = all(ranking_checks.values()) if acceptance["ranking_rule"] == "all_ranking_metrics" else any(ranking_checks.values())
    heterogeneity_supported = calibration >= acceptance_values["minimum_calibration_r_squared"] and lower_bounds["BLP"] >= acceptance_values["minimum_blp_lower_bound"] and ranking_pass
    primary_baseline = acceptance["primary_policy_baseline"]
    primary_contrast = contrasts[primary_baseline]
    policy_supported = primary_contrast["confidence_interval"]["lower"] >= acceptance_values["minimum_policy_value_improvement"]
    warnings = [
        "CATE_scores_are_conditional_average_predictions_not_individual_true_effects",
        "heterogeneity_identification_inherits_source_design_assumptions",
        "policy_value_is_incremental_on_the_registered_outcome_scale_before_cost_capacity_or_fairness_decisions",
        "external_GRF_parity_simulation_and_independent_review_pending",
    ]
    return {
        "development_sample_size": int(len(development)),
        "evaluation_sample_size": int(len(evaluation)),
        "GATE": {"groups": gate, "simultaneous_method": "Bonferroni", "family_confidence_level": level},
        "BLP": blp,
        "calibration": {"r_squared": calibration, "groups": groups},
        "Qini": qini,
        "AUTOC": autoc,
        "policy_value": {"threshold": threshold, "treated_fraction": float(np.mean(candidate_policy)), "incremental_vs_treat_none": policy_values, "candidate_contrasts": contrasts},
        "decision_diagnostics": {"heterogeneity_supported": heterogeneity_supported, "policy_supported": policy_supported, "positive_ranking_required": True, "lower_bounds": lower_bounds, "ranking_checks": ranking_checks, "primary_policy_baseline": primary_baseline, "acceptance_policy": {**acceptance_values, "ranking_rule": acceptance["ranking_rule"], "primary_policy_baseline": primary_baseline}, "business_action_authorized": False},
        "overlap": {"source_design": source_design, "minimum_propensity": float(np.min(propensities)), "maximum_propensity": float(np.max(propensities)), "bounds": {"lower": lower_bound, "upper": upper_bound}},
        "CATE_distribution": {"quantile_probabilities": [0, .1, .25, .5, .75, .9, 1], "quantiles": [float(item) for item in quantiles], "row_level_predictions_emitted": False},
        "split_binding": {"partition_values": ["development", "evaluation"], "evaluation_outcomes_used_for_training": False, "seed": seed, "folds": folds, "honest_forest": True},
        "warnings": warnings,
    }


def response(ok: bool, result=None, error=None) -> dict:
    return {"schema_version": "1.0.0", "backend_id": BACKEND_ID, "candidate_id": CANDIDATE_ID, "package": "econml", "version": EXPECTED_VERSION, "ok": ok, "result": result, "warnings": result.get("warnings", []) if result else [], "error": error}


try:
    request = json.load(sys.stdin)
    if not isinstance(request, dict):
        raise AdapterError("BACKEND_REQUEST_INVALID", "Request must be a JSON object")
    output = response(True, run(request))
except AdapterError as exc:
    output = response(False, error={"code": exc.code, "message": str(exc), "details": exc.details})
except Exception as exc:
    output = response(False, error={"code": "BACKEND_INTERNAL_ERROR", "message": str(exc), "details": None})
json.dump(output, sys.stdout, allow_nan=False, separators=(",", ":"))
