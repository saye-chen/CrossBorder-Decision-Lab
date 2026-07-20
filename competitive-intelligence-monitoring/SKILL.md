---
name: competitive-intelligence-monitoring
description: 默认用中文执行跨境电商竞品发现、建档、投资级竞争尽调与持续监控。支持从自然语言、链接、ASIN/SKU、店铺、图片或截图识别商品，在 Amazon、TikTok Shop、Shopee、Lazada、Shopify/DTC、Walmart、eBay、Etsy、Temu、Shein 等平台和国家发现、去重和分层竞品，监控价格促销、排名评论、变体库存、上新 Listing、广告竞争、达人竞争、渠道扩张、供应履约和品牌口碑信号，确认变化、归因窗口并输出事件卡、周报/月报和专项研究；当用户要求找竞品、分析竞争格局、建立竞品池、监控增长/降价/上新/内容换版，或把外部竞争信号路由给选品、内容、Listing、定价、广告、达人、库存、供应链、品牌和客户增长时使用。不独立给最终投资、调价、投放或补货动作，不把公开代理信号写成后台事实。
---

# 竞品情报与持续监控

运行时版本：`CIM-2026.10`。

## 与广告分析 Skill 的边界

发现竞品广告素材、版位、促销、落地页、投放代理信号或可见广告变化时，本 Skill 只确认外部对象、时间线、证据等级、变化范围和替代解释；需要判断我方账户结构、归因、广告内部预算/出价、边际利润或 Scale/Stop 时路由 `advertising-analysis-measurement-optimization`。向 D09 提交情报事件卡、证据指纹和禁止用途；D09 回传广告相关性、待验证机制和广告动作建议。本 Skill 不把可见广告数量推断为真实花费，D09 也不得把我方效果反写为竞品事实。任一方失败时保留已确认事实，未确认归因标记 `inconclusive`。

## 专业性与决策可用性硬约束

无论单 Skill、联合 Skill、快报、监控告警、正式报告、demo、压测、数据不足或极端场景，都只允许压缩展示，不允许降低竞争研究标准。每次交付至少保留：对象与范围、当前竞争判断、事实/估算/假设、反对证据与替代解释、商业影响、风险、动作、成功条件、停止条件、未覆盖范围及其决策影响。缺少时间序列、后台数据或独立信号时降低归因强度，不删除决定性模块，也不把单次快照、代理指标或未知写成趋势、销量或确定归因。

本 Skill 对外部竞争事实、变化确认和竞争归因拥有主权；不拥有品类投资、视频机制或客户增量主权。联合调用时只输出带版本、对象、证据/事件 ID、允许/禁止用途、置信度和验证状态的情报事件卡。任何影响投资分数、门槛或档位的内容必须路由 CIDM 接受并重算；联动失败时仍交付专业完整的本域判断和补证方案，不得用辅助 Skill 缺席作为降级研究的理由。

## 目标与边界

默认用中文把自有商品线索和外部竞争信号转换为可追溯的竞品池、可验证的竞争判断和可执行的经营或投资动作。能力贯穿准入前竞争尽调、进入验证、上市后监控和退出复盘；不将销量、广告投入或市场份额估算写成事实。

- 负责：自有商品识别、搜索词扩展、竞品发现、分层、画像、快照、异动、归因、竞争窗口、竞争投资姿态、预警、结果回收、专业报告和下游路由。
- 不负责：仅凭竞争数据独立完成最终品类准入、全量 VOC 原子编码、视频逐镜头拆解、Listing 成稿或自动执行调价/广告/库存动作。
- 不独立决定品类是否值得进入，不完成详细 VOC 原子编码，不完成视频逐镜头拆解；竞争结论作为完整投资决策或下游专业分析的输入。
- 可以输出竞争维度的 `Advance / Test / Watch / Stop`；最终投资 Go/No-Go 必须补齐需求、利润、合规、供应链和卖家能力，路由给 `category-investment-decision`。
- 法务、侵权、恶意竞争指控、大幅调价、大额预算和重仓进入必须人工复核。

## 一句话入口

接受商品链接、ASIN/SKU/商品 ID、店铺链接、商品图片/截图、自然语言描述或品类名称。先读取 [product-identification-and-query-expansion.md](references/product-identification-and-query-expansion.md)，建立自有商品识别卡，再发现竞品。

- 高置信识别直接执行。
- 中置信识别带显式假设执行，不因非关键字段缺失反复追问。
- 只有歧义会显著改变品类、平台、国家或竞品池时，才追问一个最关键问题。
- 店铺包含多个商品时列出最可能候选；不得擅自认定目标商品。
- 未指定平台或国家且上下文无法安全继承时，只补问会改变结果的字段。

## 与消费者洞察与客户增长 Skill 的边界

本 Skill 负责竞品差评、服务、价格、内容和渠道的外部变化；`consumer-insights-customer-growth` 负责这些变化是否也出现在我方客户中、影响哪些人群/生命周期及其经济结果。只在用户提供 CIG 卡片或明确要求联动时交换已去识别的汇总结论；不将公开竞品受众与我方客户做个人级匹配，不用外部信号直接触达我方客户。

## 工作区与时效

对价格、排名、库存、广告、平台规则和市场状态默认进行当日外部核验。保留平台、市场、URL、采集时间和展示条件。复杂或可恢复任务使用受管临时目录 `${TMPDIR:-/tmp}/competitive-intelligence-monitoring/<YYYYMMDD-HHMMSS>-<task-slug>/`，写入 `.task-owner.json`；任务后只删除本任务目录并验证。

## 任务路由

涉及广告、达人、价格促销、渠道、供应物流或品牌口碑竞争时，必须读取 [extended-competitive-signal-domains.md](references/extended-competitive-signal-domains.md)，按代理信号边界确认变化并向对应主权域提交事件卡，不把外部可见信号写成后台事实或直接经营动作。

| 模式 | 触发 | 必读 | 默认交付 |
|---|---|---|---|
| 快速竞品分析 | 一句话、图片、描述、链接或商品 ID | [product-identification-and-query-expansion.md](references/product-identification-and-query-expansion.md)、[competitor-discovery-and-tiering.md](references/competitor-discovery-and-tiering.md) | 识别卡、T1/T2 竞品、差距、机会、下一步 |
| 竞品建档 | 要求完整竞品池、画像或基线 | [competitor-discovery-and-tiering.md](references/competitor-discovery-and-tiering.md)、[competitor-profile-schema.md](references/competitor-profile-schema.md) | 竞品池、T1-T4、画像、基线计划 |
| 竞争投资尽调 | 要求专业、投资级、投委会或进入判断 | [competitive-scoring-and-positioning.md](references/competitive-scoring-and-positioning.md)、[competitive-advantage-and-opportunity-windows.md](references/competitive-advantage-and-opportunity-windows.md)、[professional-report-delivery.md](references/professional-report-delivery.md) | 竞争姿态、优势来源、窗口、门槛、风险、验证、投决路由 |
| 单次情报 | 询问竞品最近发生了什么 | [anomaly-detection-and-attribution.md](references/anomaly-detection-and-attribution.md) | 变化、归因、影响、动作 |
| 持续监控 | 要求周期跟踪或对比快照 | [monitoring-signals-and-frequency.md](references/monitoring-signals-and-frequency.md)、[baseline-and-dynamic-thresholds.md](references/baseline-and-dynamic-thresholds.md)、[platform-category-lifecycle-calibration.md](references/platform-category-lifecycle-calibration.md)、[attribution-learning-and-outcome-loop.md](references/attribution-learning-and-outcome-loop.md) | 校准基线、绿/黄/红/机会告警、归因验证和下周重点 |
| 专项研究 | 价格战、新品、内容换版、渠道扩张等 | [competitive-scoring-and-positioning.md](references/competitive-scoring-and-positioning.md)、[anomaly-detection-and-attribution.md](references/anomaly-detection-and-attribution.md) | 专项判断与验证方案 |

所有模式均读 [professional-depth-governance.md](references/professional-depth-governance.md) 和 [evidence-quality-control.md](references/evidence-quality-control.md)。前者保证快速分析只压缩展示，不降低竞争研究、归因和报告专业深度。需要告警或正式报告时读 [alert-and-report-protocols.md](references/alert-and-report-protocols.md)；需要生成可下载文件时必须再读 [professional-report-delivery.md](references/professional-report-delivery.md)；需要与其他 Skill 交换结果时读 [skill-integration-protocol.md](references/skill-integration-protocol.md)。
涉及结构化数据、周期任务、平台采集或自动化流水线时必须读 [data-contract-and-automation.md](references/data-contract-and-automation.md)。

正式情报报告、竞争归因或跨域事件卡必须运行 `scripts/validate_decision_contract.py`，校验对象身份、证据血缘、代理信号状态、主权和允许/禁止用途；失败时不得把事件升级为已确认竞争事实。

## 核心流程

1. **翻译决策问题**：锁定自有商品、平台、国家、时间窗口和将被改变的经营或投资决策。
2. **识别商品**：生成自有商品识别卡，记录输入、属性、场景、价格带、置信度、假设和排除项。
3. **扩展检索**：组合核心品类词、功能需求词、场景词、目标人群词和替代方案词；记录发现渠道与查询词。
4. **建立对象和基线**：召回、去重、排除并分层竞品；记录搜索覆盖、停止条件和未覆盖渠道；分开主体、商品、快照、事件和机会。单次快照不得声称趋势。
5. **采集与标注**：区分 `O` 直接观测、`M` 实测/平台数据、`U` 用户输入、`B` 外部基准、`E` 估算、`I` 推断。
6. **分析竞争**：比较定位、价格、产品、内容、口碑和渠道；向下归因优势来源与可复制性，输出暴露、进入楔子、机会窗口、反例与最弱假设。
7. **检测与归因**：确认变化，复核证据，评估影响，提出 2-3 个原因假设，用独立信号交叉验证。
8. **决策与路由**：输出 `Advance / Test / Watch / Stop` 竞争姿态、反例、最弱假设、动作、风险、最小验证、成功/停止条件和复查日期；最终投资判断按边界路由。
9. **学习闭环**：后续快照验证或推翻归因，回收我方动作和结果，检查替代解释，计算监控质量指标，保留原结论、模型版本和修订记录。

## 默认输出深度

- 用户只说“找竞品/看看竞品”时，交付快速竞品分析，不机械生成长报告。
- 用户要求深入、专业、投资级、投委会或可下载报告时，交付完整 Competitive Investment Intelligence Report；文件交付默认生成 Markdown 到 `$HOME/Downloads`。
- 用户要求持续关注时，把首轮结果转为监控基线；未经明确要求不自动创建周期任务。
- 用户要求最终是否值得进入或投资时，先完成竞争尽调，再联合 `category-investment-decision` 输出最终投决；不得用 CPI 代替完整投资模型。

## 计算脚本

- `python3 scripts/compare_snapshots.py --previous old.json --current new.json --output changes.json`：对比两期 JSON 快照。
- `python3 scripts/detect_changes.py --input history.json --output alerts.json`：按阈值与滚动基线检测异动。
- `python3 scripts/build_monitoring_report.py --alerts alerts.json --output report.md`：生成可复核的 Markdown 简报。
- `python3 scripts/compute_competitive_metrics.py --input metrics.json --output result.json`：计算可追溯的 CRI、CPI、RCG 和代理 HHI。
- `python3 scripts/evaluate_learning_loop.py --input reviewed.json --output quality.json`：汇总异动、归因和动作验证质量。

脚本只计算和整理用户提供或已取证的数据，不自动采集、不补行业阈值、不发明归因。平台采集必须通过已授权连接或用户提供数据执行，并遵守标准对象、字段缺失、展示条件和失败状态契约；未经明确要求不创建周期任务或外发通知。

## 必要输出

1. 决策问题、对象、平台、国家、截止时间、输入来源和数据缺口。
2. 自有商品识别结果、置信度、关键假设及可能改变竞品池的歧义。
3. 搜索范围、发现渠道、候选排除、竞品层级和比较基线。
4. 关键事实、估算、推断、反例、证据等级和是否已确认。
5. 对我方的威胁、机会、进入楔子、适用 SKU/市场和时间窗口。
6. 竞争投资姿态、理由、风险、最小验证、成功信号和停止条件。
7. 情报事件卡或专业报告、推荐路由；无需路由时明确写“继续监控”。
8. 正式报告的 Evidence / Assumption Ledger，以及搜索覆盖、排除对象、未覆盖范围和证据截止时间。

## 质量门槛

- 商品识别必须保留输入来源、置信度和假设；图片可见特征不得冒充材质、性能或认证事实。
- 每个纳入竞品保留发现渠道、查询词、纳入理由；每个排除对象保留关键排除理由。
- 时间趋势至少需要 3 个可比快照；显著异动原则上需要连续 2 期确认。
- 高置信归因至少需要 3 个一致信号，中置信至少 2 个，否则为低置信待验证。
- 销量、利润款、广告投入、库存、市场份额和恶意竞争等不可直接观测内容只能写成代理估算或待复核假设；不得由单一公开信号升级为事实。
- 不同模型版本的 CPI 不直接比较；必须使用同一权重和归一化基准重算。
- 初始阈值必须按平台、品类、生命周期和季节事件校准；样本不足时明确“校准未成熟”，不得伪造系数。
- 优势来源和机会窗口必须包含支持/反驳信号、可复制性、我方准备度、关闭信号和停止条件。
- 到期归因必须标记为验证、推翻或无法判断；结果改善不得自动归因于我方动作。
- 投资级报告必须包含竞争决策页、Evidence/Assumption Ledger、反例、最弱假设、验证预算或资源边界及停止条件。
- 建议不得超过证据支持的范围；无法核验时降级结论并给出补证动作。

## D08 页面执行路由

本 Skill 保留竞品发现、外部页面事实、变化确认与归因主权。用户要求把竞品快照或变化转化为我方标题、主图、详情、落地页或店铺转化的具体修改与实验时，向 `platform-store-listing-conversion` 交接对象、快照、时间、证据ID、指纹、可见/不可见边界和禁止用途；不得直接复制竞品表达或把公开代理信号写成我方因果结论。
