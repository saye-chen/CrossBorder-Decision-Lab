# ERDG Economic, Risk & Decision Governance

Runtime version: `ERDG-2026.01`

Contract version: `ERDG-CONTRACT-2026.01`

Maturity: `controlled pilot`. L1—L3 automated gates may pass; L4 requires authorized, deidentified real replays and independent review.

All nine professional Skill entrypoints consume `ERDG-CONTRACT-2026.01` through their local decision-contract validator and registered adapter. Draft 2020-12 schemas are executed with format checking. Golden reports must carry valid deterministic recomputation bindings. Reference capacity is governed by `capacity-contract.json`; exceeding a hard limit fails closed and the reference gate does not claim a production SLO.

## Charter

ERDG is repository-owned neutral infrastructure. It defines canonical objects, evidence and claim semantics, economic layers, cash, risk, state transitions, cross-domain envelopes, parameter resolution, lineage hashing and recomputation rules. It validates structural safety and performs deterministic shared calculations.

ERDG does not own business decisions, choose production thresholds, infer causal effects, approve actions or execute external writes. Domain owners retain their professional models and final decisions. A validated claim never auto-approves a decision, and a proposed adjustment never becomes effective without acceptance and recomputation by its owner.

## Normative modules

- [Object and evidence](references/object-evidence-and-claims.md)
- [Economics, units and risk](references/economics-units-and-risk.md)
- [State, handoff and lineage](references/state-handoff-and-lineage.md)
- [Parameters, migration and release](references/parameters-migration-and-release.md)

## Runtime

- `scripts/validate_contract.py`: authoritative shared decision-contract validator.
- `scripts/calculate_economic_layers.py`: E0—E8 decimal accounting.
- `scripts/calculate_cash_flow.py`: dated cash ledger and peak funding requirement.
- `scripts/evaluate_risk_and_redlines.py`: non-compensable redlines and comparable expected loss.
- `scripts/validate_units_currency_tax_time.py`: quantity metadata and comparability.
- `scripts/validate_state_transition.py`: claim, decision, action and replay state machines.
- `scripts/resolve_parameters.py`: scoped, versioned parameter resolution.
- `scripts/canonicalize_payload.py` and `scripts/hash_lineage.py`: canonical JSON and SHA-256 lineage.

All external actions are out of scope. Missing values are never converted to zero. Financial authority uses decimal strings; binary floating-point values are rejected from authoritative economic ledgers.

The physical and runtime identity is `governance/erdg/`. The former planning
path `governance/f03/` is retired and forbidden in active sources, contracts,
tests, evaluations and user-facing output. Domain-local validators remain thin
compatibility entrypoints only; they must delegate to the authoritative ERDG
contract and may not fork its semantics.

## Release contract

Every change requires contract version review, authoritative-source and consumer impact closure, schema tests, Golden tests, adversarial tests, property tests, adapter parity, migration evidence, full repository audit and a tested rollback path.

The `f03` path migration is complete in `ERDG-2026.01`. Release validation must
fail if an active repository file reintroduces `governance/f03`, `test_f03.py`
or `f03_common.py`. Rollback means reverting the release as one Git unit; it
does not restore a second authoritative physical namespace.
