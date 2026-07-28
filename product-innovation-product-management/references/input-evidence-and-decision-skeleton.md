# 输入、证据与决策骨架

## 输入层级

| 等级 | 最小内容 | 动作上限 |
|---|---|---|
| M0 | 对象、国家平台、产品阶段、问题和至少一个来源 | 登记与补证 |
| M1 | 支持/反对证据、用户任务、约束和版本 | 产品假设 |
| M2 | 需求/规格候选、验证计划、D06边界和红线 | 产品定义与受控验证建议 |
| M3 | 授权结果、样品/批次、异质性和历史版本 | 更高置信度建议；不关闭L4 |

缺失状态必须区分 `missing`、`unavailable`、`not_applicable`、`not_yet_observed`、`withheld`、`invalid` 与 `observed_zero`。只有 `observed_zero` 可以作为数值零参与计算。

## ERDG 正交合同

- evidence 只记录来源与处理状态；
- claim 单独记录状态和结论等级；
- calculation 单独记录模型、输入输出哈希和执行状态；
- decision 绑定主权、对象、候选、不行动、Hard Gates、动作上限和闭环；
- verified evidence 不自动生成 validated claim；
- validated claim 不自动生成 causal grade；
- F01未建成前 D03 禁止确认 causal；
- synthetic fixture 仅支持L1—L3测试。

## 决策顺序

`对象/版本 → 输入质量 → 证据与反证 → Hard Gates → 用户任务与最弱假设 → 不行动/保守/推荐/压力候选 → 依赖请求 → 动作/成功/停止/回滚/退出`

存在未关闭安全、合规、主权、版本、关键规格、D06现金经济或授权红线时，决策必须 `blocked`，不得由权重或综合分抵消。
