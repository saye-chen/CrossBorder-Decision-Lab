# AAMO 专业 Decision Card

对象：AAMO-GOLDEN@v1；运行时：`AAMO-2026.07`。

结论：受控修复。表面ROAS 4.2 vs 净ROAS 1.06，差距来自增量比例低(38%)和蚕食($2,400/月)。行动: PMax缩减30%预算，增量实验扩展至全campaign，30天后重算三本账。

专业门核验：三本账、边际效率、增量、归因逐项独立核验，任一为unknown则冻结动作。

翻转条件：见evaluation-catalog.json各case的flip_condition字段。

## 证据与执行控制

支持证据是平台ROAS与净ROAS的差异，反证是增量比例和蚕食仍需成熟窗口确认。动作对象：AAMO-GOLDEN@v1；责任人：广告负责人；观察窗：30天成熟贡献窗口。成功条件：边际贡献为正且增量实验通过；停止条件：追踪、归因或退款成熟失败；回滚：恢复已验证预算上限并停止放量。

## 主权与联动

主权属于 `advertising-analysis-measurement-optimization`；参与域只能提交 `proposed`。允许用途：预算和出价候选、测量设计与诊断；禁止用途：替代D06利润、D08页面或D13客户触达决定。翻转条件由三本账、边际效率和增量证据共同决定。
