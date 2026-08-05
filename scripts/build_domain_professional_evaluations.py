#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build self-contained professional evaluation assets for legacy domains.

These small, domain-local suites are the common audit surface. They complement
rather than replace each domain's deeper model and scenario evaluations.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P={
"category-investment-decision":dict(code="CIDM",runtime="CIDM-2026.07",owner="investment",markers=["资本姿态","机会损失","组合约束","退出纪律"],cases=[("高增长低证据品类","inconclusive"),("组合资金争用","reallocate"),("合规红线机会","blocked"),("国家平台迁移","recompute"),("需求代理失效","hold"),("退出后再进入","controlled_reentry")]),
"competitive-intelligence-monitoring":dict(code="CIM",runtime="CIM-2026.07",owner="competition",markers=["对象去重","代理信号","来源独立性","变化确认"],cases=[("竞品身份错配","blocked"),("同源价格信号","inconclusive"),("排名骤升归因","review_required"),("跨国迁移","recompute"),("证据过期","blocked"),("监控恢复","controlled_recovery")]),
"video-link-breakdown":dict(code="VLB",runtime="VLB-2026.07",owner="content_creative",markers=["钩子","证明机制","平台迁移","疲劳"],cases=[("高播放无商品证明","inconclusive"),("医疗话术越界","blocked"),("达人素材权利缺失","blocked"),("跨平台节奏迁移","recompute"),("素材疲劳漂移","refresh"),("自然内容转广告","review_required")]),
"consumer-insights-customer-growth":dict(code="CIG",runtime="CIG-2026.07",owner="customer_growth",markers=["身份授权","收入守恒","Cohort","净增量价值"],cases=[("身份错误合并","blocked"),("退款未成熟CLV","inconclusive"),("触达疲劳","holdout"),("评价事故恢复","controlled_recovery"),("会员增量","experiment_required"),("隐私授权撤回","blocked")]),
"advertising-analysis-measurement-optimization":dict(code="AAMO",runtime="AAMO-2026.07",owner="advertising",markers=["三本账","边际效率","增量","归因"],cases=[("高ROAS负贡献","stop"),("PMax品牌蚕食","experiment_required"),("追踪断裂","blocked"),("库存容量不足","blocked"),("预算渐进漂移","recompute"),("退款成熟后恢复","controlled_recovery")]),
"logistics-inventory-fulfillment-decision":dict(code="LIFD",runtime="LIFD-2026.07",owner="logistics",markers=["ATP/CTP","库存保护","路线容量","反向履约"],cases=[("需求激增库存争用","allocate"),("清关延误级联","controlled_recovery"),("危险品路线不合格","blocked"),("多仓调拨","recompute"),("承运商时效漂移","hold"),("海外尾货退出","controlled_exit")]),
"platform-store-listing-conversion":dict(code="PLCO",runtime="PLCO-2026.07",owner="listing_conversion",markers=["索引可见性","Offer承接","变体治理","漏斗定位"],cases=[("流量正常转化下滑","diagnose"),("主图高点击低成交","experiment_required"),("受限宣称上架","blocked"),("跨平台Listing迁移","recompute"),("变体评论错配","hold"),("抑制恢复","controlled_recovery")])}

for skill,p in P.items():
 base=ROOT/skill/"evaluations"; golden=base/"golden";golden.mkdir(parents=True,exist_ok=True)
 cases=[]
 for i,(name,status) in enumerate(p["cases"],1):
  cases.append({"id":f"{p['code']}-PE-{i:02d}","name":name,"mode":["standard","conflict","extreme","multi_turn","adversarial","recovery"][i-1],"object_ref":f"{p['code']}-OBJECT-{i}@v1","evidence":[f"E{i}S"],"counterevidence":[f"E{i}C"],"expected_status":status,"must":p["markers"]+["停止条件","回滚"],"forbidden":["代理升级为事实","跨域越权","模板占位结论"],"mutation":{"field":"object_version","value":"stale","expected":"blocked"}})
 (base/"evaluation-catalog.json").write_text(json.dumps({"runtime":p["runtime"],"owner":p["owner"],"cases":cases},ensure_ascii=False,indent=2)+"\n")
 (golden/"decision-card.md").write_text(f"# {p['code']} 专业 Decision Card\n\n对象：{p['code']}-GOLDEN@v1；运行时：`{p['runtime']}`。\n\n结论：受控修复。支持证据 E1S 与反对证据 E1C 分离；{'、'.join(p['markers'])}逐项核验。未知值不填零，辅助域结果保持 proposed。\n\n行动：冻结受影响动作，补齐独立证据后重算。成功条件：对象、证据、时间和专业门关闭；停止条件：红线或版本变化；回滚：恢复最后验证版本。\n")
 lines=[f"# {p['code']} 完整专业报告","",f"运行时：`{p['runtime']}`。","","## 执行摘要",f"决策结论：对象 `{p['code']}-GOLDEN@v1` 当前为 `Repair`；一句话理由：证据冲突使{p['markers'][0]}与{p['markers'][1]}不能同时成立。","","## 对象与边界",f"适用范围限当前国家、平台、对象版本和生命周期；缺失数据保持 unknown，决策影响不扩展到其他对象。对象身份由平台标识、业务主体、产品或账户版本共同确定，任一关键字段变化都必须新建版本，不能把旧结论静默迁移。","","## 证据与反证","支持证据 E1S 来自授权对象快照；反对证据 E1C 来自独立结果。最弱假设 A1 是来源和版本可比；替代解释必须保留，证据截止为 2026-08-05。相同来源家族的多个页面、导出或摘要只算一个证据家族；时间靠近、结论一致或格式完整都不能替代来源独立性。","","## 门槛与评分",f"{'、'.join(p['markers'])}作为专业门；红线不能由总分补偿。任一专业门为unknown时只允许补证、诊断或可逆实验，不允许把综合分数、收入机会或管理层偏好升级成validated。","","## 证据台账","E1S/E1C 均保留来源、指纹、业务时间、允许用途和禁止用途。证据过期、对象错配、授权撤回或上游状态改变时，只失效依赖字段并触发影响闭包；无关事实继续保留。","","## 假设台账","A1 来源独立；A2 对象稳定；A3 时间窗成熟。推翻条件为任一验证失败。每项假设都有责任人、核验方法、截止时间和对决策的影响，未核验假设不包装成事实。","","## 经济与计算","C1 仅消费相应主权域接受的经济输入；输入哈希 sha256:domain-in，输出哈希 sha256:domain-out，币种 USD，使用确定性计算器，可复算：是。经济结果只能约束可承受动作，不能签发本域之外的资本、价格、库存或客户决定。","","## 计算台账","C1 状态 complete；输入缺失时为不可计算而不是零。单位、币种、税口径、归因口径和时间窗不一致时阻断比较，历史计算保留原始参数版本。","","## 根因",f"根因定位到{p['markers'][0]}与{p['markers'][1]}的证据闭包冲突；反证和替代解释不被多数投票消除。现象、相关性、机制和可执行根因分层记录，只有能够解释受影响范围并产生可证伪修复动作的原因进入推荐。","","## 决策推导","先对象与红线，再证据和计算，最后比较不行动、修复与受控实验。不行动也要计算风险和机会成本；推荐方案必须说明为什么优于保守方案，以及哪些新证据会翻转排序。","","## 主权与联动",f"主决策 Skill 为 `{skill}`；主权越界：否。参与域只提交 proposed；允许用途为诊断，禁止用途为外部执行。跨域包保留生产者、消费者、对象、版本、允许用途、禁止用途和重新验收触发条件。","","## 行动计划",f"动作对象为 {p['code']}-GOLDEN@v1；幅度限影响闭包；责任人为{p['code']} owner；观察窗按证据成熟度。成功条件：专业门关闭；停止条件：红线恶化；回滚：恢复已验证版本。每个动作必须记录当前基线、目标变化、护栏、最晚复核时间和失败后的恢复责任。","","## 专业核对清单","- 对象与版本匹配。","- 来源独立性已检查。","- 业务时间与有效期已检查。","- 未知、缺失和零值分开。","- 反证能够改变结论。","- 计算可独立复现。","- 主权和允许用途明确。","- 停止、回滚和恢复具名。","","## 国家/平台与动态事实","国家/平台必须当前核验，核验日期 2026-08-05；动态事实过期即重算。公开信息、授权后台和专业意见分别记录证明上限，不能用相邻国家、相似平台或历史经验填补当前事实。","","## 自检摘要","支持证据、反对证据、最弱假设、成功条件、停止条件、回滚、置信度和决策影响齐全。伪造事实：否；因果越界：否；主权越界：否；隐私违规：否；可复算：是。"]
 (golden/"professional-report.md").write_text("\n".join(lines)+"\n")
print(f"built={len(P)}")
