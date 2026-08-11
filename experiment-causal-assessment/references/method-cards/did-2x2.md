# 方法卡：2×2 Difference-in-Differences

- **目标量**：在共同趋势、无 anticipation、稳定构成和无差异并发干预下的 ATT。
- **实现边界**：native 仅支持 treated/control × pre/post 的独立重复横截面 cell summary；估计为两组变化之差，方差为四个独立 cell 均值方差之和。
- **非覆盖**：panel/cluster dependence、多个 pre/post、错峰处理和异质动态效应必须走 verified backend。
- **诊断**：制度共同趋势论证、composition、placebo outcome/time、并发活动、functional-form sensitivity。只有一个 pre-period 不能经验检验平行趋势。
- **禁止**：错峰场景朴素 TWFE、用不显著 pretrend 证明平行趋势、把 ATT 外推为全总体 ATE。
- **CE 上限**：CE4；若识别合同或敏感性不完整则最高 CE3。
