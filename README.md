# Miles-Chen Codex Skills

Personal Codex skills for cross-border ecommerce investment research and video content teardown, with integrated competitor/VOC intelligence and launch validation.

See [RULES.md](RULES.md) for repository conventions: directory structure, source file rules, temporary work directories, delivery naming, sync to local Codex, and Git workflow.

---

## Skills

### Category Investment Decision

Structured, evidence-driven category-entry decisions for cross-border ecommerce. Integrates competitor/VOC intelligence, investment scoring, portfolio selection, localization, unit economics, staged launch experiments, and evidence feedback.

**Path:** `category-investment-decision/`

**Scopes supported (25+ scenarios):** category entry, competitor/VOC research, link reverse analysis, multi-candidate portfolio, country localization (US/EU/UK/JP/SEA), trend/seasonal/opportunity screening, platform-specific analysis (Amazon, TikTok Shop, Temu, Shopify/DTC, Walmart, Etsy, eBay, Shopee/Lazada), competitor monitoring, keyword strategy, product monitoring, store gap filling, SKU extension, old-product diagnosis, post-launch scaling, exit review, profit calculation, experiment design, and launch review.

**Core model (CIDM-2026.08):** 7 dimensions × weighted scoring (100 pts), 5 pre-checks with redline priority, 4 decision tiers, dimension confidence, LTV/content-fit/growth-sustainability calibration. Outputs include full reports, rapid screening cards, link reverse-analysis cards, portfolio comparison tables, country entry matrices, competitor monitoring reports, post-launch decision cards, exit reviews, and phased validation plans.

**Files:**

| Path | Purpose |
|---|---|
| `SKILL.md` | Full decision framework, scenario routing, scoring model, execution checklist |
| `agents/openai.yaml` | Codex Skill UI metadata |
| `scripts/workspace_manager.py` | Create and clean marked temporary workspaces |
| `scripts/profit_model.py` | Deterministic per-unit profit and break-even ad rate calculator |
| `scripts/portfolio_selector.py` | Constrained portfolio selection under budget/SKU limits |
| `scripts/analyze_voc.py` | Deterministic profiling and aggregation for coded VOC datasets |
| `scripts/evaluate_experiment.py` | Funnel metrics and preregistered launch-gate evaluator |
| `scripts/test_models.py` | Regression tests for finance, portfolio, VOC, experiments and workspace safety |
| `references/scoring-model.md` | 7-dimension scoring anchors, confidence levels |
| `references/selection-scenarios.md` | 25+ scenario routes with evidence priorities |
| `references/report-style-guide.md` | Professional report structure, decision page and evidence ledger rules |
| `references/report-template.md` | Investment memo, screening card, matrix, operating review and exit memo templates |
| `references/universal-scenario-kernel.md` | Universal decision/object/output routing for uncovered scenarios |
| `references/link-reverse-analysis.md` | 6-step ASIN/product link reverse analysis |
| `references/portfolio-decision.md` | Multi-candidate ranking and combinatorial selection |
| `references/country-localization.md` | US/EU/UK/JP/SEA localization checks |
| `references/country-routing-universal.md` | Any-country localization fallback and regional split rules |
| `references/validation-playbooks.md` | Phased testing plans and review framework |
| `references/post-launch-playbook.md` | Post-launch scale, steady-state, decline and exit decisions |
| `references/competitor-monitoring.md` | Ongoing competitor monitoring, alerts and monthly report structure |
| `references/keyword-strategy.md` | Keyword classification, lifecycle strategy and traffic-gap application |
| `references/command-reference.md` | Command-style scene entry points and routing rules |
| `references/pressure-test-matrix.md` | Ten-scenario regression matrix for report quality and routing coverage |
| `references/voc-competitor-intelligence.md` | VOC coding, competitor layering and market-gap qualification |
| `references/evidence-and-finance.md` | Evidence grading, unit economics, sensitivity scenarios |
| `references/platform-playbooks.md` | Platform-specific analysis (Amazon, TikTok, Temu, etc.) |
| `references/platform-routing-universal.md` | Any-platform routing by traffic logic, fees, fulfillment and risk |
| `references/scene-output-protocols.md` | Per-scene deliverable structure |
| `references/usage-guide.md` | Minimum input requirements, call examples |
| `references/source-routing.md` | Data source selection by question type |
| `references/error-and-fallback.md` | Degradation levels, partial completion, recovery |
| `references/input-schemas.md` | Product, portfolio, VOC and experiment input specifications |

### Video Link Breakdown

Analyzes short-form video links into structured content teardowns covering script structure, editing techniques, content quality, audience fit, replicable templates, and upgrade suggestions.

**Path:** `video-link-breakdown/`

**Supported platforms:** TikTok, YouTube Shorts, Instagram Reels, X/Twitter videos, Bilibili, Douyin.

**Analysis output:** basic video facts, strategic diagnosis, script structure (hook/setup/beats/payoff/CTA), editing techniques (pacing/jump-cuts/captions/transitions/sound/camera), content quality scores (hook/pacing/clarity/persuasion/originality/replication value), replicable beat-by-beat template, concrete upgrade suggestions, and rewritten script when useful.

**Files:**

| Path | Purpose |
|---|---|
| `SKILL.md` | Analysis framework, workflow, link handling, output templates |
| `agents/openai.yaml` | Codex Skill UI metadata |
| `scripts/prepare_video_link.py` | Video download via yt-dlp, metadata extraction, frame extraction, contact sheet generation |

---

# Miles-Chen Codex 技能库

跨境电商投资研究与视频内容拆解技能库；品类投决中内建竞品/VOC 情报与上市验证闭环。

仓库公约（目录结构、源文件规则、临时目录、交付命名、本地同步、Git 工作流）详见 [RULES.md](RULES.md)。

---

## 技能

### 品类投资决策

面向跨境的、证据驱动的品类进入决策。内建竞品/VOC 取证、投资评分、组合决策、国家本地化、单位经济、分阶段测款与证据回写。

**路径：** `category-investment-decision/`

**支持场景（25+）：** 品类进入、竞品/VOC 情报、链接反查、多候选组合、国家本地化（美国/欧盟/英国/日本/东南亚）、趋势/季节/机会筛选、平台专项分析（Amazon、TikTok Shop、Temu、Shopify/DTC、Walmart、Etsy、eBay、Shopee/Lazada）、竞品监控、关键词策略、店铺补品、老品扩展、老品诊断、上市后放量、退出复盘、利润核算、测款设计与复盘。

**核心模型（CIDM-2026.08）：** 七维加权评分（100 分制）、五道前置门槛（红线优先）、四档决策阈值、维度置信度、复购/LTV、达人/联盟适配度和增长可持续性校准。交付物包括完整报告、快速初筛卡、链接反查卡、组合对比表、国家进入矩阵、竞品监控月报、上市后决策卡、退出复盘和分阶段验证计划。

**文件清单：**

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 完整决策框架、场景路由、评分模型、执行自检 |
| `agents/openai.yaml` | Codex Skill 界面元数据 |
| `scripts/workspace_manager.py` | 安全创建与清理任务临时目录 |
| `scripts/profit_model.py` | 确定性单件利润与盈亏平衡广告率计算 |
| `scripts/portfolio_selector.py` | 预算/SKU 约束下的组合优化选择 |
| `scripts/analyze_voc.py` | 已编码 VOC 数据的确定性质量检查与聚合 |
| `scripts/evaluate_experiment.py` | 漏斗指标与事先测款门槛评估 |
| `scripts/test_models.py` | 利润、组合、VOC、实验与工作空间回归测试 |
| `references/scoring-model.md` | 七维评分锚点与置信度定义 |
| `references/selection-scenarios.md` | 25+ 个场景的路由与取证重点 |
| `references/report-style-guide.md` | 高密度专业报告结构、决策页与 Evidence/Assumption Ledger 规则 |
| `references/report-template.md` | 投资备忘录、压缩版完整报告、场景模块、经营复盘与退出复盘模板 |
| `references/universal-scenario-kernel.md` | 未覆盖场景的通用决策/对象/输出路由 |
| `references/link-reverse-analysis.md` | ASIN/商品链接六步反查 |
| `references/portfolio-decision.md` | 多候选排名与组合选择 |
| `references/country-localization.md` | 美/欧/英/日/东南亚本地化检查 |
| `references/country-routing-universal.md` | 任意国家本地化兜底与区域拆分规则 |
| `references/validation-playbooks.md` | 分阶段测款与复盘框架 |
| `references/post-launch-playbook.md` | 上市后放量、稳态、衰退与退出决策 |
| `references/competitor-monitoring.md` | 竞品持续监控、告警和月报结构 |
| `references/keyword-strategy.md` | 关键词分类、生命周期策略与流量缺口应用 |
| `references/command-reference.md` | 命令式场景入口与路由规则 |
| `references/pressure-test-matrix.md` | 报告质量与路由覆盖的 10 场景回归矩阵 |
| `references/voc-competitor-intelligence.md` | VOC 编码、竞品分层与市场空白判定 |
| `references/evidence-and-finance.md` | 证据分级、单位经济模型、敏感性场景 |
| `references/platform-playbooks.md` | 各平台分析剧本（Amazon、TikTok、Temu 等） |
| `references/platform-routing-universal.md` | 任意平台按流量逻辑、费用、履约和风险路由 |
| `references/scene-output-protocols.md` | 各场景交付物结构 |
| `references/usage-guide.md` | 最小输入要求、调用示例 |
| `references/source-routing.md` | 按问题类型选择数据源 |
| `references/error-and-fallback.md` | 降级等级、部分完成、中断恢复 |
| `references/input-schemas.md` | 商品、组合、VOC 与实验输入规范 |

### 视频链接拆解

将短视频链接拆解为结构化分析报告，覆盖脚本结构、剪辑手法、内容质量、受众匹配、可复刻模板和优化建议。

**路径：** `video-link-breakdown/`

**支持平台：** TikTok、YouTube Shorts、Instagram Reels、X/Twitter 视频、Bilibili、抖音。

**分析输出：** 基础信息、一句话诊断、脚本结构（钩子/铺垫/节奏/收尾/CTA）、剪辑手法（节奏/跳切/字幕/转场/音效/镜头）、内容质量评分（钩子/节奏/清晰度/说服力/原创性/复刻价值）、可复刻模板、具体优化建议、以及改写脚本（如适用）。

**文件清单：**

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 分析框架、工作流、链接处理、输出模板 |
| `agents/openai.yaml` | Codex Skill 界面元数据 |
| `scripts/prepare_video_link.py` | 视频下载（yt-dlp）、元数据提取、关键帧提取、联系表生成 |
