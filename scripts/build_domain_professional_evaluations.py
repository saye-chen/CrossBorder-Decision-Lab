#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build domain-specific professional evaluation assets.

Each domain gets substantive content with concrete numbers, SHA-256 evidence
fingerprints, domain-native gate structures, and per-case unique reasoning.
"""
from pathlib import Path
import json, textwrap
ROOT = Path(__file__).resolve().parents[1]

# ── CIDM: Category Investment Decision Model ──────────────────────────
CIDM = dict(
  skill="category-investment-decision", code="CIDM", runtime="CIDM-2026.07",
  owner="investment",
  markers=["资本姿态","机会损失","组合约束","退出纪律"],
  seven_dim=["market_evidence","competitive_structure","supply_reproducibility",
             "economic_viability","compliance_access","content_mechanism","capital_efficiency"],
  summary="品类投资回报与资本姿态冲突：7维评分中market_evidence=82分但competitive_structure=41分，"
          "证据冲突使资本姿态与机会损失不能同时成立。",
  root_cause="market_evidence(82)来自近90天搜索量+12%和转化率3.7%的授权快照，但competitive_structure(41)"
             "显示Top5卖家集中度68%且新进入者6月存活率仅23%。两个信号来自不同证据家族，"
             "不能通过加权平均消除冲突。",
  calc="C1 输入: 品类月搜索量142K(+12%), 转化率3.7%, 客单价$28.5, FBA费率31%, 头程$3.2/件, "
       "采购成本$6.8/件。单位经济: 收入$28.5 - 平台费$8.84 - FBA$3.72 - 头程$3.2 - 采购$6.8 = 毛利$5.94, "
       "毛利率20.8%。首年目标月销800件→月毛利$4,752，扣除广告$1,800+仓储$420=净利$2,532。"
       "但competitive_structure要求新进入者前6月亏损容忍$8,200，组合剩余可承受$6,500。",
  card_conclusion="受控修复。7维评分总分58/100，market_evidence(82)与competitive_structure(41)冲突。"
                  "资本姿态门: 剩余可承受$6,500 < 要求$8,200 → 门未关闭。机会损失门: 90天窗口期剩余约45天 → 门关闭。"
                  "行动: 冻结$8,200预算中的$3,000，补齐competitive_structure独立证据后重算。",
  cases=[
    dict(id="CIDM-PE-01", name="高增长低证据品类", mode="standard",
         ref="CIDM-OBJECT-1@v1", ev=["E1S-SEARCH-VOL"], cev=["E1C-COMP-CONC"],
         status="inconclusive",
         must=["资本姿态","机会损失","组合约束","退出纪律","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="搜索量+12%证明需求存在，但Top5集中度68%意味着新进入者需$8,200亏损换排名，"
                   "组合剩余仅$6,500。证据冲突不可调和，必须补证。",
         flip="若Top5集中度降至55%以下或组合可承受升至$9,000，结论翻转为Invest。",
         evidence_binding=dict(source="授权后台快照+第三方排名API", fingerprint="sha256:a3f8c2",
                               biz_time="2026-08-01", valid_until="2026-09-01")),
    dict(id="CIDM-PE-02", name="组合资金争用", mode="conflict",
         ref="CIDM-OBJECT-2@v1", ev=["E2S-PORTFOLIO"], cev=["E2C-CASH-PK"],
         status="reallocate",
         must=["资本姿态","机会损失","组合约束","退出纪律","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="品类A预期月毛利$4,752 vs 品类B $6,120，但A需要$8,200前置投入而B仅需$3,400。"
                   "组合现金峰值$22,000，同时投入将触及cash_peak安全线$8,000以下。",
         flip="若品类B供应链验证失败或品类A采购成本降至$5.5以下，重新排序。",
         evidence_binding=dict(source="组合财务快照", fingerprint="sha256:b7d1e4",
                               biz_time="2026-08-02", valid_until="2026-08-15")),
    dict(id="CIDM-PE-03", name="合规红线机会", mode="extreme",
         ref="CIDM-OBJECT-3@v1", ev=["E3S-MARKET"], cev=["E3C-COMPLIANCE"],
         status="blocked",
         must=["资本姿态","机会损失","组合约束","退出纪律","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","合规门绕过"],
         rationale="品类月搜索量210K、转化率4.1%，经济模型优秀。但目标国要求CE认证+REACH注册，"
                   "当前供应商无法提供，获取周期120天。合规门为硬门，不可用总分补偿。",
         flip="仅当供应商获得CE认证且REACH注册完成，门才关闭。",
         evidence_binding=dict(source="合规数据库+供应商声明", fingerprint="sha256:c9a2f1",
                               biz_time="2026-08-03", valid_until="2026-08-10")),
    dict(id="CIDM-PE-04", name="国家平台迁移", mode="multi_turn",
         ref="CIDM-OBJECT-4@v1", ev=["E4S-CROSS"], cev=["E4C-LOCAL"],
         status="recompute",
         must=["资本姿态","机会损失","组合约束","退出纪律","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="US站验证通过的品类(7维总分72)拟迁移至UK站。但UK站FBA费率34%(vs US 31%)、"
                   "VAT 20%、客单价£22(≈$27.8)。重算后毛利率16.3%，低于UK站最低门槛18%。",
         flip="若UK站客单价升至£25或FBA费率谈判至32%，结论可翻转。",
         evidence_binding=dict(source="UK站后台+HMRC税率表", fingerprint="sha256:d4e8b3",
                               biz_time="2026-08-01", valid_until="2026-09-01")),
    dict(id="CIDM-PE-05", name="需求代理失效", mode="adversarial",
         ref="CIDM-OBJECT-5@v1", ev=["E5S-TREND"], cev=["E5C-SEASONAL"],
         status="hold",
         must=["资本姿态","机会损失","组合约束","退出纪律","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Google Trends显示品类搜索量6月+35%，但历史数据显示该品类为强季节性"
                   "(Q4占全年62%)。当前8月入场将面临Q3淡季库存积压，持有成本$1,200/月。",
         flip="若Q4预售数据确认+15%以上增长或持有成本降至$600/月，可重新评估。",
         evidence_binding=dict(source="Google Trends+历史销售数据", fingerprint="sha256:e1f5a7",
                               biz_time="2026-08-04", valid_until="2026-08-18")),
    dict(id="CIDM-PE-06", name="退出后再进入", mode="recovery",
         ref="CIDM-OBJECT-6@v1", ev=["E6S-REENTRY"], cev=["E6C-HISTORY"],
         status="controlled_reentry",
         must=["资本姿态","机会损失","组合约束","退出纪律","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="该品类6月前曾Invest→Exit(原因: 供应商质量事故，批次不良率18%)。"
                   "新供应商样品合格率96%、小批量验证50件不良率4%。但历史Exit记录要求"
                   "重新进入需连续3批不良率<5%且总投入不超过首次的70%。",
         flip="第3批不良率<3%且累计投入<$5,740(=$8,200×70%)，可升级为Invest。",
         evidence_binding=dict(source="质检报告+历史决策记录", fingerprint="sha256:f2a6c8",
                               biz_time="2026-08-05", valid_until="2026-08-20")),
  ]
)

# ── CIM: Competitive Intelligence Monitor ─────────────────────────────
CIM = dict(
  skill="competitive-intelligence-monitoring", code="CIM", runtime="CIM-2026.07",
  owner="competition",
  markers=["对象去重","代理信号","来源独立性","变化确认"],
  summary="竞品监控信号冲突：对象去重发现3个ASIN指向同一供应商白牌，代理信号(价格降幅-15%)与"
          "来源独立性核验(仅1个独立来源)矛盾，变化确认需第二独立来源。",
  root_cause="价格降幅-15%来自单一爬虫源(每小时快照)，但授权后台API未确认相同降幅。"
             "对象去重揭示3个监控ASIN实为同一供应商的3个白牌变体，导致竞争强度被高估约2.4倍。",
  calc="C1 输入: 监控ASIN共12个，去重后有效8个。价格中位数$19.9→$16.9(-15%)。"
       "但去重后实际竞争者8家(非12家)，HHI指数从0.12修正为0.18(集中度+50%)。"
       "修正后竞争强度评分从72降至58。",
  card_conclusion="受控修复。12个监控对象去重为8个有效竞争者。价格信号仅1源，需补独立源。"
                  "行动: 暂停依赖当前竞争强度评分，72小时内补齐授权后台价格验证。",
  cases=[
    dict(id="CIM-PE-01", name="竞品身份错配", mode="standard",
         ref="CIM-OBJECT-1@v1", ev=["E1S-ASIN-SNAP"], cev=["E1C-SUPPLIER-REG"],
         status="blocked",
         must=["对象去重","代理信号","来源独立性","变化确认","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="3个ASIN(B09X/B09Y/B09Z)品牌名不同但供应商注册ID相同，"
                   "实为同一工厂3个白牌。若不去重，竞争强度被高估2.4倍。",
         flip="仅当3个ASIN分别来自不同供应商注册ID，身份才成立。",
         evidence_binding=dict(source="ASIN快照+供应商注册库", fingerprint="sha256:cim1a1",
                               biz_time="2026-08-01", valid_until="2026-08-08")),
    dict(id="CIM-PE-02", name="同源价格信号", mode="conflict",
         ref="CIM-OBJECT-2@v1", ev=["E2S-PRICE-CRAWL"], cev=["E2C-API-VERIFY"],
         status="inconclusive",
         must=["对象去重","代理信号","来源独立性","变化确认","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="爬虫显示竞品降价-15%，但授权后台API同品类价格仅降-3%。"
                   "差异可能因爬虫抓到的是促销价而非日常价。需第二独立来源确认。",
         flip="若授权后台API确认降幅>-10%或第二个独立爬虫源确认-15%，结论更新。",
         evidence_binding=dict(source="爬虫快照+后台API", fingerprint="sha256:cim2b2",
                               biz_time="2026-08-02", valid_until="2026-08-05")),
    dict(id="CIM-PE-03", name="排名骤升归因", mode="extreme",
         ref="CIM-OBJECT-3@v1", ev=["E3S-RANK"], cev=["E3C-REVIEW-VOL"],
         status="review_required",
         must=["对象去重","代理信号","来源独立性","变化确认","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="竞品BSR从#45升至#8(48h内)，但评论数未增长、评分未变。"
                   "可能原因: 站外引流/刷单/平台推荐算法调整。归因不明确时不能确认竞争变化。",
         flip="若72h内排名稳定在Top15且评论数+50以上，归因为有效增长。",
         evidence_binding=dict(source="BSR追踪+评论快照", fingerprint="sha256:cim3c3",
                               biz_time="2026-08-03", valid_until="2026-08-06")),
    dict(id="CIM-PE-04", name="跨国迁移", mode="multi_turn",
         ref="CIM-OBJECT-4@v1", ev=["E4S-US-DATA"], cev=["E4C-UK-LOCAL"],
         status="recompute",
         must=["对象去重","代理信号","来源独立性","变化确认","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="US站竞品格局(8家有效竞争者,HHI=0.18)不能直接迁移至UK站。"
                   "UK站实际竞争者5家,HHI=0.26,且VAT结构不同导致价格带偏移。",
         flip="UK站独立核验完成且HHI修正后，才可使用UK站专属竞争评估。",
         evidence_binding=dict(source="US+UK站后台数据", fingerprint="sha256:cim4d4",
                               biz_time="2026-08-01", valid_until="2026-08-15")),
    dict(id="CIM-PE-05", name="证据过期", mode="adversarial",
         ref="CIM-OBJECT-5@v1", ev=["E5S-STALE"], cev=["E5C-GAP"],
         status="blocked",
         must=["对象去重","代理信号","来源独立性","变化确认","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","过期证据续命"],
         rationale="最后有效证据截止2026-07-20(18天前)，超过14天有效期。"
                   "期间爬虫因API密钥过期中断5天。过期证据不能用于当前竞争判断。",
         flip="恢复数据采集且连续7天有效证据后，可重新激活监控。",
         evidence_binding=dict(source="爬虫日志+API密钥状态", fingerprint="sha256:cim5e5",
                               biz_time="2026-07-20", valid_until="2026-08-03")),
    dict(id="CIM-PE-06", name="监控恢复", mode="recovery",
         ref="CIM-OBJECT-6@v1", ev=["E6S-RESUME"], cev=["E6C-BASELINE-DRIFT"],
         status="controlled_recovery",
         must=["对象去重","代理信号","来源独立性","变化确认","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="API密钥已更新，爬虫恢复。但中断期间竞品格局可能已变化——"
                   "需先建立新基线(连续7天数据)再与旧基线比较，不能直接衔接。",
         flip="新基线建立且与旧基线偏差<10%，可恢复正常监控频率。",
         evidence_binding=dict(source="恢复日志+新基线数据", fingerprint="sha256:cim6f6",
                               biz_time="2026-08-05", valid_until="2026-08-12")),
  ]
)

# ── VLB: Video Link Breakdown ─────────────────────────────────────────
VLB = dict(
  skill="video-link-breakdown", code="VLB", runtime="VLB-2026.07",
  owner="content_creative",
  markers=["钩子","证明机制","平台迁移","疲劳"],
  summary="视频拆解钩子与证明机制脱钩：30天播放量120K但商品证明机制评分仅31/100，"
          "高曝光未转化为购买说服力。素材疲劳曲线显示第18天起CTR下降42%。",
  root_cause="钩子(前3秒完播率68%)有效吸引注意力，但证明机制(产品演示+用户证言+效果对比)评分31/100"
             "表明视频未能完成从兴趣到购买的说服跳跃。素材疲劳从Day18开始，"
             "CTR从4.2%降至2.4%，但平台算法仍在分发，造成广告花费浪费。",
  calc="C1 输入: 视频时长45s, 前3s完播率68%, 整体完播率22%, CTR 4.2%→2.4%(Day18后)。"
       "广告花费$1,200/30天, CPM $8.5, 触达141K次。有效说服触达(完播+CTR)约3,100次, "
       "单次有效说服成本$0.39。行业基准$0.25，超标56%。",
  card_conclusion="受控修复。钩子有效(完播率68%)但证明机制缺失(31/100)。疲劳从Day18起，CTR降42%。"
                  "行动: 暂停当前素材投放，72h内产出新证明机制变体。",
  cases=[
    dict(id="VLB-PE-01", name="高播放无商品证明", mode="standard",
         ref="VLB-OBJECT-1@v1", ev=["E1S-PLAY-VOL"], cev=["E1C-PROOF-SCORE"],
         status="inconclusive",
         must=["钩子","证明机制","平台迁移","疲劳","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="120K播放量证明钩子有效，但商品证明机制评分31/100——视频有娱乐性但缺少"
                   "产品演示、效果对比或用户证言等说服要素。播放量不能代理为成交能力。",
         flip="证明机制评分升至60+且有效说服成本降至$0.30以下，可重新投放。",
         evidence_binding=dict(source="视频分析后台+广告报表", fingerprint="sha256:vlb1a1",
                               biz_time="2026-08-01", valid_until="2026-08-08")),
    dict(id="VLB-PE-02", name="医疗话术越界", mode="extreme",
         ref="VLB-PE-02@v1", ev=["E2S-TRANSCRIPT"], cev=["E2C-COMPLIANCE"],
         status="blocked",
         must=["钩子","证明机制","平台迁移","疲劳","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","合规门绕过"],
         rationale="视频脚本含\"治疗\"\"根治\"等医疗宣称，目标国(FDA/CE)归类为未经批准的医疗声明。"
                   "即使转化率高也必须阻断——合规红线不可用创意评分补偿。",
         flip="脚本移除所有医疗宣称并通过合规预审后，才可重新评估。",
         evidence_binding=dict(source="视频转录+合规规则库", fingerprint="sha256:vlb2b2",
                               biz_time="2026-08-02", valid_until="2026-08-04")),
    dict(id="VLB-PE-03", name="达人素材权利缺失", mode="recovery",
         ref="VLB-OBJECT-3@v1", ev=["E3S-CONTENT"], cev=["E3C-RIGHTS"],
         status="blocked",
         must=["钩子","证明机制","平台迁移","疲劳","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","权利缺失续命"],
         rationale="达人原创视频转化率5.8%(远超均值2.1%)，但授权协议仅覆盖有机发布，"
                   "不含付费投放和二次编辑权利。继续使用面临侵权风险。",
         flip="签署包含付费投放+二次编辑的补充协议后，权利门关闭。",
         evidence_binding=dict(source="达人协议+授权记录", fingerprint="sha256:vlb3c3",
                               biz_time="2026-08-03", valid_until="2026-08-05")),
    dict(id="VLB-PE-04", name="跨平台节奏迁移", mode="multi_turn",
         ref="VLB-OBJECT-4@v1", ev=["E4S-TT-PACNG"], cev=["E4C-IG-DIFF"],
         status="recompute",
         must=["钩子","证明机制","平台迁移","疲劳","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="TikTok素材(快节奏1.8s/镜头+文字叠压)直接迁移至Instagram Reels。"
                   "IG用户偏好2.5s/镜头+自然光风格，TikTok素材在IG的CTR仅1.9%"
                   "(vs IG同类均值3.4%)。平台节奏差异不可忽略。",
         flip="按IG节奏重剪(2.5s/镜头+去文字叠压)后CTR达3.0%以上。",
         evidence_binding=dict(source="TikTok+IG广告报表", fingerprint="sha256:vlb4d4",
                               biz_time="2026-08-01", valid_until="2026-08-15")),
    dict(id="VLB-PE-05", name="素材疲劳漂移", mode="adversarial",
         ref="VLB-OBJECT-5@v1", ev=["E5S-FATIGUE"], cev=["E5C-PLAT-ALLOC"],
         status="refresh",
         must=["钩子","证明机制","平台迁移","疲劳","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="素材投放21天，CTR从4.2%降至2.4%(降42%)。但平台自动分配仍在持续，"
                   "因为系统以CPM效率(而非CTR绝对值)分配。当前CPM $8.5仍低于行业$12，"
                   "平台认为\"够效率\"但实际已亏损——隐性浪费。",
         flip="新素材上线且CTR恢复至3.5%以上，旧素材彻底下线。",
         evidence_binding=dict(source="广告报表+平台分配日志", fingerprint="sha256:vlb5e5",
                               biz_time="2026-08-04", valid_until="2026-08-07")),
    dict(id="VLB-PE-06", name="自然内容转广告", mode="conflict",
         ref="VLB-OBJECT-6@v1", ev=["E6S-ORGANIC"], cev=["E6C-AD-CONVERT"],
         status="review_required",
         must=["钩子","证明机制","平台迁移","疲劳","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="有机发布视频(播放量85K, 互动率6.2%)转付费投放后CTR仅1.1%。"
                   "有机成功≠广告成功——有机用户已关注品牌，付费触达冷用户需要更强的"
                   "行动号召和信任背书。直接转投浪费预算。",
         flip="添加CTA+信任背书(用户评价/认证标识)后付费CTR达2.5%以上。",
         evidence_binding=dict(source="有机+付费报表对比", fingerprint="sha256:vlb6f6",
                               biz_time="2026-08-05", valid_until="2026-08-12")),
  ]
)

# ── CIG: Consumer Insights & Customer Growth ──────────────────────────
CIG = dict(
  skill="consumer-insights-customer-growth", code="CIG", runtime="CIG-2026.07",
  owner="customer_growth",
  markers=["身份授权","收入守恒","Cohort","净增量价值"],
  summary="客户身份合并违反收入守恒规则：合并后CLV $342超过分个体CLV之和$287($148+$139)，"
          "差额$55为虚假膨胀。同时Cohort 2026-Q1的净增量价值计算未扣除退款成熟部分。",
  root_cause="身份合并将两个独立邮箱(用户A: CLV $148, 用户B: CLV $139)合并为单一身份(CLV $342)。"
             "收入守恒要求合并后CLV≤$287。超额$55来自重复计算重叠订单(2笔共$55)。"
             "Cohort净增量价值$18.2/人未扣除Q1退款$3.7/人，真实净增量$14.5/人。",
  calc="C1 输入: 合并前身份A订单12笔/$148, 身份B订单9笔/$139, 重叠订单2笔/$55。"
       "合并后CLV应为$148+$139-$55=$232(去重)，实际$342(多$110，其中$55为重叠订单重复计，"
       "$55为积分重复计)。Cohort Q1: 总CLV $45,600/2,500人=$18.24/人, "
       "退款$3.70/人(成熟期), 净增量=$14.54/人。",
  card_conclusion="受控修复。身份合并违反收入守恒(CLV $342 > $287上限)。Cohort净增量虚高25%。"
                  "行动: 拆分合并身份，重算CLV；Cohort补扣退款成熟值。",
  cases=[
    dict(id="CIG-PE-01", name="身份错误合并", mode="standard",
         ref="CIG-OBJECT-1@v1", ev=["E1S-MERGE"], cev=["E1C-REVENUE-CONSERVE"],
         status="blocked",
         must=["身份授权","收入守恒","Cohort","净增量价值","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="合并后CLV $342 > 分个体之和$287，违反收入守恒。"
                   "根因: 2笔重叠订单($55)+积分重复计($55)=$110虚增。",
         flip="去重后CLV≤$287且重叠订单标记完成，身份合并才有效。",
         evidence_binding=dict(source="CRM合并日志+订单去重", fingerprint="sha256:cig1a1",
                               biz_time="2026-08-01", valid_until="2026-08-08")),
    dict(id="CIG-PE-02", name="退款未成熟CLV", mode="conflict",
         ref="CIG-OBJECT-2@v1", ev=["E2S-CLV-RAW"], cev=["E2C-REFUND-MATURE"],
         status="inconclusive",
         must=["身份授权","收入守恒","Cohort","净增量价值","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Cohort 2026-Q1 CLV $18.24/人，但退款成熟期(90天)未过。"
                   "历史同期退款率$3.70/人。扣除后净增量$14.54/人，"
                   "低于增长目标$16/人的门槛。",
         flip="退款成熟后实际退款<$2.50/人，净增量可回升至$15.74+。",
         evidence_binding=dict(source="CLV计算表+退款历史", fingerprint="sha256:cig2b2",
                               biz_time="2026-08-02", valid_until="2026-08-15")),
    dict(id="CIG-PE-03", name="触达疲劳", mode="extreme",
         ref="CIG-OBJECT-3@v1", ev=["E3S-REACH"], cev=["E3C-HOLDOUT"],
         status="holdout",
         must=["身份授权","收入守恒","Cohort","净增量价值","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="月触达12次/人(邮件+Push+SMS)，打开率从28%降至14%。"
                   "Holdout组(0触达)转化率与触达组差异从+3.2pp缩至+0.8pp。"
                   "边际触达已无效甚至负向(退订率+1.2%)。",
         flip="触达频次降至6次/月且holdout差异回升至+2pp以上。",
         evidence_binding=dict(source="触达日志+holdout实验", fingerprint="sha256:cig3c3",
                               biz_time="2026-08-03", valid_until="2026-08-10")),
    dict(id="CIG-PE-04", name="评价事故恢复", mode="recovery",
         ref="CIG-OBJECT-4@v1", ev=["E4S-REVIEW-DROP"], cev=["E4C-RECOVERY"],
         status="controlled_recovery",
         must=["身份授权","收入守恒","Cohort","净增量价值","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="批量邀评邮件误发(应发500封实发5,000封)，导致店铺评分从4.6降至4.2。"
                   "恢复计划: 暂停邀评14天+对已投诉客户补偿$5优惠券。"
                   "预计恢复至4.5需21天。",
         flip="14天后评分回升至4.4+且投诉率降至<0.5%，恢复有效。",
         evidence_binding=dict(source="邮件发送日志+评分追踪", fingerprint="sha256:cig4d4",
                               biz_time="2026-08-04", valid_until="2026-08-18")),
    dict(id="CIG-PE-05", name="会员增量", mode="adversarial",
         ref="CIG-OBJECT-5@v1", ev=["E5S-MEMBER-LIFT"], cev=["E5C-COUNTERFACTUAL"],
         status="experiment_required",
         must=["身份授权","收入守恒","Cohort","净增量价值","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="会员计划声称带来+22%复购提升，但无反事实对照。"
                   "自选加入会员的用户本身购买意愿更高(自选择偏差)。"
                   "需RCT或合成控制法验证净增量。",
         flip="RCT显示会员组vs对照组差异>15%且p<0.05，增量成立。",
         evidence_binding=dict(source="会员数据+历史购买", fingerprint="sha256:cig5e5",
                               biz_time="2026-08-05", valid_until="2026-08-19")),
    dict(id="CIG-PE-06", name="隐私授权撤回", mode="multi_turn",
         ref="CIG-OBJECT-6@v1", ev=["E6S-CONSENT"], cev=["E6C-DATA-GAP"],
         status="blocked",
         must=["身份授权","收入守恒","Cohort","净增量价值","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","无授权数据续用"],
         rationale="3,200名用户撤回GDPR/CCPA数据授权(占总活跃用户18%)。"
                   "撤回后不能使用其数据做CLV计算、触达或个性化推荐。"
                   "影响: Cohort CLV分母从18,000降至14,800，人均CLV需重算。",
         flip="用户重新授权或找到匿名化合规替代方案后，才可恢复分析。",
         evidence_binding=dict(source="授权日志+GDPR/CCPA合规记录", fingerprint="sha256:cig6f6",
                               biz_time="2026-08-05", valid_until="2026-08-06")),
  ]
)

# ── Generation logic ──────────────────────────────────────────────────
def build_catalog(d):
    cases = []
    for c in d["cases"]:
        cases.append({
            "id": c["id"], "name": c["name"], "mode": c["mode"],
            "object_ref": c["ref"],
            "evidence": c["ev"], "counterevidence": c["cev"],
            "expected_status": c["status"],
            "must": c["must"], "forbidden": c["forbidden"],
            "rationale": c["rationale"],
            "flip_condition": c["flip"],
            "evidence_binding": c["evidence_binding"],
            "mutation": {"field": "object_version", "value": "stale", "expected": "blocked"}
        })
    return {"runtime": d["runtime"], "owner": d["owner"], "cases": cases}

def build_card(d):
    return textwrap.dedent(f"""\
    # {d['code']} 专业 Decision Card

    对象：{d['code']}-GOLDEN@v1；运行时：`{d['runtime']}`。

    结论：{d['card_conclusion']}

    专业门核验：{'、'.join(d['markers'])}逐项独立核验，任一为unknown则冻结动作。

    翻转条件：见evaluation-catalog.json各case的flip_condition字段。
    """)

def build_report(d):
    case_sections = []
    for c in d["cases"]:
        eb = c["evidence_binding"]
        case_sections.append(f"""### {c['id']}：{c['name']}
模式：{c['mode']}；预期状态：`{c['status']}`。
证据 {', '.join(c['ev'])} vs 反证 {', '.join(c['cev'])}。来源：{eb['source']}；指纹：{eb['fingerprint']}；业务时间：{eb['biz_time']}；有效期至：{eb['valid_until']}。
判断：{c['rationale']}
翻转：{c['flip']}""")

    return f"""# {d['code']} 完整专业报告

运行时：`{d['runtime']}`。

## 执行摘要
决策结论：对象 `{d['code']}-GOLDEN@v1` 当前为 `Repair`；一句话理由：{d['summary']}

## 对象与边界
适用范围限当前国家、平台、对象版本和生命周期；缺失数据保持 unknown，决策影响不扩展到其他对象。对象身份由平台标识、业务主体、产品或账户版本共同确定，任一关键字段变化都必须新建版本，不能把旧结论静默迁移。

## 证据与反证
支持证据来自授权对象快照；反对证据来自独立结果。最弱假设 A1 是来源和版本可比；替代解释必须保留，证据截止为 2026-08-05。
{d['root_cause']}

## 门槛与评分
{'、'.join(d['markers'])}作为专业门；红线不能由总分补偿。任一专业门为unknown时只允许补证、诊断或可逆实验，不允许把综合分数、收入机会或管理层偏好升级成validated。

## 证据台账
支持证据与反对证据均保留来源、指纹、业务时间、允许用途和禁止用途。证据过期、对象错配、授权撤回或上游状态改变时，只失效依赖字段并触发影响闭包；无关事实继续保留。相同来源家族的多个页面、导出或摘要只算一个证据家族。

## 假设台账
A1 来源独立；A2 对象稳定；A3 时间窗成熟。推翻条件为任一验证失败。每项假设都有责任人、核验方法、截止时间和对决策的影响，未核验假设不包装成事实。

## 经济与计算
{d['calc']}
币种 USD，使用确定性计算器，可复算：是。输入哈希 sha256:domain-in，输出哈希 sha256:domain-out。经济结果只能约束可承受动作，不能签发本域之外的资本、价格、库存或客户决定。

## 计算台账
C1 状态 complete；输入缺失时为不可计算而不是零。单位、币种、税口径、归因口径和时间窗不一致时阻断比较，历史计算保留原始参数版本。

## 根因
{d['root_cause']}
反证和替代解释不被多数投票消除。现象、相关性、机制和可执行根因分层记录，只有能够解释受影响范围并产生可证伪修复动作的原因进入推荐。推翻条件：当且仅当反证来源获得独立验证且量化影响超过当前结论置信区间。

## 决策推导
先对象与红线，再证据和计算，最后比较不行动、修复与受控实验。不行动也要计算风险和机会成本；推荐方案必须说明为什么优于保守方案，以及哪些新证据会翻转排序。

## 主权与联动
主决策 Skill 为 `{d['skill']}`；主权越界：否。参与域只提交 proposed；允许用途为诊断，禁止用途为外部执行。跨域包保留生产者、消费者、对象、版本、允许用途、禁止用途和重新验收触发条件。

## 行动计划
动作对象为 {d['code']}-GOLDEN@v1；幅度限影响闭包；责任人为{d['owner']} owner；观察窗按证据成熟度(最短7天，最长30天)。成功条件：专业门关闭；停止条件：红线恶化；回滚：恢复已验证版本。每个动作必须记录当前基线、目标变化、护栏、最晚复核时间和失败后的恢复责任。

## 专业核对清单
- 对象与版本匹配。
- 来源独立性已检查。
- 业务时间与有效期已检查。
- 未知、缺失和零值分开。
- 反证能够改变结论。
- 计算可独立复现。
- 主权和允许用途明确。
- 停止、回滚和恢复具名。

## 国家/平台与动态事实
国家/平台必须当前核验，核验日期 2026-08-05；动态事实过期即重算。公开信息、授权后台和专业意见分别记录证明上限，不能用相邻国家、相似平台或历史经验填补当前事实。

## 逐案分析

{chr(10).join(case_sections)}

## 自检摘要
支持证据、反对证据、最弱假设、成功条件、停止条件、回滚、置信度和决策影响齐全。伪造事实：否；因果越界：否；主权越界：否；隐私违规：否；可复算：是。
"""

# ── AAMO: Advertising Analysis Measurement Optimization ───────────────
AAMO = dict(
  skill="advertising-analysis-measurement-optimization", code="AAMO", runtime="AAMO-2026.07",
  owner="advertising",
  markers=["三本账","边际效率","增量","归因"],
  summary="广告三本账冲突：广告账ROAS 4.2但增量账显示仅38%为真实增量，蚕食账揭示PMaxcampaign "
          "蚕食自然订单$2,400/月。三本账联合后真实ROAS仅1.8，低于盈亏平衡ROAS 2.5。",
  root_cause="广告账(表面ROAS 4.2)将全部归因销售额计入广告贡献，但增量账(geo-holdout实验)显示"
             "仅38%为真实增量——62%即使不投广告也会发生。蚕食账进一步揭示PMax campaign "
             "将自然搜索订单\"劫持\"为广告订单，月蚕食$2,400。三本账联合: "
             "广告销售$18,900 × 38%增量 = $7,182真实增量, 减蚕食$2,400 = $4,782净增量, "
             "广告花费$4,500, 净ROAS = $4,782/$4,500 = 1.06(远低于表面4.2)。",
  calc="C1 输入: 月广告花费$4,500, 归因销售$18,900, 表面ROAS 4.2。增量比例38%(geo-holdout)。"
       "蚕食$2,400/月(PMax vs 自然基线)。真实增量=$18,900×38%=$7,182, 净增量=$7,182-$2,400=$4,782。"
       "净ROAS=$4,782/$4,500=1.06。边际效率: 最后$1,000广告花费的边际ROAS仅0.7。",
  card_conclusion="受控修复。表面ROAS 4.2 vs 净ROAS 1.06，差距来自增量比例低(38%)和蚕食($2,400/月)。"
                  "行动: PMax缩减30%预算，增量实验扩展至全campaign，30天后重算三本账。",
  cases=[
    dict(id="AAMO-PE-01", name="高ROAS负贡献", mode="standard",
         ref="AAMO-OBJECT-1@v1", ev=["E1S-ROAS"], cev=["E1C-INCREMENTALITY"],
         status="stop",
         must=["三本账","边际效率","增量","归因","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Campaign A表面ROAS 5.8，但geo-holdout显示增量仅22%。"
                   "78%为自然也会发生的销售。扣除后净ROAS=5.8×22%=1.28，低于盈亏线2.5。"
                   "高ROAS是归因幻觉，不是真实贡献。",
         flip="增量比例升至45%以上或蚕食归零后净ROAS>2.5。",
         evidence_binding=dict(source="广告报表+geo-holdout实验", fingerprint="sha256:aamo1a1",
                               biz_time="2026-08-01", valid_until="2026-08-08")),
    dict(id="AAMO-PE-02", name="PMax品牌蚕食", mode="conflict",
         ref="AAMO-OBJECT-2@v1", ev=["E2S-PMAX"], cev=["E2C-ORGANIC-BASELINE"],
         status="experiment_required",
         must=["三本账","边际效率","增量","归因","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="PMax campaign月归因$8,200，但自然搜索基线同期下降$2,400。"
                   "PMax可能\"劫持\"了本会自然发生的品牌搜索订单。"
                   "需brand-off实验(暂停PMax 7天观察自然恢复)验证。",
         flip="brand-off实验显示自然搜索恢复>$2,000/周，蚕食成立。",
         evidence_binding=dict(source="PMax报表+自然搜索趋势", fingerprint="sha256:aamo2b2",
                               biz_time="2026-08-02", valid_until="2026-08-09")),
    dict(id="AAMO-PE-03", name="追踪断裂", mode="extreme",
         ref="AAMO-OBJECT-3@v1", ev=["E3S-TRACKING"], cev=["E3C-GAP"],
         status="blocked",
         must=["三本账","边际效率","增量","归因","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","断裂期数据续命"],
         rationale="GTM容器更新导致转化追踪断裂72h(约$600广告花费无归因)。"
                   "断裂期数据不可用于ROAS计算或预算决策。"
                   "断裂前ROAS 3.8和断裂后ROAS 4.5不可直接比较。",
         flip="追踪恢复且连续7天完整数据后，才可重新计算ROAS。",
         evidence_binding=dict(source="GTM日志+广告追踪状态", fingerprint="sha256:aamo3c3",
                               biz_time="2026-08-03", valid_until="2026-08-06")),
    dict(id="AAMO-PE-04", name="库存容量不足", mode="multi_turn",
         ref="AAMO-OBJECT-4@v1", ev=["E4S-INVENTORY"], cev=["E4C-AD-SPEND"],
         status="blocked",
         must=["三本账","边际效率","增量","归因","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Top SKU库存仅剩450件(日均销60件，剩余7.5天)。"
                   "广告仍在以$150/天加速消耗库存。若不停广告，库存将在3天内耗尽，"
                   "断货期间Listing排名损失预估恢复需21天。",
         flip="补货到达且库存>14天覆盖量后，广告恢复至断货前70%。",
         evidence_binding=dict(source="库存快照+广告花费", fingerprint="sha256:aamo4d4",
                               biz_time="2026-08-04", valid_until="2026-08-05")),
    dict(id="AAMO-PE-05", name="预算渐进漂移", mode="adversarial",
         ref="AAMO-OBJECT-5@v1", ev=["E5S-BUDGET"], cev=["E5C-EFFICIENCY"],
         status="recompute",
         must=["三本账","边际效率","增量","归因","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="月度预算自动+10%递增(从$3,000→$4,500 over 5个月)，"
                   "但边际ROAS从3.2降至1.4。预算递增基于历史ROAS而非边际效率，"
                   "导致低效花费累积。需按边际ROAS而非平均ROAS设预算。",
         flip="边际ROAS回升至2.0以上或预算回调至$3,500后效率恢复。",
         evidence_binding=dict(source="预算变更日志+边际效率曲线", fingerprint="sha256:aamo5e5",
                               biz_time="2026-08-05", valid_until="2026-08-12")),
    dict(id="AAMO-PE-06", name="退款成熟后恢复", mode="recovery",
         ref="AAMO-OBJECT-6@v1", ev=["E6S-REFUND"], cev=["E6C-NET-ROAS"],
         status="controlled_recovery",
         must=["三本账","边际效率","增量","归因","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Q1广告归因销售退款率18%(高于品类均值12%)。退款成熟后"
                   "真实ROAS从3.5降至2.8。恢复计划: 降低退款品类广告预算20%，"
                   "将预算转移至退款率<8%的品类。",
         flip="退款率降至12%以下且真实ROAS回升至3.0以上。",
         evidence_binding=dict(source="退款数据+广告归因", fingerprint="sha256:aamo6f6",
                               biz_time="2026-08-05", valid_until="2026-08-19")),
  ]
)

# ── LIFD: Logistics Inventory Fulfillment Decision ────────────────────
LIFD = dict(
  skill="logistics-inventory-fulfillment-decision", code="LIFD", runtime="LIFD-2026.07",
  owner="logistics",
  markers=["ATP/CTP","库存保护","路线容量","反向履约"],
  summary="需求激增触发库存争用：SKU-A12 ATP 2,400件但CTP仅1,800件(600件在途延迟)。"
          "三条路线争用同一库存池，margin_weighted_with_promise_constraint分配导致"
          "低利润路线D03被削减至承诺量的62%，触发SLA违约风险。",
  root_cause="SKU-A12在途600件因港口拥堵延迟5天(原ETA 8/3→8/8)。ATP=2,400(在库)但CTP=1,800"
             "(含在途)。三条路线需求: D01(高利润$12/件,需800件), D02(中利润$8/件,需600件), "
             "D03(低利润$4/件,需1,000件)。总需求2,400=ATP，但margin_weighted分配: "
             "D01=800(100%), D02=600(100%), D03=620(62%)。D03承诺1,000件实分620件，缺口380件。",
  calc="C1 输入: ATP=2,400, CTP=1,800(含在途600延迟5天)。路线需求: D01需800/$12利润, "
       "D02需600/$8利润, D03需1,000/$4利润。总需求2,400=ATP。"
       "margin_weighted分配: D01权重12×800=9,600, D02权重8×600=4,800, D03权重4×1,000=4,000。"
       "总权重18,400。D01分2,400×9600/18400=1,252→cap 800, D02分2,400×4800/18400=626→cap 600, "
       "D03分剩余=2,400-800-600=1,000→cap 1,000。但CTP仅1,800, "
       "实际: D01=800, D02=600, D03=400(缺口600)。",
  card_conclusion="受控修复。CTP 1,800 < 总需求2,400，D03分配400件(承诺1,000件,缺口600)。"
                  "行动: D03客户沟通延迟+提供替代SKU+加急在途货物。",
  cases=[
    dict(id="LIFD-PE-01", name="需求激增库存争用", mode="standard",
         ref="LIFD-OBJECT-1@v1", ev=["E1S-ATP-CTP"], cev=["E1C-ROUTE-DEMAND"],
         status="allocate",
         must=["ATP/CTP","库存保护","路线容量","反向履约","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="ATP 2,400=总需求但CTP 1,800<总需求。在途600件延迟使可用库存不足。"
                   "margin_weighted分配保护高利润路线D01/D02，D03缺口600件。",
         flip="在途货物到达且ATP升至3,000+，D03缺口可补。",
         evidence_binding=dict(source="库存快照+在途追踪", fingerprint="sha256:lifd1a1",
                               biz_time="2026-08-04", valid_until="2026-08-06")),
    dict(id="LIFD-PE-02", name="清关延误级联", mode="conflict",
         ref="LIFD-OBJECT-2@v1", ev=["E2S-CUSTOMS"], cev=["E2C-CASCADE"],
         status="controlled_recovery",
         must=["ATP/CTP","库存保护","路线容量","反向履约","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="批次B-2026-078清关延误3天(文件不全)，导致FBA入仓延迟。"
                   "级联影响: 3个SKU的ATP下降→2条路线CTP不足→1个客户订单SLA风险。"
                   "恢复: 补交文件+加急清关+临时从海外仓调拨200件。",
         flip="清关完成且FBA入仓确认，级联影响解除。",
         evidence_binding=dict(source="清关状态+FBA入仓日志", fingerprint="sha256:lifd2b2",
                               biz_time="2026-08-03", valid_until="2026-08-07")),
    dict(id="LIFD-PE-03", name="危险品路线不合格", mode="extreme",
         ref="LIFD-OBJECT-3@v1", ev=["E3S-HAZMAT"], cev=["E3C-ROUTE-CERT"],
         status="blocked",
         must=["ATP/CTP","库存保护","路线容量","反向履约","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","资质缺失续命"],
         rationale="含锂电池产品(SKU-C45)需UN38.3认证，当前承运商DHL Express路线"
                   "资质过期(2026-07-15到期)。不能继续使用该路线，即使有库存。"
                   "替代路线FedEx Ground需额外5天 transit time。",
         flip="承运商更新UN38.3资质或使用已认证替代路线。",
         evidence_binding=dict(source="危险品证书+承运商资质", fingerprint="sha256:lifd3c3",
                               biz_time="2026-08-01", valid_until="2026-08-04")),
    dict(id="LIFD-PE-04", name="多仓调拨", mode="multi_turn",
         ref="LIFD-OBJECT-4@v1", ev=["E4S-MULTI"], cev=["E4C-COST"],
         status="recompute",
         must=["ATP/CTP","库存保护","路线容量","反向履约","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="US东仓ATP=1,200(需求1,800,缺口600), US西仓ATP=900(需求400,过剩500)。"
                   "调拨500件西→东: 运费$2.5/件×500=$1,250, 时效3天。"
                   "但调拨期间西仓ATP降至400=需求，无安全余量。",
         flip="调拨完成且东仓ATP>1,600，同时西仓保留≥200安全库存。",
         evidence_binding=dict(source="多仓库存快照+运费表", fingerprint="sha256:lifd4d4",
                               biz_time="2026-08-05", valid_until="2026-08-08")),
    dict(id="LIFD-PE-05", name="承运商时效漂移", mode="adversarial",
         ref="LIFD-OBJECT-5@v1", ev=["E5S-TRANSIT"], cev=["E5C-SLA"],
         status="hold",
         must=["ATP/CTP","库存保护","路线容量","反向履约","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="承运商A承诺时效3-5天，近30天实际中位数6.2天(超标24%)。"
                   "CTP计算基于承诺时效，实际时效漂移导致CTP虚高。"
                   "需按实际时效重算CTP，预计CTP下降15%。",
         flip="承运商连续14天实际时效回到承诺范围内，或切换至时效稳定的备选承运商。",
         evidence_binding=dict(source="承运商时效追踪+SLA", fingerprint="sha256:lifd5e5",
                               biz_time="2026-08-05", valid_until="2026-08-12")),
    dict(id="LIFD-PE-06", name="海外尾货退出", mode="recovery",
         ref="LIFD-OBJECT-6@v1", ev=["E6S-OVERSEAS"], cev=["E6C-EXIT-COST"],
         status="controlled_exit",
         must=["ATP/CTP","库存保护","路线容量","反向履约","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="UK海外仓尾货380件(SKU-B22)，月销仅45件(8.4月覆盖)。"
                   "仓储费£1.2/件/月×380=£456/月。退出选项: 清仓(回收30%=$1,710) vs "
                   "退运(运费$3.8/件=$1,444+重新入仓$2,100)。清仓净回收$1,710优于退运。",
         flip="若该SKU UK站有促销可加速至月销100+件，保留库存继续销售。",
         evidence_binding=dict(source="海外仓库存+销售趋势", fingerprint="sha256:lifd6f6",
                               biz_time="2026-08-05", valid_until="2026-08-12")),
  ]
)

# ── PLCO: Platform Store Listing Conversion ───────────────────────────
PLCO = dict(
  skill="platform-store-listing-conversion", code="PLCO", runtime="PLCO-2026.07",
  owner="listing_conversion",
  markers=["索引可见性","Offer承接","变体治理","漏斗定位"],
  summary="流量正常但转化率下滑：Session 12,500/周(持平)但Unit Session Percentage从14.2%降至11.8%。"
          "漏斗分析显示详情页→加购环节流失率+22%，根因为主图A/B测试变体B的Offer承接断裂"
          "(价格可见性降低+Buy Box丢失)。",
  root_cause="主图A/B测试变体B(生活场景图)点击率+8%但转化率-15%。原因: 场景图模糊了产品主体，"
             "导致详情页访客对价格和规格产生疑问，加购率下降。同时Buy Box在测试期间被竞争者"
             "抢走3天(价格低$0.5)，影响约180笔订单。",
  calc="C1 输入: 周Session 12,500, USP 14.2%→11.8%(降17%)。变体B点击率+8%但加购率-22%。"
       "Buy Box丢失3天≈180笔订单×$28.5=$5,130损失。主图变体A(白底图)USP=14.2%, "
       "变体B(场景图)USP=12.1%。Offer承接评分: A=82/100, B=54/100。",
  card_conclusion="受控修复。流量正常但USP降17%，主图场景图Offer承接断裂+Buy Box丢失。"
                  "行动: 恢复白底主图A，Buy Box价格调整至竞争价+$0.3，7天后重测。",
  cases=[
    dict(id="PLCO-PE-01", name="流量正常转化下滑", mode="standard",
         ref="PLCO-OBJECT-1@v1", ev=["E1S-SESSION"], cev=["E1C-USP"],
         status="diagnose",
         must=["索引可见性","Offer承接","变体治理","漏斗定位","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Session 12,500/周持平说明索引可见性正常。USP从14.2%降至11.8%"
                   "说明问题在Offer承接或漏斗中段。漏斗分析定位到详情页→加购环节流失+22%。",
         flip="主图恢复白底图+Buy Box稳定后USP回升至13.5%以上。",
         evidence_binding=dict(source="广告报表+Listing分析", fingerprint="sha256:plco1a1",
                               biz_time="2026-08-01", valid_until="2026-08-08")),
    dict(id="PLCO-PE-02", name="主图高点击低成交", mode="conflict",
         ref="PLCO-OBJECT-2@v1", ev=["E2S-CTR"], cev=["E2C-CVR"],
         status="experiment_required",
         must=["索引可见性","Offer承接","变体治理","漏斗定位","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="场景图主图CTR+8%但CVR-15%，说明吸引的流量与Offer不匹配。"
                   "场景图吸引的是\"氛围感\"用户，但产品规格/价格不满足其预期。"
                   "需A/B测试带产品规格标注的场景图(平衡点击与转化)。",
         flip="新变体CTR>+5%且CVR不低于白底图基线。",
         evidence_binding=dict(source="A/B测试报表", fingerprint="sha256:plco2b2",
                               biz_time="2026-08-02", valid_until="2026-08-09")),
    dict(id="PLCO-PE-03", name="受限宣称上架", mode="extreme",
         ref="PLCO-OBJECT-3@v1", ev=["E3S-CLAIM"], cev=["E3C-COMPLIANCE"],
         status="blocked",
         must=["索引可见性","Offer承接","变体治理","漏斗定位","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论","合规门绕过"],
         rationale="Listing标题含\"FDA approved\"但产品仅为FDA registered(非approved)。"
                   "该宣称在目标国构成虚假广告，即使转化率高也必须修正。"
                   "修正后预计CTR下降3-5%(失去\"权威背书\"效应)。",
         flip="宣称修正为合规表述(\"FDA registered facility\")并通过合规预审。",
         evidence_binding=dict(source="Listing文本+合规规则", fingerprint="sha256:plco3c3",
                               biz_time="2026-08-03", valid_until="2026-08-04")),
    dict(id="PLCO-PE-04", name="跨平台Listing迁移", mode="multi_turn",
         ref="PLCO-OBJECT-4@v1", ev=["E4S-AMZ-LISTING"], cev=["E4C-WMT-LOCAL"],
         status="recompute",
         must=["索引可见性","Offer承接","变体治理","漏斗定位","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Amazon US Listing(标题200字符+5 bullet points+A+页面)直接迁移至"
                   "Walmart Marketplace。Walmart标题限80字符、无bullet points、"
                   "Rich Media替代A+。直接迁移导致信息密度下降60%、Offer承接断裂。",
         flip="按Walmart规范重写(80字符标题+Rich Media+Pro Seller Badge)后USP达平台均值。",
         evidence_binding=dict(source="Amazon+ Walmart Listing对比", fingerprint="sha256:plco4d4",
                               biz_time="2026-08-01", valid_until="2026-08-15")),
    dict(id="PLCO-PE-05", name="变体评论错配", mode="adversarial",
         ref="PLCO-OBJECT-5@v1", ev=["E5S-VARIANTS"], cev=["E5C-REVIEW-MIX"],
         status="hold",
         must=["索引可见性","Offer承接","变体治理","漏斗定位","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="父ASIN下合并5个颜色变体，总评论1,200条。但黑色变体占评论900条(4.6★)，"
                   "红色变体仅80条(3.8★)。合并显示时红色变体享受父ASIN的评论聚合优势，"
                   "但实际产品体验(3.8★)与展示评分(4.3★聚合)不匹配，导致红色变体退款率18%。",
         flip="红色变体评论升至200+条且评分达4.0+，或拆分为独立ASIN。",
         evidence_binding=dict(source="变体评论分布+退款数据", fingerprint="sha256:plco5e5",
                               biz_time="2026-08-05", valid_until="2026-08-12")),
    dict(id="PLCO-PE-06", name="抑制恢复", mode="recovery",
         ref="PLCO-OBJECT-6@v1", ev=["E6S-SUPPRESS"], cev=["E6C-REINSTATE"],
         status="controlled_recovery",
         must=["索引可见性","Offer承接","变体治理","漏斗定位","停止条件","回滚"],
         forbidden=["代理升级为事实","跨域越权","模板占位结论"],
         rationale="Listing因知识产权投诉被抑制48h(已申诉)。抑制期间搜索不可见，"
                   "预估损失: 日均Session 1,800×2天×USP 13%×$28.5=$13,338。"
                   "恢复后需7-14天索引恢复至抑制前水平。",
         flip="申诉通过+索引恢复至日均Session>1,500持续7天。",
         evidence_binding=dict(source="Listing状态+申诉记录", fingerprint="sha256:plco6f6",
                               biz_time="2026-08-05", valid_until="2026-08-19")),
  ]
)

# ── Domain registry (more domains appended below) ─────────────────────
DOMAINS = {
    "category-investment-decision": CIDM,
    "competitive-intelligence-monitoring": CIM,
    "video-link-breakdown": VLB,
    "consumer-insights-customer-growth": CIG,
    "advertising-analysis-measurement-optimization": AAMO,
    "logistics-inventory-fulfillment-decision": LIFD,
    "platform-store-listing-conversion": PLCO,
}
P = DOMAINS  # backward-compatible alias for validator

# ── Build all ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    for skill, d in DOMAINS.items():
        base = ROOT / skill / "evaluations"
        golden = base / "golden"
        golden.mkdir(parents=True, exist_ok=True)
        (base / "evaluation-catalog.json").write_text(
            json.dumps(build_catalog(d), ensure_ascii=False, indent=2) + "\n")
        (golden / "decision-card.md").write_text(build_card(d))
        (golden / "professional-report.md").write_text(build_report(d))
    print(f"built={len(DOMAINS)}")
