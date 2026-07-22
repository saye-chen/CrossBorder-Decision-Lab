# CAPM Golden：Progressive Decision

## 执行摘要

决策结论：R3保持自然发布，supersede付费投流候选，并在权利到期前续期或下架。一句话理由：新证据提高身份质量，但付费使用权仅限US TikTok 30天，不能继承为全球长期权利。主决策 Skill：`creator-affiliate-partnership-management`；运行时：`CAPM-2026.07`。未解决红线：否。

## 对象与边界

对象creator-0423，当前object_version v3，parent_report_id R2，生命周期为已发布待成熟；适用范围US/TikTok、USD，证据截止2026-08-20。缺失数据为AAMO接收和退款最终成熟。若用户换达人则建立新object_id和新报告链，禁止继承R1-R3。

## 证据与反证

E1为R1公开主页S1；E2为R2授权后台S3；E3为签署自然发布权S3；E4为R3付费使用权附件S3；E5为退款成熟数据S4。支持证据提高身份和自然发布可信度。反对证据是E4期限短且地区受限。A1假设可在到期前谈成续期。替代解释为合同附件版本错误。置信度：高；推翻条件为权利方撤回或附件签名无效。

## 证据台账

E1-E5分别绑定R1-R3、对象版本和允许用途；E4只支持US TikTok 30天，不能静默扩大范围。

## 门槛与评分

G1A从inconclusive变为pass；G1B自然发布pass、付费使用到期后blocked；G2 pass；G3 conditional；G4按E5重算；G5保持parent约束；G6仍C0。P0证据撤回将反向失效相关claim和动作。

## 经济与计算

C1使用E5重算成熟净收入、退款和佣金，固定费上限由420 USD调整为310 USD。币种USD，舍入0.01。计算器 `partnership_economics.py` 与 `decision_state.py`，输入哈希 `9999999999999999999999999999999999999999999999999999999999999999`，输出哈希 `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`，可复算：是。

## 根因

根因是权利版本变化而非内容质量下降。反证是自然发布合法并不证明付费使用合法。替代解释为旧附件尚有效，但必须由证据确认。最弱假设是续期价格不超过经济上限；推翻条件为报价使成熟利润下界为负。

## 主权与联动

主决策 Skill：CAPM。允许用途：自然发布、续期谈判、到期下架。禁止用途：未获AAMO接受就投流、静默改写R1/R2、跨达人继承证据。paid candidate状态由proposed变为superseded；AAMO接收仍pending。

## 行动计划

A1动作对象为rights-R3，责任人rights owner，在到期前10日给出续期报价，幅度≤310 USD，观察窗7日；A2若未续期，责任人content ops在到期时下架全部付费衍生版；A3保留自然发布。成功条件：新rights version验证通过或取得下架证明；停止条件：撤回、签名冲突或利润下界负；回滚：冻结新使用并沿传播闭包下架。

## 国家/平台与动态事实

国家/平台为US/TikTok。动态事实包括身份广告入口和平台下架流程，核验日期2026-08-20；跨国或跨平台使用必须新建规则和权利判断。

## 假设台账

A1续期可承受，A2附件签名有效，A3自然权与付费权可拆分。每项记录支持证据、反对证据、置信度和决策影响。

## 计算台账

C1成熟经济重算；C2权利用途闭包；C3affected claims/calculations；每项保存parent、输入、脚本版本和hash。

## 决策推导

R2新增身份与自然权使建联动作升级；R3退款和付费权范围变化只重算affected closure。旧paid action进入superseded，未变自然发布和G5约束保留。

## 自检摘要

report_id R3、parent R2、changed_fields、new_evidence_ids、preserved_constraints、superseded_actions和next trigger齐全。伪造事实：否；主权越界：否；因果越界：否；隐私违规：否。结果回填为续期版本或下架证明。
