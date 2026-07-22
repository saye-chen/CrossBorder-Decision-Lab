---
name: video-link-breakdown
description: 默认用中文执行跨境电商内容创意与传播决策。用于 TikTok、YouTube Shorts、Instagram Reels、X/Twitter、Bilibili、抖音、TikTok Shop、Shopee Video、Pinterest 等平台的视频、直播切片、静态图、轮播、UGC、测评、教程和品牌片拆解与对标，以及账号诊断、脚本分镜、创意母题、产品证明、生产 Brief、创意实验矩阵、探索/主力/防疲劳/再营销素材组合、疲劳刷新、自然内容转广告、达人内容转品牌资产和跨平台/国家迁移；当用户要求分析内容机制、钩子节奏、传播策略、内容质量、生产方案、复刻价值、素材测试或出海适配时使用。不决定达人商务、广告预算、品牌总定位或品类投资，不用内容评分证明销量、竞争优势或客户级增量。
---

# 视频链接拆解

运行时版本：`VLB-2026.10`。

## 专业性与决策可用性硬约束

无论单 Skill、联合 Skill、快速拆解、正式报告、demo、压测、只有关键帧、无后台数据、视频不可访问或极端场景，都只允许压缩展示，不允许降低内容与商业研究标准。每次交付至少保留：对象与素材边界、可观察事实、机制假设、反对证据/替代解释、产品一致性、商业约束、风险、动作、成功条件、停止条件、缺失素材及其决策影响。证据不足时降低结论强度，不删除决定性模块，也不把高播放写成高留存、把内容评分写成转化或利润、把单条成功素材写成可复制事实。

本 Skill 对视频观察、内容机制和迁移性拥有主权；不拥有竞争归因、客户增量或品类投资主权。联合调用时只输出带版本、对象、证据 ID、允许/禁止用途、迁移等级、置信度和验证状态的结构化建议。任何影响投资评分、门槛或档位的内容只能保持 `proposed`，由 CIDM 接受并用原模型重算；相近品必须验证，跨品类或 A/B/C 三者互不相同不得立即调分。联动失败时仍须交付专业完整的本域判断与补证实验。

## 与竞品情报 Skill 的边界

当 `competitive-intelligence-monitoring` 已确认竞品视频/广告素材换版并伴随排名、口碑或投放代理信号时，本 Skill 负责拆解内容机制、产品一致性、迁移性和复制测试；CIM 负责变化确认、时间序列和竞争影响。只在用户提供 CIM 事件卡或明确要求联动时消费；回收内容观测、机制推断、迁移等级、验证和停止条件，不将内容高分直接写成竞品销量或竞争优势事实。

## 与消费者洞察与客户增长 Skill 的边界

`consumer-insights-customer-growth` 可提供已去识别的高价值人群、生命周期、任务/阻力/语言和内容假设；本 Skill 输出视频机制、产品迁移性、生产方案和可测试变体。只在用户明确要求联动时交换；VLB 不证明客户增量，内容点击/评分不等于增量留存或利润，必须由 CIG 的可信实验/准实验评估。

## 与广告分析 Skill 的边界

当用户要把自然内容、达人素材、脚本变体或素材组合用于付费流量，且问题涉及广告交付、学习、归因、广告内部预算/出价、边际利润或放量停投时，路由 `advertising-analysis-measurement-optimization`。本 Skill 向 AAMO 提交素材对象、观察证据、机制假设、产品迁移等级、授权/合规状态、生产成本和测试变体；AAMO 回传付费交付结果与广告动作。本 Skill 仍拥有内容机制判断，AAMO 仍拥有付费预算与放量；付费胜出不自动证明机制，内容高分不自动授权预算。AAMO 不可用时只交付内容测试设计，广告经济与 Scale/Stop 标记 `inconclusive`。

默认用中文把视频转化为可执行的内容或商业决策。先还原事实，再解释机制，最后给出复刻、优化或 Go/Iterate/Stop 建议。不要用内容评分代替真实留存、转化或利润数据。

## 执行工作流

用户目标涉及静态图、轮播、UGC、直播切片、测评、教程、品牌片、创意策略、生产 Brief、素材组合、创意实验、疲劳刷新或跨格式/平台/国家迁移时，必须读取 [content-creative-and-propagation.md](references/content-creative-and-propagation.md)。此时按“内容创意与传播”能力执行，不要求输入必须是视频链接；仍保留内容机制主权，不越权决定达人商务、广告预算、品牌总定位或品类投资。正式决策报告、跨域回写和创意状态迁移必须运行 `scripts/validate_decision_contract.py`；失败时只交付待补证结果。

所有模式先读取 [professional-depth-governance.md](references/professional-depth-governance.md)。它定义内容与商业研究的专业性不变量、升级条件、证据阻断、文件级追溯、跨 Skill 边界和结果回收；短交付只压缩呈现，不得把内容观察降格为浅层点评。

1. 明确用户目标、目标平台、国家、对象和交付深度。
2. 准备视频、元数据、字幕、关键帧和可见互动数据；标注素材来源信号（production_source / traffic_source / commerce_binding）。
3. 选择一个主场景，并按“资源路由”只读取必要参考文件。
4. 建立证据台账，区分观察、元数据、用户输入、外部基准和推断。
5. 先给决策结论，再给证据、推理、动作和验证方案。
6. 清理本任务创建的临时文件；失败时披露残留路径与原因。

## 视频准备

解析已安装的 Skill 目录，不要假设当前仓库已经安装到固定位置。找到本文件所在目录后运行：

```bash
TASK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/video-link-breakdown.XXXXXX")"
python3 "<skill-dir>/scripts/prepare_video_link.py" "<video-url>" --out "$TASK_DIR"
```

该目录仅属于当前任务；完成交付后只删除已记录的 `$TASK_DIR` 并验证路径不存在。清理失败时报告准确残留路径和原因，不得按通配符或临时根目录宽泛清理。

- 读取 `summary.json`；存在 `contact_sheet.jpg` 时先用图像查看工具检查。
- 默认让脚本在抽帧成功后删除下载的视频。仅在用户明确要求保存时使用 `--keep-video`。
- 不默认安装依赖。只有用户授权修改环境后才使用 `--install-missing`。
- 若返回 `needs_user_input`，只索取真正缺失且会影响结论的上传视频、字幕、截图或可访问镜像。
- 有讲话但无字幕或转写时，只分析可见画面、屏幕文字和剪辑结构；不得编造对白。
- 页面登录、地区、验证码或反爬限制导致访问失败时，使用用户授权的浏览器状态或用户提供的材料，不重复使用同一失败方法。

## 证据协议

为影响决策的事实和推断分配编号：

- `O`：直接观察到的画面、音频、字幕或屏幕文字；
- `M`：可见元数据、账号数据或平台后台数据；
- `U`：用户提供的产品、成本、人群或经营数据；
- `B`：带国家、平台、品类、来源和日期的外部基准；
- `I`：仍需验证的推断。

留存、受众、算法、竞争、转化和 ROI 结论必须回指证据编号。不得把 `I`、无上下文的 `B` 或关键帧观察写成真实表现。

没有后台数据时：

- 使用高/中/低风险、方向性变化或显式区间；
- 说明区间依据和推翻变量；
- 不输出看似精确的单点留存率、转化率或效果增幅；
- 不把固定时长、产品露出比例、达人预算比例和素材生命周期当成通用平台规则。

## 素材来源信号

拆解开始前，先对视频标注三项前置信号，决定后续创意有效性判断的归因置信度。读取 [signal-attribution.md](references/signal-attribution.md) 获取完整检测启发式和归因修正规则。

| 字段 | 取值 | 判断依据 |
|---|---|---|
| `production_source` | `human_shot` / `ai_generated` / `hybrid` / `unknown` | 画面一致性、AI 标注、元数据；无法判断时保持 `unknown` |
| `traffic_source` | `organic` / `paid` / `mixed` / `unknown` | Ad 标签、播放/粉丝比、传播曲线、评论区反馈 |
| `commerce_binding` | `shoppable` / `non_shoppable` | 商品卡片、购物袋图标、评论区购买链接 |

归因修正：`traffic_source = paid` 时创意有效性降级为"待验证"；`production_source = ai_generated` 且 `traffic_source = organic` 时需区分 AI 新奇感红利与创意结构贡献。拆解报告结论段必须显式声明归因前提。

## 主场景路由

一次选择一个主场景；横向模块可叠加。

| 用户目标 | 主场景 | 默认交付 | 必读资源 |
|---|---|---|---|
| 拆解一个视频、为什么有效 | 单视频拆解 | Content Teardown | `standard-teardown.md`、`scoring-model.md`，按需叠加 `video-type-typology.md`（确定视频类型）和 `category-video-expression.md`（确定品类表达） |
| 比较多个视频或竞品 | 竞争对标 | Comparison Memo | `standard-teardown.md`、`scoring-model.md`，按需叠加 `video-type-typology.md` 和 `category-video-expression.md` |
| 诊断账号 | 账号诊断 | Account Diagnosis | `standard-teardown.md`，按需叠加 `video-type-typology.md`（账号内容类型混合时） |
| 判断能否带货或用于某产品 | 商业决策 | Commerce Decision | `standard-teardown.md`、`commerce-decision.md`、`scoring-model.md`，按需叠加 `category-video-expression.md`（品类表达是否到位） |
| 改写脚本或分镜 | 脚本优化 | Script Test Card | `standard-teardown.md`，按需叠加 `category-video-expression.md`（品类节拍偏好） |
| 出海、本地化、合规 | 市场适配 | Localization Memo | `localization-and-compliance.md`，需要内容诊断时叠加 `standard-teardown.md` |
| 达人矩阵、批量素材、规模化 | 规模系统 | Scale System | `creator-scale-system.md`，需要商业测算时叠加 `commerce-decision.md` |
| 回写品类投决 | CIDM 对接 | Adjustment Proposal | `cidm-integration.md` 及相关场景资源 |

不要为了展示能力机械展开全部模块。只有用户明确要求完整尽调，或结论同时依赖内容、商业、本地化和规模化时，才组合所有模块。

## 入口与交付层级

### Decision Card

用于快速判断、简单拆解和局部问题。保留：结论、关键观察、主要失效点或可复用点、风险、下一步测试。

### Decision Memo

默认用于单视频拆解、对标、账号诊断、脚本优化和商业判断。根据主场景加载模块，不要求固定十二或十六个标题。

### Investment Diligence

仅在用户明确要求完整报告、商业尽调、多个市场/平台比较或规模化方案时使用。覆盖内容机制、商业门槛、本地化、合规、单位经济、规模系统和证据台账。

完整闭环指结论、证据、推理、风险、动作和验证齐全，不等于所有模块都必须出现。

## 跨域边界与双向数据交换

与 CIDM、CIM、CIG、LIFD、PLCO、AAMO 的统一输入输出、部分失败和冲突裁决读取 [skill-integration-protocol.md](references/skill-integration-protocol.md)。素材自动化读取 [data-contract-and-automation.md](references/data-contract-and-automation.md)，正式交付读取 [professional-report-delivery.md](references/output-protocols/professional-report-delivery.md)。结果卡必须带素材版本、证据、允许/禁止用途和状态。

## 核心分析顺序

无论使用哪种交付层级，按需完成以下链路：

1. **战略目标**：曝光、涨粉、信任、成交、复购或素材测试。
2. **观察还原**：时间轴、节拍、视听语言、产品露出、CTA 和承接路径。
3. **机制解释**：注意力、情绪、说服、平台适配和受众匹配；推断必须标记。
4. **质量判断**：按内容类型选择权重并引用证据评分。
5. **商业判断**：涉及带货时先过利润、合规、供应链和退货门槛，再讨论放量。
6. **可复制性**：区分结构可复用部分与依赖创作者、时机或流量环境的部分。
7. **行动实验**：给出假设、预期方向、代价、指标、样本和停止条件。

## 动态事实与外部取证

- 当前平台功能、政策、广告披露、合规要求、市场表现和算法相关说法必须联网核验。
- 优先使用平台官方说明、监管机构、可见页面和用户后台数据；行业文章只作补充。
- “Top 10”“红海/蓝海”“热门 BGM”“最佳时长”等判断必须有当前样本或外部证据；没有取证时改写为待验证假设。
- 平台矩阵和国家画像只能作为研究起点，不能替代目标国家、品类、价格带和账号阶段校准。

## 资源路由

- 读取 [references/standard-teardown.md](references/standard-teardown.md)：分析节奏、脚本、剪辑、受众、平台、竞争、变现和复刻结构时。
- 读取 [references/scoring-model.md](references/scoring-model.md)：需要内容质量评分、多视频横向比较或评分解释时。
- 读取 [references/commerce-decision.md](references/commerce-decision.md)：涉及带货、产品适配、利润、转化漏斗、CPA/ACOS、ROI 或 Go/Iterate/Stop 时。
- 需要正式内容评分时运行 `scripts/score_video.py`；需要判断贡献利润、盈亏平衡或商业停止线时运行 `scripts/unit_economics.py`。两者输出必须保留输入口径，不得用手算总分或收入指标替代利润。
- 读取 [references/localization-and-compliance.md](references/localization-and-compliance.md)：涉及出海市场、语言文化、本地化成本、产品或广告合规时。
- 读取 [references/creator-scale-system.md](references/creator-scale-system.md)：涉及达人矩阵、批量素材、预算分配、素材疲劳和规模化生产时。
- 读取 [references/cidm-integration.md](references/cidm-integration.md)：用户提供 CIDM 报告或明确要求把视频结论回写品类投决时。
- 读取 [references/category-video-expression.md](references/category-video-expression.md)：需要按品类选择视频表达方式、判断品类表达是否到位、或优化品类专属视频策略时。
- 读取 [references/video-type-typology.md](references/video-type-typology.md)：需要区分视频类型（货架/内容/广告/品牌/达人）、选择对应评价标准、或调整评分权重时。
- 读取 [references/signal-attribution.md](references/signal-attribution.md)：需要判断素材来源信号的归因修正、检测启发式或报告措辞模板时。
- 读取 [references/brief-seed-spec.md](references/brief-seed-spec.md)：需要输出 Production-Ready Brief Seed、检查三层约束传递或对接 D10 生产端时。
- 读取 [references/selection-handoff-spec.md](references/selection-handoff-spec.md)：用户提供 CIDM 选品移交包、进入战略锚定拆解模式或需要检查 Brief Seed 与选品卖点对齐时。

## 输出规则

- 先给一句话结论和推荐动作，再展开证据。
- 时间轴优先覆盖 Hook、关键转折、证明、Payoff 和 CTA；短视频通常按 3-5 秒切片，中视频按叙事节拍切片。
- 情绪曲线标注峰值、低谷和注意力风险，不把推测的峰值写成真实完播节点。
- A/B 建议使用“假设 → 预期方向或区间 → Trade-off → 验证方式 → 停止条件”。没有基线时不承诺具体提升幅度。
- 成本、达人报价和市场基准必须注明币种、地区、日期和来源；缺少数据时使用反推门槛或显式假设。
- 用户未要求文件时在对话中交付；只有用户明确要求保存、报告文件或指定格式时才生成本地文件。
- 用户要求保存但未指定目录时保存到 `$HOME/Downloads`；同名文件先询问，不覆盖用户文件。

## Production-Ready Brief Seed

每次拆解（Decision Memo 及以上）必须同时输出完整报告和 Brief Seed。Brief Seed 是报告的可执行摘要，面向生产端（D10 达人 Brief、AI 生成工具）直接消费。完整 schema、约束传递规则和 Golden 样例读取 [brief-seed-spec.md](references/brief-seed-spec.md)。

三层结构：

1. **Layer 1 — 产品证明点**（What to prove）：核心证明点 + 证据呈现形式 + 证明段时长占比。
2. **Layer 2 — 创意方案**（How to tell）：母题类型 + 叙事结构（hook → 展开节拍 → 转化节点）+ 节奏模板（时长/切镜/信息密度/能量曲线）。
3. **Layer 3 — 执行参数**（How to shoot/generate）：镜头语言、光线、演员/素材类型、音频、字幕策略、AI 生成备注。

约束传递：Layer 1 约束 Layer 2 的母题选择，Layer 2 约束 Layer 3 的执行参数。Brief Seed 的 Layer 1 必须与 CIDM 选品移交包（如存在）的 `selling_points_ranked` 对齐。

置信度联动：`vlb_confidence` 继承素材来源信号的归因修正结果。`vlb_confidence = low` 时 Brief Seed 标记 `usage: "hypothesis_only"`，D10 消费时必须设计 A/B 验证而非直接量产。

选品移交包消费：当用户提供 CIDM Selection Handoff Package 时，VLB 进入"战略锚定拆解模式"。读取 [selection-handoff-spec.md](references/selection-handoff-spec.md) 获取消费规则和触发条件。

任何结构化 Selection Handoff Package 交付前必须运行 `scripts/validate_selection_handoff.py <input.yaml|json>`；任何 Brief Seed 交付前必须运行 `scripts/validate_brief_seed.py <input.yaml|json>`。校验失败时只能交付 `blocked`或待补证结果，不得标记 `production_ready`。

## 能力边界

- 关键帧不能证明完整对白、真实节奏、音效、留存或成交。
- 可见互动不能单独证明内容质量或归因销售。
- 合规、税务和 IP 结论只作商业快筛；高风险事项指定律师、检测机构或目标市场专业人士复核。
- 不提供刷量、伪造互动、隐瞒广告关系、侵权搬运、误导宣称或规避平台审核的建议。
- 复刻结构、节奏和测试思路时避免复制受版权保护的完整脚本、画面或独特表达。

## 交付前自检

1. 是否记录版本、证据截止时间、目标平台/国家和主场景。
2. 是否区分 `O/M/U/B/I`，且关键结论能回指编号。
3. 是否只加载并输出与用户目标有关的模块。
4. 是否把留存、算法、受众、竞争和 ROI 推断标为推断或基准。
5. 是否避免无校准的精确阈值、固定平台规律和效果承诺。
6. 是否给出明确结论、风险、动作、验证指标和停止条件。
7. 商业模式下是否先完成利润、合规、供应链和退货门槛。
8. 单位经济是否区分用户输入、外部基准和假设，并分开报告 ROI 与净利润率。
9. 本地化是否具体到语言、演员、场景、音乐、卖点、价格和合规动作。
10. 本任务创建的下载视频、关键帧、截图和临时目录是否已清理。
11. 是否标注素材来源信号（production_source / traffic_source / commerce_binding），且结论段包含归因前提声明。
12. Decision Memo 及以上是否同时输出 Production-Ready Brief Seed，且三层约束传递无违反。
13. 存在 CIDM 选品移交包时，Brief Seed Layer 1 是否与 selling_points_ranked 对齐（或标注 handoff_aligned: false 及原因）。

## PLCO 页面执行路由

本 Skill 保留内容机制、脚本、镜头、素材组合、生产和传播判断主权。用户要求决定主图、图组、视频封面或详情素材在页面中的槽位、顺序、承接任务和转化实验时，路由 `platform-store-listing-conversion`；PLCO可产出页面级生产Brief，具体创意机制和素材生产继续由本 Skill 决定。
