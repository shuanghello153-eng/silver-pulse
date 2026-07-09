# Silver Pulse · Loop Engineering 深度调研与落地方案

> 调研：general-purpose-1（技术调研智能体）｜日期：2026-07-09
> 目的：为「无后端静态站点 + 每周自动化」的 Silver Pulse 项目，给出**可落地**的 Loop Engineering 实战方案，而非概念空谈。
> 配套已存在文件：`loop_engineering_design.md`（V1 三层映射）、`docs/loop_self_iteration_v2.md`（自我迭代 7 方向设计）、`RULES.md` / `PROJECT_STATUS.md` / `.workbuddy/memory/`。

---

## 核心结论（先说人话）

1. **Loop Engineering 不是新算法，是「范式迁移」**：从「人写提示词、AI 干一次」变成「AI 自己 observe→act→verify→(adapt)→repeat，带停止条件和护栏」。它的命门是**自我校验（verify）**和**边界控制（stop）**，缺了这两样就会退化成 2023 年翻车的 AutoGPT。
2. **我们项目已经走得很远**：写查分离、L2 质量自审、噪音护栏、反馈回灌、阈值自适应、健康报告、视觉回归**全部已有代码**。但当前是个「**报告型半闭环**」——大多数进化逻辑只产出建议、不真正改线上行为（例如 `adapt_thresholds` 默认 `ENABLE_AUTO_THRESHOLD=False`）。
3. **最值钱、最该先做的不是更复杂的循环，而是把「校验」做厚**：加死链检测、JSON Schema 断言、评分一致性抽样、前后产出条数对比。这些零成本、立刻能挡住 90% 的翻车。
4. **真正的缺口只有三处**：①闭环「只报告不动作」（需 owner 拍板激活）；②L3 反馈回灌因 `feedback.jsonl≈0` 实际是伪闭环；③没有把循环发现**自动沉淀成记忆**（`.workbuddy/memory/` 目前靠人工写）。这三处就是本方案的 P0/P1/P2。

---

## 一、Loop Engineering 到底是什么

### 1.1 权威定义（Anthropic 官方，2026-07-01）

Anthropic Claude Code 团队在官方博客 *Getting started with loops*（作者 Delba de Oliveira、Michael Segner）给出的定义最严谨：

> **Loops = agents repeating cycles of work until a stop condition is met.**
> （循环 = 智能体重复执行工作周期，直到满足某个停止条件。）

它把 loop 按四个维度分类：**触发方式 / 停止条件 / 使用的底层原语 / 适合的任务类型**。并明确提醒：**Not all tasks require complex loops; start with the simplest solution.**（不是所有任务都需要复杂循环，从最简单的解法开始。）

### 1.2 四种 Loop 类型（Anthropic  taxonomy，强烈建议照此对齐）

| 类型 | 触发 | 停止条件 | 最适合 | 我们项目的对应 |
|------|------|---------|--------|---------------|
| **Turn-based** | 用户提示 | AI 判断完成或需补充上下文 | 探索/决定类短任务 | 每次手动跑 `run_daily.py`；AI 改完代码后用自己的 SKILL 自检 |
| **Goal-based** (`/goal`) | 实时手动 | 目标达成 **或** 达到最大轮次 | 有可验证出口标准的任务 | 「STATE.md=FAIL → 09:00 补跑重试」；部署门禁（CRITICAL 阻断） |
| **Time-based** (`/loop`,`/schedule`) | 固定时间间隔 | 你取消 / 工作完成 | 周期性工作、对接外部系统 | 每周自动化、每天 06:00 健康快照 |
| **Proactive** | 事件/计划，**无人实时在场** | 每个子任务达目标；routine 持续到你关掉 | 周期性、定义良好的工作流（triage/迁移） | **P2 远景**：全自动闭环，路由到小模型 + auto mode |

### 1.3 与「Agentic Coding / Vibe Coding」的区别（避免概念混淆）

| 概念 | 提出/代表 | 核心 | 有没有自检闭环 |
|------|----------|------|--------------|
| **Vibe coding** | Andrej Karpathy（2025-02） | 「我说想法，AI 写码，我基本不读，能跑就行」 | ❌ 没有。靠人的模糊信任，最容易埋雷 |
| **Agentic coding** | Claude Code / Cursor / Devin / Codex | AI 自主执行多步任务（读码、改码、跑测试） | 部分。单轮有工具调用，但仍是「人下一条指令」 |
| **Loop Engineering** | P. Steinberger / B. Cherny / A. Ng（2026-06 引爆） | 在 agentic 之上**显式设计闭环**：观察→行动→**校验**→（自适应）→重复，带停止条件与护栏 | ✅ 必须有。校验与边界是定义的一部分 |

一句话区分：**Vibe coding 是人懒得验；Agentic coding 是 AI 替你干；Loop Engineering 是让 AI 干完自己验、验完自己改、改完还记笔记。** 它是 agentic coding 的「工程化封装」。

### 1.4 为什么 2026 年火（时间线）

- **2025-02** Karpathy 提出 vibe coding，埋下「不校验」的隐患。
- **2026-06 初** 两条高关注度发声几乎同时出现：
  - **Peter Steinberger**（OpenClaw 创始人）发推，一条引发约 **800 万次浏览**，正式把 "Loop Engineering / 循环工程" 推成热词，主张「别再给一次性提示，去设计让 AI 自己转圈的 harness」。
  - **Boris Cherny**（Anthropic，Claude Code 负责人）公开说「我不再 prompt Claude 了，我在写一堆循环」——把 loop 当成工程对象。
- **2026-06** 吴恩达（Andrew Ng）提出**三层 Loop**（时间尺度不同，见 1.5），把「用户反馈回灌」抬到决定质量天花板的高度。
- **2026-07-01** Anthropic 官方博客发布 *Getting started with loops*，给社区一个权威、可操作的定调。

### 1.5 代表人物与项目（Steinberger 之外）

- **Peter Steinberger / OpenClaw**：引爆者，强调「写 harness 而非写 prompt」。
- **Boris Cherny / Anthropic（Claude Code）**：提出「写循环不写提示」，并给出四类 loop 分类法。
- **Andrew Ng / 吴恩达**：三层 Loop 框架（L1 执行/分钟级、L2 系统审计/天级、L3 外部反馈/周月级），强调最慢的 L3 决定天花板。
- **Anthropic Claude Code 团队**（Delba de Oliveira、Michael Segner）：官方博客 + `/goal` `/loop` `/schedule` / dynamic workflows 原语。
- **历史前车之鉴 · AutoGPT（2023）**：最早的自循环 Agent，正是**因为没有校验机制和边界控制**而失败——这是 Loop Engineering 必须吸取的反面教材。

### 1.6 官方/权威资料链接（放最后「参考资料」一节，便于 owner 查阅）

---

## 二、对本项目「无后端静态站点 + 每周自动化」的适用性判断

### 2.1 我们不是大厂 Agent 团队——哪些 Loop 实践能直接套用

| Anthropic 推荐实践 | 我们能否套用 | 落地形态（本项目已有/可加） |
|-------------------|------------|---------------------------|
| **用 SKILL 把人工检查步骤编码成自动校验** | ✅ 完美契合 | `loop_audit.py` / `validator.py` / `visual_regression.py` 就是把「人工走查」固化成脚本 |
| **Goal-based 停止条件 + 轮次上限** | ✅ 已用 | 部署门禁：CRITICAL 阻断部署 + 「FAIL→补跑」；`/goal` 思路等价于「STATE.md 不 OK 就不算完」 |
| **Time-based 定时循环** | ✅ 已用 | 每周自动化、`daily_health` 每天 06:00 快照 |
| **统计脚本替代模型推理（省钱）** | ✅ 已贯彻 | 评分/聚类/阈值/权重**全规则兜底**，进化层零模型（见 `0722_token_downgrade_plan.md`） |
| **写查分离（一个干、一个挑错）** | ✅ 已贯彻 | `loop_audit`（查）vs `noise_spike_guard`（进化/写），`validator`（查）vs 生成器（写） |

### 2.2 哪些是为重型 infra 设计的、对我们是「过度工程」（明确不碰）

- ❌ **Dynamic workflows 派生几百个并行 agent**：我们是单仓库 Python 脚本，没这需求，纯烧钱烧时间。
- ❌ **第二 agent 做 `/code-review` 跨仓评审**：我们改动小、护栏已够；真要时可让主 AI 跑一次 `loop_audit` 当 reviewer 即可。
- ❌ **向量数据库 / RAG 长期记忆**：我们的「记忆」就是 `data/*.json` + `.workbuddy/memory/*.md`，文本文件够用，不引入新依赖。
- ❌ **RL / 元学习自训练**：Adaptive 用确定性统计（精选率目标带、P90 分位）就够，绝不训练模型。
- ❌ **实时常驻 loop（/loop 5m 盯 PR）**：我们每周跑一次，按事件频率匹配间隔，常驻反而浪费。

> 结论：**我们只取 Loop 的「校验闭环 + 保守自适应 + 定时触发」三件套，不取它的「多智能体编排」外壳。** 这与 Anthropic 自己的建议一致——从最简单的解法开始。

---

## 三、自我校验机制（最值钱，P0 重点做厚）

核心思想（Anthropic 原话）：*The more quantitative the checks are, the easier it is for Claude to self-verify.* —— 校验越可量化，AI 越容易自验。

### 3.1 现实可行的「自我校验清单」（建议在 `loop_audit.py` / `validator.py` 增补）

| # | 校验项 | 现在有没有 | 怎么做（零成本） |
|---|--------|-----------|----------------|
| 1 | **JSON Schema 结构断言**（scored_latest.json 含必需字段、类型对） | ❌ 缺 | 读 JSON 后断言每条有 `url/title/date/final_score/is_selected` 等；缺字段直接 FAIL |
| 2 | **死链检测**（生成 HTML 里所有 `<a href>` 外部链接可达） | ❌ 缺（用户明确点名） | 跑完用 `requests.head` 抽样/全量检测外链，50x/超时记为死链，超阈值阻断 |
| 3 | **评分一致性抽样**（同一条目跑两次终分结果一致） | ❌ 缺 | 对 5 条随机样本重算 `final_score`，与已存值比对，误差 > 0.01 报警（抓随机性 bug） |
| 4 | **前后产出条数对比**（今日 vs 昨日资讯/精选数） | ⚠️ 部分 | 已有基线（`l2_baseline.json`），加「骤降 >40% 即 FAIL」硬门槛 |
| 5 | **噪音率断言**（不通过 `is_relevant` 闸门的比例） | ✅ 已有 | 保留，`noise>30` 判 CRITICAL |
| 6 | **精选率区间**（避免空集或垃圾堆） | ✅ 已有 | 保留，`<10%` 或 `>95%` 报警 |
| 7 | **HTML 结构/回归**（死 JS、残余 `<select>`、标签爆炸） | ✅ 已有 | 保留 `loop_audit.py` |
| 8 | **视觉回归**（截图+控制台报错+收藏抽屉可开） | ✅ 已有 | 保留 `visual_regression.py`（需 playwright，可选） |
| 9 | **部署门禁**（关键步失败或 CRITICAL 不部署） | ✅ 已有 | 保留 `run_daily.py` 的 deploy gate |
| 10 | **校验器自身健康**（校验脚本别 silent fail） | ❌ 缺 | 给校验器加「若能跑到这里说明我没崩」的心跳断言 |

### 3.2 伪代码（可并入 `loop_audit.py` 或新建 `self_verify.py`）

```python
def self_verify(scored, html_pages):
    blockers = []   # 任一 => 阻断部署
    warnings = []   # 不阻断，但进报告

    # 1) JSON Schema 断言
    REQUIRED = ["url","title","date","final_score","is_selected","source"]
    for i, it in enumerate(scored):
        missing = [k for k in REQUIRED if k not in it]
        if missing:
            blockers.append(f"条目#{i} 缺字段 {missing}")   # 数据坏了，绝不发布

    # 2) 死链检测（抽样外部链接，避免每次全量太慢）
    ext_links = extract_external_links(html_pages)          # 解析 <a href="http...">
    dead = []
    for url in sample(ext_links, min(30, len(ext_links))):
        try:
            r = requests.head(url, timeout=8, allow_redirects=True)
            if r.status_code >= 400:
                dead.append((url, r.status_code))
        except Exception:
            dead.append((url, "timeout"))
    if len(dead) > 3:                                       # 容忍个别源抽风
        blockers.append(f"死链 {len(dead)} 条: {dead[:3]}")
    elif dead:
        warnings.append(f"死链 {len(dead)} 条(未超阈值): {dead[:3]}")

    # 3) 评分一致性抽样（抓非确定性 bug）
    for it in sample(scored, 5):
        recomputed = recompute_final_score(it)              # 复用 config 公式
        if abs(recomputed - float(it["final_score"])) > 0.01:
            warnings.append(f"评分不一致 {it['title'][:20]}: "
                            f"存{it['final_score']} 重算{recomputed}")

    # 4) 前后条数骤降
    prev = load_baseline()
    if prev and len(scored) < prev["total"] * 0.6:
        blockers.append(f"资讯数骤降 {len(scored)} < 昨日 {prev['total']}*0.6")

    return {"blockers": blockers, "warnings": warnings,
            "has_blocking": bool(blockers)}
```

> 关键护栏：**校验器自己也要有「心跳」**——如果 `self_verify` 因为异常提前退出，必须 `sys.exit(1)` 而非静默通过（`loop_audit` 已有「异常即不部署」的部署门禁兜底）。

---

## 四、自我迭代机制（从自身产出识别改进点）

「迭代」= 从运行数据里发现「下次该改什么」，并**保守地**改。吴恩达的 L2/L3 + 我们已有的 `noise_spike_guard` / `adapt_thresholds` / `feedback_loop` 已覆盖大部分。下面把「识别改进点」的具体信号和伪代码补齐。

### 4.1 应从自身产出识别的改进信号（含「尚未自动化」的项）

| 信号 | 已自动化？ | 触发动作 | 护栏 |
|------|-----------|---------|------|
| 某源连续失败/噪音高 | ⚠️ 半自动 | 连续 2 天 spike → 写入 `noise_blocklist.json` 封禁 | `noise_spike_guard.py`（已建，仅告警+保守封禁） |
| 精选率越出 15–25% 目标带 | ⚠️ 只建议 | 写 `threshold_override.json`（默认 `applied=False`） | `adapt_thresholds.py`（**未激活**） |
| 用户收藏偏好（L3） | ❌ 休眠 | 读 `feedback.jsonl` → ±0.03 微调权重 | `feedback_loop.py`（代码完整但 `feedback.jsonl≈0`） |
| **某类资讯连续低分** | ❌ 未做 | 统计低分簇的 event_type/domain，降权或加弱词 | 建议 P1 新增 `meta_learn.py` |
| **标签爆炸** | ✅ 已检 | `loop_audit` 检测 `data-tag>40` 且无折叠 → CRITICAL 阻断 | 已建 |
| **推荐理由重复** | ✅ 已检 | `max_dup>5` 报警 | 已建，待变体库修复（见 v2 方向4） |
| 规则漂移（config 改了 about 没重生成） | ✅ 已检 | `noise_spike_guard` 告警 | 已建 |

### 4.2 伪代码：元学习信号（补「某类资讯连续低分自动降权」缺口）

```python
def detect_lowscore_categories(scored, history):
    """连续 N 天某 event_type/domain 平均 final_score 偏低 → 产出降权建议。"""
    from collections import defaultdict
    by_cat = defaultdict(list)
    for it in scored:
        by_cat[it.get("event_type")].append(float(it.get("final_score", 0)))
    suggestions = []
    for cat, scores in by_cat.items():
        avg = sum(scores)/len(scores) if scores else 0
        # 历史中该类别连续低分计数
        streak = history.get("low_cat_streak", {}).get(cat, 0)
        if avg < 4.0:                      # 远低于精选线
            streak += 1
        else:
            streak = 0
        if streak >= 3:                    # 连续 3 天 → 出建议（不自动改）
            suggestions.append({
                "type": "downweight_category",
                "category": cat,
                "avg_score": round(avg,2),
                "action": "consider adding to SILVER_WEAK_KEYWORDS or lowering centrality",
                "auto": False,              # 永远人工拍板
            })
        history.setdefault("low_cat_streak", {})[cat] = streak
    return suggestions
```

> 设计原则（沿用现有护栏）：**识别可以自动，动作必须保守**。降权/封禁类动作走「覆盖层 JSON + git 备份 + pitfalls_log 留痕」；跨权重的「晋升类」动作一律只出报告、等人确认（见 v2 方向2 A/B 晋升机制）。

### 4.3 当前最大的「伪闭环」风险（必须写入方案）

- `adapt_thresholds` 默认 `ENABLE_AUTO_THRESHOLD=False` → 阈值是**建议而非动作**。
- `feedback_loop` 因 `feedback.jsonl≈0` → L3 **没有训练样本，等于空转**。
- 这两点导致「自我迭代」目前是**报告型**而非**闭环型**。要让它真正转起来，需要 owner 做两个拍板（见第六节 P0/P1）。

---

## 五、自我记录机制（把循环发现沉淀成可复用记忆）

RULES.md 第十二条已规定「完成后更新 PROJECT_STATUS.md + 在 `.workbuddy/memory/YYYY-MM-DD.md` 追加日志」。但这是**人工**动作。真正的 Loop 应当让循环**自动**把发现写进记忆。

### 5.1 现有记忆资产

- `.workbuddy/memory/2026-07-09.md` 等：每日工作记忆（目前靠主 AI 手写）。
- `data/pitfalls_log.json`：L2 进化层留痕（自动写）。
- `data/threshold_history.json` / `health_history.json`：趋势（自动写）。
- `PROJECT_STATUS.md` / `RULES.md`：单一真相源（人工维护）。

### 5.2 缺口：没有「自动把循环发现蒸馏成记忆」的环节

建议新增 `loop_memorize.py`（零成本，每日跑），把当天的循环产物**浓缩成一段可复用记忆**自动追加到 `.workbuddy/memory/`，并把「值得长期固化的规则」标记给 owner 审阅是否进 `RULES.md`。

### 5.3 伪代码：自动记忆蒸馏

```python
def loop_memorize():
    """每天把循环结论自动写进 .workbuddy/memory/，并标出『待固化规则』。"""
    today = date.today().isoformat()
    mem_path = f".workbuddy/memory/{today}.md"
    # 汇集今天所有循环产物
    audit = read("data/L2_AUDIT.md")
    health = read("data/HEALTH_REPORT.md")
    pitfalls = load_json("data/pitfalls_log.json", [])
    thresholds = load_json("data/threshold_override.json", {})
    feedback = load_json("data/feedback_report.md", "")

    lines = [f"# {today} · Loop 自动记忆摘要", ""]
    # 1) 今日健康一句话
    lines.append(f"- 健康：{health_oneliner(health)}")
    # 2) 今日进化决策（系统自己改了什么）
    if thresholds.get("applied"):
        lines.append(f"- 进化：阈值已自适应（精选率 {thresholds.get('select_rate')}%）")
    # 3) 待 owner 拍板的规则候选（从 pitfalls 里挑重复≥3次的同类）
    repeated = find_repeated_pitfalls(pitfalls, min_count=3)
    for p in repeated:
        lines.append(f"- ⚠️ 待固化规则：{p['type']} 连续出现，建议写入 RULES.md 第X条")
    # 4) 异常阻断（若有）
    if audit_has_blocking(audit):
        lines.append(f"- 🔴 今日部署被阻断：{blocking_reason(audit)}")

    append_to_file(mem_path, "\n".join(lines))
    # 同时更新 PROJECT_STATUS.md 的『最近循环』章节（若结构允许）
```

> 护栏：自动写 memory 只**追加**，绝不改写历史；「待固化规则」只是**建议**，进 `RULES.md` 必须人工确认（防止 AI 自己改自己的规则 → 幻觉自我强化，见第七节）。

---

## 六、具体落地路线图（P0/P1/P2，标注「已建/缺口」）

> 已建项来自：`validator.py` `loop_audit.py` `noise_spike_guard.py` `feedback_loop.py` `adapt_thresholds.py` `daily_health.py` `visual_regression.py` `run_daily.py` 部署门禁。
> 下列「待做」都是**低成本**（纯脚本、零模型、走覆盖层 + git 备份）。

### P0 · 先把「自我校验」做厚（最值钱，本周）
- [ ] **新增死链检测**（3.1-#2 / 3.2）：并入 `loop_audit` 或新建 `self_verify.py`，外链抽样 HEAD 检测，超 3 条死链阻断部署。
- [ ] **新增 JSON Schema 断言**（3.1-#1）：`scored_latest.json` 必需字段/类型校验，缺字段即 FAIL。
- [ ] **新增评分一致性抽样**（3.1-#3）：5 条样本重算终分，误差>0.01 报警（抓随机性/配置漂移）。
- [ ] **前后条数骤降硬门槛**（3.1-#4）：今日 < 昨日×0.6 → 直接 FAIL（已有基线，加判定）。
- [ ] **校验器心跳**：任何校验脚本异常必须 `exit(1)`，绝不静默通过。
- [ ] **owner 拍板 A**：是否激活 `adapt_thresholds`（置 `ENABLE_AUTO_THRESHOLD=True` 并让 `reapply_centrality` 读 override）。这是把「报告型」变「闭环型」的关键开关。

### P1 · 自我迭代 + 自我记录（月内）
- [ ] **L3 激活引导**：在小爽的网站/推送里提醒「收藏→同步云端」上传 `feedback.jsonl`；一旦有数据，`feedback_loop` 自动跑起来（代码已就绪，只差数据）。
- [ ] **新增 `meta_learn.py`**（4.2）：某类资讯连续 3 天低分 → 出降权建议（不自动改）。
- [ ] **新增 `loop_memorize.py`**（5.3）：每天自动把循环结论蒸馏进 `.workbuddy/memory/`，并标「待固化规则」供 owner 审阅。
- [ ] **A/B 影子评分**（v2 方向2）：`selection/ab_test.py` 只算影子分、不发布，用收藏命中率做 ground truth，显著更优才出报告等确认。
- [ ] **推荐理由变体库**（v2 方向4）：把 `max_dup` 从 14 压到 <5，消掉现有 WARN。

### P2 · 谨慎的自主闭环（季度内，必须带强护栏）
- [ ] **Proactive 化**：在 owner 确认「连续 30 天无阻断 + 进化建议采纳率>80%」后，把每周运行从「人工触发」升级为「无人实时 + auto mode」的 proactive loop。
- [ ] **信源质量自动层**（v2 方向3）：`source_quality.py` 周级统计 → `source_tier_auto.json` 覆盖层（不改 `SOURCES.tier` 源码）。
- [ ] **企业分自进化**（v2 方向5）：`ent_pref.json` 微调 v1–v4 / event_boost。
- [ ] **元学习二阶**（v2 P3）：跨月发现「某类事件长期低收藏 → 自动降权」。

### 明确不做的（过度工程，写进 RULES 防回头）
- 多 agent 编排 / dynamic workflows / 第二 reviewer agent / 向量记忆 / RL 自训练 / 实时常驻 loop。

---

## 七、风险与坑（Loop 自主循环最容易翻车的地方）

| 翻车点 | 表现 | 我们的护栏（已建/待建） |
|--------|------|------------------------|
| **AI 自己改坏配置** | 自适应步长过大，精选池变空集/垃圾堆 | 阈值走 `threshold_override.json` 覆盖层、绝不直接改 `config.py`；`THRESHOLD_FLOOR` 下限夹紧；改动前 `git` 备份（`noise_spike_guard._backup_config`） |
| **无限循环烧积分** | 循环自调用无休止 | 全部进化层零模型（纯统计）；定时触发（非实时）；Goal-based 有轮次/补跑上限 |
| **幻觉自我强化** | AI 从错误结论里「学」出更错的规则 | ①「识别可自动、动作须保守」；②权重/规则晋升一律人工确认；③自动写 memory 只追加、不回写 RULES.md |
| **可观测性丢失** | 后台自己改，人看不懂 | `pitfalls_log.json` + `threshold_history.json` + `HEALTH_REPORT.md` + `STATE.md`；每次进化在报告末尾列「今天自己改了什么」 |
| **伪闭环自嗨** | 没有真实反馈却调出「看起来健康」的假象 | L3 必须以 `feedback.jsonl` 收藏为 ground truth；A/B 用收藏命中率验证；无反馈时不自动晋升 |
| **校验器自己崩了却静默通过** | 自检脚本异常退出 → 当作 OK 发布 | 部署门禁对「关键步失败 / CRITICAL」一律阻断；校验脚本异常 `exit(1)`（3.2 心跳） |
| **人工知识资产被覆盖** | 自动 tier/权重冲掉小爽拍的定值 | 信源 tier 只做 `SOURCE_ADJ` 偏移 + 覆盖层，不改 `SOURCES.tier` 源码 |

### Human-in-loop 边界（哪些事**必须**留给人确认）
1. **激活任何「自动改线上行为」的开关**（如 `ENABLE_AUTO_THRESHOLD`）——先观察建议 1–2 周再开。
2. **权重/阈值「晋升类」动作**（A/B 显著更优、跨类降权）——只出报告，owner 拍板。
3. **把循环发现写进 `RULES.md`/改 `config.py` 常量**——AI 只提「待固化规则」候选。
4. **首次部署 proactive 全自动闭环**——需连续 30 天无阻断的业绩背书。
5. **死链/数据损坏的「强制修复」决定**——AI 可阻断部署，但修法由人定（避免 AI 删数据自救）。

---

## 八、推荐参考资料链接

- **Anthropic 官方 · Getting started with loops**（最权威，四类 loop 定义 + 护栏 + 成本管控）：https://claude.com/blog/getting-started-with-loops
- **Anthropic · Steering Claude Code（skills/hooks/subagents 用于把检查编码成 SKILL）**：https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- **Claude Code 文档 · goal / schedule / routines / workflows**：https://code.claude.com/docs/en/goal 、https://code.claude.com/docs/en/routines
- **Peter Steinberger / OpenClaw**（Loop Engineering 引爆推文源头，2026-06）：OpenClaw 官方与 Steinberger 的 X 动态
- **Boris Cherny（Claude Code 负责人）**「我不再 prompt，我在写循环」相关访谈/推文（2026-06）
- **Andrew Ng / 吴恩达 · 三层 Loop（L1 执行 / L2 审计 / L3 外部反馈）** 公开演讲与文章（2026-06）
- **AutoGPT（2023）失败复盘**——作为「无校验+无边界=翻车」的反面教材检索阅读
- **本项目内部已落地文件**（直接复用，不必重造）：
  - `loop_engineering_design.md`（V1 三层映射）
  - `docs/loop_self_iteration_v2.md`（自我迭代 7 方向详细设计 + 改动落点速查表）
  - `RULES.md` / `PROJECT_STATUS.md`（单一真相源与护栏约定）
  - `validator.py` `loop_audit.py` `noise_spike_guard.py` `feedback_loop.py` `adapt_thresholds.py` `daily_health.py` `visual_regression.py` `run_daily.py`

---

## 一句话给小爽

> 银脉的 Loop 骨架已经搭得比绝大多数同类项目扎实——校验、护栏、反馈、自适应**代码都在**。现在最该做的不是加更复杂的循环，而是：①把「死链/字段/评分一致性」三道校验补上（立即可挡 90% 翻车）；②你点一下「允许阈值自适应生效」+ 多用网站收藏（让 L3 不再空转）；③让系统每天自动把发现写进记忆。剩下那些「AI 自己改自己规则」的事，全部留在你手里拍板。
