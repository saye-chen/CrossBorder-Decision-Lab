# D03 WP10 Independent Review Guide

## Review boundary

This package supports an independent L3 expert review of
`product-innovation-product-management`. It does not authorize external
execution, make D03 authoritative, close consumer-owner acceptance, or prove
L4 production maturity.

Reviewers must not have designed or implemented the reviewed D03 changes. A
disclosed conflict may be accepted only when mitigation is recorded.

## Required reviewers

1. Independent product reviewer: evaluates product-management depth,
   lifecycle completeness, decision usefulness and hard-gate semantics.
2. Independent engineering or data reviewer: recomputes deterministic
   mechanisms, checks lineage, versioning, failure handling, rollback and
   tamper resistance.
3. Consumer-domain owner reviewer: samples cross-Skill envelopes and confirms
   retained sovereignty, forbidden writeback, local rejection and legacy-read
   safety.

All three roles must approve the same frozen `evidence-index.json`. One person
may not fill multiple roles unless the conflict is disclosed and independently
mitigated; such consolidation should normally block approval.

## Mandatory review questions

- Single Skill: are opportunity, MVP, specification, variant, packaging,
  roadmap, change and retirement decisions supported by deterministic
  mechanisms rather than generic advice?
- Cross Skill: do D03, D04, D05, D06 and all consumers preserve sovereignty,
  versions, partial failures, evidence requests and forbidden writeback?
- Continuous follow-up: are identity, history, unique-current state, revisions,
  invalidation, recomputation, rollback and exit preserved across turns?
- Complex and extreme: do tail failures, stale evidence, version conflicts,
  partial tools and irreversible actions fail closed?
- Evaluation validity: does each declared professional engine really execute,
  and does a mechanism mutation change or block the result?
- Migration validity: is acceptance generated and tested on the consumer side,
  with the old reader retained until independent acceptance?
- Maturity accuracy: are synthetic evidence, automated tests and self-review
  prevented from claiming L3 independent signoff or L4 readiness?

## Finding severity

- P0: safety, compliance, irreversible external action, fabricated evidence or
  unauthorized sovereignty transfer. Always blocks.
- P1: professional mechanism can silently produce a wrong decision, an
  execution path is not real, a consumer can accept incompatible data, or
  lineage/rollback is unreliable. Always blocks.
- P2: bounded deficiency with a documented safe fallback. May be accepted only
  with owner, deadline and verification condition.
- P3: editorial or usability improvement that does not affect correctness.

## Execution

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 product-innovation-product-management/scripts/test_wp8_evaluations.py
PYTHONDONTWRITEBYTECODE=1 python3 product-innovation-product-management/scripts/test_wp9_migration.py
PYTHONDONTWRITEBYTECODE=1 python3 product-innovation-product-management/scripts/test_wp10_review_package.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_full_repository_audit.py
```

Reviewers must also manually inspect at least:

- three Golden chains, including one hard-tail failure and one lifecycle exit;
- three consumer adapters from different sovereignty classes;
- one multi-turn revision conflict;
- one cross-domain partial failure;
- one evidence or report hash tamper;
- one attempted L3/L4 maturity shortcut.

## Signoff rule

Update `independent-signoff.json` only after review. Every approval must include
reviewer identity, independence statement, conflict status, decision, findings,
timestamp and the unchanged evidence-index hash. Any unresolved P0/P1, missing
required role, stale evidence hash or maturity shortcut keeps WP10 blocked.

Even after L3 independent approval, L4 remains `controlled pilot` until
authorized, deidentified, mature real replays satisfy outcome, heterogeneity,
failure/exit, calibration, incident/rollback, drift and independent-review
requirements.
