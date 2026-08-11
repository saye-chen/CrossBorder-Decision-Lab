# Knowledge and Delivery Quality Gate

Contract: `CBDS-KNOWLEDGE-QUALITY-2026.07`

This gate prevents repository growth from creating stale facts, duplicated hard
constraints, generic delivery checks, unactionable missing-data requests,
unverifiable scale claims, orphaned health findings, incomplete scaffolds, or
tests that are made green by copying evaluation language.

It is a thin repository-governance layer. It does not score a product, change a
domain decision, authorize an external write, or replace ERDG. Formal decisions
still require the owning domain and an ERDG-passed Decision Packet.

## Eight enforced controls

1. Dynamic facts are registered with scope, source, review and expiry dates.
2. Hard constraints are referenced by ID; consumers and impact closure are
   recorded, and stale or invalidated constraints fail closed.
3. Delivery self-checks bind to a concrete object, country/platform, weakest
   assumption, evidence state, counterevidence, stop and rollback conditions.
4. Missing-data requests name the field, authoritative retrieval location,
   exact field/window/unit, decision impact, frozen conclusions, fallback
   experiment and recomputation mode.
5. Repository scale and maturity claims are derived from authoritative files.
6. Scheduled health findings have an owner, due time, affected consumers,
   freeze action, recovery batch and closure evidence.
7. New governed assets are created from complete scaffolds.
8. Duplicate self-checks, copied evaluation phrases, threshold weakening and
   unapproved special-case bypasses are rejected.

Run `python3 scripts/validate_knowledge_quality.py`. The scheduled workflow is
reporting plus fail-closed validation; it never refreshes a fact or closes a
recovery event automatically.
