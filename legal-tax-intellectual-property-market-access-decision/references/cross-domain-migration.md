# ERDG、跨域交接与迁移

## ERDG 接入

D05 使用唯一 v2 handoff 和 Decision Cycle，不接受 v1，不拥有外部写入。暂存 adapter 只能用于合成验证；发布时再原子迁入 `governance/erdg/adapters/`。

## 生产者与消费者

| 域 | 向 D05 提供 | D05 回传 | 禁止用途 |
|---|---|---|---|
| D01 | 资本姿态、风险暴露 | Gate、补证与退出约束 | D05 改写资本决定 |
| D03 | 产品、用途、规格、材料、包装、Claim | 产品准入问题、Claim 边界 | D05 修改产品定义 |
| D04 | 供应商、工厂、BOM、工艺、测试、批次 | 认证/材料/批次约束 | D05 决定生产放行 |
| D06 | 税基、经济和整改成本 | 税务事实包、情景成本请求 | D05 计算最终利润或税务结论 |
| D07 | 路线、进口、仓储和逆向情景 | 路线/库存合规约束 | D05 分配库存或运输 |
| D08 | 页面、Listing、平台状态 | Claim 与平台使用边界 | D05 直接编辑页面 |
| D09 | 广告动作和素材用途 | 广告 Claim/准入约束 | D05 改预算出价 |
| D10 | 合作方、权利、素材许可 | 权利与合作限制 | D05 签达人合同 |
| D11 | 内容、脚本、素材与 Claim | 内容使用边界 | D05 生产内容 |
| D12 | 品牌、Offer、GTM 和活动 | GTM/Offer 合规约束 | D05 决定品牌定位 |
| D13 | 投诉、伤害、退货和服务结果 | 事故范围和专业通知请求 | D05 决定客户补偿 |

消费者必须回传 `accepted/rejected/partially_accepted/pending`。`pending` 不等于接受；部分接受列出接受和拒绝字段并进入影响闭包。

## 临时合同迁移

迁移 PIPM `PIPM-D05-TEMP-2026.07`、专业意见合同和 SPPQ 占位字段。每个字段记录 source、target、transform、`lossless/lossy/unmapped/conflict/expired`、criticality、validator、consumer 和 rollback。

同一对象、版本、快照和业务时点运行旧/新双轨比较。出现安全关键字段非 lossless、P0/P1 差异、对象错配、消费者拒绝、新合同扩大动作上限或旧读未保留时必须回滚。回滚恢复旧读和旧 Current Decision State，不只回滚代码。

## 部分失败

只冻结依赖失败字段的 Claim、决定和动作。D05 某市场失败不否定其他市场的独立事实；D06 拒绝成本输入不改变 D05 的规则证据；消费者拒绝不得被显示层“已接收”替代。
