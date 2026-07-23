# Offer需求响应与渠道曲线

## Offer响应

会计守恒只回答“方案发生后赚不赚钱”；响应模型回答“折扣变化会带来多少订单”。

基础弹性模型：

`log(Q) = alpha + elasticity × log(P) + controls + error`

价格弹性通常为负，但不得预设。历史回归须控制季节、库存、竞争、媒体、页面和产品版本；无法控制时只作情景。至少三个正价格—订单点才可拟合，少于八点或拟合弱时动作上限为受限测试。

候选折扣不得假设线性。对每个折扣网格计算：

1. 新价格；
2. 弹性预测订单；
3. 疲劳/参考价修正；
4. 全核销成本；
5. 拉前、蚕食与欺诈；
6. 成熟贡献和边际贡献。

最优折扣是可行网格中成熟贡献最大者，不是订单最大者。价格底线仍由D06确认。

## 参考价格与疲劳

- 明确外部参考价、内部历史参考价和活动展示参考价。
- 频繁促销会下调消费者内部参考价；用活动频次、折扣深度与恢复期估计疲劳。
- 当前工具的`fatigue_rate`是显式情景参数，不是自动识别结果；没有历史变化时不得声称已估计。
- 对15%→20%折扣必须比较边际订单与边际折扣成本，不能按比例外推。

使用`offer_response_optimization.py`估计log-log弹性并进行非线性网格优化；使用`offer_economics.py`完成全成本守恒。

## 渠道adstock与饱和

几何adstock：

`A_t = Spend_t + decay × A_(t-1)`

Hill饱和：

`Response_t = Max × A_t^shape / (A_t^shape + half_saturation^shape)`

参数含义：

- decay：影响保留率；
- half_saturation：达到半最大响应的adstock；
- shape：曲线陡峭度；
- max_response：该渠道当前情景的响应上界。

这些参数必须由历史实验、MMM或明确情景提供。使用`channel_curve_estimation.py`在声明的decay、half-saturation和shape网格中拟合参数并报告R²与候选数量；使用`channel_response.py`计算adstock、饱和响应与渠道交互。候选网格之外不外推“最优参数”。

## 频次与渠道交互

频次响应应至少区分首次有效触达、累积证明、饱和和疲劳区。没有用户级频次授权数据时，只使用聚合频次桶。

渠道交互项：

`Total = Σ channel_response + Σ beta_ij × response_i × response_j`

正交互表示协同，负交互表示抢单或替代。交互系数没有实验/MMM支持时只能做敏感性情景。

## Pacing

- continuous：稳定需求、需要持续学习或渠道衰减快。
- flighting：强季节窗口、固定事件或需要集中声量。
- pulsing：维持基础存在并在关键窗口加压。

三种节奏必须保持预算守恒，并比较容量、学习速度、疲劳、竞争成本和活动窗口，而不是用同一平均ROAS排序。

## 归因窗口敏感性

至少使用短、中、长三个窗口重算渠道排序。若排序随窗口翻转，则资源方向必须标记`window_sensitive`，优先通过holdout或增量实验解决，不能选择对目标渠道最有利的窗口。
