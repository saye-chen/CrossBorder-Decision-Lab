# 对象、生命周期与状态

## 对象层级

`market_context → audience_segment → brand/brand_architecture → marketing_program → marketing_campaign → execution_unit`。执行单元关联`offer/message_promise/channel_role/touchpoint/execution_version/exposure_window/outcome_window`。

核心对象还包括`marketing_resource_envelope`、`brand_metric_definition`、`brand_metric_observation`和`incident`。市场级人群不是个人名单；个人身份与资格归CIG。

## 身份合同

至少记录`object_type/object_id/parent_id/country_or_region/locale/currency/timezone/platform/channel/product_id/sku_ids/segment_id/lifecycle_stage/object_version/execution_version/rule_version/as_of_time/evidence_cutoff/decision_owner/execution_owner/review_owner`。未知使用`unknown`，不适用使用`not_applicable`。

## 生命周期

L0资格与问题定义；L1市场与人群；L2定位与品牌；L3上市准备；L4冷启动验证；L5放量扩张；L6稳态与品牌积累；L7异常疲劳恢复；L8收缩重定位退出。

所有阶段允许`proceed/test/hold/repair/reduce/stop/escalate/inconclusive`，`proceed`不等于`scale`。

## 状态机

`draft → proposed → reviewed → approved → scheduled → live → paused/degraded/blocked → completed → measured → archived`。`approved`不等于上线，`live`必须有实际版本，`measured`必须注明成熟窗。停止后恢复需要新决策版本。

## 禁止混用

品牌与SKU；营销项目与广告Campaign；Offer机制与页面呈现；资源方向与广告账户预算；计划/审批/执行/曝光/结果版本；活动订单/归因订单/成熟订单/增量订单；单国定位与全球定位。
