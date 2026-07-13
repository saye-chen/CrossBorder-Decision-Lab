# CLV 与回收期

`CM_t = Revenue - COGS - Fulfillment - PlatformFee - PaymentFee - ReturnLoss - ServiceCost - Incentive`。

`CLV_H = Σ E[CM_t × Survival_t]/(1+r)^t - CAC - ExpectedFutureCost`。明确窗口、折现率、币种、CAC、退款、权益、客服和固定成本口径。输出 P10/P50/P90 或区间，不强行切分区间高度重叠的客户。

非合约型可在数据/假设满足时使用 BG/NBD + Gamma-Gamma；频次与金额相关、强促销或结构突变时使用更稳健的分层/生存/模拟方法。合约型用生存或多状态模型处理升降级、暂停和恢复。无法回测时降级为情景 CLV，不声称个体预测。

`LTV/CAC=IncrementalCLV/IncrementalCAC`。回收期是折现累计增量贡献首次覆盖 CAC 的时点。高比率但超过现金承受窗口仍不可执行。
