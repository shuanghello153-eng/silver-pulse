# Silver Pulse 银脉 — 规则文档（沟通单一真相源）

> 本文件与 `about.html`（由 `gen_about.py` 生成）同步维护。任何规则变更必须同时更新 `config.py` / `selection/*` 代码 与 本文件 + `gen_about.py`，再重新生成 `about.html`。

## 一、项目定位
银发经济投融资资讯聚合看板 + 企业数据库，服务商业写作者（小爽）的选题决策。本质是「选题情报台」：核心交付 = 深度选题（企业研究）。三层愿景：资讯看板 → 企业数据库 → 供需对接。

## 二、铁律（IRON RULE）
- 终分 / 精选判定 / 聚类主条，**100% 由代码计算**。
- 模型（L3）只输出维度分（0–10），**绝不直接给出 final_score**，也不决定精选、不挑聚类主条。
- 能用代码/关键词处理的，一律不用模型（省积分）。

## 三、资讯 5 维评分（选题雷达）
- **闸门（L1 预筛）**：`collector.is_relevant()` 二元判断「是否属银发经济」，不相关直接丢弃。位于 5 维之前。
- **赛道核心度（industry）**：**代码推导，零成本**。依据资讯领域（企业库 L1 分类）映射到 `CATEGORY_CENTRALITY`：核心=10（养老照护/养老用品/适老化改造/健康服务/失智老人），重要=7（康复/地产/日常消费/文娱），外围=4（行业服务/资本），未命中=6。
- 其余 4 维由模型打：信号强度(25%) / 写作潜力(20%) / 国内可比性(20%) / 时效紧迫度(15%)。
- **终分 = Σ(维度分 × 权重) + 信源调整(SOURCE_ADJ)**。

## 四、差异化精选阈值（SELECT_THRESHOLDS，按信源层级）
- T1 权威垂直：高价值 ≥ 6.0 · 值得关注 ≥ 4.0
- T2 综合/代理：高价值 ≥ 7.0 · 值得关注 ≥ 5.0
- T3 宽覆盖：仅进观察池（watch ≥ 6.0，不单独精选）

## 五、事件聚类（CLUSTER_SIM_THRESHOLD = 0.82）
- 主规则：`(entity_name, event_type)` 相同即同簇。
- 回退：余弦 > 0.82 且 event_type 相同亦同簇。
- 每簇仅留 1 条 `is_main` 主条，其余折叠。

## 六、企业研究价值公式（research_value = 0–100）
- `base_value(0–70)` = V1 规模(0–25) + **V2 信息丰富度(0–20, 最高权重)** + V3 模式创新(0–15) + V4 国内可比性(0–15)。
- **权重决策（2026-07-07，用户共同定）**：信息丰富度(V2)上调为最高；国内企业 V4 下调（国内标杆稀少，分数更靠 V2 + 最新事件）。
- `event_boost(0–35)`：近期新闻信号（上限 35，强化最新大事件）。
- `research_value = min(100, base + boost + MIRROR_BONUS)`，MIRROR_BONUS=5 仅海外。
- **分级 S/A/B/C**：≥75=S / ≥65=A / ≥55=B / ≥45=C（借鉴评分.md 的 F 级，非照搬）。
- **值得深写(worth_deep_write)**：命中 ≥2 项标准（S1 大企业 / S2 近期事件 / S3 差异化模式 / S4 标杆可借鉴）或 rv≥45。

## 七、借鉴 评分.md（批判性整合，非照搬）
- 每日衰减 DAILY_DECAY=0.1（文档化备用）。
- 同一事件 72h 内重评（RE_SCORE_WINDOW_H=72）。
- 去重：标题 >85% / 语义 >80%（由聚类实现）。
- 覆盖度目标：海外:国内 = 7:3（COVERAGE_RATIO）。
- 选题卡 JSON（未来）：含 维度分 / 终分 / 分级 / 推荐理由。

## 八、展示与语言
- UI 中文；企业名/源名保留原文。标题/摘要/推荐理由中文。
- 三页互跳：index.html(资讯+选题雷达) / enterprise.html(企业库) / about.html(规则)。
- 「研究的xx」徽章已改为「研究价值 NN」/「值得深写」。

## 九、部署
- 主分支 `main` 被 3 个每日自动化占用 → 改用 **CloudStudio** 部署 `output/`，并规划独立 `gh-pages` 分支正式上线（不动自动化）。
- 每日流水线 `run_daily.py`：collector → score_and_merge → score_skill(L3) → translate → **reapply_centrality(零成本核心度)** → enterprise_score → generator → gen_enterprise → gen_about。

## 十、免费期(至 0720)后切换预案
- 深度长文写作：HY3 → 切回用户自有流程/规则模板。
- 翻译：HY3 全量 → 批量规则/词典 或 hunyuan-lite，必要时浏览器自带翻译兜底。
- L3 强模型 5 维：hunyuan → hunyuan-lite 或规则估算兜底。
- V2 全量扩展：每日全量 → 仅 TOP 企业定时扩或按需触发。

## 十一、选题 JSON 导出（新需求，待实现）
- generator.py 生成 HTML 同时产出 `weekly_topics.json`（精选/high 条目 + 5 维分 + 原文链接）。
- index.html 加"下载选题 JSON"按钮（JS 序列化当前精选条目）。
- Schema 用站点 5 维（industry/signal/writing/cn_fit/urgency），不另搞 F1-F6，单一真相源。
- v1 最简：导出全部精选(high)条目；v2 才加"采纳"复选框。
- 挂钩周一 06:00 推送：生成 JSON 后在推送消息附路径。
- 参考文档：`G:\workbuddy\2026-07-03-10-13-25\选题JSON导出_建议.md`

## 十二、多账号协作 & 上下文管理
- **项目交接入口**: `PROJECT_STATUS.md`（repo 根目录）+ 本文件 + `.workbuddy/memory/`
- **写操作互斥**: 不同 WorkBuddy 账号不能同时写同一文件。分工或错开时间。
- **Agent 模式（避免上下文过载）**: 重活（搜索/翻译/大批量数据处理）用 Agent 后台跑，主对话只保留摘要+产出路径，不吞原文。
- **完成工作后必须**: 更新 `PROJECT_STATUS.md` 对应章节 + 在 `.workbuddy/memory/YYYY-MM-DD.md` 追加日志。
- **新账号接手流程**: 读 `PROJECT_STATUS.md` → 读 `RULES.md` → 读 `config.py` → 查今天 memory 日志 → 从"未完成"清单挑任务。
