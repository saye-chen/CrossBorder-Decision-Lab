---
name: experiment-causal-assessment
description: 默认用中文执行跨境电商实验设计、因果识别、净增量评估与证据治理。用于 Amazon、TikTok Shop、Shopee、Lazada、Shopify/DTC、Walmart、eBay、Etsy、Temu、SHEIN 等平台的 A/B 或 A/B/n、分层与集群随机、Geo/holdout、Switchback、序贯试验、准实验、DiD、合成控制、RDD、IV、观察性因果、Uplift/HTE、长期效应、外部迁移、实验诊断、增量经济解释、因果证据分级、结果复现和跨域交接；当用户要求判断某项经营动作是否真正产生增量、设计或复核实验、排查实验污染/SRM/多重性/偷看、区分平台归因与因果效果、评估实验结果能否用于决策时使用。不替代品类、定价、广告、营销、达人、库存、页面或客户经营域的最终动作主权，不把相关性、预测或平台归因升级成因果结论。
---

# 实验与因果评估底座（ECAE）

跨域统一硬门禁：实验报告或 F01 handoff 交付前运行 `python3 ../governance/decision-quality/validate_domain_quality.py <report> --handoff`；缺少反事实、证据等级、成功/停止/回滚和适用范围时保持 `blocked`。

## 目标与不可突破边界

将业务问题编译为可审计的因果问题、估计对象、设计、分析和证据等级，回答“指定动作对指定总体、指标与时间窗造成了多大净增量，以及结论在什么边界内可用于什么决定”。

始终遵守：

- 分开 `识别 → 估计 → 决定`；统计显著不能弥补识别失败，经营价值不能升级证据等级。
- 先确定 estimand，再选设计和估计器。不得由现有字段或易跑模型反推问题。
- 业务域提供动作、阈值、约束和最终决定；ECAE 只提供设计、估计、诊断、等级、失效条件与动作上限。
- 未知、缺失、不适用和冲突分别编码，禁止用 `0`、空字符串或默认值代替。
- `native`、`verified_backend`、`protocol_only` 严格分档。后端不可用或未验证时失败关闭，不降级为自制近似算法。
- 不执行业务动作，不写外部系统，`external_write=false`。

先读 [章程与术语](references/charter-sovereignty-and-terminology.md)。涉及 CE4/CE5 时必须再读 [识别、Estimand 与 DAG](references/identification-estimands-and-causal-graphs.md)。

## 标准工作流

### 1. 建立决策问题与证据边界

记录业务 owner、真实可变决定、干预、比较条件、总体、时间、主要指标、护栏、最小重要差异、成本与风险。若结果不会改变真实决定，停止并返回 `not_actionable`。

判断用户当前问的是：

- 描述：发生了什么；最高通常 CE1。
- 关联：哪些变量共同变化；最高通常 CE2。
- 预测/规则归因：未来或平台规则分配了什么；最高通常 CE3。
- 因果：若执行相对于不执行会怎样；必须进入识别合同，才可能 CE4/CE5。

### 2. 注册双表示因果模型与 Estimand

CE4/CE5 候选必须同时包含：

1. 潜在结果合同：处理版本、分配单位、分析单位、目标总体、时间、结果变量、效果尺度和 estimand。
2. 因果图合同：处理前共同原因、中介、碰撞点、选择、并发干预、代理和潜在泄漏，并说明调整集为何识别目标量。

按 [识别、Estimand 与 DAG](references/identification-estimands-and-causal-graphs.md)执行。不可识别时输出 CE0–CE3 与补证方案，不强行给因果数值。

### 3. 运行 Q1–Q10 资格门与设计路由

按 [资格与设计路由](references/experiment-eligibility-and-design-routing.md)逐项判定。顺序为：个体随机 → 分层/区组随机 → 集群/Geo/Switchback → 合格自然实验 → 观察性因果 → 非因果证据。

关键识别、处理定义、时间顺序、数据血缘、干扰、停止规则或主要指标合同失败时，阻断 CE4/CE5。不得用“结果符合预期”抵消失败。

### 4. 冻结协议、指标、样本与分析计划

协议至少冻结：主要/次要/护栏指标、假设家族、样本单位、分配比例、随机化与种子治理、MDE/精度目标、停止规则、序贯范式、缺失/流失/不依从、异常排除、估计器、标准误、多重性、敏感性和偏差处理。

读 [指标、样本与分析合同](references/metrics-sample-and-analysis-contract.md)；序贯、多重性或偏差场景再读 [序贯、多重性与偏差](references/sequential-multiplicity-and-deviation.md)。

### 5. 选择能力档并执行

| 方法族 | 能力档 | 结论上限（所有 Gate 通过时） |
|---|---|---|
| 两组/多组随机、分层、固定样本、CUPED、2×2 DiD | `native_executable` | CE4/CE5（依方法和诊断） |
| 集群、Switchback、错峰 DiD、SCM/SDID、RDD、IV、AIPW/TMLE/DML、HTE | `verified_backend` | CE4/CE5（须后端校验与 parity） |
| 网络干扰、动态处理、中介、Bandit 推断 | `protocol_only` | 外部合格分析后至多 CE4 |
| Proximal causal | `research_only` | 不进入常规决定 |

可执行脚本只接收 JSON，成功与错误都返回结构化 JSON。运行前检查 `backends/backend-registry.json`；任何 `unavailable`、版本不匹配、parity 过期或数值异常均失败关闭。

### 6. 诊断、降级与反证

随机实验至少检查分配实现、SRM、曝光/交叉污染、指标成熟、缺失/流失、不依从、异常、干扰和协议偏差。准实验至少检查识别假设、预趋势/操纵/first stage/供体质量、placebo、negative control、替代规格、overlap、敏感性和支持域。

寻找足以推翻结论的证据，而非只寻找显著性。宽区间不是“无效”，而是精度不足。事后子组、事后换窗、未登记停止、坏控制或选择性报告必须显式降级。

### 7. 生成 CE0–CE5、经济解释与交接

因果等级语义：

- CE0 `insufficient`：数据或设计不合格。
- CE1 `descriptive`：仅观察事实。
- CE2 `associational`：统计关联。
- CE3 `predictive_or_attributed`：预测或规则归因，无反事实净增量。
- CE4 `causal_bounded`：指定范围和假设下的因果效应。
- CE5 `causal_decision_grade`：识别、诊断、精度、稳健性与经济解释均通过，可供指定决定使用。

CE5 仍不自动等于最终业务动作。经济换算使用调用域提供且带版本/适用期的参数，必须和因果资格分开。读 [经济、等级与交接](references/economics-claim-grading-and-handoff.md)。

### 8. 固化复现包与失效条件

保存协议、数据快照哈希、代码哈希、环境、参数、随机种子、结果、日志、偏差、后端证明和依赖。生成 invalidation/recompute triggers；输入、口径、数据成熟度、代码、后端或关键假设变化时，不允许旧结论静默继续消费。

按 [血缘、复现与重放](references/data-lineage-reproducibility-and-replay.md)执行。

## 输出协议

默认交付以下对象，而不是只给一段结论：

1. 决策问题与主权边界。
2. estimand 与双表示识别合同。
3. Q1–Q10、设计路由和能力档。
4. 协议、指标、样本、停止和多重性合同。
5. 估计值、区间、诊断、敏感性、偏差与反证。
6. CE 等级、claim ceiling、允许/禁止措辞。
7. 增量经济区间、动作上限和业务 owner 待决项。
8. 适用范围、失效/重算触发器、复现包与 handoff。

正式报告读 [专业报告交付](references/output-protocols/professional-report-delivery.md)。输出不得使用“证明”“一定”“普遍有效”等超出支持域的措辞。

## 专项路由

- 集群、Geo、Switchback、spillover：读 [集群、Switchback 与干扰](references/randomized-cluster-switchback-and-interference.md)。
- DiD、SCM/SDID、RDD、IV、观察性因果：读 [准实验与观察性因果](references/quasi-experiments-and-observational-causality.md)。
- HTE/Uplift、长期效应、Surrogate、跨环境迁移：读 [异质性、长期与迁移](references/heterogeneity-uplift-long-term-and-transport.md)。
- D01—D13 交接、双轨、差异、签收、失效或回滚：读 [消费者迁移与验收](references/consumer-migration-and-acceptance.md)。
- 执行 L4 生产只读双轨、冻结快照、差异处置、回滚演练和生产 owner 待签包：读 [消费者生产验收操作手册](references/consumer-production-acceptance-operator-runbook.md)。
- D01—D13 消费者侧回执通过 `scripts/domain_consumer_adapter.py` 与各域 `integrations/experiment-causal-assessment/adapter.json` 执行；共享内核不共享业务主权、用途门槛、payload 或验收哈希。
- 专业深度、方法卡、验证证据与发布边界：读 [专业深度治理](references/professional-depth-governance.md)。
- 选择、锁定、探测或验证科学后端：读 [科学后端选择与 parity 治理](references/scientific-backend-selection-and-parity.md)。
- 执行 native 方法前按需读方法卡：[随机 ITT](references/method-cards/randomized-itt.md)、[样本/MDE/精度](references/method-cards/sample-size-mde-precision.md)、[CUPED](references/method-cards/cuped-adjustment.md)、[2×2 DiD](references/method-cards/did-2x2.md)、[多重性/护栏/序贯](references/method-cards/multiplicity-guardrails-sequential.md)。

## 实现与发布治理

- 权威蓝图：`../governance/f01-experiment-causal-assessment-blueprint-review.md`。
- 需求追踪：`../governance/f01-requirements-traceability.json`。
- 当前实现状态：`../governance/f01-implementation-manifest.json`。
- 共享底座注册：`../governance/foundation-capability-registry.json`。
- 科学后端先核对 `backends/backend-lock.json` 与 registry；`scripts/probe_backend_environment.py` 只探测、不安装。只有符合 `schemas/backend-proof.schema.json` 的未过期 proof 才能把状态改为 `verified`。
- 开发完成不等于发布。L1–L3 必须通过权威门；L3 需要解析/设计真值、独立成熟软件 parity、公开一手方法来源和 owner 授权技术审查。没有完整资格证据的高级后端继续失败关闭，不进入受控试点可执行面。
- 即使 L1–L3 通过，成熟度最高为 `controlled_pilot`。L4 真实授权数据重放、生产消费者接受、高级后端外部资格和独立非实现者复核保持独立开放。

## 失败处理

当输入不完整、方法不合格或后端不可用时：

1. 返回明确错误码、失败 Gate、受影响 estimand 和最高允许 CE；
2. 不生成伪精确估计、不把空值变零、不以相关方法替代因果方法；
3. 给出最小补证、重设计或外部合格分析路径；
4. 保留已确认事实和非因果结果，但限制措辞与消费动作。
