# State, handoff and lineage contract

Claim, decision, action and replay use independent append-only state machines. Only an approved effective decision may authorize an action. Validated claims do not approve decisions.

The cross-domain envelope includes message identity and version, source and target, decision question, canonical object reference, runtime versions, evidence/claim/calculation references, constraints, allowed and forbidden uses, participant status, requested response, deadline, lineage and namespaced extensions. Receivers explicitly accept, reject, partially accept or request evidence and recompute with their owned model.

Canonical JSON uses sorted keys, compact separators, Unicode NFC, UTC ISO time and decimal strings. SHA-256 protects normalized input, evidence, calculation and output. Object version flows to evidence, input, calculation, claim, decision, action, outcome and replay. Hash mismatch is invalid; it is not auto-repaired. Dependency changes trigger selective impact-closure recomputation.
