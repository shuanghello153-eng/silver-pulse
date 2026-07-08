# 信源体检报告（一手 / 二手 / 宽覆盖）

> 生成日期：2026-07-08
> 背景：用户要求「挖掘一手渠道而非二手」（例：AgeClub 多编译自其他源，应找原始出处）。
> 配套改动：新增 7 个一手/原始源；4 个泛科技聚合噪音源降级为 T3。

## 一、结论速览

| 指标 | 数量 |
|---|---|
| 信源总数 | 44（原 37 + 新增 7） |
| T1 核心 | 13 |
| T2 扩展 | 24 |
| T3 参考/观察 | 7 |
| 已降级聚合源 | FinSMEs、Pulse 2.0、TechCrunch、BetaKit |

## 二、一手源（primary）—— 原始发布，优先采用

**海外行业协会 / 研究机构（本次新增）**
- LeadingAge（美国老年服务行业协会）
- Argentum（美国养老社区协会）
- NIC（美国养老地产与投资研究中心）
- NCOA（美国国家老龄化委员会）

**海外银发垂直行业媒体（本就在一手梯队，T1/T2）**
- McKnight's Senior Living / McKnight's Home Care
- Senior Housing News、Hospice News、Home Health Care News
- MobiHealthNews、FierceHealthcare、The Gerontechnologist
- Crunchbase News（融资数据库）、StartUp Health
- AgeTech.com / AgeTech.news / AgeTech Collaborative（AARP）、Mary Furlong
- Creating A New Healthcare、HomeCare Magazine、Modern Healthcare
- HIT Consultant（医疗 IT）、FemTech Insider（女性健康）、Coverager（保险科技）

**政府 / 监管一手（本次新增）**
- 民政部（mca.gov.cn）
- 国务院政策（gov.cn，银发经济/养老服务）
- 中国老龄协会（cncaprc.gov.cn）

**国内银发垂直（二手编译，但银发专属、噪音低，保留）**
- AgeClub、36氪-银发经济、动脉网-养老医疗、Google News-银发经济

## 三、二手 / 聚合源（需降权或强把关）

**泛科技 / 融资聚合（已降级 T3，只进观察池，绝不进精选）**
- FinSMEs、Pulse 2.0、TechCrunch、BetaKit

**新闻稿平台（保留 T2，但需强词把关）**
- Business Wire、PR Newswire、Yahoo Finance、Axios

**宽覆盖关键词聚合（Google News 关键词，T3 发现用）**
- Silver Economy、Aging Tech（原）；gov/mca 关键词式但域名为一手（新）

## 四、关于「AgeClub 是二手」怎么解决

AgeClub 的资讯通常编译自三类原始出处：
1. 海外一手行业媒体（McKnight's / Senior Housing News / Fierce / MobiHealth 等）—— **已在 T1 一手梯队**；
2. 国内 36氪 / 动脉网 —— 已纳入；
3. 企业自身公告（Business Wire / PR Newswire）—— 已纳入；
4. **政府政策 / 协会动态** —— 本次新增的「民政部 / 国务院政策 / 中国老龄协会 / LeadingAge / Argentum / NIC / NCOA」正好补齐这一类原始源。

自动化采集现已能直连这些一手域名（经 Google News 代理），拿到原文而非 AgeClub 的编译稿，**实质性降低对二手媒体的依赖**。

## 五、噪音治理三道闸

1. **两级相关性闸门**：强词（养老/银发/照护/认知症…）命中，或主体在企业库，才算相关；仅「融资/AI」弱词命中则拦截。
2. **聚合源降级**：泛科技聚合源降级 T3，即便漏过闸门也只进观察池，不污染精选。
3. **每日自检**：validator 监控噪音数，反弹（较前次 +30）即告警，状态转 WARN。

> 历史遗留：2026-07-08 已用闸门对存量 173 条过筛，清理 127 条真噪音，保留 46 条纯净内容（见 STATE.md）。
