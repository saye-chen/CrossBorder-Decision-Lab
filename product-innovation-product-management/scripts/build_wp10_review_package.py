#!/usr/bin/env python3
"""Build a deterministic, tamper-evident D03 independent-review package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "evaluations/review-package"

EVIDENCE = [
    "governance/pipm-blueprint-implementation-manifest.json",
    "product-innovation-product-management/SKILL.md",
    "product-innovation-product-management/evaluations/review-package/REVIEW_GUIDE.md",
    "product-innovation-product-management/evaluations/fixtures/evaluation-catalog.json",
    "product-innovation-product-management/evaluations/golden-execution-results.json",
    "product-innovation-product-management/evaluations/multiturn-challenges.json",
    "product-innovation-product-management/evaluations/extreme-scenarios.json",
    "product-innovation-product-management/evaluations/migration/consumer-acceptance.json",
    "product-innovation-product-management/evaluations/migration/dual-run-results.json",
    "product-innovation-product-management/evaluations/migration/rollback-manifest.json",
    "product-innovation-product-management/scripts/run_wp8_evaluations.py",
    "product-innovation-product-management/scripts/test_wp8_evaluations.py",
    "product-innovation-product-management/scripts/test_wp8_execution_bindings.py",
    "product-innovation-product-management/scripts/test_wp9_migration.py",
    "scripts/test_full_repository_audit.py",
]

REVIEW_ROLES = [
    "independent_product_reviewer",
    "independent_engineering_or_data_reviewer",
    "consumer_domain_owner_reviewer",
]


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name: str, value: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build() -> None:
    missing = [path for path in EVIDENCE if not (REPO / path).is_file()]
    if missing:
        raise SystemExit("missing review evidence: " + ",".join(missing))
    index = {
        "package_version": "PIPM-WP10-REVIEW-2026.01",
        "generated_at": "2026-07-28T00:00:00Z",
        "evidence": [
            {"path": path, "sha256": file_hash(REPO / path)}
            for path in EVIDENCE
        ],
        "automated_regression": {
            "wp8_expected": "6 tests pass",
            "wp9_expected": "27 tests pass",
            "full_repository_expected": "17 tests pass",
        },
        "maturity_constraint": {
            "l3": "not_passed_until_independent_signoff",
            "l4": "controlled_pilot",
            "authoritative": False,
            "external_write": False,
        },
    }
    signoff = {
        "package_version": index["package_version"],
        "overall_status": "pending_independent_review",
        "required_roles": [
            {
                "role": role,
                "reviewer_id": None,
                "independent_of_implementation": None,
                "conflict_of_interest": None,
                "decision": "pending",
                "findings": [],
                "signed_at": None,
                "evidence_index_hash": None,
            }
            for role in REVIEW_ROLES
        ],
        "prohibited_shortcuts": [
            "self_review_as_independent",
            "automated_pass_as_l3_signoff",
            "synthetic_fixture_as_l4_proof",
            "unsigned_consumer_owner_acceptance",
        ],
    }
    checklist = {
        "single_skill_depth": "pending_reviewer",
        "cross_skill_sovereignty_and_failure": "pending_reviewer",
        "continuous_follow_up_state": "pending_reviewer",
        "complex_extreme_and_pressure": "pending_reviewer",
        "consumer_owned_acceptance": "pending_reviewer",
        "maturity_claim_accuracy": "pending_reviewer",
        "blocking_rule": "any unresolved P0/P1 or missing required role blocks WP10",
    }
    dump("evidence-index.json", index)
    signoff["required_roles"] = [
        {**row, "evidence_index_hash": file_hash(OUT / "evidence-index.json")}
        for row in signoff["required_roles"]
    ]
    dump("independent-signoff.json", signoff)
    dump("review-checklist.json", checklist)
    print(f"PIPM_WP10_PACKAGE=PASS evidence={len(EVIDENCE)} reviewers={len(REVIEW_ROLES)}")


if __name__ == "__main__":
    build()
