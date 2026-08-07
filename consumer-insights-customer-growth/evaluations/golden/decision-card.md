# CIG 专业 Decision Card

对象：CIG-GOLDEN@v1；运行时：`CIG-2026.07`。

结论：受控修复。身份合并违反收入守恒(CLV $342 > $287上限)。Cohort净增量虚高25%。行动: 拆分合并身份，重算CLV；Cohort补扣退款成熟值。

专业门核验：身份授权、收入守恒、Cohort、净增量价值逐项独立核验，任一为unknown则冻结动作。

翻转条件：见evaluation-catalog.json各case的flip_condition字段。
