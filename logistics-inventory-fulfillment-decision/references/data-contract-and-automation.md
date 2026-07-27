# LIFD 数据合同与自动化

## 规范对象与数量状态

SKU/变体/批次、货权主体、国家、仓、库位、渠道、路线、承运商、订单、在途和退货使用稳定 `object_id`。每条记录保存单位、币种、税口径、时区、状态时点、`as_of_time`、有效期、来源、对象版本和证据指纹。缺失使用 `unknown`，不得填零值。

库存状态至少分 `physical/on_hand/quality_hold/blocked/eligible_sellable/protected/allocated/in_transit/available_to_promise`；不得用一个“库存”字段代替。数量守恒为期初+合格入库+调入−出库−调出−损耗/处置=期末，差异必须进入异常桶。

## 计算血缘

预测、交期、ROP、安全库存、补货、ATP/CTP、路线、仓容、分配、退货和退出计算保存 `calculation_id/model_version/input_ids/input_hash/output_hash/unit/currency/window/assumptions/constraints`。非有限值、负数量、混合单位、循环血缘、多个当前版本或不可行约束必须失败。

## 接口与部分失败

接口、节点、承运商或仓库失败返回 `complete/partial/inconclusive/failed`、最后成功游标、成功对象、失败对象、数据截止和重试条件。计划、报价、ASN 和系统可售不得自动升级为实际到货、物理库存或真实能力；失败分区不补零。

自动化候选默认 `proposed`。补货、调拨、承诺和处置结果必须带货权、批次、数量、最晚时间、能力版本、现金/成本、成功、停止、回滚和退出条件。

## 外部写入

下单、调拨、承运商订舱、改仓、取消、客户承诺、退供、清算和销毁必须获得明确授权并验证精确对象、前值、货权、审批、幂等键、回执和回滚/补救。批量动作先 dry-run；部分成功后按订单/批次对账，禁止整批重放。

召回、安全、禁运和客户地址等敏感数据执行最小权限、用途限制、去识别和保存期限；不得写入公开 fixture。
