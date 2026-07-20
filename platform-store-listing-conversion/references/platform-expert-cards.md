# P1 平台专家卡

机器可校验的逐平台深度卡见 [platform-expert-cards.json](platform-expert-cards.json)。该文件逐平台固定对象、页面、诊断、异常、实验、证据和禁止外推，本页仅作为快速路由表。

执行时必须用当前官方/授权资料重验字段、图片、类目、变体、评论、品牌内容、实验和商家控制权。本表定义诊断重点，不固化易变数字。

| 平台 | 原型 | 首要对象 | 深诊重点 | 典型失败 | 必须重验 |
|---|---|---|---|---|---|
| Amazon | 搜索货架 | ASIN/SKU/父子体/Offer | 类目属性、索引、标题图组、变体、Buy Box/可购买、A+/评论语境 | 抑制、索引丢失、父子污染、内容覆盖 | 站点字段、图片/标题、变体、品牌权限 |
| Walmart Marketplace | 搜索货架 | item/SKU/Offer | 内容质量、变体、配送、价格/库存同步 | unpublished、内容冲突、履约承诺错位 | 当前item规范与卖家控制权 |
| eBay | 搜索货架/多卖家 | listing/item specifics/variation | 标题、类目属性、状态、运费退货与兼容 | item specifics缺失、变体错组 | 站点类目与刊登规则 |
| Etsy | 垂直/搜索 | listing/variation/shop | 手工/设计事实、标题标签、图片、个性化、配送 | 权利/真实性风险、个性化错选 | 当前政策、类目和属性 |
| TikTok Shop | 推荐内容电商 | product/SKU/card/PDP | 内容到商品卡承诺、移动首屏、审核、库存/活动 | 素材承诺不一致、审核/同步失败 | 国家开放、字段、内容与商品规则 |
| Temu | 低价/托管 | product/SKU/platform-controlled offer | 平台改写、价格活动、素材审核、履约显示 | 商家控制权误判、页面版本漂移 | 模式、站点、可控字段与审核 |
| SHEIN Marketplace | 推荐/托管混合 | product/SKU/store | 移动呈现、素材、变体、活动和配送 | 平台改写、信息/库存错位 | 国家开放、类目、商家权限 |
| AliExpress | 区域综合 | product/SKU/locale | 多语言属性、变体、税运费、配送与本地化 | 机器翻译失真、站点承诺冲突 | 国家/语言/字段/物流展示 |
| Shopee | 区域综合/推荐 | item/model/shop | 本地标题属性、主图、变体、活动、支付配送 | model错绑、站点复制失真 | 站点类目、图片、促销与履约 |
| Lazada | 区域综合 | item/SKU/shop | 类目属性、内容质量、多语言、变体、配送 | 属性/变体/站点同步失败 | 国家站点字段与内容政策 |
| Mercado Libre | 区域综合 | item/variation/listing type | 本地属性、分期支付、配送、声誉展示 | 类目/属性错配、承诺与履约冲突 | 国家站点、刊登类型和字段 |
| Shopify/DTC | 独立站 | product/variant/PDP/landing/cart/checkout | 速度、移动、导航、PDP、落地页、结账、追踪 | 入口承诺断裂、事件丢失、技术/支付失败 | 主题/app/市场/支付/隐私与事件实现 |

未知平台先完成：平台身份及官方入口、国家/站点、页面原型、对象/版本、可控字段、审核/索引/变体/评论、图片详情、价格库存配送、数据/实验权限、规则证据日期。任一关键项未知时只给条件诊断。
