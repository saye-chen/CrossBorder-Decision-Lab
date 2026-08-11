# 经济解释、证据等级与交接

## 两条独立轴

`causal_eligibility` 回答是否识别及可信程度；`economic_value` 回答效应在成本、利润、风险和时间下是否值得。经济收益再高也不能修复 CE0–CE3；因果可信也可能经济上不值得。

## 增量经济合同

换算参数由 D06/F02 或调用域提供：贡献利润、退款/取消、平台费、履约、广告/达人/促销、固定实施成本、持续成本、税汇率、现金回收、容量和机会成本。每个参数带来源、版本、币种、有效期、情景和不确定区间。

以因果效应区间传播经济区间，至少提供 bear/base/bull 或概率分布、保本阈值、下行风险和敏感度。不能将相关收入、GMV 或平台归因直接称为 incremental profit。

## CE 等级规则

等级取多项最小支持上限：问题类型、识别合同、能力档、协议完整、数据血缘、诊断、偏差、敏感性、精度、复现、后端验证和经济参数资格。任何不可补偿 Gate 失败阻断 CE4/CE5。

CE5 额外需要：设计/识别通过；主要与护栏结论可解释；精度足以区分决策阈值；关键诊断和稳健性通过；复现包完整；经济解释使用合格参数；结论仅绑定指定决定。若因果成立但精度/经济未达到决定级，通常 CE4。

## 结果姿态与动作上限

允许姿态：`adopt_candidate`、`continue_evidence`、`redesign`、`stop_for_harm`、`no_action`、`inconclusive`。它们是 ECAE 的证据建议，不是最终业务动作。输出明确 `allowed_actions`、`prohibited_actions` 和 `business_owner_decision_required=true`。

## Handoff 最小字段

- `handoff_id`、schema/version、producer、consumer、created_at；
- causal question、estimand、design、analysis version；
- estimate、effect scale、interval、sample/support；
- CE grade、claim ceiling、allowed/prohibited wording；
- diagnostics、deviations、sensitivity、limitations；
- economic interval 与参数版本；
- population/platform/country/time applicability；
- data/code/environment/result hashes；
- invalidation/recompute triggers、expires_at；
- owner、review status、external_write=false。

消费者只能在 claim ceiling 内使用，不得去掉限制、替换总体或将 CE4/CE5 跨环境继承。触发失效条件后先标 `stale/invalidated`，重算前不得用于新决定。
