# Versioned Platform Knowledge Contract

Contract: `CBDS-PLATFORM-KNOWLEDGE-2026.07`

Platform knowledge is a dated evidence layer, not a hidden ranking formula.
Cards distinguish `official`, `research`, `observed`, and `inferred` claims;
name sources and review/expiry dates; state affected objects, measurable
hypotheses, and invalidation conditions. Expired cards fail closed for formal
recommendations. Inferred claims may create diagnostics or experiments only and
may not directly change a stable score, budget, bid, replenishment quantity, or
business posture.

PLCO owns page and conversion use, AAMO owns advertising use, and LIFD owns
inventory and fulfillment use. A card never transfers sovereignty. Run
`scripts/validate_platform_cards.py` before using a card in a formal decision.

## Claim and lifecycle model

Each card is a set of scoped claims, not a platform-wide truth. Scope includes
platform, country, account or program type, affected object, feature surface,
valid-from time and evidence cutoff. The normative lifecycle is `draft ->
reviewed -> active -> stale -> invalidated -> archived`. Expiry moves an active
card to `stale`; contradictory official evidence or a failed invalidation test
moves it to `invalidated`. Neither state may be manually relabelled active.

`official`, `research`, `observed` and `inferred` describe evidence status, not
truth certainty. Promotion requires new independent evidence and reviewer
identity; demotion preserves the previous claim and records affected consumers.
Same-source repetition is not independence. Conflicting active cards remain a
conflict set until the owning domain adjudicates them.

## Consumer and change controls

Every use records card id/version/hash, consumer domain, allowed use and
decision object version. PLCO, AAMO and LIFD may accept, reject or request
recomputation; no consumer may broaden the card scope. Rule or feature changes
compute an impact closure covering consumers, Decision Packets, experiments and
operator playbooks. Unaffected conclusions remain preserved.

Hypotheses require a metric, window, success threshold, guardrail, stop rule and
invalidation condition. Observational or inferred cards may only create a
diagnostic or experiment. They cannot establish causality, modify stable scores,
change bids/budgets/replenishment, or authorize an external action.

The executable lifecycle and responsibility contract is
`knowledge-lifecycle-contract.json`. Run
`../../scripts/validate_operational_governance_depth.py` in addition to the card
schema validator. Passing either check does not establish that a platform
mechanism remains true in the real world.
