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
9. LC-1/LC-2 高分场景是否仍受生命周期动作上限约束，未输出批量备货、重仓或多平台铺开。
10. 公开页面事实是否保留为观察数据，只有代理信号推导出的销量、需求强度和竞争结论被标为分析假设。
11. 卖家画像为默认假设时，是否避免直接给出预算比例、首批数量和重仓动作。
12. 店铺结构、价格带和新品节奏数字是否注明为需按国家、平台、品类和卖家能力校准的研究先验。

## 轻量烟测

不联网时可只验证路由和报告结构；联网压测时必须核验当前价格、费率、法规、平台规则和竞品页面。

轻量烟测通过标准：

- 10 个场景均可映射到决策类型、对象类型和输出格式。
- 未覆盖国家和平台会触发 universal fallback。
- 报告模板能覆盖所有输出格式，不出现“无模板可用”的场景。
