# 《选题维度升级建议》— Silver Pulse 银脉选题雷达

> 调研对象：顶级银发财经内容创作者的选题逻辑（AgeClub / AgeTimes / 36氪银发 / 动脉网 / McKnight's / Senior Housing News / The Gerontechnologist 等）+ 用户「小爽」亲述的 8 条选题角度。
> 目标：把"人脑选题直觉"翻译成"可量化、可落地的评分维度与推荐理由模板"，直接指导 `config.py` 的 `NEWS_SCORING_DIMS` 与 `scorer.py` / `score_and_merge.py` 的代码升级。
> 原则：不编造数据；凡涉及数据均标注可查来源或明确为"待采集信号"。

---

## 0. 调研结论速览（顶级创作者的共性选题逻辑）

通过公开渠道可查的内容特征归纳（非精确统计，为方法论观察）：

| 创作者 | 可观察的选题偏好 | 公开来源 |
|---|---|---|
| **AgeClub / NewAgingPro** | 偏"产业服务平台"视角：企业战略动向、融资、消费趋势、流量渠道大会；强调"对标海外+国内落地" | ageclub.net 已发布 1000+ 篇产业深度、500+ 篇用户调研（2025.1 公开活动稿） |
| **AgeTimes（AgeClub 英文版）** | 面向海外讲中国银发故事，选题偏"中国模式可输出/可借鉴" | AgeClub 矩阵 |
| **36氪-银发经济 / 动脉网** | 创投/医疗视角：融资事件、IPO、并购、政策；以"信号大、参与者分量重"为选题门槛 | 平台定位 |
| **McKnight's / Senior Housing News** | 垂直老年住区/长期照护：并购、关店、监管（CMS/Medicaid）、人力短缺 | mcknights.com / seniorhousingnews.com 日更选题 |
| **The Gerontechnologist** | 单一专家 IP，选题偏"技术反常识/趋势判断"，强观点、强钩子 | 个人媒体 |

**跨创作者共性（与小爽 8 条高度吻合）：**
1. **"大就有研究价值"** — 头部企业/大金额事件天然是选题（对应小爽角度①）。
2. **"反常识才有钩子"** — 最易传播的是"预期违背"：如 CVS 以 **106 亿美元收购 Oak Street Health**，不到 3 年即计提 **57 亿美元商誉减值并关闭 16 家门店**（来源：homehealthcarenews.com 2025.10.30；emarketer 2025.10.31；CVS Q4-2025 财报）。这是"巨额收购→暴雷关店"的反常识范本，属顶级钩子选题。
3. **"海外为镜、国内落地"** — 国内信息稀薄处，海外案例即稀缺资产（对应小爽角度⑧）。
4. **"看竞品流量差判热点"** — 平时 1000、某篇突然 5000+/上万 = 选题被验证（对应小爽角度④）。
5. **"别人写得好就不写"** — 写之前先搜国内已有报道，覆盖度高且质量好则放弃，能写得更好才写（对应小爽角度④，本方案核心新增信号）。

---

## 1. 建议新增 / 调整的选题维度

> 标注：**[新]** = 本次新增维度；**[调]** = 对现有维度的定义/量化方式升级。
> 每个维度给出：定义、为什么重要（绑定小爽角度）、量化/打分方式、数据来源。

### 1.1 [新] 反常度 `novelty_surprise`（钩子强度）
- **定义**：选题是否包含"预期违背/反常识"元素——大收购后暴雷、高估值后关店、政策利好但企业退场、融资热但模式存疑。
- **为什么重要**：小爽角度②。反常识是传播钩子，也是"写作潜力"的可量化子集，比笼统的"故事性"更易自动判定。
- **量化（0–10）**，由代码规则叠加：
  - 命中"暴雷/减值/关店/停运/裁员/退出"关键词且伴随"收购/融资/IPO/政策利好"前置事件 → +6
  - 金额/规模量级大（≥1亿美元 或 国内 ≥1亿人民币）→ +2
  - 事件类型为 `收购并购` 但出现 `减值/impairment/write-down/closure` → +2（Oak Street 范式）
  - 默认为 0，上限 10。
- **数据来源**：`title + summary` 关键词；`EVENT_MAP` 事件类型；`detect_amount()` 金额提取（已存在）。
- **代码落点**：在 `score_and_merge.py` 新增 `detect_novelty(text)` 返回 0–10，注入维度字典。

### 1.2 [新] 国内覆盖度机会 `cn_coverage_opportunity`（红海/蓝海信号）
- **定义**：同一选题/实体在国内公开渠道已有多少报道、质量如何。**覆盖度低 = 蓝海机会；覆盖度高但质量低 = 可重写；覆盖度高且质量高 = 红海应放弃**（小爽角度④的"别人写得好就不写"）。
- **为什么重要**：这是小爽反复强调的核心决策逻辑，当前引擎完全缺失。
- **量化（0–10，机会分，越高越值得写）**：
  - `coverage_count`（国内相关文章数）< 3 → 9–10（蓝海）
  - 3–10 → 5–8（需看质量）
  - > 10 → 2–4（红海）
  - 再叠加质量修正：若 Top 结果来自 AgeClub/36氪/动脉网 等头部且为深度文 → 机会分 −4；若现有结果多为快讯/浅稿 → 机会分 +2（"能写得更好"）。
- **数据来源（现阶段）**：WebSearch 模拟（见第 4 节）；未来接搜索引擎/公众号文章数 API。
- **代码落点**：新增 `cn_coverage.py` 模块，返回 `{count, top_quality, opportunity_score}`。

### 1.3 [新] 竞品热度差 `viral_gap`（热点验证）
- **定义**：某选题在竞品账号上的流量相对其基线的突增倍数。
- **为什么重要**：小爽角度④"追热点看竞品流量：平时 1000，突然 5000+/上万说明选题热"。
- **量化（0–10）**：
  - `gap = 该文阅读 / 该账号近 30 篇均值`
  - gap ≥ 5 → 10；gap 3–5 → 7；gap 1.5–3 → 4；< 1.5 → 0
- **数据来源**：`SILVER_FINANCE_ACCOUNTS`（config.py 已定义）各账号历史阅读量，需采集基线（见 4.2）。
- **代码落点**：`viral_gap` 字段挂在 article 上，评分时读取；当前可先置 0，待采集。

### 1.4 [新] 读者兴趣匹配 `reader_fit`（写给谁看）
- **定义**：选题命中高互动品类（活力老人/有钱有闲/自费消费/文娱）的程度，相对低互动品类（失能照护/长护险，受众窄但政策价值高）。
- **为什么重要**：小爽角度⑤"文章是写给读者看的"+ 角度⑦"赛道差异"。
- **量化（0–10）**：基于历史互动数据给赛道打"读者兴趣档"：
  - 活力/文娱/自费消费类（老年旅游、再就业、兴趣社群、智能硬件自费）→ 8–10
  - 健康服务/居家照护 → 5–7
  - 失能/长护险/监管政策 → 3–5（读者面窄，但 B 端/政策研究者价值高，不惩罚研究分，只调 reader_fit）
- **数据来源**：`SILVER_FINANCE_ACCOUNTS` 历史文章互动（赞/在看/留言）；当前可用赛道标签粗分，后续用真实互动校准。
- **代码落点**：`READER_INTEREST_TIER` 字典（按 L1 赛道映射），与现有 `CENTRALITY` 档位并列。

### 1.5 [新] 赛道自付能力 `pay_power`（商业研究价值）
- **定义**：该选题所处"人群×支付方"组合的商业自循环能力——活力老人自费市场 > 政策/长护险依赖市场（小爽角度⑦）。
- **为什么重要**：决定"研究价值"而非"新闻价值"。自费市场有真实付费意愿，更易产出可变现选题；长护险市场政策驱动、付费方单一。
- **量化（0–10）**：
  - 活力老人 × 自费 → 9–10
  - 活力老人 × 医保/商保 → 6–7
  - 失能老人 × 长护险/政府买单 → 4–5
  - 失能老人 × 纯自费（少数高端）→ 7
- **数据来源**：企业 L1 分类（`config.py` CATEGORY 体系）+ 赛道标签（活力/失能）+ 支付方关键词（长护险/商保/自费）。
- **代码落点**：`PAY_POWER_TIER` 字典 + `score_and_merge.py` 中按 tag 映射。

### 1.6 [调] 渠道权威性 `source_quality`（原 SOURCE_ADJ 升维）
- **定义**：来源是否来自"优质渠道"——Inc.5000 上榜企业、A2 Collective、Mary Furlong 等策展型来源（小爽角度⑥"Inc.5000 等排名企业一般优质，每年重排，可作渠道来源"）。
- **为什么重要**：把"渠道即选题来源"显式化，而非仅作展示微调。
- **量化**：在 `SOURCES` 配置增加 `curated_channel: true` 标志（Inc.5000 / A2 Collective / Mary Furlong / AgeTech Collaborative），命中 → 维度 +2（上限 10）。
- **数据来源**：config.py `SOURCES` 已含上述渠道，仅需加标志位。

### 1.7 [调] 海外镜鉴稀缺度 `mirror_scarcity`（强化现有 MIRROR_BONUS 逻辑）
- **定义**：国内信息越稀缺、海外越成熟 → 镜鉴价值越高（小爽角度⑧"国内信息匮乏→以海外为镜；国内融资极少、海外极多"）。
- **与 1.2 的关系**：`mirror_scarcity ≈ f(低 cn_coverage, 高海外成熟度)`。可直接由 `cn_coverage_opportunity` 与 `region=overseas` 推导，不单独设维，避免重复计分；保留 config.py 已有 `MIRROR_BONUS=5` 作为企业侧加成。

---

## 2. 现有 5 维评分的权重调整建议

当前 `NEWS_SCORING_DIMS`（config.py:654）：
```
industry 0.20 / signal 0.25 / writing 0.20 / cn_fit 0.20 / urgency 0.15  = 1.00
```

**问题**：signal(0.25) 权重过高，会系统性偏向"大金额事件"，压低反常识小事件与蓝海选题；writing(0.20) 笼统，无法体现"别人写得好就不写"。

**建议升级为 7 维模型**（新增 novelty、cn_coverage 两个核心维度，并把 reader_fit / pay_power 作为"展示+软乘子"接入，不进主权重以免稀释过重）：

| 维度 | 标签 | 旧权重 | 新权重 | 变化理由 |
|---|---|---|---|---|
| industry | 赛道核心度 | 0.20 | **0.15** | 仍重要但需让位给钩子维度 |
| signal | 信号强度 | 0.25 | **0.15** | 降低"唯金额论"，避免大事件独大 |
| writing | 写作潜力 | 0.20 | **0.12** | 拆分为 novelty（钩子）+ 故事性 |
| cn_fit | 国内可比性 | 0.20 | **0.13** | 保持，与 cn_coverage 互补 |
| urgency | 时效紧迫度 | 0.15 | **0.10** | 适度下调 |
| novelty | 反常度/钩子 **[新]** | — | **0.15** | 承载小爽角度②的反常识钩子 |
| cn_coverage | 国内覆盖度机会 **[新]** | — | **0.20** | 承载小爽角度④"别人写得好就不写"，权重最高，因其是差异化决策核心 |

**合计 = 1.00**。

> `reader_fit` 与 `pay_power` 不直接进入主加权（避免维度过多稀释），而是作为：
> - 推荐理由模板的"写给谁/商业价值"段落输入（见第 3 节）；
> - 可选软乘子：`final_score × (1 + 0.05×reader_fit/10)`（默认关闭，待数据校准后开启）。

**config.py 代码改法（示例）：**
```python
NEWS_SCORING_DIMS = {
    "industry":      {"label": "赛道核心度",   "weight": 0.15, "desc": "与银发核心赛道贴合度"},
    "signal":        {"label": "信号强度",     "weight": 0.15, "desc": "投融资/收购/政策事件分量"},
    "writing":       {"label": "写作潜力",     "weight": 0.12, "desc": "差异化角度/故事性"},
    "cn_fit":        {"label": "国内可比性",   "weight": 0.13, "desc": "对中国创业/政策可借鉴度"},
    "urgency":       {"label": "时效紧迫度",   "weight": 0.10, "desc": "是否应本周处理"},
    "novelty":       {"label": "反常度钩子",   "weight": 0.15, "desc": "反常识/预期违背/暴雷"},
    "cn_coverage":   {"label": "国内覆盖机会", "weight": 0.20, "desc": "蓝海机会/红海规避(别人写得好就不写)"},
}
```

---

## 3. 推荐理由模板升级示例（含"国内覆盖度"判断）

现状 `gen_recommendation()` 仅拼接 `事件类型 + 金额 + CHINA_REF 通用句`，无差异化/覆盖度判断。

**升级模板（伪代码逻辑）：**
```
def gen_recommendation(article, tags, cn, novelty, reader_fit, pay_power):
    primary = tags[0]
    rec  = f"【{primary}】{entity}。{novelty_hook(novelty)}"        # 钩子
    rec += coverage_verdict(cn)                                      # 国内覆盖度判断 ★核心
    rec += f" 读者侧：{reader_fit_desc(reader_fit)}；"               # 写给谁
    rec += f"商业侧：{pay_power_desc(pay_power)}。"                  # 自付能力
    rec += CHINA_REF.get(primary, "值得关注其对国内银发经济的参照意义。")
    return rec
```

**`coverage_verdict(cn)` 三态输出（体现小爽"别人写得好就不写"）：**
| cn_coverage 状态 | 输出话术 |
|---|---|
| 蓝海（count<3） | "国内尚无深度对标报道，属蓝海选题，建议抢先以海外为镜做拆解。" |
| 红海·高质量（count>10 且 top 来自头部深度） | "国内已有 AgeClub/36氪 等优质深度报道，同质化风险高，不建议重复；除非拿到独家数据/新进展。" |
| 可重写（count>10 但多为快讯/浅稿） | "国内已有报道但偏快讯、缺乏深度，存在'写得更好'的差异化空间，建议补齐商业逻辑与数据。" |

**实例（Oak Street Health 范式）：**
> 【收购并购】CVS 以 106 亿美元收购 Oak Street Health，不到 3 年即计提 57 亿美元商誉减值并关闭 16 家门店——巨额收购反噬，强反常识钩子。国内覆盖度：中等，已有快讯但缺"并购估值/关店逻辑"深度拆解，可重写。读者侧：偏 B 端创投/养老运营研究者；商业侧：失能/照护支付方依赖型，政策与并购风险参考价值高。可对标国内"保险+养老社区"模式的并购踩坑。

---

## 4. "国内文章覆盖度"信号的落地路径（WebSearch 模拟 → 未来 API）

当前无国内文章覆盖度 API。分三阶段落地，每阶段均可独立运行不阻塞主流程。

### 4.1 阶段一：WebSearch 模拟（现在即可做，低成本）
- **触发**：对每条进入 `watch/high` 候选的 article，提取 `entity`（企业名/核心关键词）。
- **查询构造**：`"{entity} 银发 OR 养老 OR 融资 OR 模式"`（中文）+ 可选英文回查。
- **指标提取**：
  - `coverage_count` = 返回结果数（去重域名后），以 10/20/30 为分档阈值；
  - `top_quality` = 若 Top3 结果含 `ageclub.net / 36kr / vcbeat / 动脉网` 且标题含"深度/拆解/研究/报告" → `high`，否则 `shallow`；
  - `opportunity_score` = 由 1.2 规则映射为 0–10。
- **成本**：每条候选 1 次搜索；每日候选通常 < 30 条，可控。
- **代码**：`cn_coverage.py::estimate_via_websearch(entity) -> dict`，失败/限流时返回 `{"count": None, "opportunity_score": 5, "source": "fallback"}` 不阻断。

### 4.2 阶段二：基线采集 + 竞品热度差（1–2 周）
- 为 `SILVER_FINANCE_ACCOUNTS` 各账号建立**阅读量基线**（近 30 篇均值），支持 `viral_gap` 与 `reader_fit` 校准。
- 用阶段一的 `coverage_count` 反哺 `cn_coverage` 真实分布，替换硬编码阈值。

### 4.3 阶段三：接 API（未来）
- 候选 API：微信公众号文章搜索 API（需授权）、百度资讯检索 API、天眼查/企查查"新闻"接口、自建国内银发文章索引库（爬取 AgeClub/36氪/动脉网 RSS + 站内搜索）。
- **接口契约**（建议）：`get_domestic_coverage(entity) -> {count:int, top_sources:[str], top_quality:enum, fetched_at:ts}`。
- `cn_coverage.py` 顶层只暴露 `estimate(entity)`，内部 `if API_AVAILABLE: return api_call() else: return estimate_via_websearch()`，**主流程零改动切换**。

---

## 5. 代码改动清单（给工程师，可执行）

| 文件 | 改动 |
|---|---|
| `config.py` | ① `NEWS_SCORING_DIMS` 改为 7 维新权重；② `SOURCES` 加 `curated_channel` 标志（Inc.5000/A2/Mary Furlong 等）；③ 新增 `READER_INTEREST_TIER`、`PAY_POWER_TIER`、`NOVELTY_KEYWORDS`、`CN_COVERAGE_BANDS` 字典 |
| `score_and_merge.py` | ① 新增 `detect_novelty(text)`；② `gen_recommendation()` 接入 `cn/novelty/reader_fit/pay_power` 四参；③ 调用 `cn_coverage.estimate()` |
| `cn_coverage.py` | **新建**：`estimate(entity)` → WebSearch 模拟 + 未来 API 开关；返回 `{count, top_quality, opportunity_score, source}` |
| `scorer.py` | `build_scoring_prompt` 维度描述同步更新为 7 维；若用 AI 打分，增加 novelty/cn_coverage 两项输出要求 |
| `collector.py` | 候选进入评分前先跑 `cn_coverage.estimate`（仅对 watch/high 候选，控成本） |

---

## 6. 关键边界与免责
- 本方案所有"阈值/权重"为**初始可运行默认值**，需用阶段二真实互动数据回归校准，避免拍脑袋固化。
- `novelty`、`cn_coverage`、`viral_gap` 为**启发式信号**，存在误判（如"关店"可能是战略收缩非暴雷），推荐理由模板应保留"建议人工复核"提示。
- 凡引用事实（Oak Street 106 亿/57 亿减值/16 关店）均来自公开财报与媒体（homehealthcarenews 2025.10.30、emarketer 2025.10.31、CVS Q4-2025），可复核；其余为方法论建议，非统计结论。
