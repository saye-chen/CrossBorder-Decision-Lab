# Amazon Ads 运营决策备忘录

运行时：`AAMO-2026.07`；专项契约：`AAMO-AMAZON-ADS-2026.07`；成熟度：`controlled_pilot`。

## 执行摘要

决策结论：`conditional / do not scale`。一句话理由：Amazon 广告只有在 Ads Profile、Campaign/Target、零售准备度、归因成熟和成熟贡献利润同时可解释时才允许受控试验；缺失数据不能用账户平均 ACoS、品牌光环或平台归因销售补齐。生命周期按上新、冷启动、验证、放量、稳态、衰退、异常或退出分层；当前默认仍是 controlled pilot。

## 对象与边界

适用范围限一个 `store_profile_id × seller_account_id × marketplace_id × ads_profile_id × ad_type × promoted_asin × date/window` 对象。Seller Central 3P、Vendor Central 1P、品牌商、授权经销商、FBA 和 MFN 不共享结论。缺失数据包括身份、资格、Offer、库存、配送、目标/查询、归因类型、退款成熟和边际经济；缺失影响是降级为 conditional、inconclusive 或 blocked，而不是零值。

## 证据与反证

支持证据 E1：授权 Ads 报告、Seller/Offer/库存快照和成熟订单账可通过对象键对齐。反对证据：同一 Campaign 下目标、搜索词、购买 ASIN 或广告位混合；品牌词归因上升但自然基线未改善；退款成熟后贡献转负。A1 最弱假设是来源权限、对象身份和时间窗可比。证据截止：执行日按当前站点和控制台重验。替代解释必须保留，例如低交付可能来自零售资格、库存、Offer、相关性、预算或资格，而非单一竞价。

## 门槛与评分

G1 Profile/账户/站点，G2 Campaign/目标资格，G3 可购买/Featured Offer/库存/价格/配送，G4 查询/受众/广告位血缘，G5 归因与成熟，G6 成熟贡献与边际经济。门槛不可由 ROAS 或综合评分补偿；任一关键门为 unknown 只允许补证或诊断。

## 证据台账

E1 记录来源、授权范围、对象键、抓取时间、观察时间、payload hash、允许用途和禁止用途；E2 记录零售准备度和 Offer 版本；E3 记录业务订单、退款成熟和库存护栏。广告报告与业务订单对象不一致时保留冲突，不静默合并。

## 假设台账

A1 来源与对象可比；A2 Campaign/Target/ASIN 版本在观察窗内未发生未记录变更；A3 退款和退货观察窗已经成熟；A4 预算变化没有与价格、库存、页面或促销同时发生不可分离的并发变化。每项假设都要有责任人、复核时间、证伪证据和对决策的影响。

## 1. 首屏结论与动作上限

本备忘录用于 Amazon Sponsored Products、Sponsored Brands、Sponsored Display 或 DSP 的每日、每周和事件型运营。结论先写状态：`validated / proposed / conditional / blocked / inconclusive`。在店铺身份、广告资格、零售准备度、归因成熟度或成熟贡献缺失时，默认只能补证、诊断或设计可逆实验；不生成外部写入动作。

## 2. 对象、身份与版本

必须记录 `store_profile_id`、Seller Account、Seller ID、法定主体、Marketplace、销售项目、卖家角色、履约模式、库存所有权、目录所有权、Ads Profile、Campaign、Ad Group/Line Item、Ad/Creative、Target、Query/Search Term、Placement、推广 ASIN、购买 ASIN、页面/Offer 版本、日期、时区和 `as_of_time`。跨店铺、跨站点、跨履约或跨销售项目不得继承结论。

## 3. 广告类型与架构

Sponsored Products 分自动、关键词、商品和类目定向；Sponsored Brands 另需品牌授权、品牌素材和目的地版本；Sponsored Display 分上下文、商品、受众、拓新、再营销和 cross-sell；DSP 分受众、上下文、再营销、拓新、素材、库存来源和频次。报告须明确对象血缘：Ads Profile → Campaign → Ad Group/Line Item → Ad/Creative → Target → Query/Search Term → Placement/Inventory Source → Promoted Object → Outcome Object。

## 4. 数据与三本账

广告账保留花费、展示、点击、订单/单位、归因销售、归因类型、归因窗、广告位和购买 ASIN；业务订单账保留订单、取消、退款、退货和履约；成熟经营账扣除平台费、履约、促销、退款成熟和商品/Offer 可变成本。平台归因不等于利润，利润不等于增量；品牌光环、New-to-brand、点击/浏览归因只能按其定义使用。

## 经济与计算

C1 使用 `ad_economics.py`、`marginal_analysis.py` 和 `mature_profit.py` 重算广告账、边际效率和成熟贡献；输入包括花费、归因销售、订单/单位、平台费、履约、促销、退款成熟和库存护栏。币种、税口径、归因窗和时间窗必须一致；可复算：是。输入哈希 `synthetic:amazon-ads-input-v1`；输出哈希 `synthetic:amazon-ads-output-v1`。没有成熟利润或边际结果时只能输出 no-scale/补证，不给统一目标 ROAS。

## 计算台账

C1 状态按 `observed / derived / unknown / conflict` 留痕；平均效率和边际效率分开，平台归因销售和增量分开，退款未成熟不包装成最终利润。任何数值动作必须保留当前值、幅度、观察窗、敏感性和回滚版本。

## 5. 低交付与不消耗诊断

按 G1 Profile/账户/Marketplace → G2 Campaign/广告/目标资格 → G3 ASIN 零售准备度 → G4 查询/目标/受众/广告位 → G5 归因、币种、时间窗和成熟 → G6 成熟贡献和边际经济排查。G1 失败为 `blocked`；G3 失败冻结放量；G4 仅诊断；G5 证据不足为 `inconclusive`；G6 缺失不得 `scale`。提高竞价必须是通过门禁后的候选动作，不是低交付的默认答案。

## 6. 搜索词、目标与否定

每日输出搜索词覆盖、目标与查询错配、收割队列、否定覆盖、购买 ASIN 结构和重复归功检查。自动发现转手动目标时记录来源、去重方式、匹配类型、推广 ASIN、观察窗和后续验证；竞品 ASIN、类目细分、品牌词、非品牌词和 B2B 意图不得混池。缺失搜索词或目标血缘时，不得按 Campaign 平均 ACoS 直接改出价。

## 7. 预算、出价与广告位

每日看预算状态、预算节奏、当前出价、广告位调节、交付率和库存/配送护栏；每周看目标、ASIN 和广告位边际贡献；月度比较平均效率与边际效率。任何预算/出价候选都要注明当前值、拟议幅度、成熟窗口、预算上限、库存上限、成功条件、停止条件和回滚版本。不存在可迁移到所有站点的固定阈值，平台控制项和当前规则须在执行日核验。

## 8. 零售准备度与页面交接

广告操作须先确认可购买、Featured Offer、库存、价格、配送承诺、页面版本、Offer 版本和活动/广告资格。点击后转化断点交给 PLCO，广告不替代页面改版；PLCO 不反向改预算或出价。任何零售准备度冲突都冻结放量，并记录影响 ASIN、站点、时间窗和恢复条件。

## 9. 归因、蚕食与增量

Sponsored Brands 的品牌词、品牌光环和自然需求必须与非品牌、竞品词和类目词拆开；Sponsored Display/DSP 必须拆 click-through、view-through、再营销和拓新；DSP 必须有频次与反事实测量设计。可采用 brand-off、地域留出、查询层留出或其他适用实验，报告同时写支持证据、反证和替代解释，不能用平台归因销售证明增量。

## 10. 店铺类型路由

3P 品牌 FBA 关注零售准备度、FBA 可售/预留/在途和品牌资产；3P 品牌 MFN 关注配送承诺、迟发/取消和履约容量；授权经销商关注授权、购买成本、价格政策、Featured Offer 和 Offer 退出；Vendor 1P 与 3P 销售、采购订单、批发价格、扣款/索赔分账。每种店铺必须有独立的 Ads Profile、利润口径和动作上限。

## 11. 每日主板

每日主板至少写：`cadence`、`lifecycle`、`workflow_id`、`metric_scope`、`metric_class`、`value_state`、`window_start/window_end`、`observed_at`、`source_contract`、`evidence_id`、`attribution_type`、`maturity_state`、`unknown_reason`、`decision_question`、`current_state`、`action_ceiling`、`success_conditions`、`stop_conditions`、`rollback_ref` 和 `next_due`。缺失不记 0，冲突不静默平均。

## 12. 每周与每月经营板

每周复盘 Campaign 结构、搜索词/目标去重、收割/否定、广告位边际、购买 ASIN、零售门禁、库存和页面交接；每月复盘成熟退款、贡献利润、保本 ROAS、边际 ROAS、增量销售、蚕食、品牌/经销商权限、B2B 分层、组合冲突和异常残余暴露。报告应指出本周期决策与上周期相比发生的变化。

## 13. 异常恢复与回滚

追踪断裂、资格失败、账户受限、预算漂移、ASIN 不可购、跨店污染和错误归因分别建 Incident Card。保留变更前值、变更时间、影响范围、责任域、最近有效版本、回滚步骤、回滚验收、残余暴露和关闭证据。恢复不是简单重新启用：必须重新通过 G1–G6。

## 14. 跨域交接

交给 PLCO：查询/受众、素材承诺、落地页/页面版本、到达事件和证据；交给 LIFD：可履约数量、补货、配送承诺和降级条件；交给定价利润域：Offer、可变成本、促销、退款和成熟贡献；交给增量评估域：实验单元、控制组、识别假设和有效期；交给品类投资域：广告可行性、成熟利润、边际效率、预算上限和退出条件。参与域只能提交 `proposed`，不得执行外部变更。

## 15. 专业自检

报告在交付前确认：对象和店铺身份无冲突；四轴、生命周期和站点固定；数据、追踪、归因和成熟状态可解释；三本账分离；广告类型和定向族没有混算；平均/边际/增量分开；支持证据、反证和替代解释齐全；动作幅度、观察窗、成功、停止、回滚、责任人、复核时间齐全；动态平台事实已在执行日核验；`external_write=false`；无任何未授权的自动预算或出价变更。

## 根因

根因必须落到 G1–G6 的对象层，并同时写支持证据、反对证据、替代解释和推翻条件。低展示不能直接写成出价不足，高点击低成交不能直接写成页面问题，高 ROAS 不能直接写成增量或成熟利润。

## 决策推导

先比较不行动、补证、可逆修复、受控实验和放量候选，再按专业门、边际贡献、库存/配送和增量证据排序。决策影响包括广告花费、库存、自然需求、品牌资产、客户承诺、退款和跨店组合；任何跨域结论必须重新验收。

## 主权与联动

主决策 Skill：`advertising-analysis-measurement-optimization`。AAMO 拥有广告内部预算、出价、目标、归因、放量/降量/停投主权；PLCO、LIFD、定价利润、增量评估和品类投资只提交 `proposed`。允许用途为诊断、候选与实验设计；禁止用途为未经审批的外部写入、跨店合并、替代库存/价格/页面/资本结论。

## 行动计划

动作对象、幅度、责任人、审批、观察窗和复核时间必须明确。成功条件：资格、零售准备度、追踪、成熟利润和边际/增量门关闭；停止条件：身份/Offer 冲突、零售门禁失败、库存或配送护栏恶化、追踪断裂、边际贡献转负；回滚：恢复最近验证通过的预算/出价/目标/素材版本并重新走 G1–G6。

## 国家/平台与动态事实

平台：Amazon；Marketplace 和广告产品能力按执行日核验，核验日期：2026-09-21。广告类型、归因窗、资格、广告位、权限、报告字段和控制项不可用历史资料或其他站点默认值替代；无法确认时写 `unknown capability`，不生成数值动作。

## 自检摘要

支持证据、反对证据、最弱假设、成功条件、停止条件、回滚、置信度、决策影响和外部写入边界齐全。伪造事实：否；因果越界：否；主权越界：否；隐私违规：否；可复算：是；当前状态：controlled pilot，不是 production ready。
