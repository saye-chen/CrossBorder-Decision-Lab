# REALITY_RECOVERY恢复协议

证据进入`stale`或`invalidated`后，不创建新的SignalStatus，而是启动`REALITY_RECOVERY`。执行入口为`scripts/reality_recovery_engine.py`。

## 主链

```text
证据失效
→ 血缘闭包定位派生信号和全部决策消费者
→ 创建单一根节点恢复批次
→ 冻结受影响的planned/approved/executing动作
→ R0-R4硬分层
→ 逐消费者补证和独立重算
→ 重过五道门槛、红线和生命周期上限
→ 生成新的Current Effective Decision或升级人工接管
→ 全部消费者解决后关闭根批次
```

R0覆盖安全、违法、召回、卫生和账号级红线；R1覆盖即将发生的不可逆动作或持续扩大损失；R2由经过治理的净风险资本阈值触发；R3覆盖可能改变决策档位或高传播半径；其他进入R4。R等级优先于同层分数。

净风险资本按资产/合同ID去重。同一资产不得同时把已付款现金和库存成本重复计入。自动化只冻结或告警，不自动下线、召回、取消付款或终止合同。

## 关闭硬门

- 新证据已验证，或明确不可恢复并进入退出、召回或人工接管；
- 全部消费者重算并重过门槛；
- 每个对象只有一个新的Current Effective Decision；
- 旧动作已冻结、撤销或明确保留；
- 全部消费者已收到新状态；
- 根因已进入contract、mutation或事故测试；
- 损失、责任人和防复发动作已登记。

任何消费者仍为`frozen`、`recalculating`或`partially_recovered`时，根批次不得关闭。
