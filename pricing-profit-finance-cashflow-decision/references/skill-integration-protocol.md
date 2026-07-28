# PPFC 跨域集成协议

规范交接键为 `subject_id × subject_version × country × platform × currency × tax_basis × business_time × parameter_snapshot × model_version`。输入和输出必须携带生产域、接收域、证据/计算 ID、状态、允许用途、禁止用途、有效期和血缘。

PPFC 最终确认价格架构、单位经济、贡献利润、通用保本指标、财务边界和现金承受力；不接管 CIDM 的资本决策、LIFD 的路线库存、AAMO 的预算出价、PLCO 的页面动作、CAPM 的合作条款、MBCM 的活动动作、CIG 的客户事实或其他域的专业主权。

业务域向 PPFC 提交事实或候选动作；PPFC 只返回版本化的 `proposed/validated/blocked/inconclusive` 财务结果。接收域必须按自身模型接受、拒绝或请求重算，不得把 PPFC 结论静默升级为执行。PPFC 也不得自签接收域的业务接受。

允许用途限于登记对象的财务判断、情景比较和重算请求。禁止自动修改价格、预算、订单、库存、广告、页面、合同或账户。部分失败时保留相互独立且已验证的结果，污染部分进入异常报告；身份、币税、单位、时间、版本或守恒冲突时整体相关结论阻断。冲突按主权、证据等级、时效、确定性红线和可逆性裁决，不投票、不平均。

字段级矩阵、九域方向、异常树和部分失败处理的权威细节见[跨域合同与异常树](cross-domain-contract-and-exception-tree.md)；迁移、双轨等价、消费者接受、旧实现退役和整包回滚见[迁移兼容与回滚](migration-compatibility-and-rollback.md)。
