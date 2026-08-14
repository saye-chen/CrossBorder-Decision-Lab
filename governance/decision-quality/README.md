# Cross-domain decision quality contract

所有业务域和联合报告必须同时满足本合同与本域专用校验器。它只定义不可删减的共同决策闭环，不替代各域的专业字段、计算和主权。

## Universal decision chain

```text
object/scope → current conclusion → evidence → counter-evidence → assumptions
→ gates/constraints → analysis/calculation → action → success guardrail
→ stop/pause/rollback → unknowns and recomputation trigger
```

缺少任一环节时只能输出 `blocked`、`proposed` 或 `inconclusive`，不能输出可执行、放量、生产就绪或投资批准。

## Domain handoff minimum

跨域交接必须额外包含：`domain`、`packet_id`、`object`、`version`、`status`、`evidence_ids`、`calculation_ids`、`allowed_uses`、`forbidden_uses`、`owner`、`valid_until` 和 `recompute_trigger`。

联合报告不得把多个域的局部 `proposed` 拼成全局 `validated`；任何参与域 blocked、过期或缺字段，联合结论必须继承最弱状态。
