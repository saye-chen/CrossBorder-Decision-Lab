# 数据合同与自动化

## 决策合同

必填`decision_id/decision_version/parent_decision_id/question_type/intent/primary_object/object_id/scope/lifecycle_stage/business_objective/non_objectives/authority/constraints/as_of_time/evidence_cutoff/decision_deadline/reversibility`。

## 字段规则

所有金额含币种、币税和时间；数量含对象单位；比率在合法范围；时区明确；未知`unknown`、不适用`not_applicable`、不可用`unavailable`。禁止将缺失填零值、0、False或行业均值。非有限值、负容量/数量、无效折扣、混币混窗必须报错。

## 血缘

记录claim/evidence/calculation/model/input/output/decision/execution/outcome ID与SHA-256。计划、批准、执行、曝光和成熟结果分开。滚动窗口、规则、价格、库存或参与包变化触发影响闭包。

## 连续状态

保存`changed_fields/new_evidence_ids/affected_claims/affected_calculations/preserved_constraints/superseded_actions/current_actions/next_recompute_trigger`。父状态哈希不匹配时阻断继承；换对象必须新建证据账。

## 权限与外部写入

读取用户提供或授权数据，不扩展用途。市场级细分不得转个人名单。发布、改价、投放、签约、触达、补货、删内容和公开响应需要用户明确授权及主权责任人。

## 自动化边界

自动化可校验合同、计算、生成报告和提出请求；不得自动使`proposed`生效、自动放宽Gate、触发外部不可逆动作或生成L4声明。重复调用必须幂等。

## 临时数据

真实客户、财务、合同和平台导出不得写入Skill目录。复杂任务使用受控临时目录和具名任务所有者；仅清理可验证属于本任务的文件。
