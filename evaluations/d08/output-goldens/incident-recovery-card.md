# PLCO Incident & Recovery Card Golden
## Incident
`INC-01`，Shopee TH item/model批量改版，后台3/5成功、前台2/5传播，状态`partially_applied`，证据截止2026-07-20。
对象为同一item下5个model及v5；反证为后台已返回成功。根因可能是传播、权限或缓存，需逐项验证而非提前归因。
## 影响与Gates
两个model图片错绑、一个库存显示延迟；G2/G5/G6 conditional，新增流量承诺受限。
## 部分成功与失败
逐model记录成功、失败、重试、前后台、移动/桌面和event状态；提交成功不等于恢复。
## 止损与修复
冻结受影响model推广，恢复v4图片映射，向LIFD请求ATP确认；平台规则和权限现场核验。
具体动作逐model记录，不以批次平均状态代替。
## 验证与关闭
前台图片、variation、价格、库存、配送、购买和事件全部一致才verified。成功条件为5/5传播；停止条件为再次覆盖；回滚v4。剩余暴露和owner明确。
