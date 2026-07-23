---
name: advertising-analysis-measurement-optimization
description: 默认用中文执行专家级跨境广告分析、测量与优化。覆盖 TikTok Shop、Amazon、Shopee、SHEIN、Temu、Mercado Libre、Google Search、Google Shopping、Google Performance Max、Meta Ads、TikTok Ads 站外/Shopify/DTC，以及未知平台通用路由；用于广告可行性、追踪准备、账户结构、搜索/商品/内容/自动化广告、冷启动、预算出价、漏斗与九层根因诊断、归因与增量、成熟利润、平均与边际效率、放量降量、异常恢复、停投复盘。当用户要求判断广告能否投、为什么不消耗/高成本/低转化/有单无利润、如何设置预算出价或目标ROAS、如何测量真实增量、是否放量或停投时使用。不用于抖音、巨量千川、随心推及中国大陆广告生态；不替代品类投资、定价、补货、Listing、内容、达人、品牌或CRM主权。
---

# 跨境广告分析、测量与优化

运行时版本：`AAMO-2026.08`。

成熟度：`controlled pilot`；授权真实历史回放门未通过，不得声明 `production ready`。

## 专业性与决策可用性硬约束

只允许压缩展示，不降低研究标准。每次交付至少保留：对象与四轴、生命周期、数据/成熟状态、结论层级、证据/反证/替代解释、利润或关键约束、动作与幅度、观察窗、成功条件、停止条件、回滚、缺失影响及其决策影响。

本 Skill 拥有广告架构、广告内部预算/出价、广告诊断/测量、放量/降量/暂停/重建/停投主权。不拥有品类投资、价格、补货、Listing、内容机制、达人商务、品牌总战略或客户触达主权。跨域结果使用 `proposed / validated / blocked / inconclusive`；不可补偿红线可阻断，但不得越权改写其他域结论。

任何改变预算、出价、目标、放量或停投的数量结论必须使用确定性脚本。平台归因不等于利润，利润不等于增量，平均效率不等于边际效率。本 Skill 不包含抖音，明确排除抖音、巨量千川、随心推和中国大陆广告规则。

## 入口与交付层级

- Decision Card：单一可行性、追踪、异常或 Scale/Stop 问题。
- Decision Memo：账户、渠道、预算、诊断、测量或平台专项。
- Advertising Diligence：多国家/平台、大预算、复杂归因或完整广告系统。

用户未要求文件时对话交付；要求文件时保存到 `$HOME/Downloads`，同名先询问。用户源文件只读。

## 临时工作区

复杂、可恢复任务使用 managed 模式：`${TMPDIR:-/tmp}/advertising-analysis-measurement-optimization/<YYYYMMDD-HHMMSS>-<task-slug>/`，创建包含 Skill、任务 ID 和创建时间的 `.task-owner.json`。短任务使用 `mktemp -d`。中间报表、截图、授权导出和计算文件只放本任务目录；结束时只删除标记与任务 ID 匹配的目录并验证不存在。清理失败时报告准确路径与原因，不使用宽泛清理命令。

## 跨域边界与双向数据交换

与 CIDM、CIM、VLB、CIG、LIFD、PLCO 的输入、主权、允许/禁止用途、部分失败和冲突裁决读取 [skill-integration-protocol.md](references/skill-integration-protocol.md)。AAMO 只决定广告内部动作。结构化数据与外部写入读取 [data-contract-and-automation.md](references/data-contract-and-automation.md)。所有任务先读 [professional-depth-governance.md](references/professional-depth-governance.md)，正式交付读 [professional-report-delivery.md](references/output-protocols/professional-report-delivery.md)。

## 与品类投资决策 Skill 的边界

当广告可行性、效率或预算结论影响品类进入、追加投资或退出判断时，路由 `category-investment-decision`。本 Skill 向 CIDM 提交广告对象、国家、平台、生命周期、可行性、成熟利润、边际效率、预算上限和停止条件；CIDM 回传资本姿态、利润/现金/库存红线和最弱广告假设。本 Skill 拥有广告内部预算/出价与放量/停投主权，CIDM 拥有资本进入/退出主权；AAMO 不得直接改变进入、追加投资或退出结论，只有 CIDM 接受其 `proposed` 信号并按原模型重算后才能生效。CIDM 缺失或失败时仍完成广告诊断，资本可行性标记 `inconclusive`。

## 与竞品情报 Skill 的边界

当 `competitive-intelligence-monitoring` 确认竞品广告素材、版位、促销或投放代理信号变化时，本 Skill 负责判断我方广告内部响应（出价、预算、素材、定向）；CIM 负责外部变化确认、时间序列和竞争影响。只在用户提供 CIM 事件卡或明确要求联动时消费；不把可见广告数量推断为真实花费，不把竞品素材变化直接写成我方广告动作。CIM 不可用时仍完成本域诊断，竞争响应标记 `inconclusive`。

## 与消费者洞察与客户增长 Skill 的边界

`consumer-insights-customer-growth` 提供经授权且去识别的人群定义、生命周期、贡献利润 CLV、频控和不触达约束；本 Skill 据此执行广告定向、出价和预算分配。本 Skill 拥有广告内部预算/出价与投放动作，CIG 拥有客户证据、客户状态和因果有效性；平台归因不得替代实验增量，AAMO 不得执行客户触达。CIG 不可用时只完成非人群定向部分，人群增量标记 `inconclusive`。

## 与视频链接拆解 Skill 的边界

当用户要把自然内容、达人素材、脚本变体或素材组合用于付费流量时，`video-link-breakdown` 提供素材对象、观察证据、机制假设、产品迁移等级、授权/合规状态、生产成本和测试变体；本 Skill 回传付费交付结果与广告动作。本 Skill 拥有付费预算与放量主权，VLB 拥有内容机制判断；付费胜出不自动证明机制，内容高分不自动授权预算。VLB 不可用时只完成广告经济诊断，素材机制标记 `inconclusive`。

## 与物流库存履约 Skill 的边界

当广告放量涉及库存可售量、配送承诺、仓容或尾程能力时，`logistics-inventory-fulfillment-decision` 提供 ATP/CTP、可履约数量、承诺上限和降级条件；本 Skill 据此约束广告消耗上限和放量节奏。本 Skill 拥有广告预算/出价主权，LIFD 拥有库存履约主权；广告消耗不得超出可履约容量，LIFD 不得反向修改广告预算或出价。LIFD 不可用时广告放量标记 `inconclusive`，不得用行业平均库存假设补结论。

## 与平台店铺Listing转化 Skill 的边界

本 Skill 保留广告账户、预算、出价、归因、增量和放量/停投主权。问题发生在点击后的 PDP、商品卡、落地页、购物车或结账承接时，向 `platform-store-listing-conversion` 交接流量来源、查询/人群、素材承诺、落地页版本、到达事件、实验边界和证据 ID；PLCO 返回页面断点和具体改版。本 Skill 拥有广告内部主权，PLCO 拥有页面承接主权；不能以页面评分替代广告增量判断，PLCO 不得反向修改广告预算或出价。PLCO 不可用时保留已验证广告结论，页面承接标记 `inconclusive`。

## 核心工作流

1. 固定对象、国家、平台、时间窗、生命周期与广告四轴。
2. 读取 [input-evidence-and-measurement.md](references/input-evidence-and-measurement.md)，执行数据、追踪、归因和成熟门禁。
3. 读取 [scenario-lifecycle-and-routing.md](references/scenario-lifecycle-and-routing.md)，选择主场景、动作上限和平台卡。
4. 读取 [decision-and-nine-layer-diagnosis.md](references/decision-and-nine-layer-diagnosis.md)，按影响范围和九层断点形成根因树。
5. 读取 [economics-and-budget-control.md](references/economics-and-budget-control.md)，用脚本计算利润、保本、目标、安全空间、成熟和边际。
6. 涉及归因、实验、准实验、MMM或品牌测量时读取 [incrementality-and-experimentation.md](references/incrementality-and-experimentation.md)。
7. 涉及其他专业域时读取 [cross-domain-and-output-contract.md](references/cross-domain-and-output-contract.md)。
8. 生成专业报告时读取 [professional-report-delivery.md](references/professional-report-delivery.md)，按交付层级保留决策页、诊断树、计算、Ledger 和自检摘要。
9. 正式报告、预算/出价/放量/停投决策和跨域结果卡运行 `scripts/validate_decision_contract.py`；合同失败时阻断正式动作。
10. 输出动作、幅度、预算、观察窗、成功、停止和回滚；动态平台事实执行时联网核验。

## 四轴与生命周期

四轴必须同时记录：流量场景、控制模式、计费方式、优化目标。不得把 PMax/GMV Max 等产品名与 CPC/CPM 计费方式混成同一层。

生命周期固定为规划、冷启动、验证、放量、稳态、衰退、停投/退出。高分、高 ROAS 或卖家资金充足不能突破数据、利润、库存、履约、合规或阶段动作上限。

## 平台路由

平台专项文件位于 `references/platforms/`：

- 所有平台卡先读取 [platform-card-contract.md](references/platforms/platform-card-contract.md)，统一执行对象、测量、根因、利润、动作和禁止推断六组契约。
- `tiktok-shop.md`、`amazon.md`、`shopee.md`、`shein.md`、`temu.md`、`mercado-libre.md`
- `google-search.md`、`google-shopping-pmax.md`、`meta-ads.md`、`tiktok-ads-dtc.md`
- 未覆盖平台读取 `universal-platform-routing.md`

平台产品、国家开放、字段、归因和政策是动态事实，平台卡只提供核验框架与专业差异，不把旧资料固化为当前事实。

平台路由不得只按名称加载；先识别决定性交付机制和首要失效：

| 平台 | 首要交付机制 | 必须拆开的归因/经济问题 | 优先失败检查 |
|---|---|---|---|
| Amazon | 查询/定向×商品×广告位，并受零售资格约束 | 推广ASIN、购买ASIN、品牌光环和退款成熟 | Featured Offer、库存、搜索词与品牌蚕食 |
| TikTok Shop | 素材/直播×货盘×优化事件 | 自然、达人、付费GMV与退款贡献 | 授权、库存、直播时段和自动化切片 |
| Shopee | 关键词/发现×商品×站点活动 | 广告、券、闪购和补贴分账 | 广泛词、活动叠加和跨境承诺 |
| SHEIN | 先核验合作模式与后台可控项 | 结算、活动、退货和可验证营销费 | 禁止虚构自助竞价能力 |
| Temu | 先核验商家模式、国家和开放控制 | 平台分发、活动流量与商家广告分开 | 禁止虚构预算/出价按钮 |
| Mercado Libre | 搜索/商品×本地声誉与配送 | 国家币种、通胀、退款和品牌词 | 汇率假增长、配送/声誉下降 |
| Google Search | 查询×匹配×质量×自动出价 | Ads、GA4、后端与品牌自然蚕食 | 广泛匹配、回传延迟和目标过紧 |
| Shopping/PMax | Feed×商品×资产×价值出价 | 商品级利润、跨网络和品牌需求 | Feed拒登、低毛利SKU、黑箱限制 |
| Meta | 受众/版位×素材×优化事件 | 点击/浏览、建模转化与后端成熟 | CAPI去重、频次疲劳和再营销蚕食 |
| TikTok Ads DTC | 素材×受众×事件×站外承接 | view/click、Spark/自然与后端订单 | 浅层事件、授权到期和页面追踪 |

无法确认平台是否存在某控制项时，输出 `unknown capability` 与核验步骤，不得生成预算、出价或目标ROAS数值动作。

## 脚本路由

- `scripts/ad_economics.py`：CPC/CPM/CPV/CPA/CPS/固定/混合模式利润、保本和目标线。
- `scripts/mature_profit.py`：订单退款、取消、拒付、佣金和成熟收入重述。
- `scripts/marginal_analysis.py`：相邻预算档平均/边际收入和贡献利润。
- `scripts/evaluate_incrementality.py`：基础两组增量收入、利润、区间和护栏。
- `scripts/design_incrementality_experiment.py`：广告实验 MDE、功效、聚类设计效应和所需分配单元。
- `scripts/estimate_causal_incrementality.py`：按广告分配单元执行聚类 ITT、DiD 平行趋势门和合成控制。
- `scripts/estimate_media_response.py`：执行带时间留出的 adstock-Hill 响应估计；输出仅为方向性预算响应，不冒充完整 MMM。
- `scripts/allocate_budget.py`：在预算、上下限和边际贡献约束下配置候选增量预算。
- `scripts/validate_decision_contract.py`：校验广告主权、对象、证据、成熟状态、计算血缘、跨域用途与停止回滚。

脚本只计算用户提供或已取证数据，不抓取、不补平台阈值、不自动执行广告动作。

## 必要输出

1. 决策问题、对象、国家/平台、时间窗、四轴和阶段。
2. 数据、追踪、归因、成熟和三本账状态。
3. Hard gates、影响范围、九层断点、根因假设、支持/反证/替代解释。
4. 计算版本、输入、币税口径、结果、区间和最危险约束。
5. 本域结论与跨域 `proposed/blocked` 信号。
6. 动作对象、幅度、预算、责任人/审批、观察窗、成功、停止和回滚。
7. 缺失数据、补证任务、复核日期及结论可能如何改变。

## 交付前自检

1. 是否排除抖音与国内广告规则。
2. 是否固定对象、四轴、生命周期、国家、平台和版本。
3. 数据、追踪、归因和订单是否成熟；三本账是否分离。
4. 是否先过不可补偿红线，再诊断和评分比较。
5. 是否从影响范围进入九层诊断，而非单指标归因。
6. 平台规则是否当前核验，平台先验是否未跨平台硬套。
7. 预算/出价/放量是否经确定性脚本，平均与边际是否分开。
8. 是否保留反证、替代解释、动作幅度、停止与回滚。
9. 是否守住 D01、D06—D13 的主权边界。
10. 因果结论是否有可执行估计器、识别诊断、区间和动作上限；BSTS/完整 MMM 未实际运行时是否标为 unavailable。
11. 正式交付前是否运行适用脚本测试并清理本任务临时文件。
