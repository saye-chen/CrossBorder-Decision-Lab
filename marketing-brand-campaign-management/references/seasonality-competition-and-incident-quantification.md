# 季节、竞争与事故量化

## 季节基线

数据充足时优先使用STL或等价趋势—季节—残差分解；轻量工具使用多年度“月值/年度均值”构造季节指数：

`season_index_m = average_y(value_y,m / annual_mean_y)`

指数和应接近12。少于两个完整年度、结构变化或缺货严重时，季节指数只能作情景。

使用`seasonality_competition.py`计算季节指数、事件峰值和节后透支。活动反事实必须包含趋势、季节、竞争和库存，而不是简单同比。

## 节前爬坡与节后透支

- 估计峰值前各期相对基线的爬坡率；
- 峰值后实际低于自然基线的部分计入pull-forward；
- 恢复窗覆盖到累计缺口停止扩大；
- 将透支量传给`pull_forward_cannibalization.py`计算贡献损失。

## 竞争动态

CIM提供带版本的竞品促销、价格、SOV、活动和渠道事实；MBCM估计其对本方结果的影响。

基础竞争模型：

`own_outcome_t = alpha + beta × competitor_pressure_t + controls + error`

同时报告beta、标准误、拟合度与替代解释。SOV与SOM是诊断关系，不是固定定律；ESOV不能自动承诺增长。

姿态规则：

- beta显著为负且本方SOV不足：比较对冲与避让；
- beta为负但本方差异/容量不足：优先避让；
- beta接近0且区间窄：可忽略或独立测试；
- 区间宽或竞争事实过期：`inconclusive`。

竞争性出价成本由AAMO估计；MBCM只把成本通胀情景纳入渠道和活动方案。

## 事故经济影响

受控前后差：

`incident_effect = Δaffected - Δcontrol`

控制单元应尽量匹配市场、平台、产品和季节，且未受事故扩散。

恢复差距可用指数衰减：

`gap_t = gap_0 × decay^t`

对正gap取对数回归，得到decay和半衰期。拟合差、二次舆情或结构断点出现时不得使用单一恢复曲线。

## 修复还是自然恢复

`repair_incremental_NPV = Σ incremental_recovery_t/(1+r)^t - repair_cost`

只有修复增量NPV为正、客户/法律/品牌门通过且存在停止规则时，才提出修复投入候选。MBCM不自动发布回应或补偿。

使用`incident_recovery_quantification.py`计算受控影响、恢复半衰期和修复增量NPV。
