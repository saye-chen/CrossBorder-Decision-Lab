# CrossBorder Decision Lab

[中文首页](README.md) · [Skill Directory](#skill-directory) · [F01 and ERDG](#shared-decision-infrastructure) · [System Architecture](#system-architecture) · [How to Use](#how-to-use)

> Professional decision infrastructure for cross-border commerce—turning experience-dependent judgment into evidence-based, model-backed, actionable, and compounding decision assets.

Current release train: `2026.07`; target architecture: `CBDS-ARCH-2026.07`; shared contract: `ERDG-CONTRACT-2026.07`.

CrossBorder Decision Lab is built for cross-border operators, brands, investors, and professional teams. It connects category investment, competitive intelligence, product, supply/procurement/production/quality, legal/tax/IP/market access, pricing finance, fulfillment, conversion, advertising, partnerships, content, marketing, and customer growth into thirteen professional domains that can operate independently and collaborate under shared decision contracts.

The system includes thirteen professional domains with complete core workflows whose expert-level L1–L3 repository gates are complete, ERDG, and the current F01 experiment and causal-assessment foundation. D05/LTMA adds commercial market-access gates, action ceilings, claim-use boundaries, qualified professional-review routing, dynamic-rule controls, incident recovery, and temporary-contract migration. It does not issue legal, tax, FTO, certification, or laboratory opinions. System maturity remains `controlled_pilot`; L4 is open, so real production decisions, high-stakes use, and external writes are unavailable.

CIDM now includes the governed `OSL-v1` opportunity-signal layer. It clean-room reimplements external research ideas as eight deterministic candidate-signal families with multi-source field quality, five composition playbooks, effective-supply/VOC analysis, proof-bound CIDM-to-PLCO handoff, partial-failure DAG execution, R0–R4 recovery, an independent oracle, and 13 source mutations. The layer expands candidate coverage only; it cannot directly change the seven-dimension score, capital posture, or cross-domain sovereignty. The authorized 20-case blind replay, 20-person non-implementer comprehension test, and forward calibration remain open, so this is not a production-maturity claim.

### OSL-v1 opportunity-signal architecture

```mermaid
flowchart TB
    subgraph IN["1. Evidence intake"]
      direction LR
      RAW["External research<br/>raw evidence"] --> ADP["Evidence Adapter<br/>normalization · freshness · source family · lineage"]
      ADP --> CON["Signal contract<br/>object · window · counterevidence · alternatives"]
    end
    subgraph CORE["2. Signal computation"]
      direction LR
      MOD["8 deterministic<br/>models"] <--> ORA["Independent Oracle<br/>status and metric dual calculation"]
      ORA --> SIG["12 canonical<br/>signals"]
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
    RECOMPUTE -.re-enters evidence intake.-> RAW
    EXT["External gates remain closed<br/>20-case blind replay · 20-person test · forward calibration"] -.limits maturity.-> CARD
    classDef evidence fill:#e8f1ff,stroke:#3269a8,color:#17324d
    classDef signal fill:#eaf7f0,stroke:#31845c,color:#153b2a
    classDef decision fill:#fff4d8,stroke:#a87716,color:#4d3810
    classDef recovery fill:#f3ecff,stroke:#7652a8,color:#34234d
    classDef stop fill:#ffe9e7,stroke:#b84a42,color:#541e1a
    class RAW,ADP,CON evidence
    class MOD,ORA,SIG signal
    class PLAY,GATE,CARD,HAND decision
    class DRIFT,FREEZE,RECOMPUTE recovery
    class BLOCK,EXT stop
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

### D01-D14 target architecture

```mermaid
flowchart TB
    U["Operating question · event · new evidence"] --> D14["D14 coordinated posture and orchestration<br/>Planned"]
    D14 --> D01["D01 CIDM<br/>Capital and portfolio"]
    D14 --> D02["D02 CIM<br/>Competitive facts"]
    D14 --> D03["D03 PIPM<br/>Product definition"]
    D14 --> D05["D05 LTMA<br/>Compliance and market access"]
    D14 --> D06["D06 PPFC<br/>Pricing, profit, and cash"]
    D01 --> D03 --> D04["D04 SPPQ<br/>Supply, procurement, production, and quality"] --> D07["D07 LIFD<br/>Logistics, inventory, and fulfillment"]
    D07 --> D12["D12 MBCM<br/>Marketing, brand, and campaigns"]
    D12 --> D11["D11 VLB<br/>Content creative"]
    D12 --> D10["D10 CAPM<br/>Creator and affiliate"]
    D11 --> D08["D08 PLCO<br/>Platform and conversion"]
    D11 --> D09["D09 AAMO<br/>Advertising measurement"]
    D10 --> D08
    D10 --> D09
    D08 --> D13["D13 CIG<br/>Customer, experience, and growth"]
    D09 --> D13
    D02 -.facts and continuous monitoring.-> D01
    D05 -.access and continuous compliance.-> D04
    D06 -.economic and cash boundaries.-> D04
    D13 --> O["Actions, customer, and operating outcomes"]
    O --> D06 --> D01 --> D14
    O -.quality, competition, rules, and customer feedback.-> D02
    O -.quality, competition, rules, and customer feedback.-> D04
    O -.quality, competition, rules, and customer feedback.-> D05
    E["ERDG governance control plane<br/>Objects · evidence · calculations · economics · risk · state · parameters · lineage"] -.governs.-> D14
    F["F01 experiment and causal assessment<br/>Protocols · estimands · CE0–CE5 · diagnostics · reproducibility"] -.causal and incremental claim eligibility.-> D01
    F -.causal and incremental claim eligibility.-> D06
    F -.causal and incremental claim eligibility.-> D12
    O -.authorized outcome replay and calibration.-> F
    E -.contract and release governance.-> F
    E -.contract and redline validation.-> D01
    E -.contract and redline validation.-> D04
    E -.contract and redline validation.-> D12
    O -.replay and parameter calibration.-> E
    classDef planned stroke-dasharray:6 5
    class D14 planned
```

Thirteen domains and F01 are currently runnable; D14 remains planned and is blocked from execution by the registry validator. Every professional domain retains its decision sovereignty. F01 governs experiment design, causal/incremental claim eligibility, and evidence grades but never makes the final business decision. D14 only orchestrates, escalates conflicts, synthesizes a coordinated posture from owner-approved decisions, and sequences work within approved resource envelopes; it cannot adjudicate professional conclusions, approve capital, or write externally. ERDG performs neutral governance and deterministic shared calculations without making domain business decisions.

### Continuous D01-D14 decision loop

```mermaid
sequenceDiagram
    actor U as User/operating event
    participant D14 as D14 orchestration (planned)
    participant D02 as D02 CIM
    participant D13 as D13 CIG
    participant D01 as D01 CIDM
    participant D03 as D03 PIPM
    participant D04 as D04 SPPQ
    participant D05 as D05 LTMA compliance and market access
    participant D06 as D06 PPFC
    participant D07 as D07 LIFD
    participant M as D12/D11/D10/D08/D09 market domains
    participant E as ERDG
    U->>D14: Question, event, or new evidence
    par Facts and constraints
      D14->>D02: Competitive facts
      D14->>D13: Customer evidence
      D14->>D06: Economic and cash boundaries
      D14->>D05: Compliance and market access
    end
    D14->>E: G0 evidence qualification
    E-->>D14: Pass / degrade / block
    D14->>D01: Capital posture
    D01-->>D14: Budget, stop, and exit boundaries
    D14->>D03: Product definition
    D03-->>D14: Product Definition Packet
    par Product realization
      D14->>D04: Supplier, sample, capacity, and quality
      D14->>D06: Product economics recomputation
      D14->>D05: Formal product access
    end
    D14->>E: G2 product-supply-economics-access
    E-->>D14: Pass / partially accept / block
    D04->>D07: Qualified batch, capacity, and lead time
    D07-->>D14: ATP/CTP, fulfillment, and reverse plan
    D14->>M: Parallel positioning, content, creator, page, and media work
    M-->>D13: Conversion, acquisition, service, and partner outcomes
    D13-->>D14: Outcome Packet
    par Operating review
      D14->>D06: Actual economics
      D14->>D02: Competitive change review
      D14->>D04: Quality and supplier recovery
      D14->>D05: Continuous compliance review
    end
    D14->>E: G5 lineage closure and selective recomputation
    E-->>D14: Child cycle and impact closure
    D14->>D01: Actual operating results
    D01-->>D14: Add / hold / reduce / exit
    D14-->>U: New current effective operating posture
```

The sequence shows the cross-phase spine only. The five market Skills keep separate sovereignty and exchange standard packets. The authoritative D01-D14 registry is [`governance/domain-architecture-registry.json`](governance/domain-architecture-registry.json). The whole system now uses v2 handoffs and Decision Cycle; the old v1 runtime path is retired.

## Skill Directory

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

Detailed platform coverage, models, workflows, inputs, outputs, and failure boundaries live inside each Skill.

Shared foundations do not own final business decisions:

| Foundation | Runtime | Question answered | Entry |
|---|---|---|---|
| **F01 / ECAE** | `ECAE` · `controlled_pilot` | Is an experiment executable, is the estimand identifiable, what claim grade is allowed, and when must the result be downgraded or redesigned? | [Experiment and Causal Assessment](experiment-causal-assessment/SKILL.md) |

## Shared Decision Infrastructure

The thirteen domains share [`ERDG-CONTRACT-2026.07`](governance/erdg/ERDG.md) and use [F01 Experiment and Causal Assessment](experiment-causal-assessment/SKILL.md) for experiment protocols, estimands, CE0–CE5 evidence grades, diagnostics, reproducibility, and causal claim ceilings. ERDG owns structural safety, deterministic shared calculations, and cross-domain contract validation; F01 owns causal-evidence eligibility; each Skill retains its models, thresholds, and final business decisions.

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

The current version provides thirteen professional decision Skills that have completed their expert-level L1–L3 repository gates and can operate independently or collaborate across domains. It includes:

- professional scenario and lifecycle coverage;
- deterministic economics and statistical estimation tools;
- single-Skill, cross-Skill, and multi-turn execution;
- extreme combinations, conflicts, missing inputs, failures, and pressure tests;
- evidence, calculation, conclusion, action, and version lineage;
- professional ownership, risk redlines, stopping, rollback, and exit governance;
- repository-wide automated validation and release gates.

The unified thirteen-domain engineering release contract is documented in [`governance/professional-engineering-release.md`](governance/professional-engineering-release.md). The current release snapshot binds 790 source cases across 13 domains, their Goldens, semantic validators, and numerical recomputation entrypoints to a fingerprinted normalized index; it executes 31 professional validation entrypoints and uses 12 anti-tamper mutations. F01 has passed L1–L3, 163 tests, source binding for 23 methods, and 13/13 controlled-pilot consumer acceptances; its 91 read-only preflight cases make no production-evidence claim. Run `python3 scripts/validate_release_integrity.py` and `python3 scripts/validate_f01_release.py --require-l3` to recompute release status. L4 production dual-runs, real-outcome calibration, advanced-backend external qualification, and independent non-implementer review remain separate; an engineering pass is not production readiness, external-write authority, or permission to unfreeze D14.

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
| Thirteen Skill directories | Professional workflows, models, references, and tests |
| [`evaluations/`](evaluations/) | Single-Skill, cross-Skill, multi-turn, adversarial, and extreme scenarios |
| [`governance/`](governance/) | Ownership, maturity, change-impact, and shared contracts |
| [`governance/erdg/`](governance/erdg/ERDG.md) | ERDG economics, risk, evidence, state, parameters, lineage, and cross-domain governance |
| [`experiment-causal-assessment/`](experiment-causal-assessment/SKILL.md) | F01 experiment design, causal qualification, evidence grades, diagnostics, reproducibility, consumer acceptance, and reserved L4 gates |
| [`governance/foundation-capability-registry.json`](governance/foundation-capability-registry.json) | F01/F02 identities, capabilities, consumers, sovereignty, and maturity |
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
