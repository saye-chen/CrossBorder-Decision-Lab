# CIDM → PLCO 交接包

CIDM只交付投资对象、商品事实、Proof、目标人群、购买任务、关键词簇、痛点和实验假设。PLCO拥有标题、五点、A+、Search Terms、QA和页面实验的执行判断；页面结果必须回写CIDM后按原模型重算。

交接包必须满足：

- `allowed_use`只能为`listing_and_store_acceptance_design`；
- `forbidden_use`必须包含`investment_score_override`；
- 每条差异化声明必须绑定现有`proof_id`；
- `unsupported_claims`和`prohibited_claims`不得进入可用卖点；
- 包内不得出现`invest`、`capital_posture`、`order_quantity`或`production_ready`；
- 页面校验、关键词覆盖或语义覆盖通过，不等于排名、转化或销量因果已证实。

使用`opportunity_signals.validate_cidm_plco_packet`做确定性校验。
