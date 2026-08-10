# D01—D13 消费者生产验收操作手册

## 1. 目标与边界

本手册只用于 L4：把同一冻结生产快照并行送入 legacy reader 与 F01 consumer adapter，生成可重放差异、回滚证据和消费者 owner 待签记录。全程使用 `read_only_shadow_dual_run`：允许读取、计算、比较和留证，不允许调价、补货、投放、发布、付款、签约、客户触达或任何外部写入。

生产双轨是数据回流的一部分，但回流对象是带授权、时间、范围、血缘和哈希的数据快照及结果证据，不是无边界的数据同步。旧轨和新轨必须消费同一个冻结快照；任何一侧换窗、补数、改口径或改参数都必须重开 run。

## 2. 总控计划

权威计划为 `integrations/consumer-production-acceptance-plan.json`。第一批执行 D06、D07、D10，验证专用财务、库存和达人消费者逻辑；第二批并行执行其余十域。

截至 `2026-08-10`，Miles Chen 已完成 D01—D13 的受控试点条件接受，并登记为生产消费者负责人。`scripts/build_consumer_preflight.py` 已用于生成并重放 13 域非生产预检；预检只关闭模拟技术风险，不填充任何 `production_*` 引用，也不创建生产结果签收。

每个域开始前补齐：

1. `owner_identity`：真实业务负责人；角色必须等于 `Dxx_consumer_owner`。
2. `production_snapshot_ref`：受控存储中的只读快照或 manifest，不能把密钥、令牌或不必要的个人数据写入仓库。
3. 旧轨代码及环境版本、F01 commit、adapter hash、consumer contract hash。
4. 在看结果前冻结的数值容差和七类案例选择规则。

未补齐 owner 和生产快照时，状态保持 `waiting_owner_and_production_snapshot`，不得用 fixture 冒充生产证据。

## 3. 快照与数据回流

快照至少登记：source ref、授权 owner、授权范围、snapshot hash、captured at、maximum event time、业务时区、去重规则、迟到/回填政策和质量断言。原始敏感数据可留在受控系统；仓库只保存安全引用、哈希、最小结果和日志。

执行拓扑固定为：

```text
authorized production snapshot (read only)
  ├── legacy reader, writes disabled ──> raw legacy result + hash
  └── F01 consumer adapter, writes disabled ──> raw F01 result + hash
                                          ↓
                     claim/grade/scope/numeric/action comparison
                                          ↓
                         owner disposition and rollback drill
```

禁止让 legacy 和 F01 读取不同时间窗，禁止一侧使用回填后数据、另一侧使用回填前数据，禁止只保留汇总结论而丢弃原始结果哈希。

## 4. 七类强制案例

每域至少覆盖 `normal`、`near_decision_threshold`、`negative_or_harm`、`expired`、`invalidation_triggered`、`scope_mismatch` 和 `missing_required_field`。每个 case 都要保存 snapshot hash、两轨原始结果引用、两轨结果对象和差异处置状态。

使用 `schemas/consumer-production-run.schema.json` 组装 run package，再由 `scripts/evaluate_consumer_production_run.py` 评估。只有真实 `production_dual_run`、七类案例齐全、无 blocking 差异、expected restriction 已由 owner 明确知情、回滚演练通过时，才输出 `eligible_for_owner_acceptance=true`。

在接入真实快照前，可运行 `scripts/build_consumer_preflight.py` 生成 D01—D13 共 91 个脱敏模拟案例。每个模拟包绑定当前 F01 源码树哈希、消费者合同哈希、适配器哈希和旧轨资产哈希；`f01_commit_hash=null` 明确表示当前证据不是可发布的生产 commit。模拟结果必须保持 `fixture_non_production`、`eligible_for_owner_acceptance=false` 和 `external_write=false`。

## 5. 差异与处置

差异分为 claim、grade、scope、numeric 和 action：

- `equivalent`：处置为 `not_required`。
- `expected_restriction`：处置为 `owner_acknowledged_restriction`。
- 任何 blocking：保持 `pending` 或 `rejected`，修复后必须用新 run 重跑，不能在旧结果上手工改成通过。

旧轨 causal/incremental 语义、F01 新增动作、范围变化、空值状态变化或数值超过预注册容差均阻断签收。

## 6. 回滚演练

生产 run 必须触发 expiry、contract change、data correction、treatment change 或 scope change 中至少一个，并证明：因果措辞关闭、增量状态为 `unknown`、高风险动作被阻断、recompute request 已创建、没有业务写入。回滚失败时不得进入 owner review。

## 7. Owner 签收与关门

通过双轨的 run 只获得“可交负责人审阅”资格，不会自动接受。负责人使用 `consumer-acceptance.schema.json` 选择 accepted、conditionally accepted 或 rejected，并绑定精确 migration、contract hash、production run、差异处置、回滚证据、accepted uses、条件、有效期和身份。

ECAE 开发者不得代签。合同、schema、claim、适用范围、adapter、关键依赖或生产输入定义变化后必须重跑并重新签收。

13 域全部具备 production run、差异处置、rollback evidence 和真实 production acceptance 后，更新总控计划与 `integrations/consumer-migration.json`；`l4_production_acceptance_complete` 只能由引用自动推导，不能手工提前改成 true。
