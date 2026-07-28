# 动态参数、费率与物流规则

## 唯一规则解析

先过滤语义代码、审批状态、业务有效时间和系统知识时间，再匹配国家、平台、合同、店铺、类目、SKU、渠道、计划、履约方式、承运商、服务、路线、分区、运输方式、货物类型、支付方式和结算计划。

按命中维度数量决定具体性。最高具体性有多个不同规则时返回 `BLOCKED_AMBIGUOUS_RULE`；没有有效规则返回 `MISSING_PARAMETER`；只有过期规则返回 `EXPIRED_PARAMETER`。规则载入顺序不得影响结果。

## 参数快照

每次场景冻结解析上下文、业务时间、知识时间、规则 ID/版本、值、单位、币种、基数、来源和覆盖。新规则不得覆盖旧快照。

## 动态物流

逐段计算揽收、头程、港站、干线、清关、入仓、仓储、出库、尾程和逆向：

`VolumetricWeight = Volume / Divisor`

`ChargeableWeight = RoundByRule(max(ActualWeight, VolumetricWeight))`

`SegmentCharge = max(MinimumCharge, BaseCharge + TierCharge + ΣStackableSurcharge) + Tax`

每段记录运输方式、路线、分区、承运商、服务、重量档、进位、最低收费、燃油、旺季、偏远、住宅、超长超重、危险品、币种、税、时效和容量。任一关键段缺失或不适用时整条路线阻断，不以零补齐。
