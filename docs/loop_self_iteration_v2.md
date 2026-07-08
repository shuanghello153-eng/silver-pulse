# Silver Pulse · Loop Engineering 自我迭代优化设计（V2）

> 调研 / 撰写：general-purpose-1（Loop Engineering 架构研究员）
> 日期：2026-07-08
> 面向对象：项目 owner（小爽）
> 配套文档：`loop_engineering_design.md`（V1 三层映射）、`0722_token_downgrade_plan.md`（成本基线）

---

## 一、执行摘要

当前 Silver Pulse 已经把"写查分离"的骨架搭起来了——L2 安检门（`loop_audit.py`，当前 0 CRITICAL / 3 WARN）、L2 安全气囊（`noise_spike_guard.py`，从未触发）、L3 反馈回灌（`feedback_loop.py`，代码完整但 `feedback.jsonl` 为 0 条待激活）。但**这三层都还是"规则驱动 + 人工定参"**，没有真正从自己的运行数据里长出自适应能力。本设计回答一个问题：**如何让这套 Loop 在不烧模型积分的前提下，用历史数据持续自我调优**。核心结论先行——经核对，本流水线的评分/推荐/聚类/阈值**全部已经是规则兜底（零模型）**，因此 7 个进化方向里 6 个可以**零模型成本**落地；真正需要模型的只有一个可选增强点（推荐理由 LLM 化）。下表把"进化"拆成可落地的数据闭环，并给出每个方向的改动位置（文件名 + 函数 + 行号）、复杂度、收益与优先级。

---

## 二、当前架构诊断（SWOT）

### 优势 Strength
- **写查分离已成型**：`loop_audit.py`（查）与 `noise_spike_guard.py`（进化）职责清晰，互不直接改架构。
- **护栏机制成熟**：`noise_spike_guard._backup_config()`（config.py:113-120）改动前 git 备份；`pitfalls_log.json` 留痕；`WEIGHT_BOUNDS`（feedback_loop.py:28-35）+ `DELTA_CAP=0.03`（:36）夹紧权重，不会失控。
- **零模型成本基线已立**：据 `0722_token_downgrade_plan.md`，评分/聚类/推荐全规则兜底，token 只来自"自动化框架读 stdout + 写报告"，降级空间大。
- **反馈采集链路已通**：网站 ⭐收藏 → `feedback.jsonl` → `feedback_loop.py` 已能解析 news/ent 收藏并产出 `user_pref.json` 与 `feedback_report.md`。

### 劣势 Weakness
- **所有阈值硬编码**：`SELECT_THRESHOLDS`（config.py:832-836）、`CLUSTER_SIM_THRESHOLD=0.82`（:842）、`SILVER_WEAK_KEYWORDS`（:784-794）、`EVENT_BOOST`（:848）、`SOURCE_TIER_WEIGHTS`（:991）都是拍脑袋定值，不随环境漂移。
- **聚类逻辑休眠**：`CLUSTER_SIM_THRESHOLD` 已定义，但 `scored_latest.json` 里 `cluster_id` 恒为 `null`（score_skill.py:112-113 仅置 None），`generator.py` 读取 `cluster_id`（:609/:751）却永远拿到空值——**聚类从未真正激活**。
- **推荐理由重复严重**：L2 审计已报 `max_dup=14`（data/L2_AUDIT.md:26），根因是 `recommend.py gen_recommendation()`（:61-123）的 `CHINA_REF` 模板固定 + 大量条目 `tags[0]=同事件类型` + `subj` 退化。
- **进化层"无米下锅"**：`feedback.jsonl=0` 条，`noise_spike_guard` 从未触发（环境太干净）——所有自适应逻辑都**缺训练/触发样本**，这是当前最大的"伪闭环"风险。
- **可观测性只有单点**：`STATE.md`（validator.py:273-287）是静态状态行，`L2_AUDIT.md`（loop_audit.py:443-520）是单日快照，**没有跨日趋势**。

### 机会 Opportunity
- 历史数据已积累：`data/history.json`、`data/scored_latest.json`、`data/raw_2026*`、各 `run_daily_*_*.log` 提供了做自适应统计的原材料。
- 进化动作本身都是"调阈值/关键词/权重"这类**零模型、纯文件写入**，完美契合已建立的护栏。
- 用户收藏行为一旦开始（配 Token 上传 `feedback.jsonl`），L3 立刻从空转变实跑。

### 威胁 Threat
- **伪进化**：没有真实反馈样本时，自适应算法只能靠内部指标（精选率/噪音率）自娱自乐，可能调出"看起来健康但用户不买账"的假象。
- **阈值漂移失控**：若自适应步长过大或目标函数错位，可能把精选池改窄到空集或宽到垃圾堆。
- **成本陷阱**：一旦把"自进化"误接成"每轮调 LLM 重新打分"，免费期后积分会失控（本设计明确规避）。

---

## 三、7 个方向的详细方案

> 标注约定：🔵 = 零模型成本（纯代码/统计）；🟡 = 可选模型增强（可降级）

### 方向 1 · 数据驱动的阈值自适应
**问题**：`SELECT_THRESHOLDS`（config.py:832-836，按 T1/T2/T3 各定 high/watch）、`CLUSTER_SIM_THRESHOLD=0.82`（:842）都是定值。环境会变（某信源变差、某赛道爆发热点），定值阈值会慢慢失准。

**方案**（🔵 零成本）：
1. **先激活聚类**（前置依赖）：实现 `selection/cluster.py`（当前缺失），在 `reapply_centrality.py main()`（:102-126）之后跑余弦相似度，把相同 `(entity_name, event_type)` 且 cosine>阈值的条目归入同簇、写回 `cluster_id`，并对非主条目施加 `CLUSTER_NONMAIN_PENALTY=1.5`（config.py:843）。
2. **阈值自适应引擎**：新增 `adapt_thresholds.py`（在 `run_daily.py STEPS`，:24-51 末尾插入），逻辑：
   - 读 `data/threshold_history.json`（新增，记录每日 噪音率/精选率/收藏命中率/当前阈值）。
   - 定义目标函数 = **精选率目标区间 15%–25%**（避免空集或垃圾堆）+ 收藏命中率（有反馈后接入）。
   - 若昨日精选率 < 15% → 按小步长 **+0.1** 调低 watch/high 阈值（夹紧下限：high≥4.0 / watch≥3.0）；若 > 25% → **−0.1** 调高。每轮只动一档、幅度 ±0.1，且**写入 `data/threshold_override.json` 覆盖层**（不直接改 config.py 源码，遵循护栏），`reapply_centrality` 读取时优先用 override。
   - `CLUSTER_SIM_THRESHOLD` 自适应：统计历史同事件簇内 cosine 分布，取 **P90 分位数**作为新阈值（初始 0.82 作为冷启动值），同样走 override 层。
3. **护栏沿用**：改动前 git 备份 config（复用 `_backup_config`），写入 `pitfalls_log.json`（复用 `_log_pitfall`）。

**实现复杂度**：中（聚类激活 + 统计引擎约 150 行）
**预期收益**：高——减少人工调参，自动吸收信源质量漂移；聚类激活还能去重、降噪声。
**优先级**：P1（月内）

---

### 方向 2 · A/B 测试框架（评分权重）
**问题**：`NEWS_SCORING_DIMS` 6 维权重（config.py:818-829）与 `feedback_loop` 的 ±0.03 微调都**没有对照验证**——我们不知道"调了是不是真的更好"。

**方案**（🔵 零成本）：
1. 新增 `selection/ab_test.py`，引入**影子评分**：
   - **对照组**：用 `config.NEWS_SCORING_DIMS` 权重算 `final_score_A`（现有逻辑）。
   - **实验组**：用 `data/ab_exp_weights.json`（从 `user_pref.json` 或人工实验文件读）算 `final_score_B`。
   - 线上只发布对照组结果；实验组结果写入 `data/ab_shadow.json` 留存。
2. **衡量"更好"的 ground truth**：以 `feedback.jsonl` 收藏为标签。指标 = **收藏命中率**（进入精选池的条目中，后续被收藏的比例）。也可算 NDCG：把收藏条目标为相关，对比 A/B 两组在精选池内的排序质量。
3. **晋升机制**：实验组连续 K=5 天收藏命中率显著高于对照组（如 +5pp）→ 生成"建议晋升"报告，**经人工确认**后才把实验权重写入 `config.NEWS_SCORING_DIMS`（或 override 层）。默认不自动晋升（护栏）。

**实现复杂度**：中（约 120 行，纯线性组合计算）
**预期收益**：高——把"拍脑袋调权"变成"有证据调权"，是 L3 闭环的质量保证。
**优先级**：P2（季度内）

---

### 方向 3 · 信源质量自动评估
**问题**：`SOURCES` 的 `tier`（config.py:186 起，人工定）+ `SOURCE_ADJ`（:839）+ `SOURCE_TIER_WEIGHTS`（:991）是静态的，没法反映"这个源最近是不是变差了"。

**方案**（🔵 零成本）：
1. 新增 `source_quality.py`，读 `data/scored_latest.json` + 各 `raw_2026*` + `feedback.jsonl`，每周统计每个 `source`：
   - **信号密度** = `is_relevant` 通过率（复用 `collector.is_relevant`）。
   - **噪音率** = 被 `purge_legacy` / 审计判为噪音的比例。
   - **时效性** = 采集日期 − 发布日期 的平均延迟。
   - **被收藏率**（有反馈后）。
   - **重复度** = 同事件簇内该源占比（配合方向 1 聚类）。
2. 算 `source_quality_score = w1·信号密度 + w2·(1−噪音率) + w3·时效 + w4·收藏率`，排名后自动重算 tier 映射，写入 **`data/source_tier_auto.json` 覆盖层**（**不直接改 `SOURCES.tier`**，避免破坏人工知识资产）。`score_and_merge` / `reapply_centrality` 读取 tier 时优先用自动层（或对其 `SOURCE_ADJ` 做 ±偏移）。
3. 护栏：改动前 git 备份 + `pitfalls_log` 留痕；自动 tier 仅作 adj 偏移，且夹紧（T1 不会因一次波动掉到 T3）。

**实现复杂度**：中（约 140 行）
**预期收益**：中高——让信源分层"活"起来，劣质源自动降权，优质源自动提权。
**优先级**：P2（季度内）

---

### 方向 4 · 推荐理由去重与多样性
**问题**：L2 审计 `max_dup=14`（data/L2_AUDIT.md），根因在 `recommend.py gen_recommendation()`（:61-123）：`CHINA_REF` 模板固定、主语 `subj` 常在缺 `entity_name` 时退化成同一 `domains[0]`、事件类型前缀雷同。

**方案**：
- **🔵 变体库（零成本，优先做）**：把 `CHINA_REF`（recommend.py:24-42）每类扩成 2–3 个句式变体，按 `item` 的稳定 hash / 序号**确定性轮换**选择（保证可复现）。在 `gen_recommendation` 末尾加"同事件类型簇内轮换变体"后处理，保证同类型条目不共用同一句 `CHINA_REF`。
- **🔵 主语锚点多样化**：扩展现有 `amount` 抽取逻辑（recommend.py:45-58），从摘要里再抽一个**具体实体名/数字**作 `subj`，减少"某赛道：……"式雷同。
- **🟡 LLM 差异化（可选增强）**：当 L3 强模型（HY3）可用时，仅对**精选前 10（top-N）**用 LLM 生成差异化文案，长尾仍用模板。免费期后若成本敏感，可整段降级回纯模板（不影响闭环）。
- 去重验证：把 `loop_audit._check_recommendation_quality()`（:365-408）的 `max_dup>5` 告警阈值收紧到 `>3`，并把变体库覆盖率作为新指标写入 L2 报告。

**实现复杂度**：低（变体库 ~60 行）/ 中（LLM 接入）
**预期收益**：中——直接消掉当前 3 个 WARN 之一，提升三页可读性。
**优先级**：P1（零成本部分本周即可做）

---

### 方向 5 · 企业研究价值分自进化
**问题**：`enterprise_score.py` 的 `compute_base_value()`（:202-207，v1–v4 固定权重）+ `compute_event_boost()`（:222-274，用 `EVENT_BOOST` config.py:848 固定分档）不随用户偏好漂移。

**方案**（🔵 零成本）：
1. 复用 `feedback_loop._resolve_ents()`（feedback_loop.py:76-89）已解析的企业收藏，维护 `data/ent_pref.json`。
2. 每次 `feedback_loop.run_daily_step()`（:92-167）解析 ent 收藏后，计算**收藏企业的 v1–v4 均值 vs 全体企业均值**，差值方向决定权重微调：
   - 若收藏企业系统性地 `v2`（信息丰富度）偏高 → 微提 `_v2_info` 在 `compute_base_value` 中的占比（±0.02，夹紧）。
   - `event_boost` 的 `cap`/分档由"被收藏企业的平均 event_boost"自适应抬高/压低（读 `data/enterprise/enterprise_scores.json` 现有输出）。
3. 输出写入 `ent_pref.json` history（沿用 `user_pref.json` 的留痕模式），**不直接改 `enterprise_score.py` 源码常量**，改走 override 层由 `compute_*` 读取。

**实现复杂度**：中（约 100 行）
**预期收益**：中——让企业库"值得深度写"的标准对齐小爽真实口味。
**优先级**：P2（季度内）

---

### 方向 6 · 成本意识（哪些必须模型 / 哪些纯代码）
**结论（基于 `0722_token_downgrade_plan.md` 实测）**：**本流水线的 Loop 进化全部可以零模型成本**。明确边界：

| 组件 | 是否需模型 | 说明 |
|------|-----------|------|
| 信号分 `signal_score` | 🔵 否 | 关键词权重（config.py:930-988） |
| 5 维打分 `score_skill.py` | 🔵 否 | 规则兜底（:40-87） |
| `industry`/`novelty` | 🔵 否 | `reapply_centrality.py` 关键词（:50-79） |
| 终分 / 聚类 / 阈值自适应 | 🔵 否 | 纯数学 |
| A/B / 信源质量 / 企业分自进化 | 🔵 否 | 纯统计 + 文件覆盖层 |
| **推荐理由（长尾）** | 🔵 否 | 模板轮换（方向 4） |
| **推荐理由（top-N 差异化）** | 🟡 可选 | 仅此处值得 LLM，可降级 |
| **弱信号相关性判定的 LLM 增强** | 🟡 可选 | 当前 `is_relevant` 已够用，非必需 |

**关键原则**：Loop 的"自我进化"本质是**数据驱动的 config 调参**，应永远跑在零成本规则层；模型只在"生成/理解"环节有价值，**绝不**放进"优化/评估"环节。免费期后即使 HY3 停供，本设计的 6 个零成本方向照常工作，仅方向 4 的 LLM 增强回退到模板。

**实现复杂度**：低（本就是现状，需文档化固化）
**预期收益**：明确边界，防止积分失控
**优先级**：P0（本周固化到文档 + 在 `run_daily.py` 注释标注各步成本属性）

---

### 方向 7 · 可观测性增强（自动每日健康报告）
**问题**：`STATE.md`（validator.py:273-287）是单点状态行，`L2_AUDIT.md` 是单日快照，**没有跨日趋势**；owner 想"随时看懂系统在怎么进化"还靠翻日志。

**方案**（🔵 零成本）：
1. 新增 `daily_health.py`（或在 `loop_audit.run_daily_step()` 末尾，:411-535 扩展），汇总：噪音率趋势、精选率、收藏率（有 feedback 时）、信源 top3/bottom3、当前生效阈值（含 override）、聚类簇数 → 写 **`data/HEALTH_REPORT.md`** + 追加 **`data/health_history.json`**（数组，供趋势）。
2. 趋势可视化：用纯文本 sparkline（零依赖）画关键指标的近 14 天走势；如需图表可加 `matplotlib`（可选，非必需）。
3. 推送集成：每日 06:00 摘要推送把 `HEALTH_REPORT` 摘要带上（沿用 `0722_token_downgrade_plan.md` 的模板逻辑，零模型）。
4. 把"进化动作"也接入：每次 `adapt_thresholds` / `source_quality` / `feedback_loop` 的改动，自动在 `HEALTH_REPORT` 末尾列"本次进化决策"，让 owner 一眼看到"系统今天自己改了什么"。

**实现复杂度**：低（约 100 行）
**预期收益**：中——把"可观测性丢失"这个护栏风险彻底补上，进化可见、可拦。
**优先级**：P1（月内，基础版本周可做）

---

## 四、分阶段路线图

### P0 · 本周（零成本，固化 + 止血）
- [ ] **方向 6 文档化固化**：在 `run_daily.py STEPS`（:24-51）逐行加 `# [COST: zero]` / `# [COST: model-optional]` 注释，明确成本边界。
- [ ] **方向 4 变体库**：扩 `CHINA_REF` 为变体 + `gen_recommendation` 轮换 + 收紧 `loop_audit` 的 `max_dup>5`→`>3`（:378）。目标：把 `max_dup` 从 14 压到 < 5，消掉 3 个 WARN 之一。
- [ ] **方向 7 基础版**：`daily_health.py` 生成首版 `HEALTH_REPORT.md` + `health_history.json`，先记录当前基线。

### P1 · 月内（零成本，激活核心自适应）
- [ ] **方向 1 前置**：实现 `selection/cluster.py` 激活聚类，写回 `cluster_id`（消掉休眠逻辑）。
- [ ] **方向 1 自适应**：`adapt_thresholds.py` 上线，精选率目标 15%–25% 收敛 + `CLUSTER_SIM_THRESHOLD` 走 P90 自适应，全走 override 层。
- [ ] **方向 4 增强**：主语锚点多样化 + 去重后处理。
- [ ] **方向 7 趋势面板**：`health_history.json` 折线/sparkline。

### P2 · 季度内（零成本，闭环验证 + 扩展）
- [ ] **方向 2 A/B 框架**：`selection/ab_test.py` 影子评分 + 收藏命中率晋升机制。
- [ ] **方向 3 信源质量**：`source_quality.py` 周级统计 + `source_tier_auto.json` 覆盖层。
- [ ] **方向 5 企业分自进化**：`ent_pref.json` + override 层微调 v1–v4 / event_boost。

### P3 · 远期（可选模型增强）
- [ ] **方向 4 LLM 文案**：仅 top-N 用 HY3 生成差异化推荐理由，长尾模板兜底；免费期后可降级。
- [ ] **元学习**：跨月发现"某类事件长期低收藏 → 自动降权"的二阶进化（需反馈样本积累到一定量才启动）。

---

## 五、关键决策点（需 owner 拍板）

1. **阈值自适应的目标函数**：以**精选率 15%–25%** 为收敛目标（推荐，简单稳健），还是**完全以收藏命中率为准**（更准但需 feedback 数据）？是否允许自动写 `threshold_override.json`（当前护栏已允许 L2 改阈值/关键词，技术上 OK，需确认）？
2. **A/B 晋升权限**：实验组权重"显著更优"后，是**自动晋升**为默认，还是**只出报告等人工确认**（推荐后者，护栏更稳）？
3. **信源质量自动层**：自动 tier 是否允许**覆盖人工 `SOURCES.tier`**？本设计建议**只做 `SOURCE_ADJ` 偏移 + 覆盖层，不改源码**（保护人工知识资产），请确认。
4. **推荐理由 LLM 化**：是否启用 top-N LLM 文案（方向 4 🟡）？免费期后是否值得为其保留 HY3 额度？
5. **进化自由度上限**：坚持 `DELTA_CAP=0.03`（feedback_loop.py:36）小步夹紧，还是对阈值/权重放宽到 ±0.1？建议分场景：权重 ±0.03、阈值 ±0.1。
6. **历史数据保留策略**：`health_history.json` / `threshold_history.json` / `source_quality` 等长期追加文件，是否永久保留（影响可追溯性与微量存储成本）？

---

## 六、成本预算表（token / 时间）

> 前提：沿用 `0722_token_downgrade_plan.md` 的结论——评分/推荐/聚类/阈值全规则兜底，**进化层零模型**。下表只估"新增代码的计算与 owner 审阅成本"，不含每日流水线的既有运行成本。

| 方向 | 新增文件 / 改动 | 模型 token | CPU 时间/次 | 开发工时 | 频率 |
|------|----------------|-----------|------------|---------|------|
| 1 阈值自适应 | `adapt_thresholds.py` + `selection/cluster.py` | 🔵 0 | ~0.5s（统计+余弦，61 条） | 1.5 天 | 每日（自动化） |
| 2 A/B 框架 | `selection/ab_test.py` | 🔵 0 | ~0.3s（双权重线性组合） | 1 天 | 每日（影子，不发布） |
| 3 信源质量 | `source_quality.py` | 🔵 0 | ~0.5s | 1 天 | 每周 |
| 4 变体库 | 改 `recommend.py`（:24-123） | 🔵 0（模板）/ 🟡 仅 top-N | ~0（模板）/ ~轻量 | 0.5 天 | 每日 |
| 4 LLM 增强 | 改 `recommend.py` 接 HY3 | 🟡 精选前 10 条/日 | 取决于调用 | 0.5 天 | 每日（可选） |
| 5 企业分自进化 | 改 `feedback_loop.py` + `ent_pref.json` | 🔵 0 | ~0.2s | 0.5 天 | 每周（随 feedback） |
| 6 成本固化 | 改 `run_daily.py` 注释 | 🔵 0 | 0 | 0.2 天 | 一次性 |
| 7 健康报告 | `daily_health.py` | 🔵 0 | ~0.3s | 0.5 天 | 每日 |

**月度增量成本估算**：
- **模型 token**：仅方向 4 🟡 启用时，按 top-10 × ~200 token/条 ≈ **2k token/日 ≈ 60k/月**（可降级为 0）。
- **CPU/存储**：全部统计脚本合计 < 3s/日；`health_history.json` 等追加文件按 1 年估算 < 5 MB。
- **人工审阅**：owner 每周看一次 `HEALTH_REPORT.md` + 进化决策列表，约 **10 分钟/周**。

**结论**：除一个可选 LLM 增强点外，整套 Loop 自我进化机制**边际模型成本为 0**，与"免费期后降级"策略完全兼容。

---

## 附：改动落点速查表

| 文件 | 函数 / 位置 | 行号 | 本设计改动 |
|------|------------|------|-----------|
| config.py | `SELECT_THRESHOLDS` | 832-836 | 改读 override 层 |
| config.py | `CLUSTER_SIM_THRESHOLD` | 842 | 改读 override（P90 自适应） |
| config.py | `EVENT_BOOST` | 848 | 由 `ent_pref.json` 微调 |
| config.py | `SOURCES`/tier | 186+ | 不改，仅建 `source_tier_auto.json` 覆盖 |
| loop_audit.py | `_check_recommendation_quality` | 365-408 | `max_dup>5`→`>3` + 变体覆盖率指标 |
| loop_audit.py | `run_daily_step` | 411-535 | 末尾扩展健康报告 |
| noise_spike_guard.py | `_backup_config`/`_log_pitfall` | 113-120 / 98-110 | 复用为统一护栏 |
| feedback_loop.py | `run_daily_step` | 92-167 | 解析 ent 收藏 → `ent_pref.json` |
| score_and_merge.py | `gen_recommendation` | 103-111 | （被 recommend.py 取代，可废弃） |
| selection/recommend.py | `gen_recommendation`/`run_daily_step` | 61-123 / 126-165 | 变体库 + 主语锚点 + 去重后处理 |
| reapply_centrality.py | `main` | 102-126 | 之后插入聚类 + 阈值 override 读取 |
| selection/enterprise_score.py | `compute_base_value`/`compute_event_boost` | 202-207 / 222-274 | 读 override 微调 |
| run_daily.py | `STEPS` | 24-51 | 插入 `adapt_thresholds`/`daily_health`/聚类，加成本注释 |

---

*本设计所有自适应动作均遵循既有护栏：写查分离、改动前 git 备份、pitfalls_log 留痕、权重/阈值夹紧、零模型成本优先。owner 可随时在 `HEALTH_REPORT.md` 看到系统"自己改了什么"，并人工回滚。*
