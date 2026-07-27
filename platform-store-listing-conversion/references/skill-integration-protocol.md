# PLCO 跨 Skill 集成协议

## 共享包

每个交接包必须包含 `packet_id/source_skill/source_runtime/target_skill/object_id/object_version/page_version_id/as_of_time/status/evidence_ids/calculation_ids/allowed_uses/forbidden_uses/expiry/recompute_trigger`。`proposed` 输入不得自动改页面，只有主权域确认和 PLCO 重算后才能进入候选版本。

`allowed_uses/forbidden_uses` 分别表达允许用途与禁止用途；页面候选不得超出允许用途消费来源 Claim。

## 双向主权

| 对接域 | PLCO 可消费 | PLCO 可返回 | 禁止越权 |
|---|---|---|---|
| CIDM | 资本姿态、利润红线、目标对象 | 承接质量、可恢复价值、实验结果 | 改写进入/退出 |
| CIM | 已确认竞品页面/Offer事件 | 页面响应假设和监控请求 | 把竞品页面当因果证据 |
| VLB | 内容机制、素材、Claim和权利 | 页面槽位 Brief 与承接结果 | 改写素材机制 |
| CIG | VOC、任务、阻力和不触达约束 | 页面旅程断点和实验结果 | 执行客户触达 |
| LIFD | ATP/CTP、配送、退换、容量 | 页面库存/承诺需求 | 修改补货和路线 |
| AAMO | 流量、查询/人群、素材承诺、归因边界 | 页面断点、版本和实验 | 修改预算/出价 |
| CAPM | 达人素材权利和链接要求 | 页面承接 Brief 与版本 | 修改达人合同 |
| MBCM | 定位、Offer机制、活动姿态 | 页面可执行性和承接风险 | 改写品牌/活动战略 |

## 接受、冲突与部分失败

先验证 Listing/SKU/Offer/设备/流量、页面版本、证据截止、Claim 权利、允许用途和哈希。冲突按 P0 红线、产品事实、主权、对象版本、证据等级和时效裁决。页面可见变化不自动覆盖后台授权事实。

依赖失败只污染相关层：LIFD 不可用时库存/配送承诺 `inconclusive`，不抹掉标题事实；AAMO 不可用时付费流量归因 `inconclusive`，不阻止自然流量可逆修复；权利不明只阻断相关素材槽位。

## 结果回填

回填接受版本、实际发布槽位、传播状态、曝光、点击、加购、购买、退货/投诉、利润护栏、实验区间、失败原因、回滚版本和下一重算触发。Offer、库存、页面、流量或测量版本变化时，陈旧结论必须标记 `stale/superseded`。
