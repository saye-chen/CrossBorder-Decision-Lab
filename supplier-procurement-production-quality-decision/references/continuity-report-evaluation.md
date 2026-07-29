# 连续决策、报告与评测

连续追问先分类 `Addendum/Revision/Recalculation/Rebase/New Decision Object`，重建 Current Decision State，标记 changed/preserved/invalidated/newly_required，只重算影响范围。已承诺、生产中、已发运或不可逆动作进入现实恢复。

完整报告含执行摘要、对象、主权、数据质量、硬门、候选/不行动、专业模型、反证/尾部、决定/限制、跨域、执行控制、结果回填、三类 Ledger 和外部责任。报告数字必须绑定计算哈希，禁止关键词填充和伪精确。

评测至少 160 个非重复 case：六类决定36、计算36、联动28、多轮24、复杂20、极限16。每个关键守卫有通过和独立失败，Golden oracle 不得由生产函数生成；catalog 检查近重复、覆盖轴、mutation、具体失败和部分结果保留。

## Current Decision State

状态至少保存：

- object_id、current_version 和 current_effective_decision；
- 历史决定及 superseded/revoked 状态；
- open_gates、active_actions 和 reality recovery；
- accepted/invalidated 字段与 recompute scope；
- 证据、参数、消费者响应和结果观察窗；
- 最近 delta 的 changed/preserved/invalidated/newly_required。

## Delta 分类

- Addendum：只补证据或说明，不改变决定语义。
- Revision：修改决定字段，重算其依赖。
- Recalculation：输入或参数改变，决定类型不变。
- Rebase：基准对象、规格、BOM、时点或消费者合同改变。
- New Decision Object：对象身份变化，不得继承旧对象决定。

每轮先判断 delta 类型，再做 change-impact。不得因为用户连续追问而重新从空白开始，也不得因为措辞相似静默沿用旧值。

## 状态传播

若字段 A 变化且 impact map 为 `A → B,C`：

- A 标记 changed；
- B/C 标记 invalidated 并重算；
- 无依赖字段 preserved；
- 新门标记 newly_required；
- 旧决定进入 history，current 只能保留一个。

消费者拒绝字段时，字段进入 invalidated；部分接受仅保留明确 accepted_fields。受影响下游不得继续使用旧哈希。

## 现实恢复

`committed/in_progress/irreversible/shipped` 动作受变更影响时必须进入 `REALITY_RECOVERY`：

1. 遏制新增暴露；
2. 定位已发生动作、数量、批次和责任；
3. 区分沉没、可回收和继续暴露；
4. 回滚尚可逆部分；
5. 为不可逆部分建立恢复方案；
6. 由 owner 重新批准；
7. 回填恢复结果。

不得把已发运批次从状态中删除后声称风险消失。

## 评测 oracle

- Golden 期望不得在运行时由生产函数生成；
- 金额、数量、概率和状态使用手算或第二实现；
- 失败断言具体 guard、状态、受阻动作和 preserved 结果；
- 源码 mutation 应真正改变守卫代码并由测试杀死；
- 复杂场景至少两个故障，极限场景至少三个；
- 多轮 case 必须真实执行四次迁移并检查 history；
- 报告验证语义、计算重放和主权，不只验证字段存在。

## L1—L4 边界

- L1：结构与入口；
- L2：Schema、合同、确定性和 fail closed；
- L3：专业机制、Golden、对抗、联动、多轮和复杂覆盖；
- L4：授权真实回放、真实结果、长期校准及非实现者复核。

合成数据、测试全绿、mutation 全杀或报告 100 分都不能关闭 L4。
