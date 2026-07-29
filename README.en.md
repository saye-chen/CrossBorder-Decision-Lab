# CrossBorder Decision Lab

[中文首页](README.md) · [Skill Directory](#skill-directory) · [ERDG Governance](#shared-decision-infrastructure) · [System Architecture](#system-architecture) · [How to Use](#how-to-use)

> Professional decision infrastructure for cross-border commerce—turning experience-dependent judgment into evidence-based, model-backed, actionable, and compounding decision assets.

Current release train: `2026.07`; target architecture: `CBDS-ARCH-2026.07`; shared contract: `ERDG-CONTRACT-2026.07`.

CrossBorder Decision Lab is built for cross-border operators, brands, investors, and professional teams. It is not a generic prompt collection. It connects category investment, competitive intelligence, content, customers, advertising, fulfillment, conversion, partnerships, marketing, and pricing finance into eleven professional domains that can operate independently and collaborate under shared decision contracts.

The system includes eleven professional domains with complete core workflows whose expert-level repository gates through L1–L3 are complete, plus ERDG. The new D03/PIPM domain has passed substantive depth review and includes eight deterministic product models, nine specialized outputs, 101 evaluation cases, ten scenario-owned Goldens, 404 positive/counterexample execution assertions, continuous decisions, extreme pressure tests, consumer-owned adapters, dual-run migration, and rollback evidence. Independent-owner authoritative migration remains closed, and every domain remains L4 `controlled pilot`.

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
    U["Operating question · event · new evidence"] --> D14["D14 operating posture and orchestration<br/>Planned"]
    D14 --> D01["D01 CIDM<br/>Capital and portfolio"]
    D14 --> D02["D02 CIM<br/>Competitive facts"]
    D14 --> D03["D03 PIPM<br/>Product definition"]
    D14 --> D05["D05 compliance and market access<br/>Planned"]
    D14 --> D06["D06 PPFC<br/>Pricing, profit, and cash"]
    D01 --> D03 --> D04["D04 supply, procurement, production, and quality<br/>Next build"] --> D07["D07 LIFD<br/>Logistics, inventory, and fulfillment"]
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
    E -.contract and redline validation.-> D01
    E -.contract and redline validation.-> D04
    E -.contract and redline validation.-> D12
    O -.replay and parameter calibration.-> E
    classDef planned stroke-dasharray:6 5
    class D05,D14 planned
```

Eleven domains are currently runnable; D04 is the next build, while D05 and D14 are planned and are blocked from execution by the registry validator. Every professional domain retains its decision sovereignty. D14 orchestrates only, and ERDG performs neutral governance and deterministic shared calculations without making domain business decisions.

### Continuous D01-D14 decision loop

```mermaid
sequenceDiagram
    actor U as User/operating event
    participant D14 as D14 orchestration (planned)
    participant D02 as D02 CIM
    participant D13 as D13 CIG
    participant D01 as D01 CIDM
    participant D03 as D03 PIPM
    participant D04 as D04 supply (next build)
    participant D05 as D05 compliance (planned)
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
| CIDM | `CIDM-2026.07` | Enter, invest, test, scale, reduce, or exit | [Category Investment](category-investment-decision/SKILL.md) |
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

Detailed platform coverage, models, workflows, inputs, outputs, and failure boundaries live inside each Skill.

## Shared Decision Infrastructure

The eleven domains share [`ERDG-CONTRACT-2026.07`](governance/erdg/ERDG.md). ERDG is repository-owned neutral infrastructure for structural safety, deterministic shared calculations, and cross-domain contract validation; each Skill retains its professional models, thresholds, and final business decisions.

1. evidence and counterevidence discipline;
2. auditable economics and statistical estimation;
3. explicit professional ownership;
4. object, evidence, calculation, conclusion, and action lineage;
5. multi-turn selective recomputation;
6. actions with success, stopping, rollback, and exit rules;
7. missing-data, conflict, incident, and pressure handling;
8. long-term calibration by country, platform, category, and lifecycle.

## Current Capabilities

The current version provides eleven professional decision Skills that have completed their expert-level L1–L3 repository gates and can operate independently or collaborate across domains. It includes:

- professional scenario and lifecycle coverage;
- deterministic economics and statistical estimation tools;
- single-Skill, cross-Skill, and multi-turn execution;
- extreme combinations, conflicts, missing inputs, failures, and pressure tests;
- evidence, calculation, conclusion, action, and version lineage;
- professional ownership, risk redlines, stopping, rollback, and exit governance;
- repository-wide automated validation and release gates.

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
| Eleven Skill directories | Professional workflows, models, references, and tests |
| [`evaluations/`](evaluations/) | Single-Skill, cross-Skill, multi-turn, adversarial, and extreme scenarios |
| [`governance/`](governance/) | Ownership, maturity, change-impact, and shared contracts |
| [`scripts/`](scripts/) | Repository validation, scoring, integration, and release gates |
| [`.github/workflows/expert-release.yml`](.github/workflows/expert-release.yml) | Automated release-quality gate |
| [`requirements-dev.txt`](requirements-dev.txt) | Locked dependencies for local and automated validation |
| [`RULES.md`](RULES.md) | Maintenance, versioning, testing, and release rules |
| [`README.md`](README.md) | Chinese project homepage |

## Quality and Safety

- Current platform rules, regulations, prices, and market facts are checked at execution time.
- Platform attribution, correlation, prediction, and causal incrementality remain distinct.
- Financial conclusions separate facts, user inputs, benchmarks, and scenarios.
- Legal, tax, intellectual-property, and regulatory matters retain qualified ownership.
- The system does not support deceptive claims, fake engagement, infringement, review manipulation, or platform evasion.
- Content transfer focuses on reusable mechanisms and test logic rather than copying protected expression.

## Copyright

Copyright © 2026 Miles Chen. All rights reserved.

CrossBorder Decision Lab and its original decision frameworks, scoring models, workflows, documentation, and code are protected by copyright. They may not be copied, modified, distributed, sublicensed, sold, commercially used, or used to create derivative works without prior written permission from the copyright owner. See [LICENSE](LICENSE).
