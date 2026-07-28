# PPFC 数据合同与自动化

权威对象由 `object_id`、版本、国家、平台、商业模式、生命周期、币种、税口径、数量基准、`as_of_time`、系统记录时间、参数快照和模型版本唯一确定。缺失、零值、未知、不适用、过期和冲突必须使用不同状态，不得互相转换。

输入区分 observed、authorized、derived、inferred 和 causal。金额必须带币种与税口径；费率必须带基数、范围、有效期、来源、优先级和舍入规则；物流必须逐段记录实际重、体积重、计费重、档位、最低价和附加费；订单、退款、成本、库存和现金事件必须有唯一 ID。

自动化在计算前校验有限值、Decimal 权威值、单位、币税、时间、版本、重复身份、证据指纹、费率基数和守恒。动态规则按已批准、有效、最具体原则解析；同级冲突返回 `BLOCKED_AMBIGUOUS_RULE`，缺失返回 `MISSING_PARAMETER`，过期返回 `EXPIRED_PARAMETER`。任何异常不得填零或静默沿用旧值。

所有计算保存输入哈希、输出哈希、参数快照和运行时版本。重跑使用幂等键并生成新版本，不覆盖历史；连续决策保持唯一 current，参数变化只重算依赖闭包。外部写入始终关闭，除非未来另有明确授权合同。

完整对象与状态见[对象生命周期](object-lifecycle-and-state.md)，证据、数据质量和账本见[输入、证据与对账](input-evidence-and-reconciliation.md)，动态规则见[动态参数与物流](dynamic-parameter-and-freight-rules.md)。
