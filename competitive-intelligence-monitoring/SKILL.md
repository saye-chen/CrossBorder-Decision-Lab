---
name: competitive-intelligence-monitoring
description: 默认用中文执行跨境电商竞品情报与持续监控。用于 Amazon、TikTok Shop、Shopee、Lazada、Shopify/DTC、Walmart、eBay、Etsy、Temu、Shein 等平台的竞品发现与分层、竞品建档、店铺/商品/素材画像、价格促销、排名、评论、评分、变体、库存、上新、Listing、广告、内容和渠道快照对比，基线与动态阈值、异动检测、原因归因、威胁/机会预警、竞争力评分、周报/月报和专项竞争研究；当用户要求监控竞品、追踪竞争变化、解释竞品增长/降价/上新/内容换版、建立竞品池或把外部信号路由给选品、视频、Listing、定价、广告、库存、供应链和经营诊断时使用。
---

# 竞品情报与持续监控

运行时版本：`CIM-2026.07`。

## 目标与边界

默认用中文把外部竞争信号转换为可追溯的变化、可验证的归因和可路由的经营动作。不将销量、广告投入或市场份额估算写成事实。

- 负责：竞品识别、分层、画像、快照、异动、归因、预警、情报报告和下游路由。
- 不负责：品类准入结论、全量 VOC 原子编码、视频逐镜头拆解、Listing 成稿或自动执行调价/广告/库存动作。
- 不独立决定品类是否值得进入，不完成详细 VOC 原子编码，不完成视频逐镜头拆解；将已确认的专业问题路由给对应 Skill。
- 法务、侵权、恶意竞争指控、大幅调价和大额预算变动必须人工复核。

## 与消费者洞察与客户增长 Skill 的边界

本 Skill 负责竞品差评、服务、价格、内容和渠道的外部变化；`consumer-insights-customer-growth` 负责这些变化是否在我方客户中出现、影响哪些人群/生命周期及其经济结果。只在用户提供 CIG 卡片或明确要求联动时交换已去识别的汇总结论；不将公开竞品受众与我方客户做个人级匹配，不用外部信号直接触达我方客户。

## 工作区与时效

对价格、排名、库存、广告、平台规则和市场状态默认进行当日外部核验。保留平台、市场、URL、采集时间和展示条件。复杂或可恢复任务使用受管临时目录 `${TMPDIR:-/tmp}/competitive-intelligence-monitoring/<YYYYMMDD-HHMMSS>-<task-slug>/`，写入 `.task-owner.json`；任务后只删除本任务目录并验证。

## 任务路由

| 模式 | 触发 | 必读 | 默认交付 |
|---|---|---|---|
| 竞品建档 | 首次提供品类、店铺、ASIN 或链接 | [competitor-discovery-and-tiering.md](references/competitor-discovery-and-tiering.md)、[competitor-profile-schema.md](references/competitor-profile-schema.md) | 竞品池、T1-T4、画像、基线计划 |
| 单次情报 | 询问竞品最近发生了什么 | [anomaly-detection-and-attribution.md](references/anomaly-detection-and-attribution.md)、[evidence-quality-control.md](references/evidence-quality-control.md) | 变化、归因、影响、动作 |
| 持续监控 | 要求周期跟踪或对比快照 | [monitoring-signals-and-frequency.md](references/monitoring-signals-and-frequency.md)、[baseline-and-dynamic-thresholds.md](references/baseline-and-dynamic-thresholds.md) | 绿/黄/红/机会告警和下周重点 |
| 专项研究 | 价格战、新品、内容换版、渠道扩张等 | [competitive-scoring-and-positioning.md](references/competitive-scoring-and-positioning.md)、[anomaly-detection-and-attribution.md](references/anomaly-detection-and-attribution.md) | 专项判断与验证方案 |

所有模式均读 [evidence-quality-control.md](references/evidence-quality-control.md)。需要告警或报告时读 [alert-and-report-protocols.md](references/alert-and-report-protocols.md)；需要与其他 skill 交换结果时读 [skill-integration-protocol.md](references/skill-integration-protocol.md)。

## 核心流程

1. **定义决策问题**：锁定平台、国家、品类/自有 SKU、时间窗口和将被改变的决策。
2. **建立对象和基线**：分层竞品，分开主体、商品、快照、事件和机会；单次快照不得声称趋势。
3. **采集与标注**：区分 `O` 直接观测、`M` 实测/平台数据、`U` 用户输入、`B` 外部基准、`E` 估算、`I` 推断。
4. **检测变化**：先用绝对阈值、相对变化或滚动 Z-score 筛选，再检查数据质量、季节性和平台展示差异。
5. **六步归因**：变化确认 → 证据复核 → 影响评估 → 2-3 个原因假设 → 独立信号交叉验证 → 动作输出。
6. **评估影响**：结合变化幅度、竞品层级、市场覆盖、持续时间和我方暴露。
7. **输出与路由**：输出情报事件卡、告警等级、响应窗口、最小动作、验证与停止条件；仅在用户明确要求时将结论回写其他报告。
8. **学习闭环**：后续快照验证或推翻归因，保留原结论和修订记录。

## 计算脚本

- `python3 scripts/compare_snapshots.py --previous old.json --current new.json --output changes.json`：对比两期 JSON 快照。
- `python3 scripts/detect_changes.py --input history.json --output alerts.json`：按阈值与滚动基线检测异动。
- `python3 scripts/build_monitoring_report.py --alerts alerts.json --output report.md`：生成可复核的 Markdown 简报。

脚本只计算和整理用户提供的数据，不自动采集、不发明归因。

## 必要输出

1. 决策问题、范围、截止时间和数据缺口。
2. 竞品层级与监控对象；如非建档任务，可仅列相关对象。
3. 变化前后、持续时间、证据等级和是否已确认。
4. 原因假设、支持/反驳信号、置信度；单一信号只能是待验证假设。
5. 对我方的威胁或机会、适用 SKU/市场、时间窗口。
6. 建议动作、风险、最小验证、成功信号和停止条件。
7. 情报事件卡与推荐路由；无需路由时明确写“继续监控”。

## 质量门槛

- 时间趋势至少需要 3 个可比快照；显著异动原则上需要连续 2 期确认。
- 高置信归因至少需要 3 个一致信号，中置信至少 2 个，否则为低置信待验证。
- 不同模型版本的 CPI 不直接比较；必须使用同一权重和归一化基准重算。
- 建议不得超过证据支持的范围；无法核验时降级结论并给出补证动作。
