# 随机、集群、Switchback 与干扰

## 个体与分层随机

保存随机化算法、seed/entropy 来源、strata、分配概率、生成时间和不可变 assignment 表哈希。分析按设计纳入 strata；小 strata 合并必须预登记。随机化后的“基线显著性检验”不用于决定是否调整，重点检查分配实现与系统性缺失。

## 集群随机与 Geo Holdout

先定义 cluster-average 还是 individual-average estimand；簇大小与效果相关时二者不同。报告簇数、每臂簇数、ICC、簇大小分布、设计效应、匹配/分层、cluster leverage 和有效自由度。少簇使用经验证的 CR2、wild cluster bootstrap 或随机化推断；普通个体稳健标准误不合格。

Geo 设计还需冻结：地理边界、媒体泄漏、通勤/配送 spillover、共同冲击、pre-fit、匹配变量、同时活动和平台算法变化。高 pre-fit 不自动证明因果；保留随机化或合格 placebo 分布。

## Switchback

定义切换单位、period 长度、序列、处理平衡、washout/burn-in、最大 carryover order、时区和周期性。period 必须长于主要响应/履约机制的合理滞后，或显式建模 carryover。推断需匹配随机化 scheme 并处理 serial dependence；把每个订单当 iid 会夸大精度。

至少报告：period 数、有效切换数、处理序列、丢弃 washout 后样本、lag 敏感性、时段/星期平衡、ACF 或随机化推断诊断、同时系统变化。严重 carryover 或单向时间趋势未控制时最高 CE3。

## 干扰与溢出

SUTVA 不应被默认为“肯定成立”。说明干扰图或 partial interference 边界、exposure mapping（例如自身处理×邻居处理比例）、assignment probabilities、direct/spillover/total estimand。若无法识别，只能生成 protocol 并交由外部合格分析；不能把受污染 ITT 称为纯直接效应。

## 后端边界

集群、Switchback、Geo 和网络方法在当前底座走 `verified_backend` 或 `protocol_only`。只有后端 registry 为 verified、版本匹配、parity 有效、关键诊断完整时才可执行；否则返回明确失败和数据/协议准备结果。
