# 准实验与观察性因果

## 统一要求

所有准实验先写 target trial 或制度反事实：eligibility、treatment strategies、assignment analogue、time zero、follow-up、outcome、estimand 和 analysis。记录制度如何产生可比反事实，并列出可能同时变化的机制。模型不能替代制度知识。

## 2×2 与错峰 DiD

2×2 native 只估计明确的 ATT 对比，并要求 treatment/control、pre/post、无 anticipation、处理版本稳定和共同冲击说明。单一 pre-period 无法经验验证平行趋势，结果上限 CE4 且必须诚实标注。

错峰采用 group-time ATT，以 never-treated 或 not-yet-treated 为合格对照，报告 event-time 动态效应和同时区间。禁止用朴素 TWFE 在异质处理时点/效果下输出 CE4。预趋势检验低功效不等于平行趋势成立；结合制度、placebo、composition 和 functional-form sensitivity。

## Synthetic Control / SDID

在看 post outcome 前冻结 donor pool；排除处理污染、结构断裂、口径不一致和受相同冲击单位。报告 unit/time weights、有效 donor 数、权重集中、pre-RMSPE、post gap、in-space/time placebo、leave-one-out 和不确定性。漂亮拟合不是识别；单 donor 支配、短 pre、placebo 不异常或 donor 污染时最高 CE3。

## RDD

冻结 running variable、cutoff、sharp/fuzzy、带宽规则、核、局部多项式阶数和局部 estimand。经验证后端需做偏差修正区间、密度操纵、协变量连续、带宽/阶数敏感、donut 和假 cutoff。结论只适用于 cutoff 附近，不向全总体外推。

## IV

分别报告 reduced form/ITT、first stage、2SLS/LATE、弱工具诊断和区间。排除限制与单调性依赖机制论证，不能靠统计检验完全验证。LATE 仅针对 compliers；不得重命名为 ATE。弱工具或直接路径未解决时最高 CE3。

## 观察性 AIPW/TMLE/DML

必须有 DAG 调整集、overlap/positivity、样本分割或 cross-fitting、预处理变量、nuisance learner 约束和双重稳健/orthogonal score。报告 propensity 分布、极端权重、trimming 对 estimand 的改变、balance、有效样本、替代模型、negative control/placebo 和未测混杂敏感性。

“机器学习控制很多变量”不识别因果；DML 处理高维 nuisance 偏差，不消除未测混杂。无 cross-fit、overlap 或敏感性时不得达到 CE4。

## 能力档

2×2 DiD 可 native；错峰 DiD、SCM/SDID、RDD、IV、AIPW/TMLE/DML 仅 `verified_backend`。后端不合格时输出协议、输入检查和 CE ceiling，不输出替代估计。

## WP-07 冻结执行矩阵

| 方法 | 后端 ID | 当前候选 | 执行前必须成立 | 当前发布状态 |
|---|---|---|---|---|
| 错峰 DiD | `staggered_did` | `did 2.5.1` | group-time ATT、never/not-yet control、处理时点冻结、anticipation、同时带 | runtime unavailable |
| Classic SCM | `synthetic_control` | `Synth 1.1-10` | 单 treated unit、冻结且无污染 donor、in-space/time placebo、LOO、pre-fit | runtime unavailable |
| SDID | `synthetic_did` | `synthdid 0.0.9` pinned commit | common start、unit/time weights、冻结 variance method；beta 状态显式保留 | runtime unavailable |
| RDD | `rdd_local` | `rdrobust 2.0.0` | cutoff/running variable 冻结、local linear、数据带宽、RBC、完整外部诊断 | runtime unavailable |
| IV | `weak_iv` | `ivmodels 0.10.0` | LATE/CACE、reduced form/first stage、AR/CLR、排除/独立/单调性机制 | runtime unavailable |
| AIPW | `observational_aipw` | `AIPW 0.6.9.3` | target trial、DAG、全 nuisance OOF、overlap、IF、negative control/敏感性 | runtime unavailable |
| DML | `observational_dml` | `DoubleML 0.11.3` | orthogonal score、全 nuisance OOF、冻结 folds/learners/seed、overlap | runtime unavailable |
| TMLE | `observational_tmle` | 无合格绑定 | 结果和 propensity nuisance 都必须 OOF，targeting 与 IF 可审计 | unavailable |

这里的 `runtime unavailable` 表示候选、合同和适配器存在，但没有持久运行时、独立 parity、完整模拟和专家 proof；不得解释为“工具已经可用于正式因果结论”。`tmle 2.1.1` 因所审 API 只对 outcome nuisance 提供交叉拟合而被拒绝绑定，不能由 AIPW 或 DML 静默代替。
