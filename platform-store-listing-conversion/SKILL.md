---
name: platform-store-listing-conversion
description: 默认用中文执行专家级跨境平台、店铺、Listing 与转化诊断优化。覆盖 Amazon、Walmart、eBay、Etsy、TikTok Shop、Temu、SHEIN Marketplace、AliExpress、Shopee、Lazada、Mercado Libre、Shopify/DTC 及未知跨境平台；用于渠道承接、店铺结构、Listing 创建/冷启动/优化/迁移/合并/拆分/异常/退出，标题、要点、属性、变体、Offer、索引、主图/图组、详情页、品牌内容、商品卡、集合页、落地页、购物车与结账诊断，以及具体改稿、图片生产 Brief、模块改版、漏斗根因和页面实验。当用户要求诊断或优化标题、主图、详情、落地页、店铺或转化，解释页面为何不曝光/不点击/不加购/不成交，处理页面覆盖、抑制、评论、库存承诺或跨平台迁移时使用。不替代品类投资、产品定义、法律合规、定价利润、物流库存、广告投放、内容创意、品牌营销或客户经营主权。
---

# 平台、店铺、Listing 与转化

运行时版本：`D08-2026.01`。

## 目标与主权

判断已获准销售的商品、Offer、内容和流量能否被目标页面正确承接，并给出可执行、可验证、可停止、可回滚的页面优化。

本 Skill 最终决定页面承接：店铺/类目/系列/导航结构；Listing 类目、属性、标题、要点、规格、变体、搜索承接和信息架构；主图/图组/视频封面的页面角色与顺序；详情/落地页模块和购买路径；页面异常恢复；页面版本实验与生命周期处置。

不得替代：D01资本进入退出、D02外部竞品事实确认、D03产品定义、D05法律合规结论、D06价格利润、D07库存履约、D09广告预算出价归因、D10达人商务、D11创意机制与素材生产、D12定位与Offer战略、D13客户触达/服务/CLV、D14跨域最终经营姿态。跨域动作只输出 `proposed`，等待主权域确认。

付费流量、归因、预算、出价和放量路由 `advertising-analysis-measurement-optimization`；依赖输入失败时保留已验证页面事实，受影响结论标记 `inconclusive`。任何动作必须明确成功条件、停止条件和回滚版本。

## 六道 Hard Gates

依次检查，任一 `fail` 都不得被评分补偿：

1. `G1 identity_rights`：对象同一性、品牌/素材/目录权利；
2. `G2 product_truth`：产品事实、规格、包含物、变体和证据；
3. `G3 platform_compliance`：当前平台/站点规则与 D05 专业复核；
4. `G4 offer_economics`：已批准价格/Offer及成熟贡献利润边界；
5. `G5 inventory_fulfillment`：ATP/CTP、配送、退换、容量与承诺；
6. `G6 measurement_version`：对象、版本、流量、设备、时间窗与测量可比性。

`unknown` 不是 `pass`；缺证据时降低动作上限。违法、侵权、安全、伪造宣称、评论操纵、非法合并、不可复算计算和越权为 P0。

## 九步工作流

1. **锁定对象**：平台/国家/语言、店铺、Listing、SKU/变体、Offer、页面类型、设备、流量、生命周期、`page_version_id` 与 `as_of_time`。
2. **评估输入**：区分 observed、authorized、derived、inferred、causal；登记证据、反证、冲突、时效和禁止用途。
3. **核验当前规则**：动态平台字段、规格、索引、图片、变体、评论和实验能力必须查当前官方或授权资料；未知平台先取证。
4. **执行 Gates**：先阻断不可补偿风险，再讨论优化。
5. **分层诊断**：分别检查 Listing/标题、主图/图组、详情/落地页及跨层一致性；再分解漏斗与替代解释。
6. **生成具体方案**：交付可审阅候选稿、逐槽图片 Brief、模块级改版或路径方案，不得只给评分和最佳实践。
7. **确定性计算**：运行适用脚本，保存输入/输出指纹、版本、区间、敏感性和不可计算原因。
8. **排序与实验**：比较不行动、保守修复、推荐方案和探索方案，明确依赖、主指标、护栏、成功、停止与回滚。
9. **交付与留痕**：给出责任域、人、时间、批准、传播确认、剩余暴露、实际结果回填和跨域交接。

## 场景路由与必读文件

- 对象、生命周期、14组正常/异常/失败/退出场景：读 [scenario-lifecycle-and-routing.md](references/scenario-lifecycle-and-routing.md)。
- 输入、证据、Claims、数据质量和六道 Gate：读 [input-evidence-and-gates.md](references/input-evidence-and-gates.md)。
- 标题、主图、详情和落地页的具体优化：必须读 [concrete-optimization-contract.md](references/concrete-optimization-contract.md)。
- 漏斗、实验、价值、优先级和因果边界：读 [conversion-experiment-and-value.md](references/conversion-experiment-and-value.md)。
- 平台、国家、品类、卖家模式、流量与设备校准：读 [platform-country-calibration.md](references/platform-country-calibration.md)。
- Amazon、Walmart、eBay、Etsy、TikTok Shop、Temu、SHEIN、AliExpress、Shopee、Lazada、Mercado Libre、Shopify/DTC 深诊：先读 [platform-expert-cards.md](references/platform-expert-cards.md)，再读取其中路由的逐平台结构化专家卡；不得只停留在快速矩阵。
- 覆盖、抑制、变体、Offer、权限、迁移、合并、恢复和退出：读 [incident-migration-and-lineage.md](references/incident-migration-and-lineage.md)。
- D01—D14 主权、六 Skill 迁移和交接：读 [cross-domain-and-migration.md](references/cross-domain-and-migration.md)。
- 8 类输出、20 节报告、100 分验收和生产门：读 [professional-report-and-acceptance.md](references/professional-report-and-acceptance.md)。
  机器可检查的8类输出字段见 [output-contracts.json](references/output-contracts.json)。

只读取当前任务需要的文件；完整尽调读取全部。涉及任何页面优化时，`concrete-optimization-contract.md` 不得省略。

## 确定性脚本

关键验证和数值结论必须运行对应脚本：

- `validate_d08_contract.py`：完整报告及专家级优化不可退化门；
- `validate_decision_contract.py`：仓库共享决策合同入口的 D08 本地路由；
- `validate_object_version.py`：对象身份、时间窗、页面版本和可比性；
- `validate_evidence_ledger.py`：证据、Claims、反证、重复指纹和时效；
- `evaluate_hard_gates.py`：G1—G6 与动作上限；
- `compare_page_versions.py`：字段、图片、模块、变体和Offer差异；
- `check_cross_layer_consistency.py`：承诺—证据—规格—价格—库存履约一致性；
- `evaluate_task_coverage.py`：用户任务—页面模块—证明覆盖；
- `evaluate_variant_structure.py`：变体合法性、选择复杂度、库存与评论绑定；
- `decompose_conversion_funnel.py`：漏斗守恒、断点与可比性；
- `evaluate_listing_experiment.py`：实验质量、效应区间、护栏与动作；
- `calculate_recoverable_value.py`：可恢复订单/贡献利润区间；
- `rank_repair_actions.py`：Gate和依赖约束下的稳定排序；
- `validate_page_lineage.py`：页面/报告/实验/回滚血缘与唯一当前版本。
- `validate_output_goldens.py`：验证8类独立专业输出均有对象、证据、具体方案和完整闭环；属于发布辅助门，不替代13类业务工具。
- `validate_migration_parity.py`：逐项验证六Skill源/目标锚点、双向路由、保留主权和断链；属于迁移发布门。

非有限数、负计数、分子大于分母、单位/币种/时窗冲突、循环血缘或多个当前版本必须报错，不得静默修正。

## 专家级具体优化不可退化门

当页面层适用时，必须交付：

- 标题：当前槽位拆解及 `保守修复版 / 核心推荐版 / 探索实验版` 三套候选；
- 主图/图组：首图与图2—N逐槽位目的、画面、文案、证据、裁切、权利、必须/禁止项和排序；
- 详情：模块序号、用户任务、标题/文案候选、视觉/证明、规格边界、疑虑、CTA和数据依赖；
- 落地页：入口承诺、首屏、Offer、证据、选择、CTA、购物车/表单、结账、移动、速度、追踪和逐断点改版。

每项还必须包含对象/版本、证据/反证、根因/替代解释、具体方案、依赖/禁止宣称、实施顺序、负责人/审批、指标/护栏、成功/停止/回滚和剩余暴露。缺任一核心项只能标记 `Diagnostic only / Incomplete`，不得称专家级优化报告。

平台确实没有某页面层时可写 `not_applicable`，但必须附当前平台依据和替代承接面。资料不足时用待批准 Claim 和结构化占位符，不得编造卖点、参数、认证或效果。

## 输出最低合同

```text
对象、page_version、平台/国家/语言/设备/流量/生命周期/as_of_time
输入质量、事实/假设/推断、证据/反证/冲突/时效
G1—G6、P0/P1、允许动作上限
四类页面适用性与独立诊断、跨层一致性
漏斗、主根因、替代解释、不行动基线
具体优化候选稿/生产Brief/模块方案/路径改版
计算、区间、敏感性、不可计算项和指纹
优先动作、责任域、人、时间、依赖和审批
实验、主指标、护栏、成功、停止、回滚
跨域proposed事项、剩余暴露、血缘与实际结果回填
```

快速回答可以压缩展示，不得删除 Gates、证据边界、具体方案和闭环。

## 生产验收

不得把蓝图、静态评分、Golden Case 或合成 fixture 当作真实效果证明。发布前必须：13 类工具通过；至少100个正常/边界/失败/对抗/性质测试通过；8类输出有黄金样例；完成3个经授权、脱敏、含实际结果和证据哈希的历史回放；100/100且无P0/P1；全仓回归通过。未完成真实回放时最多标记 `controlled pilot`。
