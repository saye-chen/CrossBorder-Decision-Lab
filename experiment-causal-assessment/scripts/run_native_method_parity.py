#!/usr/bin/env python3
"""Reproduce native-method parity against independently maintained Python libraries.

The script is deliberately read-only.  It evaluates the repository implementation in
the current interpreter and delegates only the oracle calculations to the frozen ECAE
Python runtime.  The oracle therefore does not import repository implementation code.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
ORACLE_PYTHON = REPO / ".venv" / "ecae-python" / "bin" / "python3"
sys.path.insert(0, str(ROOT / "scripts"))

from adjust_multiplicity import adjust_multiplicity
from apply_covariate_adjustment import apply_covariate_adjustment
from calculate_mde_precision import calculate_mde_precision
from calculate_sample_size import calculate_sample_size
from evaluate_randomized_effect import evaluate_randomized_effect
from validate_randomization import validate_randomization


def _oracle(program: str) -> dict:
    if not ORACLE_PYTHON.is_file():
        raise RuntimeError(f"locked oracle runtime missing: {ORACLE_PYTHON}")
    completed = subprocess.run(
        [str(ORACLE_PYTHON), "-c", program],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return json.loads(completed.stdout)


def _close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def run() -> dict:
    sample = calculate_sample_size({
        "metric_type": "continuous", "alpha": 0.05, "power": 0.8,
        "allocation_ratio": 1.0, "attrition_rate": 0.0,
        "minimum_important_effect": 0.25, "baseline_variance": 1.0,
    })
    mde = calculate_mde_precision({
        "metric_type": "continuous", "n_control": 252, "n_treatment": 252,
        "alpha": 0.05, "power": 0.8, "confidence_level": 0.95,
        "baseline_variance": 1.0,
    })
    randomized = evaluate_randomized_effect({
        "estimand_type": "ITT", "metric_type": "continuous",
        "groups": {"control": [1.0, 2.0, 3.0, 4.0], "treatment": [2.0, 4.0, 4.0, 6.0]},
        "control_arm": "control", "confidence_level": 0.95,
    })["comparisons"][0]
    cuped = apply_covariate_adjustment({
        "records": [
            {"arm": "control", "outcome": 2.0, "covariates": {"pre": 1.0}},
            {"arm": "control", "outcome": 4.0, "covariates": {"pre": 2.0}},
            {"arm": "control", "outcome": 5.0, "covariates": {"pre": 3.0}},
            {"arm": "treatment", "outcome": 4.0, "covariates": {"pre": 1.5}},
            {"arm": "treatment", "outcome": 6.0, "covariates": {"pre": 2.5}},
            {"arm": "treatment", "outcome": 8.0, "covariates": {"pre": 3.5}},
        ],
        "covariates": [{"name": "pre", "temporal_status": "pre_treatment"}],
        "control_arm": "control",
    })
    srm = validate_randomization({
        "observed_counts": {"control": 520, "treatment": 480},
        "expected_probabilities": {"control": 0.5, "treatment": 0.5},
        "srm_alpha": 0.001,
        "assignment_proof": {"proof_type": "fixture", "value": "frozen"},
    })
    hypotheses = [
        {"hypothesis_id": "h1", "family_id": "f1", "p_value": 0.01},
        {"hypothesis_id": "h2", "family_id": "f1", "p_value": 0.04},
        {"hypothesis_id": "h3", "family_id": "f1", "p_value": 0.20},
    ]
    multiplicity = {
        method: [item["adjusted_p_value"] for item in adjust_multiplicity({
            "hypotheses": hypotheses, "method": method, "alpha": 0.05,
        })["families"][0]["hypotheses"]]
        for method in ("bonferroni", "holm", "benjamini_hochberg")
    }

    oracle = _oracle(r'''
import json
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import zt_ind_solve_power

control=np.array([1.0,2.0,3.0,4.0]); treatment=np.array([2.0,4.0,4.0,6.0])
estimate=float(treatment.mean()-control.mean())
se=float(np.sqrt(treatment.var(ddof=1)/len(treatment)+control.var(ddof=1)/len(control)))
records=np.array([[2.0,1.0],[4.0,2.0],[5.0,3.0],[4.0,1.5],[6.0,2.5],[8.0,3.5]])
x=records[:,1]-records[:,1].mean(); y=records[:,0]-records[:,0].mean()
theta=float(np.linalg.lstsq(x[:,None],y,rcond=None)[0][0])
p=[0.01,0.04,0.20]
print(json.dumps({
  "continuous_n_per_arm": float(zt_ind_solve_power(effect_size=0.25, nobs1=None, alpha=0.05, power=0.8, ratio=1.0, alternative="two-sided")),
  "continuous_mde": float(zt_ind_solve_power(effect_size=None, nobs1=252, alpha=0.05, power=0.8, ratio=1.0, alternative="two-sided")),
  "randomized": {"estimate": estimate, "se": se, "p": float(2*stats.norm.sf(abs(estimate/se)))},
  "cuped_theta": theta,
  "srm": {"statistic": float(stats.chisquare([520,480],f_exp=[500,500]).statistic), "p": float(stats.chisquare([520,480],f_exp=[500,500]).pvalue)},
  "multiplicity": {
    "bonferroni": multipletests(p,method="bonferroni")[1].tolist(),
    "holm": multipletests(p,method="holm")[1].tolist(),
    "benjamini_hochberg": multipletests(p,method="fdr_bh")[1].tolist()
  },
  "versions": {"numpy": np.__version__, "scipy": __import__("scipy").__version__, "statsmodels": __import__("statsmodels").__version__}
},sort_keys=True))
''')

    checks = {
        "sample_size_fixed": {
            "repository_n_per_arm": sample["n_control"],
            "oracle_unrounded_n_per_arm": oracle["continuous_n_per_arm"],
            "pass": sample["n_control"] == math.ceil(oracle["continuous_n_per_arm"]),
        },
        "mde_precision_fixed": {
            "repository_mde": mde["mde_absolute"],
            "oracle_mde": oracle["continuous_mde"],
            "pass": _close(mde["mde_absolute"], oracle["continuous_mde"], 2e-6),
        },
        "randomized_itt": {
            "repository": [randomized["estimate_absolute"], randomized["standard_error"], randomized["p_value_unadjusted"]],
            "oracle": [oracle["randomized"][key] for key in ("estimate", "se", "p")],
            "pass": all(_close(a, b, 2e-7) for a, b in zip(
                [randomized["estimate_absolute"], randomized["standard_error"], randomized["p_value_unadjusted"]],
                [oracle["randomized"][key] for key in ("estimate", "se", "p")],
            )),
        },
        "cuped_linear": {
            "repository_theta": cuped["theta"]["pre"],
            "oracle_theta": oracle["cuped_theta"],
            "pass": _close(cuped["theta"]["pre"], oracle["cuped_theta"], 1e-12),
        },
        "srm_chi_square": {
            "repository": [srm["pearson_chi_square"], srm["p_value"]],
            "oracle": [oracle["srm"]["statistic"], oracle["srm"]["p"]],
            "pass": _close(srm["pearson_chi_square"], oracle["srm"]["statistic"], 1e-12)
                    and _close(srm["p_value"], oracle["srm"]["p"], 2e-12),
        },
        "multiplicity_holm_bonferroni_bh": {
            "repository": multiplicity,
            "oracle": oracle["multiplicity"],
            "pass": all(
                all(_close(a, b, 1e-12) for a, b in zip(multiplicity[method], oracle["multiplicity"][method]))
                for method in multiplicity
            ),
        },
    }
    return {
        "schema_version": "1.0.0",
        "report_id": "ECAE-NATIVE-PARITY-2026-08-10",
        "scope": "controlled_pilot_non_production",
        "oracle_runtime": str(ORACLE_PYTHON.relative_to(REPO)),
        "oracle_versions": oracle["versions"],
        "checks": checks,
        "all_pass": all(item["pass"] for item in checks.values()),
        "limitations": [
            "Library parity verifies frozen numerical vectors, not production effectiveness.",
            "Guardrail rules and 2x2 DiD design assumptions use analytical and mutation evidence rather than library parity.",
            "Advanced scientific backends are outside this native-method report and remain fail-closed.",
        ],
        "external_write": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
