# CrossBorder Decision Lab

[中文首页](README.md) · [Professional Capabilities](#professional-capabilities) · [Decision Infrastructure](#global-decision-infrastructure) · [Collaboration Architecture](#professional-capability-architecture) · [How to Use](#how-to-use)

> Professional decision infrastructure for cross-border commerce—turning experience-dependent judgment into evidence-based, model-backed, actionable, and compounding decision assets.

Current release train: `2026.07`; target architecture: `CBDS-ARCH-2026.07`; shared contract: `ERDG-CONTRACT-2026.07`.

CrossBorder Decision Lab is built for cross-border operators, brands, investors, and professional teams. It connects category investment, competitive intelligence, product, supply/procurement/production/quality, legal/tax/IP/market access, pricing finance, fulfillment, conversion, advertising, partnerships, content, marketing, and customer growth into fourteen professional domains that can operate independently and collaborate under shared decision contracts.

The system combines fourteen professional decision capabilities with three global foundations. COPO orchestrates cross-domain work; CIDM, CIM, PIPM, SPPQ, LTMA, PPFC, LIFD, MBCM, VLB, CAPM, PLCO, AAMO, and CIG retain their respective professional sovereignty. ECAE, LCCA, and ERDG govern causal eligibility, localization applicability, and shared decision contracts. Core engineering and L1–L3 release gates are complete, with maturity at `controlled_pilot`. L4 will advance through real use, outcome replay, parameter calibration, and independent assurance; until then, production automation, high-stakes use, and external writes remain unavailable.

CIDM now includes the governed `OSL-v1` opportunity-signal layer. It clean-room reimplements external research ideas as eight deterministic candidate-signal families with multi-source field quality, five composition playbooks, effective-supply/VOC analysis, proof-bound CIDM-to-PLCO handoff, partial-failure DAG execution, R0–R4 recovery, an independent oracle, and 13 source mutations. The layer expands candidate coverage only; it cannot directly change the seven-dimension score, capital posture, or cross-domain sovereignty. The authorized 20-case blind replay, 20-person non-implementer comprehension test, and forward calibration remain open, so this is not a production-maturity claim.

### OSL-v1 opportunity-signal architecture

```mermaid
flowchart TB
    subgraph IN["1. Evidence intake"]
      direction LR
      RAW["External research evidence"] --> ADP["Evidence Adapter<br/>normalization · freshness · source family · lineage"]
      ADP --> CON["Signal contract<br/>object · window · counterevidence · alternatives"]
    end
    subgraph CORE["2. Signal computation"]
      direction LR
      MOD["8 deterministic models"] <--> ORA["Independent Oracle<br/>status and metric dual calculation"]
      ORA --> SIG["12 canonical signals"]
    end
    subgraph DEC["3. Decision governance"]
      direction LR
      PLAY["5 composition playbooks<br/>Required · Supporting<br/>Counter · Veto"] --> GATE["CIDM five gates<br/>seven-dimension score"]
      GATE --> CARD["Rapid Decision Card<br/>Enter · Test · Observe · Reject"]
    end
    subgraph REC["4. Reality recovery"]
      direction LR
      DRIFT["Evidence invalidation<br/>field drift · definition change"] --> FREEZE["Freeze affected actions"]
      FREEZE --> RECOMPUTE["Impact closure · domain recomputation<br/>new effective decision"]
    end
    CON --> MOD
    SIG --> PLAY
    CARD --> HAND["Governed handoff<br/>PPFC · SPPQ · LIFD · PLCO"]
    GATE -->|redline / veto triggered| BLOCK["Blocked<br/>cannot be offset by a high score"]
    CARD -.evidence invalidated.-> DRIFT
    RECOMPUTE -.enters the next decision cycle.-> REENTRY["Re-enter evidence intake"]
    EXT["External gates remain closed<br/>20-case blind replay · 20-person test · forward calibration"] -.limits maturity.-> CARD
```

The diagram shows how candidate discovery is governed; it is not a parallel investment-scoring system. Signals pass through evidence intake, contract validation, deterministic models, independent dual calculation, composition playbooks, and CIDM's existing gates. Redlines, vetoes, and evidence invalidation take precedence and trigger blocking or recovery. The signal layer cannot approve investment, inventory, page, or advertising actions.

## System Value and Long-Term Defensibility

Foundation models will continue to improve, and the cost of generating individual answers will continue to decline. The durable value lies above the model: professional decision infrastructure embedded in real operating workflows.

CrossBorder Decision Lab converts fragmented operating experience into reusable system capabilities:

- explicit decision objects, constraints, evidence, counterfactuals, and ownership;
- auditable economics, experiments, action thresholds, and stopping rules;
- coordinated decisions across markets, customers, media, supply, pages, partners, and brands;
- one operating loop for success, failure, incidents, reduction, and exit;
- compounding records of questions, evidence, judgments, actions, outcomes, and corrections.

System value and defensibility are the same flywheel. The more important the decisions, the deeper the system is embedded in workflows, and the more decision assets it accumulates, the more effective—and harder to reproduce—the system becomes.

```text
Professional decision frameworks and models
                    ↓
Embedded cross-border operating workflows
                    ↓
Question–evidence–judgment–action–outcome records
                    ↓
Country, platform, category, and lifecycle benchmarks
                    ↓
Continuously calibrated models, gates, and counterexamples
                    ↓
Higher decision quality and operating certainty
                    ↓
Defensibility through data assets, workflows, governance, and trust
```

Models are replaceable reasoning engines. The durable layer is the accumulated professional method, operating context, calculation tools, shared governance, and decision history.

### Why stronger general-purpose models do not replace it

General-purpose models can interpret materials, generate plans, and support reasoning, but they do not inherently possess a company's accumulated:

1. decision objects and professional ownership boundaries;
2. historical judgments, version changes, and accountability chains;
3. country, platform, category, price-band, and lifecycle benchmarks;
4. success, failure, incident, stopping, and exit cases;
5. continuous links between operating actions and subsequent results;
6. shared evidence, calculation, and approval language across teams.

Models are upgradeable and replaceable reasoning engines. CrossBorder Decision Lab preserves the professional methods, operating context, calculation tools, collaboration protocols, and compounding decision assets above them.

### The compounding mechanism of long-term use

Every real use increases the system's long-term value:

- new questions expand professional scenario coverage;
- new evidence enriches country, platform, and category benchmarks;
- new actions extend operating strategies and execution boundaries;
- new outcomes recalibrate parameters, gates, and counterfactuals;
- new failures become counterexamples, pressure tests, and blocking conditions;
- new collaboration becomes traceable and reusable organizational workflow.

This moves the system from “answering professional questions” toward “continuously managing professional decisions.”

## System Architecture

### Professional capability architecture

```mermaid
flowchart TB
    U["Operating question · event · new evidence"] --> COPO["COPO<br/>Operating posture orchestration"]

    subgraph BOUNDARY["1. Decisions and constraints"]
      direction LR
      CIM["CIM<br/>Competitive facts"] -.facts and continuous monitoring.-> CIDM["CIDM<br/>Capital and portfolio"]
      LTMA["LTMA<br/>Compliance and market access"]
      PPFC["PPFC<br/>Pricing, profit, and cash"]
    end
    COPO --> CIM
    COPO --> CIDM
    COPO --> LTMA
    COPO --> PPFC

    subgraph REALIZE["2. Product realization"]
      direction LR
      PIPM["PIPM<br/>Product definition"] --> SPPQ["SPPQ<br/>Supply, procurement, production, and quality"] --> LIFD["LIFD<br/>Logistics, inventory, and fulfillment"]
    end
    CIDM --> PIPM
    LTMA -.access and continuous compliance.-> SPPQ
    PPFC -.economic and cash boundaries.-> SPPQ

    subgraph GROWTH["3. Market growth"]
      direction TB
      MBCM["MBCM<br/>Marketing, brand, and campaigns"] --> VLB["VLB<br/>Content creative"]
      MBCM --> CAPM["CAPM<br/>Creator and affiliate"]
      VLB --> PLCO["PLCO<br/>Platform and conversion"]
      VLB --> AAMO["AAMO<br/>Advertising measurement"]
      CAPM --> PLCO
      CAPM --> AAMO
      PLCO --> CIG["CIG<br/>Customer, experience, and growth"]
      AAMO --> CIG
    end
    LIFD --> MBCM
    CIG --> O["Actions, customer, and operating outcomes"]
    O --> REVIEW["4. Operating review and selective recomputation<br/>Economics · capital · competition · quality · compliance"]
    REVIEW --> NEXT["Form the next-cycle operating posture<br/>Re-enter COPO"]

    subgraph FOUNDATION["Global decision infrastructure"]
      direction LR
      E["ERDG governance control plane<br/>Objects · evidence · calculations · economics · risk · state · parameters · lineage"]
      F["ECAE experiment and causal assessment<br/>Protocols · estimands · CE0–CE5 · diagnostics · reproducibility"]
      L["LCCA localization and country calibration<br/>Scope · freshness · conversion · comparability · transfer ceiling"]
      Q["Qualification and boundary convergence<br/>Contract and redline validation · causal and incremental claim eligibility · localization applicability"]
      E --> Q
      F --> Q
      L --> Q
    end
    Q -.governance and qualification boundaries.-> COPO
    REVIEW -.outcome replay and parameter calibration.-> CAL["Calibrate ERDG · ECAE · LCCA"]
```

The fourteen professional capabilities plus ECAE, LCCA, and ERDG are within the current controlled-pilot scope. Each professional capability retains decision sovereignty. ECAE governs causal and incremental claim eligibility; LCCA governs localization scope, dynamic-fact freshness, comparability, and transferability ceilings; COPO orchestrates owner-approved conclusions and dependency order. None may override professional conclusions, approve capital outside its authority, or write externally.

### Continuous operating decision loop

```mermaid
sequenceDiagram
    actor U as User/operating event
    participant COPO as COPO
    participant CIM as CIM
    participant CIG as CIG
    participant CIDM as CIDM
    participant PIPM as PIPM
    participant SPPQ as SPPQ
    participant LTMA as LTMA compliance and market access
    participant PPFC as PPFC
    participant LIFD as LIFD
    participant M as Brand · content · creator · page · media
    participant E as ERDG
    U->>COPO: Question, event, or new evidence
    par Facts and constraints
      COPO->>CIM: Competitive facts
      COPO->>CIG: Customer evidence
      COPO->>PPFC: Economic and cash boundaries
      COPO->>LTMA: Compliance and market access
    end
    COPO->>E: G0 evidence qualification
    E-->>COPO: Pass / degrade / block
    COPO->>CIDM: Capital posture
    CIDM-->>COPO: Budget, stop, and exit boundaries
    COPO->>PIPM: Product definition
    PIPM-->>COPO: Product Definition Packet
    par Product realization
      COPO->>SPPQ: Supplier, sample, capacity, and quality
      COPO->>PPFC: Product economics recomputation
      COPO->>LTMA: Formal product access
    end
    COPO->>E: G2 product-supply-economics-access
    E-->>COPO: Pass / partially accept / block
    SPPQ->>LIFD: Qualified batch, capacity, and lead time
    LIFD-->>COPO: ATP/CTP, fulfillment, and reverse plan
    COPO->>M: Parallel positioning, content, creator, page, and media work
    M-->>CIG: Conversion, acquisition, service, and partner outcomes
    CIG-->>COPO: Outcome Packet
    par Operating review
      COPO->>PPFC: Actual economics
      COPO->>CIM: Competitive change review
      COPO->>SPPQ: Quality and supplier recovery
      COPO->>LTMA: Continuous compliance review
    end
    COPO->>E: G5 lineage closure and selective recomputation
    E-->>COPO: Child cycle and impact closure
    COPO->>CIDM: Actual operating results
    CIDM-->>COPO: Add / hold / reduce / exit
    COPO-->>U: New current effective operating posture
```

The sequence shows the cross-phase spine only. The five market capabilities retain separate sovereignty and exchange standard packets. The authoritative capability registry is [`governance/domain-architecture-registry.json`](governance/domain-architecture-registry.json). The whole system uses v2 handoffs and Decision Cycle; the old v1 runtime path is retired.

## Professional Capabilities

Choose the primary Skill by the decision that must be made. Platform coverage, professional models, workflows, inputs, outputs, and failure boundaries live inside each Skill.

| Skill | Runtime | Decision owned | Entry |
|---|---|---|---|
| CIDM | `CIDM-2026.07` + `OSL-v1` | Enter, invest, test, scale, reduce, or exit; external signals create governed candidates only | [Category Investment](category-investment-decision/SKILL.md) |
| CIM | `CIM-2026.07` | Identify competitors, detect change, interpret impact, and respond | [Competitive Intelligence](competitive-intelligence-monitoring/SKILL.md) |
| VLB | `VLB-2026.07` | Explain, adapt, produce, test, and scale content mechanisms | [Content Creative](video-link-breakdown/SKILL.md) |
| CIG | `CIG-2026.07` | Understand customers, friction, incremental value, and growth | [Customer Growth](consumer-insights-customer-growth/SKILL.md) |
| AAMO | `AAMO-2026.07` | Diagnose, measure, budget, scale, or stop advertising | [Advertising](advertising-analysis-measurement-optimization/SKILL.md) |
| LIFD | `LIFD-2026.07` | Route, replenish, allocate, fulfill, recover, or exit | [Logistics and Inventory](logistics-inventory-fulfillment-decision/SKILL.md) |
| PLCO | `PLCO-2026.07` | Diagnose and improve stores, listings, pages, and funnels | [Platform and Conversion](platform-store-listing-conversion/SKILL.md) |
| CAPM | `CAPM-2026.07` | Select, price, contract, operate, renew, or exit partners | [Creator and Affiliate](creator-affiliate-partnership-management/SKILL.md) |
| MBCM | `MBCM-2026.07` | Segment, position, launch, build brands, and orchestrate campaigns | [Marketing and Brand](marketing-brand-campaign-management/SKILL.md) |
| PPFC | `PPFC-2026.07` | Calculate and adjust price, profit, contribution, break-even metrics, financial constraints, and cash risk | [Pricing, Profit, Finance, and Cash Flow](pricing-profit-finance-cashflow-decision/SKILL.md) |
| PIPM | `PIPM-2026.07` | Turn opportunities into traceable product definitions, specifications, MVPs, and roadmaps | [Product Innovation and Product Management](product-innovation-product-management/SKILL.md) |
| SPPQ | `SPPQ-2026.07` | Qualify suppliers, govern procurement commitments, release production and batches, and recover supply or quality failures | [Supplier, Procurement, Production, and Quality](supplier-procurement-production-quality-decision/SKILL.md) |
| LTMA | `LTMA-2026.07` | Gate commercial market access, cap actions, bound claims, and route qualified professional review | [Legal, Tax, IP, and Market Access](legal-tax-intellectual-property-market-access-decision/SKILL.md) |
| COPO | `COPO-2026.07` | Diagnose multi-domain problems, escalate conflicts, synthesize owner-approved operating postures, and sequence dependencies | [Cross-domain Operating Posture Orchestration](cross-domain-operating-posture-orchestration/SKILL.md) |

Detailed platform coverage, models, workflows, inputs, outputs, and failure boundaries live inside each Skill.

Shared foundations do not own final business decisions:

| Foundation | Runtime | Question answered | Entry |
|---|---|---|---|
| **ECAE** | `ECAE` · `controlled_pilot` | Is an experiment executable, is the estimand identifiable, what claim grade is allowed, and when must the result be downgraded or redesigned? | [Experiment and Causal Assessment](experiment-causal-assessment/SKILL.md) |
| **LCCA** | `LCCA-2026.07` · `controlled_pilot` | Is a fact applicable to the target market and time, are scopes comparable, how must parameters be converted, and what is the transfer ceiling? | [Localization and Country Calibration](localization-country-calibration/SKILL.md) |

## Global Decision Infrastructure

The fourteen professional capabilities share [`ERDG-CONTRACT-2026.07`](governance/erdg/ERDG.md). [ECAE](experiment-causal-assessment/SKILL.md) governs causal-evidence eligibility, while [LCCA](localization-country-calibration/SKILL.md) governs scope, dynamic facts, deterministic conversions, comparability, and transferability ceilings. Every capability retains its professional models, thresholds, and final business decisions.

Before domain reasoning, the [`Prompt Intake Guard`](governance/interaction/interaction-governance.md) routes a request to answer, ask, research, calculate, or block. Only ERDG-passed Decision Packets can compile into operator-facing Playbooks. Dynamic platform claims use [versioned knowledge cards](governance/platform-knowledge/platform-knowledge-contract.md) with evidence status, sources, review dates, and invalidation conditions. External evidence follows the [Connector contract](governance/connectors/connector-governance.md); all current manifests are read-only contracts and grant no external-write authority.

1. evidence and counterevidence discipline;
2. auditable economics and statistical estimation;
3. explicit professional ownership;
4. object, evidence, calculation, conclusion, and action lineage;
5. multi-turn selective recomputation;
6. actions with success, stopping, rollback, and exit rules;
7. missing-data, conflict, incident, and pressure handling;
8. long-term calibration by country, platform, category, and lifecycle.

## Current Capabilities

The current version provides fourteen professional decision Skills that have completed their expert-level L1–L3 repository gates and can operate independently or collaborate across domains. It includes:

- professional scenario and lifecycle coverage;
- deterministic economics and statistical estimation tools;
- single-Skill, cross-Skill, and multi-turn execution;
- extreme combinations, conflicts, missing inputs, failures, and pressure tests;
- evidence, calculation, conclusion, action, and version lineage;
- professional ownership, risk redlines, stopping, rollback, and exit governance;
- repository-wide automated validation and release gates.

The unified professional engineering release contract is documented in [`governance/professional-engineering-release.md`](governance/professional-engineering-release.md). The current snapshot binds 835 source cases, Goldens, semantic validators, and numerical recomputation entrypoints to a fingerprinted normalized index; it executes 33 professional validation entrypoints and uses 12 anti-tamper mutations. ECAE and LCCA have completed their L1–L3 controlled-pilot gates and 13/13 consumer-contract acceptances; local fixtures and read-only preflight cases make no production-evidence claim. Run the repository-wide release validator to recompute the current status. L4 production dual-runs, real-outcome calibration, external qualification, and independent non-implementer review remain separate; an engineering pass is neither production readiness nor external-write authority.

The system is not tied to a single foundation-model provider. Models can continue to improve while professional decision contracts, calculation tools, operating benchmarks, and historical assets remain continuous.

## How to Use

### 1. Describe the decision in natural language

Examples:

- “Should we enter this category on Amazon US?”
- “Why did this competitor suddenly start growing?”
- “Why does this video work, and does the mechanism fit our product?”
- “Why did this customer cohort fail to repurchase?”
- “Our ads generate orders but no profit—what should we do?”
- “How much should we replenish, and which warehouse should we use?”
- “How should we rewrite this Listing and rebuild its image set?”
- “Is this creator worth sampling and contracting?”
- “How should we position, launch, and market this new product?”
- “How should price, profit, and break-even ROAS change when platform fees and land, sea, or air freight change?”

### 2. Let the primary Skill make the professional judgment

The owning Skill fixes the decision object, evidence, constraints, and objective; runs the relevant models; and returns actions, success conditions, stopping rules, and any required handoffs.

### 3. Add cross-Skill collaboration when needed

Complex decisions can exchange versioned evidence and constraints across domains, while the Skill that owns the decision retains the final conclusion.

### 4. Feed outcomes back into the system

Operating actions and results update benchmarks, parameters, counterexamples, and the next decision cycle.

## Repository Navigation

| Location | Purpose |
|---|---|
| Fourteen professional capability directories | Professional workflows, models, references, and tests |
| [`evaluations/`](evaluations/) | Single-Skill, cross-Skill, multi-turn, adversarial, and extreme scenarios |
| [`governance/`](governance/) | Ownership, maturity, change-impact, and shared contracts |
| [`governance/erdg/`](governance/erdg/ERDG.md) | ERDG economics, risk, evidence, state, parameters, lineage, and cross-domain governance |
| [`experiment-causal-assessment/`](experiment-causal-assessment/SKILL.md) | ECAE experiment design, causal qualification, evidence grades, diagnostics, reproducibility, consumer acceptance, and reserved L4 gates |
| [`localization-country-calibration/`](localization-country-calibration/SKILL.md) | LCCA localization scope, dynamic facts, deterministic conversion, comparability, transferability, consumer acceptance, and reserved L4 gates |
| [`governance/foundation-capability-registry.json`](governance/foundation-capability-registry.json) | ECAE/LCCA identities, capabilities, consumers, sovereignty, and maturity |
| [`governance/interaction/`](governance/interaction/interaction-governance.md) | Prompt Intake Guard and controlled Decision Packet-to-Operator Playbook compilation |
| [`governance/platform-knowledge/`](governance/platform-knowledge/platform-knowledge-contract.md) | Versioned, expiring platform knowledge cards for PLCO, AAMO, and LIFD |
| [`governance/connectors/`](governance/connectors/connector-governance.md) | Read-only SP-API, Seller Central, ads, and ERP evidence contracts plus Action Gateway |
| [`scripts/`](scripts/) | Repository validation, scoring, integration, and release gates |
| [`.github/workflows/expert-release.yml`](.github/workflows/expert-release.yml) | Automated release-quality gate |
| [`requirements-dev.txt`](requirements-dev.txt) | Locked dependencies for local and automated validation |
| [`RULES.md`](RULES.md) | Maintenance, versioning, testing, and release rules |
| [`README.md`](README.md) | Chinese project homepage |

## Quality and Safety

- Current platform rules, regulations, prices, and market facts are checked at execution time.
- Platform attribution, correlation, prediction, and causal incrementality remain distinct.
- Until L4 closes, real production decisions, high-stakes use, automated execution, and external writes must fail closed; synthetic or read-only preflight evidence cannot be relabeled as production evidence.
- Financial conclusions separate facts, user inputs, benchmarks, and scenarios.
- Legal, tax, intellectual-property, and regulatory matters retain qualified ownership.
- The system does not support deceptive claims, fake engagement, infringement, review manipulation, or platform evasion.
- Content transfer focuses on reusable mechanisms and test logic rather than copying protected expression.

## Copyright

Copyright © 2026 Miles Chen. All rights reserved.

CrossBorder Decision Lab and its original decision frameworks, scoring models, workflows, documentation, and code are protected by copyright. They may not be copied, modified, distributed, sublicensed, sold, commercially used, or used to create derivative works without prior written permission from the copyright owner. See [LICENSE](LICENSE).
