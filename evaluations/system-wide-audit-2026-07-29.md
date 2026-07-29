# System-wide release audit — 2026-07-29

Release train: `2026.07`

Architecture: `CBDS-ARCH-2026.07`

Shared contract: `ERDG-CONTRACT-2026.07`

Handoff / Decision Cycle: `v2 / v2`

Maturity: `controlled pilot`
Audit standard: [`CBDS-AUDIT-2026.07-v1`](../governance/system-audit-standard.md)

## Verdict

The active eleven-domain system, ERDG control plane and D01—D14 target
architecture pass the repository-owned L1—L3 release gates. No active release
artifact uses a stale date-based version. D04 remains `next_build`; D05 and D14
remain `planned` and fail closed at execution. L4 is not passed because no
authorized mature real replay has been registered.

## Evidence executed

- Eleven Skill structural validation and every registered local test suite.
- Ten v2 architecture, handoff and Decision Cycle semantic assertions.
- Twenty-eight ERDG schema, economics, cash, risk, state, lineage, migration
  retirement, recomputation, stress and capacity assertions.
- Twelve AAMO model/stability assertions, seven causal-measurement assertions,
  five official-platform-mechanism assertions and twelve advertising stress
  assertions.
- Nine professional-depth assertions, including advertising causal limits,
  platform DNA, adversarial coverage and non-padding checks.
- Twelve multi-domain extreme composites, cross-domain conflicts and multi-turn
  state preservation in the full repository audit.
- 101 PIPM executable evaluation cases, ten execution-bound Golden cases,
  twelve multi-turn cases and twelve extreme cases.
- Seven ERDG Golden reports recomputed from deterministic inputs.
- Full repository audit: 17/17 passed.

## Substantive conclusions

1. Advertising does not equate platform attribution with profit or incrementality,
   keeps average and marginal efficiency separate, rejects negative-margin
   allocation, and exposes identification limits for ITT, DiD, synthetic control
   and directional response estimation.
2. Cross-domain decisions preserve professional ownership. ERDG validates
   structure, deterministic calculations, evidence, state and lineage without
   taking business sovereignty.
3. v2 handoffs require both runtime versions, registered authority, non-conflicting
   uses, valid target gates and non-self-referential dependencies.
4. Decision Cycle rejects false gate completion, dependency cycles, wrong owners
   and execution by unavailable domains; blocked cycles require recovery evidence.
5. Extreme and partial-failure paths preserve unaffected results, stop unsafe
   actions and keep rollback/recovery requirements explicit.

## External boundary

Automated tests, Golden reports and synthetic fixtures do not establish
production readiness. Authorized deidentified real replays, independent review
and operating calibration remain external L4 gates.

## Audit sufficiency boundary

This release note records repository-owned evidence, but it is not by itself a
reproducible independent audit. A formal audit must additionally bind the
audited commit and worktree state, environment and dependency lock, executable
commands and exit codes, raw-log index, artifact hashes, security/release
checks, change-impact closure and independent review.

The authoritative scoring, hard-gate, evidence-ledger, remediation and
100-point acceptance rules are defined in
[`governance/system-audit-standard.md`](../governance/system-audit-standard.md).
Until G0—G5 pass, the valid maturity claim remains `controlled pilot`.

## Remediation evidence update

The repository now provides `scripts/generate_system_audit_evidence.py`, which
separates test-file, static test-case and static assertion-call inventories;
records commit, branch, worktree state, runtime environment, dependency-lock
hash, commands, exit codes, durations, raw logs and artifact hashes; and runs
release-oriented secret, absolute-path, cache and permission checks.

The 2026-07-29 remediated working-tree package recorded 80 test files, 777
static test cases and 1,482 static assertion calls. The full repository gate
passed 17/17 and the automated security/release scan passed. Because the
worktree was not clean, the package correctly reports
`PASS_WORKTREE_DIAGNOSTIC` with `FAIL_DIRTY_WORKTREE` for reproducibility and
does not claim a clean `main` release.

The second-round package adds machine scoring, reference capacity metrics,
repository-license and privacy-contract validation, and fail-closed
change-impact closure. It records 82 test files, 784 static test cases and
1,500 static assertion calls; maps all 239 changed paths to 26 governed
contracts with zero unmapped paths; and scores 84/100. G1—G4 pass. G0 remains
partial because the worktree is dirty, and G5 remains a controlled external
gate because authorized L4 replay is still absent.

The third round reconstructed the complete working-tree content in an isolated
repository, created a clean local candidate commit and reran the full evidence
chain. The authoritative candidate hash is recorded in the external immutable
evidence package rather than embedded in this source file, avoiding a
self-referential hash change. The candidate reports `PASS_CLEAN_CANDIDATE`,
passes G0—G4 and scores 87/100. It is not a claim that the source repository or
GitHub `main` has been updated. G5 remains a controlled external gate.
