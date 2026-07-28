#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent

def main()->int:
    required=[
        "SKILL.md","agents/openai.yaml","references/charter-and-sovereignty.md",
        "references/canonical-object-and-lifecycle.md","schemas/canonical-product-object.schema.json",
        "references/input-evidence-and-decision-skeleton.md","schemas/input-envelope.schema.json",
        "references/professional-models-and-calculation.md",
        "schemas/evidence-record.schema.json","schemas/claim-record.schema.json",
        "schemas/calculation-record.schema.json","schemas/decision-skeleton.schema.json",
        "schemas/product-lifecycle-state.schema.json","scripts/validate_decision_contract.py",
        "scripts/validate_wp2_contracts.py","scripts/test_wp2_contracts.py",
        "scripts/validate_wp3_package.py","scripts/test_wp3_package.py",
        "scripts/evaluate_product_models.py","scripts/test_product_models.py",
        "references/d06-recomputation-and-cross-domain.md",
        "schemas/cross-domain-envelope.schema.json","schemas/recomputation-impact.schema.json",
        "scripts/compute_product_change_impact.py","scripts/validate_cross_domain_envelope.py",
        "scripts/test_wp5_cross_domain.py",
        "references/d04-d05-localization-professional-contracts.md",
        "schemas/manufacturing-quality-handoff.schema.json",
        "schemas/market-access-review-request.schema.json",
        "schemas/professional-opinion.schema.json","schemas/localization-profile.schema.json",
        "schemas/temporary-contract-migration.schema.json",
        "scripts/validate_wp6_contracts.py","scripts/evaluate_temporary_contract_migration.py",
        "scripts/test_wp6_expert_contracts.py",
        "references/professional-output-continuity-and-rollback.md",
        "schemas/product-decision-event.schema.json",
        "schemas/continuous-product-decision-state.schema.json",
        "schemas/product-rollback-plan.schema.json","schemas/professional-report.schema.json",
        "scripts/update_continuous_product_decision.py",
        "scripts/compute_decision_impact_closure.py","scripts/validate_professional_report.py",
        "scripts/test_wp7_continuity_and_reports.py",
        "scripts/build_wp8_evaluations.py","scripts/run_wp8_evaluations.py",
        "scripts/validate_wp8_coverage.py","scripts/test_wp8_evaluations.py",
        "evaluations/fixtures/evaluation-catalog.json",
        "evaluations/fixtures/evaluation-execution-map.json",
        "evaluations/coverage-matrix.json","evaluations/multiturn-challenges.json",
        "evaluations/extreme-scenarios.json",
        "references/consumer-migration-and-acceptance.md",
        "scripts/build_wp9_migration_assets.py",
        "scripts/validate_pipm_consumer_migration.py","scripts/test_wp9_migration.py",
        "evaluations/migration/consumer-adapters.json",
        "evaluations/migration/source-inventory.json",
        "evaluations/migration/dual-run-results.json",
        "evaluations/migration/consumer-acceptance.json",
        "evaluations/migration/migration-state.json",
        "evaluations/migration/rollback-manifest.json",
        "evaluations/historical-replay-template.json",
    ]
    errors=[f"missing:{p}" for p in required if not (ROOT/p).is_file()]
    skill=(ROOT/"SKILL.md").read_text()
    for marker in ("PIPM-2026.01","controlled pilot","PLC0","ERDG-CONTRACT-2026.01","validate_decision_contract.py"):
        if marker not in skill: errors.append(f"skill_missing:{marker}")
    adapter=json.loads((REPO/"governance/erdg/adapters/product-innovation-product-management/adapter.json").read_text())
    if adapter.get("external_write") is not False: errors.append("adapter_external_write")
    if adapter.get("runtime_prefix")!="PIPM": errors.append("adapter_runtime")
    for name in ("canonical-product-object.schema.json","product-lifecycle-state.schema.json","input-envelope.schema.json","evidence-record.schema.json","claim-record.schema.json","calculation-record.schema.json","decision-skeleton.schema.json","cross-domain-envelope.schema.json","recomputation-impact.schema.json","manufacturing-quality-handoff.schema.json","market-access-review-request.schema.json","professional-opinion.schema.json","localization-profile.schema.json","temporary-contract-migration.schema.json","product-decision-event.schema.json","continuous-product-decision-state.schema.json","product-rollback-plan.schema.json","professional-report.schema.json"):
        schema=json.loads((ROOT/"schemas"/name).read_text())
        if schema.get("$schema")!="https://json-schema.org/draft/2020-12/schema": errors.append(f"schema_draft:{name}")
    if errors: raise SystemExit("PIPM_WP2_STRUCTURE=BLOCKED\n- "+"\n- ".join(errors))
    print("PIPM_WP2_STRUCTURE=PASS");return 0

if __name__=="__main__": raise SystemExit(main())
