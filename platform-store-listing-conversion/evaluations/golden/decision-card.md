# PLCO 专业 Decision Card

对象：PLCO-GOLDEN@v1；运行时：`PLCO-2026.07`。

结论：受控修复。流量正常但USP降17%，主图场景图Offer承接断裂+Buy Box丢失。行动: 恢复白底主图A，Buy Box价格调整至竞争价+$0.3，7天后重测。

专业门核验：索引可见性、Offer承接、变体治理、漏斗定位逐项独立核验，任一为unknown则冻结动作。

翻转条件：见evaluation-catalog.json各case的flip_condition字段。

## 证据与执行控制

支持证据是流量正常而USP下降，反证是主图、Offer和Buy Box的归因仍需拆分。动作对象：PLCO-GOLDEN@v1；责任人：Listing负责人；观察窗：版本发布后7天。成功条件：USP恢复且页面身份、Offer和变体保持一致；停止条件：声明无证据、Buy Box恶化或转化下界为负；回滚：恢复白底主图A和已验证页面版本。

## 主权与联动

主权属于 `platform-store-listing-conversion`；参与域只能提交 `proposed`。允许用途：页面修改、素材Brief和小流量实验；禁止用途：替代D05声明边界、D06价格结论或直接发布外部变更。翻转条件由页面版本、平台状态和成熟转化共同决定。
