# S05 Offer 工程
专属机制：“资格—兑换—增量—非增量成本—蚕食—拉前—滥用”守恒。
- 计算：增量贡献扣除全部兑换、拉前、蚕食、服务和固定成本。
- 证据/反事实：比较无 Offer、弱 Offer、目标人群与全量 Offer。
- 动作：限定对象、额度、频次、预算、成功线和停止线。
- 失败断言：兑换率、GMV 或归因订单不能替代成熟增量贡献。
- 停止/回滚：负边际、欺诈或渠道冲突越界即停券并恢复基准 Offer。
- 估计工具：先运行 `offer_response_optimization.py` 估计弹性、疲劳与非线性响应，再由 `offer_economics.py` 核算全成本；估计未识别时不得优化折扣深度。

## 最小专业合同
- 守恒：eligible ≥ redeemed ≥ incremental ≥ 0。
- 公式：增量Offer贡献 = 增量订单×增量CM − 全核销变动成本 − 拉前 − 蚕食 − 固定成本。
- 保本率：总Offer负担 ÷（核销订单×单位增量CM），单位CM≤0时不可定义。
- 识别风险：平台归因、领券率和核销率均不是因果增量。
- 翻转条件：成熟增量贡献下界转正且欺诈、投诉、老客公平通过。
- 跨域请求：D06给价格/利润底线，CIG给资格，LIFD给容量，PLCO给展示。
- 输出字段：offer_version、eligibility、full_cost、break_even_rate、abuse_guard、expiry。
