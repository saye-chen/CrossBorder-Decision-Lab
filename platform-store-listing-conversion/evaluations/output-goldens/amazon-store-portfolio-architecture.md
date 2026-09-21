# PLCO Amazon 店铺与组合架构专业报告样板

运行时：`PLCO-2026.07`；样板状态：`controlled_pilot`；本样板只定义报告结构和决策边界，不冒充当前 Amazon 规则或客户事实。

## 1. 封面版本

对象：`store_profile_id=SP-AMZ-001`；平台：Amazon；站点：`marketplace_id=MARKETPLACE-001`；Seller ID：`SELLER-001`；法定主体：`LEGAL-ENTITY-001`；Seller Central/Vendor Central：待证；卖家角色：待证；履约：待证；目录/库存所有权：待证；报告版本：`v0.1`；`as_of_time`：`2026-09-21T00:00:00+08:00`；证据指纹：`EVIDENCE-PACKET-001`。

## 2. 决策页

结论：`Conditional / do not scale`。原因不是页面分数不足，而是 Seller ID、法定主体、销售项目、履约方式、Offer 所有权和品牌权限尚未全部绑定。当前可做：补证、建立店铺画像、核对 ASIN/父子体/Offer、分桶广告和库存数据。当前不可做：把 Brand Store 当作卖家账户，把同一 ASIN 当作同一 Offer，把 FBA 承诺迁移到 MFN，或跨账户/站点合并销售与广告归因。

前三动作：

1. 由店铺负责人提交 Seller Central/Vendor Central 身份、法定主体、Marketplace site、Seller ID、Ads Profile 和当前页面/Offer 快照。
2. 由 PLCO 为每个账户×站点×经营模式建立独立 `store_profile_id`，并运行 Amazon store-profile validator。
3. 由 AAMO、LIFD、D06 和 PLCO 重新对齐广告、库存、履约、Offer 和成熟利润口径。

每日运营板必须同时标记 `operating_archetype_id`、`overlay_ids`、`lifecycle_phase`、`cadence`、`workstream_id`、`metric_scope`、`metric_class` 和 `action_ceiling`；不能把 FBA、MFN、Vendor 的工作压成一张 Amazon 通用日报。工作流必须按日内、每日、每周、每月和事件触发拆开，并在每个节奏内保留对应指标与动作上限。

## 3. 问题、阶段与动作上限

问题阶段：`identity_and_routing`，不是“转化率优化”阶段。G1—G6 任一门禁为 `unknown` 时，动作上限为 `conditional_only`：只允许补证、只读审计、可逆检查和预注册实验设计；不允许外部写入、放量、迁移、拆并店、改价或改变履约承诺。日内、每日、每周、每月和事件触发任务分别记录，领先指标、诊断指标、结果指标、护栏指标和数据质量指标不互相替代。

## 4. 对象树

`legal_entity → seller_account/Seller ID → marketplace_site → selling_program → brand_asset_layer → ASIN/parent-child → seller SKU → marketplace Offer → fulfillment/inventory → Ads Profile/campaign → page_version`。Brand Store/A+ 位于品牌资产层；Amazon Business 是商业叠加层；多账户/多站点是组合拓扑，均不能替代 Seller Account 或 Offer。

## 5. 输入质量

| 输入 | 状态 | 允许用途 | 缺失影响 |
|---|---|---|---|
| Seller ID、卖家账户、法定主体 | unknown | 仅身份补证 | 阻断归属、组合和迁移 |
| Marketplace site、销售项目 | unknown | 仅路由 | 阻断规则、税费和经营模式继承 |
| Seller role、品牌授权、目录所有权 | unknown | 仅权限调查 | 阻断 Brand Store/A+ 与品牌声明 |
| FBA/MFN/Vendor、库存所有权 | unknown | 仅履约补证 | 阻断库存、配送和经济性结论 |
| ASIN/父子体/SKU/Offer 快照 | partial | 对象核对 | 阻断可购买和变体结论 |
| Ads Profile、广告报告 | partial | 只读归因分桶 | 阻断跨店广告与销售合并 |
| `as_of_time`、来源指纹 | partial | 动态事实重验 | 过期即降级并重算 |

## 6. Gates、P0 与 P1

G1 身份和法定主体：`unknown`；G2 站点和销售项目：`unknown`；G3 品牌/目录权限：`unknown`；G4 Offer/库存/履约：`partial`；G5 证据新鲜度：`partial`；G6 测量与归因一致性：`partial`。P0：任何非法合并、身份错配、伪造授权、跨账户评价继承或绕过账户健康的方案。P1：报告缺少店铺画像、具体槽位、责任人、成功/停止/回滚条件。

## 7. 横向校准

先判基础 archetype：3P 品牌 + FBA、3P 品牌 + MFN、授权经销商 + FBA、授权经销商 + MFN 或 Vendor Central 1P。再判 overlay：Amazon Business、Brand Registry/Brand Store、多账户/多品牌/多站点。不能用 Seller Central 3P 的价格、FBA 成本、可售库存、配送和广告规律替代 Vendor Central 1P 或 MFN。

## 8. Listing、ASIN 与目录

核对 ASIN、父子体关系、目录所有权、SKU、站点标题/要点/属性、版本和当前可见页面。ASIN 级产品事实只能在同一版本、同一目录所有权和同一站点规则下重新验证后迁移；父子体合并必须同时检查产品身份、变体属性、评论语境和退货差异。

## 9. 主图与图组

主图、图组和 A+ 的判断按 `page_version × device × marketplace_site × brand_authority` 分桶。候选图必须写明槽位、画面主体、尺寸/比例、文本边界、产品事实来源、审核责任人和回滚版本；不能因为 Brand Store 有权限就推断卖家 Offer 也可使用同一素材或同一声明。

## 10. 详情、品牌内容与落地承接

详情页需要把标题、要点、属性、图组、A+、品牌店铺、价格、配送、退货和 Offer 组成跨层事实链。品牌内容只证明品牌资产层的可用性，不证明卖家账户、库存、Featured Offer 或履约能力。页面动作必须先锁定 Offer，再交给营销/广告/物流确认。

## 11. 跨层一致性

检查矩阵：

| 层 | 必须一致 | 禁止继承 |
|---|---|---|
| 身份 | Seller ID、法定主体、站点、销售项目 | 另一账户的健康或授权 |
| 品牌 | Brand ID、授权状态、目录所有权 | Brand Store 直接替代卖家权限 |
| Offer | SKU、库存所有权、价格、可购买状态 | ASIN 直接替代 Offer |
| 履约 | FBA/MFN/Vendor、库存和配送责任 | FBA 承诺迁移到 MFN |
| 广告 | Ads Profile、推广/购买 ASIN、归因窗 | 另一 Profile/站点的归因 |

## 12. 漏斗与根因

在身份未闭合前，不能把曝光、点击、加购、订单或广告 ROAS 解释为页面因果。候选根因分为：身份路由错误、目录/变体错配、Offer 不可购买、履约承诺不一致、广告 Profile 混桶、品牌内容权限不足、库存/价格并发变化。每个根因必须配一条反事实验证，并保留至少一个替代解释。

## 13. 证据、反证与反事实

支持证据：授权 Seller Central/Vendor Central 导出、当前页面快照、SP-API/Ads API 只读数据、品牌授权与目录记录。反证：同一 ASIN 下不同卖家 Offer、不同站点页面、库存和配送变化、广告 Profile 不一致。最弱假设：来源属于同一 Seller Account 且时间窗可比。若 Seller ID、Profile 或 Offer 对不上，相关结论必须变为 `inconclusive`，不能用平均值补齐。

## 14. 计算与敏感性

当前不可计算放量金额、真实 ROAS、补货量或迁移收益：缺少店铺归属、履约模式、库存责任、平台费用/税费口径和成熟退款窗口。补证后才可按店铺、站点、SKU/Offer 计算贡献利润，并对价格、广告、履约、退款和缺货分别做敏感性；零值与缺失值不得互换。

## 15. Issue Cards

- `AMZ-I01` 身份未闭合：严重度 P0/P1 取决于是否已发生跨账户写入；负责人 Seller Ops；验证 Seller ID、法定主体和授权快照。
- `AMZ-I02` 经营模式未闭合：FBA/MFN/Vendor 缺失时冻结经济性；负责人 Fulfillment；验证库存渠道与配送责任。
- `AMZ-I03` 品牌资产误当 Offer 权限：冻结 Brand Store/A+ 执行；负责人 Brand/PLCO；验证品牌授权和目录所有权。
- `AMZ-I04` Ads Profile 混桶：冻结跨店广告归因；负责人 AAMO；验证 Profile、站点、推广 ASIN、购买 ASIN 和归因窗。

## 16. 实验设计

第一阶段只做只读重放：按店铺画像重分桶，检查销售、库存、Offer、广告和页面是否能一一对齐。第二阶段才可做页面或广告实验，固定 `store_profile_id × marketplace × ASIN/Offer × page_version`，预注册主指标、利润/库存/退货护栏、观察窗、最小可检测差异、停止和回滚规则。缺少授权实验或成熟窗时只称“描述变化”，不称增量。

## 17. 异常恢复与血缘

若出现内容覆盖、Offer 错配、父子体污染、账户受限或报告部分成功，先冻结传播，保留原始快照、payload hash、时间和授权边界，再恢复最近验证通过的对象版本。每次恢复记录影响闭包：账户、站点、ASIN、SKU、Offer、广告、库存、页面、客户承诺及未消除暴露；不能只恢复页面而遗漏库存或广告口径。

## 18. 跨域交接

PLCO 输出给 AAMO：店铺画像、页面版本、Offer 状态和可测量范围；给 LIFD：SKU、库存所有权、履约模式、配送/退货证据；给 D06：成熟贡献利润所需的费用、税费和退款口径；给品类投资：基础经营模式、组合蚕食、合法性和退出成本。各域只接收 proposed 证据包，不改变对方主权，也不自动执行外部操作。

## 19. 行动计划

| 顺序 | 动作 | Owner | 前置 | 成功 | 停止/回滚 |
|---|---|---|---|---|---|
| 1 | 补齐画像与证据指纹 | Seller Ops | 授权导出 | validator=pass/conditional 可解释 | 身份冲突即 blocked |
| 2 | 对齐 Offer/库存/履约 | PLCO + LIFD | SKU/Offer/库存快照 | 对象键一一匹配 | 部分成功则隔离受影响字段 |
| 3 | 按 Profile/站点重算广告归因 | AAMO | Ads 报告与销售报告 | 归因窗口和对象一致 | 混桶则废弃该比较 |
| 4 | 设计页面/营销实验 | PLCO + Marketing | G1—G6 通过 | 预注册且可回滚 | 规则、利润或库存护栏触发即停 |

## 20. Ledger、血缘与自检

本报告必须附 `evidence_ids`、来源类型、抓取/观察时间、payload hash、允许用途、禁止用途、对象键、page_version、负责人和失效时间。自检结论：身份闭合前没有无条件方案；未知未被写成通过；品牌层、卖家账户、站点和 Offer 已分开；FBA/MFN/Vendor 未互继；广告与库存未跨 Profile/站点合并；外部写入为 `false`；生产门仍需 3 个授权历史回放通过后再开放。
