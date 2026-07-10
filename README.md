# CrossBorder Decision Lab

Evidence-driven Codex skills for cross-border commerce decisions, from category investment and unit economics to video-content validation, localization and scalable execution.

中文品牌：**出海决策实验室**。

See [RULES.md](RULES.md) for repository conventions. Run `python3 scripts/validate_repo.py` for repository-level validation in addition to the generic Codex Skill validator.

## Decision system

```text
CrossBorder Decision Lab
├── CIDM — Category Investment Decision
└── VLB  — Video Link Breakdown
```

CIDM answers what to sell, whether to enter, how much to invest and when to stop. VLB tests whether a content pattern can attract, persuade and convert for the target product and market. Their integration is optional and non-destructive: VLB emits a structured adjustment proposal but never silently rewrites a historical CIDM report.

## Category Investment Decision

**Path:** `category-investment-decision/`
**Runtime:** `CIDM-2026.08`

Evidence-driven category and SKU investment decisions for Amazon, TikTok Shop, Shopee, Lazada, Shopify/DTC, Walmart, eBay, Etsy, Temu, Shein and other cross-border channels.

Core system:

- five pre-check gates: market size, entry feasibility, profit, compliance/sellability and winning wedge;
- seven weighted dimensions with confidence and redline overrides;
- Decision Card, Decision Memo and Investment Diligence delivery levels;
- competitor/VOC, keyword, link reverse-analysis, country/platform routing and portfolio selection;
- deterministic unit economics, reverse funnel, portfolio and experiment calculators;
- launch, scale, steady-state, decline, exit and evidence-feedback workflows.

Important resources:

| Path | Purpose |
|---|---|
| `SKILL.md` | Core workflow, routing, gates, scoring and quality rules |
| `references/scoring-model.md` | Seven-dimension anchors and confidence |
| `references/benchmark-priors.md` | Conditional priors for demand, margin and competition warning lines |
| `references/scene-output-protocols.md` | Scene-specific delivery structures |
| `references/evidence-and-finance.md` | Evidence grading and financial model |
| `references/report-template.md` | Decision and operating templates |
| `scripts/test_models.py` | Finance, portfolio, VOC, experiment and workspace regression tests |

## Video Link Breakdown

**Path:** `video-link-breakdown/`
**Runtime:** `VLB-2026.08`

Evidence-driven video content and commerce decisions for TikTok, YouTube Shorts, Instagram Reels, X/Twitter, Bilibili, Douyin, TikTok Shop, Shopee Video and Pinterest.

VLB uses one shared evidence protocol and loads only the modules needed for the user's goal. It supports single-video teardown, competitive comparison, account diagnosis, script optimization, commerce decisions, localization/compliance, creator/material scale systems and optional CIDM integration.

Important resources:

| Path | Purpose |
|---|---|
| `SKILL.md` | Evidence protocol, scenario routing, delivery levels and quality gate |
| `references/standard-teardown.md` | Rhythm, script, audiovisual language, audience, platform and replication |
| `references/scoring-model.md` | Goal-specific normalized content scoring |
| `references/commerce-decision.md` | Commercial gates, commerce funnel, unit economics and ROI |
| `references/localization-and-compliance.md` | Localization levels and compliance quick-screen |
| `references/creator-scale-system.md` | Creator portfolio, batch materials and fatigue testing |
| `references/cidm-integration.md` | Structured, non-destructive CIDM adjustment protocol |
| `scripts/prepare_video_link.py` | Metadata, video preparation, frame extraction and contact sheet generation |
| `scripts/test_prepare_video_link.py` | Preparation workflow regression tests |

---

# 出海决策实验室

面向跨境商业决策的证据驱动 Codex 技能库：从品类投资、利润和风险判断，延伸到视频内容验证、本地化与规模化执行。

## 品类投资决策（CIDM）

回答“做什么、值不值得进入、投多少、怎么验证、什么时候停止”。使用五道前置门槛、七维评分、置信度、红线否决、完整单位经济、组合决策和上市后闭环。根据问题复杂度选择 Decision Card、Decision Memo 或 Investment Diligence，不再强制所有问题套用完整报告目录。

## 视频链接拆解（VLB）

回答“这个视频为什么有效、是否适合目标产品、怎样本地化、能否赚钱和规模化”。统一使用 `O/M/U/B/I` 证据协议，再按目标加载标准拆解、评分、商业判断、本地化/合规、达人规模系统或 CIDM 对接模块。没有后台基线时不输出伪精确的留存、转化或效果承诺。

## 品牌口径

> 出海决策实验室：用证据、利润模型和内容验证，帮助跨境卖家判断做什么、怎么做、什么时候停止。

## Copyright

Copyright © 2026 Miles Chen. All rights reserved.

CrossBorder Decision Lab / 出海决策实验室及其原创决策框架、评分模型、工作流、文档和代码受版权保护。未经版权所有者事先书面许可，不得复制、修改、分发、转授权、销售、商业使用或基于本仓库内容制作衍生作品。详见 [LICENSE](LICENSE)。
