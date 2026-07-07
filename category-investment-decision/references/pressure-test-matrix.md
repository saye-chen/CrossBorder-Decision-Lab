# 压力测试矩阵

## 目的

用于验证 Skill 是否满足全场景、任意国家、任意平台和专业报告输出要求。每次大版本升级后，至少抽取 3 个场景生成本地 Markdown 样例；完整回归时跑完 10 个场景。

## 10 个标准场景

| ID | 场景 | 覆盖能力 | 期望输出 |
|---|---|---|---|
| PT-01 | 美国 Amazon 商品进入 | 标准投决、Amazon、利润、VOC | Investment Memo |
| PT-02 | 日本 Rakuten 国家本地化 | 任意平台、本地化、日语/进口/税务 | Country Entry Matrix + Platform Fit |
| PT-03 | 德国 Amazon 合规敏感品类 | 欧盟、合规、标签、EPR/责任人 | Investment Memo + Compliance Checklist |
| PT-04 | TikTok Shop 内容型商品 | 内容电商、达人、素材疲劳、CPA | Investment Memo + Platform Fit + Experiment Module |
| PT-05 | Temu 低价供应链品 | 核价、低价、退货、供给效率 | Supply Chain / Platform Fit Brief |
| PT-06 | Shopify/DTC 英雄品 | CAC、AOV、复购、LTV、落地页 | DTC Investment Memo |
| PT-07 | Shopee 东南亚国家比较 | 区域拆国家、COD、低客单、物流 | Country Entry Matrix |
| PT-08 | 老品诊断 | 流量、转化、竞品、评论、广告、季节 | Post-launch Operating Review |
| PT-09 | 竞品监控月报 | S/A/B 分级、告警、重新深挖 | Monitoring Monthly Report |
| PT-10 | 失败品退出复盘 | 初始假设、损失、学习、下次规则 | Exit Review Memo |

## 验收标准

每个场景必须检查：

1. 是否正确识别决策类型、对象类型和输出格式。
2. 是否加载国家或平台的 universal fallback。
3. 是否包含决策页或对应经营决策页。
4. 是否区分观察数据、计算结果和分析假设。
5. 是否有 Evidence/Assumption Ledger 或明确来源/证据等级。
6. 是否给出下一步动作和 Stop 条件。
7. 是否避免把未验证代理信号包装成后台精确数据。
8. 用户要求 demo/压测/完整报告时，是否生成本地 Markdown。

## 轻量烟测

不联网时可只验证路由和报告结构；联网压测时必须核验当前价格、费率、法规、平台规则和竞品页面。

轻量烟测通过标准：

- 10 个场景均可映射到决策类型、对象类型和输出格式。
- 未覆盖国家和平台会触发 universal fallback。
- 报告模板能覆盖所有输出格式，不出现“无模板可用”的场景。
