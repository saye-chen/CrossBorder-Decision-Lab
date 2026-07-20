---
name: advertising-analysis-measurement-optimization
description: 默认用中文执行专家级跨境广告分析、测量与优化。覆盖 TikTok Shop、Amazon、Shopee、SHEIN、Temu、Mercado Libre、Google Search、Google Shopping、Google Performance Max、Meta Ads、TikTok Ads 站外/Shopify/DTC，以及未知平台通用路由；用于广告可行性、追踪准备、账户结构、搜索/商品/内容/自动化广告、冷启动、预算出价、漏斗与九层根因诊断、归因与增量、成熟利润、平均与边际效率、放量降量、异常恢复、停投复盘。当用户要求判断广告能否投、为什么不消耗/高成本/低转化/有单无利润、如何设置预算出价或目标ROAS、如何测量真实增量、是否放量或停投时使用。不用于抖音、巨量千川、随心推及中国大陆广告生态；不替代品类投资、定价、补货、Listing、内容、达人、品牌或CRM主权。
---

# 跨境广告分析、测量与优化

运行时版本：`D09-2026.07`。

## 专业性与决策可用性硬约束

只允许压缩展示，不降低研究标准。每次交付至少保留：对象与四轴、生命周期、数据/成熟状态、结论层级、证据/反证/替代解释、利润或关键约束、动作与幅度、观察窗、成功条件、停止条件、回滚、缺失影响及其决策影响。

本 Skill 拥有广告架构、广告内部预算/出价、广告诊断/测量、放量/降量/暂停/重建/停投主权。不拥有品类投资、价格、补货、Listing、内容机制、达人商务、品牌总战略或客户触达主权。跨域结果使用 `proposed / validated / blocked / inconclusive`；不可补偿红线可阻断，但不得越权改写其他域结论。

任何改变预算、出价、目标、放量或停投的数量结论必须使用确定性脚本。平台归因不等于利润，利润不等于增量，平均效率不等于边际效率。本 Skill 不包含抖音，明确排除抖音、巨量千川、随心推和中国大陆广告规则。

## 入口与交付层级

- Decision Card：单一可行性、追踪、异常或 Scale/Stop 问题。
- Decision Memo：账户、渠道、预算、诊断、测量或平台专项。
- Advertising Diligence：多国家/平台、大预算、复杂归因或完整广告系统。

用户未要求文件时对话交付；要求文件时保存到 `$HOME/Downloads`，同名先询问。用户源文件只读。

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

- `tiktok-shop.md`、`amazon.md`、`shopee.md`、`shein.md`、`temu.md`、`mercado-libre.md`
- `google-search.md`、`google-shopping-pmax.md`、`meta-ads.md`、`tiktok-ads-dtc.md`
- 未覆盖平台读取 `universal-platform-routing.md`

平台产品、国家开放、字段、归因和政策是动态事实，平台卡只提供核验框架与专业差异，不把旧资料固化为当前事实。

## 脚本路由

- `scripts/ad_economics.py`：CPC/CPM/CPV/CPA/CPS/固定/混合模式利润、保本和目标线。
- `scripts/mature_profit.py`：订单退款、取消、拒付、佣金和成熟收入重述。
- `scripts/marginal_analysis.py`：相邻预算档平均/边际收入和贡献利润。
- `scripts/evaluate_incrementality.py`：基础两组增量收入、利润、区间和护栏。
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
10. 正式交付前是否运行适用脚本测试并清理本任务临时文件。

## D08 落地页路由

本 Skill 保留广告账户、预算、出价、归因、增量和放量/停投主权。问题发生在点击后的PDP、商品卡、落地页、购物车或结账承接时，向 `platform-store-listing-conversion` 交接流量来源、查询/人群、素材承诺、落地页版本、到达事件、实验边界和证据ID；D08返回页面断点和具体改版，不能以页面评分替代广告增量判断。
