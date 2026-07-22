# CAPM 专业报告交付

## 目录

1. 报告类型
2. 最低合同
3. 连续报告
4. 深度与反自证
5. 专属决策内核

## 报告类型

- Decision Card：单达人、单联盟伙伴、单次报价/权利/异常。
- Decision Memo：合作模型、佣金、谈判、组合调整或联盟计划。
- Creator/Affiliate Diligence：多平台、多国家、组合、重大现金或长期权利。
- Incident & Recovery：欺诈、无权使用、未发布、拒付、泄露、账号接管、召回或突然退出。
- Progressive Decision：新报价、后台证据、退款成熟、合同/权利变化和连续追问。

## 最低合同

每份完整报告包含：

1. 决策档位、理由和动作上限；
2. canonical对象、版本、平台、国家、币种、税、时区、生命周期和as_of_time；
3. Q0-Q3输入质量、S/C证据、反证、冲突和替代解释；
4. G1A/G1B/G2-G6逐动作阻断、允许、恢复和owner；
5. 候选、不行动、walk-away和未选理由；
6. 成熟贡献、现金时序、保本区间、敏感性和翻转阈值；
7. 权利用途清单及到期/撤回；
8. 商务结构、金额、交付、修改、验收、结算和责任；
9. 验证/实验的假设、观察/成熟窗、指标、护栏；
10. 负责人、日期、审批、成功、停止、回滚、升级和退出；
11. 跨域消息、运行时、证据/计算ID、状态、用途和接收确认；
12. 剩余暴露、不行动成本、血缘、下次观察和结果回填。

字段不可用写 `not_applicable/unavailable/inconclusive`、原因、动作上限和补证路径，不得编造。Card可以短，但不能把未研究内容写成PASS。

## 连续报告

必须输出 `report_id/parent_report_id/object_version/changed_fields/new_evidence_ids/affected_claims/affected_calculations/preserved_constraints/superseded_actions/current_actions/next_recompute_trigger`。新对象不能沿用旧证据；证据撤回必须反向失效衍生claim和动作。

Incident报告另含事件时间线、影响对象、证据保全、紧急动作、顾客/付款/权利暴露、责任/追索、恢复、对外沟通owner和防再发。

## 深度与反自证

计算给输入、公式、单位、舍入、脚本/Schema版本和hash。末次点击、折扣码或播放不得称增量。动作禁止“继续观察/优化达人”这类无对象、幅度和期限表达。

P0覆盖总分。报告生成器、评分器和Golden不得共享预期答案文本。执行字段删除、证据复制、对象置换、单位/币种污染、过期规则、虚假运行时、部分失败和因果标签篡改测试。

人工盲审记录 reviewer_role、利益冲突、独立发现、分歧、裁决和时间；没有时标记 `self_reviewed_only`。

## professional-report-delivery 专属决策内核

机制：报告是可执行决策合同的可读投影，不是另一个事实源。所有关键句回链claim/evidence/calculation/action ID。

判定：对象可审计、计算可复算、证据可追、反事实诚实、动作可执行、主权不越界六门全部通过；P0任一失败即FAIL。

反事实：删除对象、反证、成熟利润、权利、停止、回滚或主权任一模块必须失败；把播放改销量、归因改增量必须失败。

失效模式：模板填满但证据空、长报告替代深度、Golden自证、旧动作未supersede、事故报告泄露PII、报告状态冒充production。

动作：退回补证、降级、重算、拆分主权、阻断发布或生成恢复报告。

机器入口：`scripts/test_capm.py` 与仓库 `scripts/evaluate_report_quality.py`；五类 Golden 必须逐份以 `full` profile 达到100分，删除关键章节必须FAIL。
