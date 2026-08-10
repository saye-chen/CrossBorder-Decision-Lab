# LIFD 数据合同与自动化

## 规范对象与数量状态

SKU/变体/批次、货权主体、国家、仓、库位、渠道、路线、承运商、订单、在途和退货使用稳定 `object_id`。每条记录保存单位、币种、税口径、时区、状态时点、`as_of_time`、有效期、来源、对象版本和证据指纹。缺失使用 `unknown`，不得填零值。

库存状态至少分 `physical/on_hand/quality_hold/blocked/eligible_sellable/protected/allocated/in_transit/available_to_promise`；不得用一个“库存”字段代替。数量守恒为期初+合格入库+调入−出库−调出−损耗/处置=期末，差异必须进入异常桶。

## 计算血缘

预测、交期、ROP、安全库存、补货、ATP/CTP、路线、仓容、分配、退货和退出计算保存 `calculation_id/model_version/input_ids/input_hash/output_hash/unit/currency/window/assumptions/constraints`。非有限值、负数量、混合单位、循环血缘、多个当前版本或不可行约束必须失败。

## 接口与部分失败

接口、节点、承运商或仓库失败返回 `complete/partial/inconclusive/failed`、最后成功游标、成功对象、失败对象、数据截止和重试条件。计划、报价、ASN 和系统可售不得自动升级为实际到货、物理库存或真实能力；失败分区不补零。

自动化候选默认 `proposed`。补货、调拨、承诺和处置结果必须带货权、批次、数量、最晚时间、能力版本、现金/成本、成功、停止、回滚和退出条件。

## F01/ECAE 增量输入合同

库存排序只读取由 `schemas/ecae_inventory_receipt.schema.json` 定义、并经 `scripts/validate_ecae_inventory_handoff.py` 校验的 D07 消费者回执。回执固定记录迁移/合同版本、handoff 哈希、CE 等级、claim ceiling、用途、有效决定、所有者签字引用、增量状态、排序资格和回执哈希。直接回放的回执必须再次对照当前权威迁移验证；旧签字、跨域回执、哈希篡改、过期或触发重算都失败关闭。

`incremental_value_state=unknown` 时不得携带数值；`ranking_use_allowed=false` 时不得进入边际排序。预测、归因、旧 C0—C3 标签、裸 `incremental_contribution`、fixture 本地通过或生产双轨未完成，均不能自动升级为合格因果输入。接口不可用只污染增量排序：LIFD 仍可核对基础保护和数量守恒，但共享池动作保持 `inconclusive`，不产生外部写入。

## 外部写入

下单、调拨、承运商订舱、改仓、取消、客户承诺、退供、清算和销毁必须获得明确授权并验证精确对象、前值、货权、审批、幂等键、回执和回滚/补救。批量动作先 dry-run；部分成功后按订单/批次对账，禁止整批重放。

召回、安全、禁运和客户地址等敏感数据执行最小权限、用途限制、去识别和保存期限；不得写入公开 fixture。
