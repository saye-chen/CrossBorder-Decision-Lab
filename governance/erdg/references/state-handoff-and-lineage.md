# State, handoff and lineage contract

Claim, decision, action, replay and recovery use independent append-only state machines. Recovery follows `detected → frozen → triaged → recalculating → partially_recovered/recovered/escalated → closed`; partial consumer recovery cannot close a shared root-cause batch. Only an approved effective decision may authorize an action. Validated claims do not approve decisions.

The cross-domain envelope includes message identity and version, source and target, decision question, canonical object reference, runtime versions, evidence/claim/calculation references, constraints, allowed and forbidden uses, participant status, requested response, deadline, lineage and namespaced extensions. Receivers explicitly accept, reject, partially accept or request evidence and recompute with their owned model.

Canonical JSON uses sorted keys, compact separators, Unicode NFC, UTC ISO time and decimal strings. SHA-256 protects normalized input, evidence, calculation and output. Object version flows to evidence, input, calculation, claim, decision, action, outcome and replay. Hash mismatch is invalid; it is not auto-repaired. Dependency changes trigger selective impact-closure recomputation.

Evidence invalidation first freezes affected active actions, then traverses lineage to every signal and decision consumer. Consumers are recovered individually; the root batch remains open until every consumer has recomputed, rechecked gates, received a new effective decision or explicit escalation, and been notified. Automation may perform only pre-authorized reversible freezes or alerts; high-impact external recovery actions retain human authorization.
