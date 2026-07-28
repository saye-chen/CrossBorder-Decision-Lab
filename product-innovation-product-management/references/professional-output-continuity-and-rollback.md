# 专业输出、连续决策与回滚

## 不可变决策链

每次追问先读取当前状态，再将输入分类为 clarification、evidence_update、product_fact_change、scope_change、scenario_override、validation_result、cross_domain_accept、cross_domain_reject、action_update、incident_or_recall、rollback 或 retire。历史记录只追加；同一链恰好一个 current。写入必须匹配 `expected_revision` 和下一事件序号，重复幂等键返回 no-op，乱序或并发冲突失败关闭。

重算事件创建新的决策版本并 supersede 旧 current。clarification、跨域接受和动作状态更新不得改变输入哈希。迟到证据保留 event time 与 recorded time，创建 rebase/new version，不回写旧决策时点。

## 四轴状态

- 产品生命周期：PLC0—PLC8。
- 决策：draft/proposed/validated/rejected/blocked/inconclusive/superseded/retired。
- 接受：not_requested/pending/accepted/partially_accepted/rejected/expired。
- 动作：proposed/approved/executing/completed/stopped/superseded/failed。

四轴不得相互推断。PLC8 不得原地重新激活；需要新对象版本复审。

## 九类输出

统一报告信封承载对象、版本、双时态、唯一结论、历史引用、证据/反证/缺失、计算、候选、主权依赖、动作、成功、停止、回滚、退出、血缘和成熟度。九类报告各自保留专属内容；见 `professional-report.schema.json` 和 `validate_professional_report.py`。

## 影响闭包

依赖图节点必须带 evidence/claim/calculation/specification/report/action/acceptance 类型和对象版本。变化沿有向边传播并输出 changed、expired、recomputed、reaccepted、preserved、blocked。循环、孤儿、未知节点或跨版本边阻断。

## 回滚

回滚创建新 current，不删除或重新激活旧版本。已执行实物或外部动作不能被信息状态“撤销”，必须登记不可逆项、剩余暴露、补偿/隔离/通知/复验动作、负责人、期限和恢复条件。始终保持 `external_write=false`。
