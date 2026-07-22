# PLCO Conversion Diagnosis Memo Golden
## 对象与数据质量
BR/Mercado Libre `OBJ-CV-01`、item `v2`、移动付费与自然分层；币种BRL，窗口和去重一致，证据截止2026-07-20。
## Gates
G1—G5 pass，G6 conditional；支付事件存在8%缺口，结论上限Repair。
## 漏斗与计算
C1以合格曝光→访问→互动→加购→结账→支付分解，计数守恒、输入/输出哈希齐全；主要断点为变体选择到加购。
## 根因与替代解释
分期展示、variation命名和配送承诺同时影响选择；反证E5显示桌面正常。替代解释为移动支付事件丢失。
## 具体修复
variation改为本地可理解命名；标题三版；图2展示尺寸选择；详情前移分期与配送边界；落地页补`variant_select`和`checkout_start`。
## 实验与闭环
修事件后按设备实验；主指标加购率，护栏支付、取消、贡献利润。成功/停止/回滚和owner明确，不把断点写成因果。
