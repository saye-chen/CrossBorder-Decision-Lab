# Amazon Ads

## 对象与最小诊断单元
覆盖 Sponsored Products、Sponsored Brands、Sponsored Display、DSP 及账户当前可见能力。最小单元为 Marketplace × 推广 ASIN × 查询/定向 × 广告位 × 购买 ASIN × 归因窗；品牌、品类、竞品、自动和再营销不得混池解释。

广告对象血缘与运行字段以 [`amazon-ads-operating-model.json`](../amazon-ads-operating-model.json) 为准：Ads Profile → Campaign → Ad Group/Line Item → Ad/Creative → Target → Query/Search Term → Placement/Inventory Source → Promoted Object → Outcome Object。任何报告缺少其中一层，都必须标记对象粒度不足，不能用 Campaign 平均值代替目标、搜索词或购买 ASIN。

### 广告类型与定向分层

- Sponsored Products：自动、关键词、商品和类目定向；重点看搜索词发现、匹配类型、否定覆盖、广告位、推广/购买 ASIN 与零售资格。
- Sponsored Brands：关键词、商品和类目定向；另查品牌授权、品牌素材版本、Brand Store/落地页版本和品牌词/非品牌词/竞品词分层。
- Sponsored Display：上下文、商品和受众定向；必须拆开 prospecting、retargeting、cross-sell，以及 click-through/view-through 归因。
- DSP：受众、上下文、再营销和拓新；必须有受众规则、频次政策、素材/目的地版本与增量测量设计，不能套用搜索广告 ROAS 或 Sponsored Products 出价曲线。

### 低交付根因门禁

低展示、低点击或不消耗按以下顺序排查：G1 Profile/账户/站点和主体 → G2 Campaign/广告组/广告/目标资格与版本 → G3 推广对象的可购买、Featured Offer、库存、价格、配送和页面 → G4 查询/目标/受众/广告位是否可解释 → G5 归因类型、窗口、币种和成熟度 → G6 ASIN/Offer 成熟贡献与边际经济。G1 失败阻断，G3 失败冻结放量，G4 只能诊断，G5 证据不足为 inconclusive，G6 缺失不得 scale；不能把“提高竞价”当成默认修复。

### 日、周、月工作流与报告路由

每日主板至少覆盖资格/零售准备度、搜索词与定向、预算节奏和广告位；周报加入 Campaign 结构、重复目标、收割/否定队列、购买 ASIN 结构、品牌词蚕食和边际贡献；月度加入归因与增量、成熟退款、库存护栏和组合冲突。标准报告路由为 `amazon_ads_daily_operations`、`amazon_search_term_target_memo`、`amazon_ads_profit_incrementality_memo` 和 `amazon_ads_incident_recovery_card`。每条结论必须给出证据、替代解释、动作上限、成功/停止条件和回滚引用。

## 数据与测量门禁
先查可售、Featured Offer、库存、价格、评价、配送、详情页和零售准备度，再查广告资格。保存点击/浏览归因窗、品牌光环、New-to-brand、购买 ASIN、退款成熟、币种和时区。业务报告与广告报告对象不一致时先对账。

## 店铺画像与广告归因路由

Amazon 广告分析必须先绑定 `store_profile_id`、Seller ID/卖家账户、法定主体、Marketplace site、销售项目和 Ads Profile。Seller Central 3P、Vendor Central 1P、授权经销商以及 FBA/MFN 不得共用一个账户平均值或零售准备度结论。至少保留 `profile_id`、`seller_account_id`、`marketplace_id`、`campaign_id`、推广 ASIN、购买 ASIN、placement、targeting、date 和 attribution window；缺少 Profile、站点或时间窗时，广告与店铺销售不得合并，结论降为 `conditional/inconclusive`。

Ads Profile 是广告归因边界，不等于品牌权限或 Seller Account。Brand Store/A+ 资产只能在品牌授权和目录所有权证据通过后交给 PLCO；B2B、跨店铺、跨站点或跨履约模式的销售、库存和利润必须在店铺画像层重新分桶。任何放量建议仍需同时通过零售资格、Featured Offer、可售库存、配送承诺和成熟贡献利润门禁。

### 按店铺类型的运营节奏

- 3P 品牌 + FBA：日内看零售准备度、可购买、预算和推广/购买 ASIN；每日看 FBA 可售/预留/入仓与页面承接；每周看广告边际、品牌词蚕食和成熟贡献。
- 3P 品牌 + MFN：把配送承诺、迟发/取消、自履约容量和退货护栏放在日内/每日优先级，不能套用 FBA 服务指标。
- 授权经销商：把授权有效期、购买成本、价格政策、Featured Offer 竞争和 Offer 退出放在每日/每周主板，不使用品牌 Owner 的 Brand Store 或品牌增量指标。
- Vendor Central 1P：广告与 3P 销售分开；每日优先核采购/零售资格和内容责任，每周/月核采购订单、批发价格、扣款/索赔与渠道冲突。

所有日常指标至少声明 `metric_scope`、`metric_class`（leading/diagnostic/outcome/guardrail/data_quality）、时间窗、Ads Profile、站点和证据 ID；缺失不记为 0，任何跨店或跨站汇总必须重新验收。

## 平台特有诊断
按资格/零售准备度 → 展示与预算 → 查询和定向 → 广告位 → 推广 ASIN/购买 ASIN → 转化 → 成熟利润排序。低展示不能直接归因竞价；高点击低购需分离查询错配、详情承接、价格配送和库存。品牌词高 ROAS需验证自然蚕食。

## 利润、放量与退出
ACoS/TACoS只是平台效率口径；贡献利润必须扣退款、平台费、FBA/履约、优惠和广告费。放量只接受成熟商品级边际贡献为正且库存/配送护栏通过；观察窗未成熟、边际转负或零售门禁失败时停止并回滚。

## 禁止推断
不得把账户平均 ACoS、品牌光环销售或 New-to-brand 直接当增量；不得把一个 Marketplace 的竞价、归因或零售规律外推到另一站点。动态规则执行时核验。


## Amazon 平台 DNA

- 竞价与交付：以商品/查询/定向和广告位竞争为核心；零售资格、Featured Offer、库存、价格与配送可在出价之外切断交付。
- 优化反馈：推广 ASIN 与购买 ASIN、品牌光环、自动/手动定向和广告位调节必须分开；搜索词收割不能把自动发现表现重复归功于手动活动。
- 归因差异：点击/浏览窗、New-to-brand、品牌光环和退款成熟度随产品/报表而异，执行日核验；TACoS只描述广告销售与总销售关系，不证明自然增量。
- 特有失败：丢失购物车、父子体/购买ASIN错配、搜索词与商品相关性弱、预算集中在品牌词、跨站点币种混合。
- 诊断反事实：品牌词暂停/地域或查询层留出、购买ASIN利润重述、广告位边际曲线；禁止直接复制另一 Marketplace 阈值。

## 可验证机制与诊断

- 机制边界：不声称 A9/COSMOS 或广告排序存在公开固定权重；只把竞价、相关性、广告位竞争和零售资格作为可验证机制层。
- 可控输入：出价、预算、查询/商品/受众定向、广告位调节、推广 ASIN 与否定项；Featured Offer、库存和配送作为外部门。
- 可观测代理：搜索词、展示份额/广告位、推广与购买 ASIN、预算状态、零售资格变化；代理信号不得冒充隐藏排序分。
- 证伪路径：保持零售状态稳定后做查询/广告位阶梯；若提高竞价仍不交付，转查资格、相关性和可售性而非继续加价。
- 竞争反馈：品牌词、竞品词和类目词分别建边际曲线；自动发现→手动收割必须去重归功并记录学习重置。
