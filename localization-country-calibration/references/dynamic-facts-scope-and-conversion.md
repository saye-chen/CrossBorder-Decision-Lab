# 动态事实、作用域与转换

先求适用性交集，再解析参数优先级。管辖区、销售国家、平台站点、主体、店铺、SKU、路线、locale、生命周期和决策时点共同限定适用性；全局不可放宽红线优先于局部覆盖。不同维度各自更具体而无法唯一排序时返回 `SCOPE_CONFLICT_UNRESOLVED`。

动态事实保存 valid_from/valid_until、recorded_at/superseded_at、verified_at、decision_time、来源、指纹、刷新触发和冲突。晚到或更正数据生成新版本，不覆盖历史快照。

金额使用 Decimal；汇率声明 base/quote；单位必须同维度；时区使用 IANA；税含/税不含转换只消费已批准税口径。输出保存输入、参数、公式和结果哈希。
