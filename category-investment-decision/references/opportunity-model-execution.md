# OSL-v1确定性模型执行协议

八类模型统一由`scripts/opportunity_signal_engine.py`执行。输入必须且只能包含`signal_type`、`data`和`calibration`；模型不内置跨国家、平台或品类的永久阈值。

| 信号模型 | 主要确定性计算 | Fail-closed条件 |
|---|---|---|
| `NEW_PRODUCT_BREAKOUT` | 周持续率、促销污染、父子体身份 | 无序列或身份不明为`inconclusive`；伪新品/高污染拒绝 |
| `DISTRIBUTED_KEYWORD_DEMAND` | 趋势增长、购买集中度 | 品牌词或低购买意图拒绝；非0-1刻度报错 |
| `MARKET_ENTRY_STRUCTURE` | CR3、HHI、新品存活 | 集中度或存活缺失为`inconclusive`；无楔子拒绝 |
| `ECONOMIC_FEASIBILITY` | 基准/压力/乐观完整贡献利润 | 三场景或成本桶不全为`blocked` |
| `VALIDATED_SUPPLY_GAP` | 有效供给、需求减有效供给 | 需求/供给缺失为`inconclusive`；禁止空白为`blocked` |
| `RESOLVABLE_PRODUCT_GAP` | 去重事件、严重度、来源家族、可控性 | 无可追溯VOC为`inconclusive`；样本计数不外推市场占比 |
| `TRAFFIC_REPLICABILITY` | 多期非品牌自然流量 | 单期或同源证据为`inconclusive` |
| `SEASONAL_PREPOSITIONING_WINDOW` | 最晚下单日 | 少于校准年数为`inconclusive`；无退出路径为`blocked` |

模型输出只形成机会信号，不进入平行评分器。五类组合剧本由`opportunity-combination-playbooks.json`治理，必要条件缺失不通过，否决条件覆盖全部支持证据，同源信号只保留一条。

17种战术的实现层级以`opportunity-tactic-capability-matrix.json`为准；`configured`、跨域`routed`和共享子模式不得写成独立模型完成。需要验证完整受控链时运行`opportunity_decision_pipeline.py`，链路固定为原始证据→`evidence_adapter.py`→主模型→独立Oracle→信号合同→七维评分→组合剧本→Rapid Decision Card。任一Adapter错误、Oracle不一致、红线或veto均失败关闭。
