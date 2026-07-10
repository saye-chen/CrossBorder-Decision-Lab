# Miles-Chen Codex Skills

Personal Codex skills for cross-border ecommerce investment research and video content teardown, with integrated competitor/VOC intelligence and launch validation.

See [RULES.md](RULES.md) for repository conventions: directory structure, source file rules, temporary work directories, delivery naming, sync to local Codex, and Git workflow.

Repository-specific validation is implemented in `scripts/validate_repo.py`; it enforces runtime version declarations, local-link integrity, frontmatter compatibility, and normalized video-scoring weights in addition to the generic Codex Skill validator.

---

## Skills

### Category Investment Decision

Structured, evidence-driven category-entry decisions for cross-border ecommerce. Integrates competitor/VOC intelligence, investment scoring, portfolio selection, localization, unit economics, staged launch experiments, and evidence feedback.

**Path:** `category-investment-decision/`

**Scopes supported (25+ scenarios):** category entry, competitor/VOC research, link reverse analysis, multi-candidate portfolio, country localization (US/EU/UK/JP/SEA), trend/seasonal/opportunity screening, platform-specific analysis (Amazon, TikTok Shop, Temu, Shopify/DTC, Walmart, Etsy, eBay, Shopee/Lazada), competitor monitoring (with category-elastic thresholds, capability attribution, SOV tracking, channel/distributor monitoring and opportunity-window classification), keyword strategy, product monitoring, store gap filling, SKU extension, old-product diagnosis, post-launch scaling (with category-adaptive timelines, phased advertising structure, portfolio interaction checks, passive/active decline distinction and cash-flow veto), exit review, profit calculation, experiment design, and launch review.

**Core model (CIDM-2026.08):** 7 dimensions × weighted scoring (100 pts), 5 pre-checks with redline priority, 4 decision tiers, dimension confidence, LTV/content-fit/growth-sustainability calibration. Outputs include full reports, rapid screening cards, link reverse-analysis cards, portfolio comparison tables, country entry matrices, competitor monitoring reports, post-launch decision cards, exit reviews, and phased validation plans.

**Five pre-check gates before scoring:** CIDM does not start from a score. It first tests whether the opportunity can pass five commercial gates. Redlines override the final score.

| Gate | Decision question | Professional judgment points | Formula / model basis |
|---|---|---|---|
| Is the market large enough? | Can demand support the target sales scale and operating cadence? | Keyword clusters, trend stability, purchase motivation, repeat/consumable potential, social and marketplace demand signals | Demand evidence triangulation; LTV/frequency adjustment; proxy-signal confidence grading |
| Can we enter? | Can a new or non-leading seller obtain traffic and break through competition? | Review moat, brand concentration, ad pressure, recent new-product breakthroughs, long-tail entry points | Competition layer analysis; review/recency moat; confidence-adjusted entry score |
| Can it make money? | Does the product remain profitable after full landed and operating costs? | Product, packaging, duty, inbound, fulfillment, commission, ad, promotion, returns, storage, QC, payment and other costs | `net profit = price - full cost stack`; `break-even ad rate = pre-ad contribution margin / price`; scenario and sensitivity analysis |
| Can it be sold safely? | Are compliance, IP, platform, safety and return risks controllable? | Regulatory path, certification, restricted/prohibited category, claim/label risk, patent/trademark/copyright exposure, return risk | Redline-first risk gate; mandatory human review triggers; risk-control confidence |
| Why us? | What concrete wedge makes buyers choose us over incumbents? | VOC pain repetition, competitor promise-experience gap, product/package/service/content wedge, execution feasibility | Wedge validation chain; weakest-assumption test; content-fit and growth-sustainability calibration |

**Scoring and decision math:** each dimension is scored from 0 to 10, then converted to a weighted 100-point score using `weighted score = raw score / 10 × dimension weight`. The seven weights are: market demand 20, competitive entry 20, profit 20, content propagation 10, supply-chain control 10, risk control 10, opportunity window 10. Default decision tiers are: 80-100 enter, 65-79.9 cautious entry / small-scale test, 50-64.9 observe or content test, below 50 do not enter. Low confidence, redlines, or failed pre-checks can downgrade the decision regardless of total score.

**Deterministic calculators:** financial and validation calculations are implemented as auditable scripts, not hidden spreadsheet logic: `profit_model.py` for unit economics and batch break-even, `reverse_funnel.py` for order/click/impression requirements, `portfolio_break_even.py` for minimum portfolio success rate, `portfolio_selector.py` for constrained SKU selection, and `evaluate_experiment.py` for preregistered launch gates.

**Files:**

| Path | Purpose |
|---|---|
| `SKILL.md` | Full decision framework, scenario routing, scoring model, execution checklist |
| `agents/openai.yaml` | Codex Skill UI metadata |
| `scripts/workspace_manager.py` | Create and clean marked temporary workspaces |
| `scripts/profit_model.py` | Deterministic unit economics, contribution margin and batch break-even calculator |
| `scripts/reverse_funnel.py` | Reverse funnel calculator for break-even orders, clicks and impressions |
| `scripts/portfolio_break_even.py` | Minimum success-rate and expected-profit calculator for testing portfolios |
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
| `references/post-launch-playbook.md` | Post-launch scale, steady-state, decline and exit decisions; category-adaptive timelines, phased ad structure, portfolio interaction, passive/active decline distinction, cash-flow veto |
| `references/competitor-monitoring.md` | Ongoing competitor monitoring with category-elastic thresholds, capability attribution, SOV tracking, channel/distributor monitoring, opportunity-window classification and monthly report structure |
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

Professional-grade short-form video teardown at creator/CMO level. Runtime model `VLB-2026.07` adds evidence IDs, six scenario routes, normalized scoring and explicit ROI/profit definitions to the 12-dimension framework. In cross-border e-commerce mode, it adds 4 business dimensions (13–16): product-video fit & commercial viability, e-commerce conversion funnel & unit economics, cross-border localization & compliance, and scalable production & creator matrix design.

**Path:** `video-link-breakdown/`

**Supported platforms:** TikTok, YouTube Shorts, Instagram Reels, X/Twitter videos, Bilibili, Douyin, TikTok Shop, Shopee Video, Pinterest Video.

**Special modes:** cross-border e-commerce (adds 4 business dimensions + localization + creator matrix), account diagnosis, competitor benchmarking, audio-first/podcast teardown.

**Analysis output:**
- Basic metadata & engagement signals
- One-sentence strategic diagnosis + three-part thesis
- Second-level rhythm map with information density, emotion value, attention risk, and functional role per 3–5s slice
- Emotion arc with peak/valley annotations and retention-rate predictions
- Beat-by-beat script structure with narrative function and psychology mechanism
- Professional editing grammar: match cuts, motion continuity, J-cut/L-cut, sound–image counterpoint, visual focus & heat-zone prediction
- Platform-fit hypothesis matrix (Douyin/TikTok vs YouTube Shorts vs Bilibili vs Reels vs TikTok Shop vs Shopee Video vs Pinterest), calibrated with current market/category/account data rather than fixed algorithm claims
- Audience segmentation: core vs reach demographics, consumption scenario, and decision-type match (impulse vs rational)
- Competitive positioning: category coordinate, trendsetter/follower/copycat label, differentiation vs Top 10
- Monetization funnel audit: exposure → play → completion → interaction → conversion → retention, with CTA and landing-page match assessment; e-commerce bridge layer (product screen time, selling-point clarity, price anchoring, CTA-to-product path, promise-vs-experience consistency) in cross-border mode
- Weighted content scoring: type-specific normalized weights across 7 standard dimensions, plus product-video fit as the eighth dimension in e-commerce mode; each score includes a one-line justification
- Replication template + execution-cost estimate (equipment, scene, talent, post-production, timeline, budget) + replication-risk warning
- A/B hypotheses in "assumption → expected impact → trade-off → validation method" format, plus rewritten script or shot list when useful
- (Cross-border mode) Product-video fit scoring, commercial viability quick-screen, unit economics, separately defined ROI and net-margin scenarios, 5-market localization matrix, compliance quick-screen, creator matrix design, and material lifecycle management
- Optional CIDM integration: structured adjustment proposal with original/new score, evidence IDs and gate-reassessment flag; historical reports are never silently overwritten

**Files:**

| Path | Purpose |
|---|---|
| `SKILL.md` | Full 12-dimension analysis framework + 4 cross-border business dimensions (13–16), special-mode routing, workflow, link handling, output templates, quality gate |
| `agents/openai.yaml` | Codex Skill UI metadata |
| `scripts/prepare_video_link.py` | Video download via yt-dlp, metadata extraction, frame extraction, contact sheet generation |
| `scripts/test_prepare_video_link.py` | Regression tests for URL/sample validation, dependency safety and preparation invariants |

---

# Miles-Chen Codex 技能库

跨境电商投资研究与视频内容拆解技能库；品类投决中内建竞品/VOC 情报与上市验证闭环。

仓库公约（目录结构、源文件规则、临时目录、交付命名、本地同步、Git 工作流）详见 [RULES.md](RULES.md)。

仓库级校验由 `scripts/validate_repo.py` 执行，在 Codex 通用 Skill 校验之外强制检查运行时版本、本地链接、frontmatter 兼容性和视频评分权重归一化。

---

## 技能

### 品类投资决策

面向跨境的、证据驱动的品类进入决策。内建竞品/VOC 取证、投资评分、组合决策、国家本地化、单位经济、分阶段测款与证据回写。

**路径：** `category-investment-decision/`

**支持场景（25+）：** 品类进入、竞品/VOC 情报、链接反查、多候选组合、国家本地化（美国/欧盟/英国/日本/东南亚）、趋势/季节/机会筛选、平台专项分析（Amazon、TikTok Shop、Temu、Shopify/DTC、Walmart、Etsy、eBay、Shopee/Lazada）、竞品监控（含品类弹性阈值、竞品能力归因、SOV 追踪、渠道/经销商监控、机会窗口分类）、关键词策略、店铺补品、老品扩展、老品诊断、上市后放量（含品类自适应时间框架、广告结构阶段演进、组合联动检查、被动/主动衰退区分、现金流压力否决）、退出复盘、利润核算、测款设计与复盘。

**核心模型（CIDM-2026.08）：** 七维加权评分（100 分制）、五道前置门槛（红线优先）、四档决策阈值、维度置信度、复购/LTV、达人/联盟适配度和增长可持续性校准。交付物包括完整报告、快速初筛卡、链接反查卡、组合对比表、国家进入矩阵、竞品监控月报、上市后决策卡、退出复盘和分阶段验证计划。

**评分前五道前置门槛：** CIDM 不从分数开始，而是先判断机会是否通过五个商业门槛。红线优先于总分。

| 门槛 | 决策问题 | 专业判断点 | 公式 / 模型依据 |
|---|---|---|---|
| 市场够大吗 | 需求是否能支撑目标销售规模和经营节奏 | 关键词簇、趋势稳定性、购买动机、复购/耗材潜力、社媒与平台需求信号 | 需求证据三角验证；LTV/购买频次修正；代理信号置信度分级 |
| 进得去吗 | 新卖家或非头部卖家能否获得流量并突破竞争 | 评论壁垒、品牌集中度、广告压力、近 12 个月新品突破、长尾切入口 | 竞争分层；评论/时间壁垒；置信度调整后的进入性评分 |
| 能赚钱吗 | 完整成本后是否仍有净利和安全垫 | 产品、包装、关税、头程、履约、佣金、广告、促销、退货、仓储、质检、支付等全成本 | `净利 = 售价 - 全链路成本`；`盈亏平衡广告率 = 扣除广告前贡献利润 ÷ 售价`；三场景与敏感性分析 |
| 能卖吗 | 合规、IP、平台、安全和退货风险是否可控 | 法规路径、认证、禁限售、宣称/标签、专利/商标/版权、退货风险 | 红线优先风险门槛；人工复核触发规则；风险可控性置信度 |
| 凭什么是你 | 有什么具体切入楔子让用户选择你而不是竞品 | VOC 反复痛点、竞品承诺-体验落差、产品/包装/服务/内容楔子、执行可行性 | 切入楔子验证链；最弱假设测试；内容适配与增长可持续性校准 |

**评分与决策数学：** 每个维度先打 0-10 原始分，再用 `加权分 = 原始分 ÷ 10 × 权重分值` 转成 100 分制。七维权重为：市场需求 20、竞争可进入性 20、利润空间 20、内容传播 10、供应链可控性 10、风险可控性 10、机会窗口 10。默认四档决策为：80-100 建议进入，65-79.9 谨慎进入 / 小规模测试，50-64.9 仅观察或内容测款，低于 50 不建议进入。低置信度、红线或前置门槛失败时，即使总分较高也必须降级。

**确定性计算工具：** 财务和验证计算使用可审计脚本，不依赖隐藏表格逻辑：`profit_model.py` 计算单位经济与批次盈亏平衡，`reverse_funnel.py` 反推订单/点击/曝光要求，`portfolio_break_even.py` 计算测品组合最低成功率，`portfolio_selector.py` 做预算/SKU 约束下的组合选择，`evaluate_experiment.py` 评估事先注册的测款门槛。

**文件清单：**

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 完整决策框架、场景路由、评分模型、执行自检 |
| `agents/openai.yaml` | Codex Skill 界面元数据 |
| `scripts/workspace_manager.py` | 安全创建与清理任务临时目录 |
| `scripts/profit_model.py` | 确定性单位经济、贡献利润与批次盈亏平衡计算 |
| `scripts/reverse_funnel.py` | 反向漏斗计算，反推盈亏平衡订单、点击与曝光 |
| `scripts/portfolio_break_even.py` | 测品组合最低成功率与预期利润计算 |
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
| `references/post-launch-playbook.md` | 上市后放量、稳态、衰退与退出决策；品类自适应时间框架、广告结构阶段演进、组合联动检查、被动/主动衰退区分、现金流压力否决 |
| `references/competitor-monitoring.md` | 竞品持续监控，含品类弹性阈值、竞品能力归因、SOV 追踪、渠道/经销商监控、机会窗口分类与月报结构 |
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

面向创作者/CMO 级别的专业短视频深度拆解。运行时模型 `VLB-2026.07` 在十二维框架上新增证据编号、六类场景路由、标准化评分和明确的 ROI/利润口径。跨境电商模式下追加四个商业维度（第十三至十六维度）：产品-视频匹配度与商业可行性、电商转化漏斗与单位经济、跨境本地化与合规、规模化生产与达人矩阵适配。

**路径：** `video-link-breakdown/`

**支持平台：** TikTok、YouTube Shorts、Instagram Reels、X/Twitter 视频、Bilibili、抖音、TikTok Shop、Shopee Video、Pinterest Video。

**特殊模式：** 跨境电商（追加 4 个商业维度 + 本地化 + 达人矩阵）、账号诊断、竞品对标、纯音频/播客型拆解。

**分析输出：**
- 基础元数据与互动信号
- 一句话战略诊断 + 三段论展开
- 秒级节奏图谱：按 3–5 秒切片，标注信息密度、情绪值、注意力风险、功能定位
- 情绪曲线：标注峰值/低谷，预测各节点留存率
- 节拍级脚本结构：每拍的叙事功能与心理学机制
- 专业剪辑语法：匹配剪辑、运动连贯性、J-cut/L-cut、声画对位、视觉焦点与热区预测
- 平台适配假设矩阵：抖音/TikTok vs YouTube Shorts vs B站 vs Reels vs TikTok Shop vs Shopee Video vs Pinterest；优先用当前国家、品类和账号数据校准，不把固定算法权重当事实
- 受众分层：核心/扩散人群、消费场景、决策类型匹配（冲动型 vs 理性型）
- 竞争格局：品类坐标、定义者/跟风者/搬运者定位、与 Top 10 的共性与差异
- 变现漏斗审计：曝光→播放→完播→互动→转化→留存，CTA 与承接页匹配度评估；跨境电商模式增加电商衔接层（产品出现时间占比、卖点传达清晰度、价格锚定、CTA 跳转路径、视频承诺与实际体验一致性）
- 加权内容评分：六类内容使用归一化权重；标准模式七维，电商模式增加产品-视频匹配形成八维，每项评分附一句话依据
- 可复刻模板 + 执行成本评估（设备、场景、演员、后期、周期、预算）+ 复刻风险提示
- A/B 假设：采用"假设→预期影响→Trade-off→验证方式"四段式，必要时附改写脚本或分镜
- （跨境电商模式）产品-视频匹配度评分、商业可行性快筛、单位经济、分别定义的 ROI 与净利润率三场景、五市场本地化矩阵、合规快筛、达人矩阵设计、素材生命周期管理
- 可选 CIDM 对接：输出包含原分、建议分、证据编号和门槛重判标记的结构化调整建议，不静默覆盖历史报告

**文件清单：**

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 完整十二维度分析框架 + 跨境电商模式四维度（十三至十六）、特殊模式路由、工作流、链接处理、输出模板、交付自检 |
| `agents/openai.yaml` | Codex Skill 界面元数据 |
| `scripts/prepare_video_link.py` | 视频下载（yt-dlp）、元数据提取、关键帧提取、联系表生成 |
| `scripts/test_prepare_video_link.py` | URL/采样参数、依赖安全和准备流程不变量回归测试 |
