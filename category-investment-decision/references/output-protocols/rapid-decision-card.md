# CIDM轻量决策卡协议

轻量卡用于快速判断，但不能绕过五道门槛、七维评分、利润红线和证据合同。机器结构至少包含：四档`decision`、`confidence`、`lifecycle`、支持与反对证据、最弱假设、恰好三项优先动作、`do_not_do_yet`、缺失数据及影响、最短可信验证、Go和Stop。

`Do Not Do Yet`必须与生命周期一致。LC-1/LC-2默认禁止开模、大货采购、多国铺开、高额广告、长期合同和无证据扩变体；具体禁做项随对象调整。验证窗口由最弱假设决定，不机械固定七天。

正式交付前使用`opportunity_signals.validate_rapid_decision_card`校验。
