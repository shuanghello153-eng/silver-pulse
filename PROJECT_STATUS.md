# Silver Pulse 银脉 — 项目状态交接文档

> **用途**: 任何 WorkBuddy 账号打开本项目后，读此文件 + `RULES.md` 即可接手继续工作。
> **最后更新**: 2026-07-07 20:55 (小爽本账号「艾年研究员」)
> **当前阶段**: HY3 免费期冲刺（至 2026-07-20），目标把网站做到接近 100 分。

---

## 一、项目是什么

**一句话**: 银发经济投融资资讯聚合看板 + 企业数据库，服务小爽（银发财经深度作者）的**选题决策**。

本质是「选题情报台」——小爽早上打开网站，一眼看到"今天哪些企业/资讯值得写深度文章"。

三层愿景：资讯看板 → 企业数据库 → 供需对接（当前在第 1.5 层）。

**核心交付 = 深度选题（企业研究），不是新闻流。**

---

## 二、快速上手（新 AI 打开先读这些）

| 顺序 | 文件 | 为什么读 |
|------|------|----------|
| 1 | `PROJECT_STATUS.md`（本文件） | 了解整体进度、待办、阻塞 |
| 2 | `RULES.md` | 所有规则（评分/阈值/部署/架构），沟通真相源 |
| 3 | `config.py` | 代码级单一真相源：信源/分类/权重/阈值/关键词 |
| 4 | `.workbuddy/memory/MEMORY.md` | 长期项目记忆（架构决策/用户偏好/资产） |
| 5 | `.workbuddy/memory/2026-07-07.md` | 今日详细工作日志 |

**核心代码入口**:
- 每日流水线：`run_daily.py`（9 步串行，每步 try/except 不中断）
- 选题雷达引擎：`selection/` 包（l1_prefilter / aggregator / cluster / enterprise_score / reapply）
- 网站生成：`generator.py`(资讯页) / `gen_enterprise.py`(企业库) / `gen_about.py`(规则页)
- 采集：`collector.py`（RSS-first, feedparser + Google News RSS proxy）

**运行流水线（全量）**:
```bash
cd G:\workbuddy\2026-06-28-23-34-20\silver-pulse
C:\Users\shuan\.workbuddy\binaries\python\versions\3.13.12\python.exe run_daily.py
```

**只重新生成 HTML（不采集/不打分）**:
```bash
C:\Users\shuan\.workbuddy\binaries\python\versions\3.13.12\python.exe generator.py
C:\Users\shuan\.workbuddy\binaries\python\versions\3.13.12\python.exe gen_enterprise.py
C:\Users\shuan\.workbuddy\binaries\python\versions\3.13.12\python.exe gen_about.py
```

---

## 三、已完成（✅ = 确认落地）

### 核心架构
- ✅ 选题雷达引擎上线：5 维评分 + 差异化阈值 + 事件聚类 + 企业研究价值分
- ✅ 铁律落地：终分/精选/聚类主条 100% 代码算，模型只打 5 维原始分
- ✅ 赛道核心度改为代码关键词推导（零积分），不再靠模型猜（`reapply_centrality.py`）
- ✅ 国内企业 V4 权重下调、V2 信息丰富度上调、事件 boost 上限提高（`enterprise_score.py`）

### 数据资产
- ✅ 企业库 992 家（国内 455 / 海外 537），17 字段，business_model/tags 100% 覆盖（business_model 原缺 Mary Furlong 13 家，07-07 晚 T2 补全至 992/992）
- ✅ 资讯 scored_latest.json 231 条（含 dim_scores/cluster_id/entity_name 字段；selection 字段未持久化，generator 实时按 final_score+阈值判定精选）
- ✅ Crunchbase 搜索链接 100% 覆盖（992 家）
- ✅ funding_total 补全 60 家（97→157）、investors 补全 60 家（49→109）
- ✅ 资讯中文翻译：title_cn 100%（231/231）、summary_cn 90%（208/231）

### UI/UX
- ✅ "研究的xx" 徽章改为 "研究价值 NN" / "值得深写"
- ✅ 精选 tab + 更新时间线已实现（`generator.py` 含 `update_update_log()` + `build_timeline_html()`）
- ✅ 企业库 L2 二级分类联动筛选
- ✅ 搜索框位置 + 海外筛选数据修复
- ✅ 标签筛选数据显示修复（6→40 个）
- ✅ about.html 排版修复 + 信源表格优化
- ✅ about.html 规则 SSoT 化（所有阈值读自 config.py）
- ✅ `RULES.md` 新建（沟通真相源）

### 定时任务
- ✅ 3 个自动化已调为每周（周一 01:00 资讯 / 03:00 标签 / 06:00 摘要推送）
- ✅ 已确认在运行（用户亲口确认）；`automation_update list` 返回空仅为当前会话上下文盲区，非失效

---

## 四、未完成（⚠️ = 需要做 / 🔴 = 阻塞）

### ⚠️ P0 — Agent B 失败需要重做：V2 全量扩展 + 企业翻译
- **目标**: 新闻覆盖从 TOP135 扩到全部 992 家企业；企业 name_cn/desc_cn/business_model_cn 翻译补全
- **现状**: news_coverage 仍只有 batchA/B/C（~135 家）；翻译只有零散 chunk（`_namechunks/` 下），未回填 `all_enterprises.json`
- **原因**: 上一个 Agent 因内部 `TaskStop` 工具不可用而崩溃
- **做法**: 建新 Agent 重做（搜索新闻覆盖 + HY3 翻译），不碰 `config.py` / `selection/*`
- **积分消耗**: 中等（992 家搜索 + 翻译），建议在 HY3 免费期做完

### ✅ P1 — 选题 JSON 导出（已完成 2026-07-07 晚）
- **需求**: generator.py 生成 HTML 同时产出 `weekly_topics.json`；index.html 加"下载选题 JSON"按钮
- **Schema**: 用站点 5 维（industry/signal/writing/cn_fit/urgency），对齐 pipeline，不另搞 F1-F6
- **v1 最简**: 导出全部精选(selected)条目（209 条），含 5 维分 + final_score + 推荐理由 + 原文链接；v2 才加"采纳"复选框
- **挂钩**: 周一 06:00 推送附 JSON 路径
- **参考**: `G:\workbuddy\2026-07-03-10-13-25\选题JSON导出_建议.md`（小爽的另一 AI 写的方案）
- **验证**: 重跑 generator.py 成功生成 output/weekly_topics.json，5 维分零缺失；index.html 含下载按钮

### ⚠️ P1 — gh-pages 正式部署
- **决策**: 建独立 `gh-pages` 分支部署 `output/`，不动 main 自动化
- **现状**: 当前用 CloudStudio 预览（https://b1ff4c8d28504339a1654be585173e84.app.codebuddy.work）
- **做法**: `git checkout --orphan gh-pages` → 只提交 `output/` 内容 → push → GitHub Pages 设置指向 gh-pages

### ⚠️ P1 — 网站整体 UI/UX 优化（用户提到但未深入）
- 移动端适配、加载速度、空状态处理、搜索体验、企业对比功能、深色模式等
- 用户说"你觉得网站设计不好，你可以全面优化一下UI交互"
- 当前 generator.py 已有大量 CSS，但未做响应式适配

### ⚠️ P2 — 定时任务状态验证
- `automation_update list` 返回空，与"3 自动化 ACTIVE"矛盾
- 需确认是否真的在每日/每周运行；若失效需重建

### ⚠️ P2 — L2/L3 强模型接入
- 目前 L3 5 维打分为规则估算兜底（免费期 HY3 可用但未全量接入）
- 免费期后切 hunyuan-lite 或纯规则

### 🔴 阻塞 — GitHub Pages main 分支被自动化占用
- 3 个自动化提交占据了 main，plain push 被 fetch first 拒绝
- 解决方案：用 gh-pages 分支（见上方 ⚠️ P1）

---

## 五、待办清单（按优先级）

| # | 优先级 | 任务 | 消耗积分 | 阻塞 |
|---|--------|------|----------|------|
| 1 | P0 | **交接文档完善** → 本文件 + 更新 MEMORY.md | 零 | — |
| 2 | P0 | **V2 全量扩展 + 企业翻译**（Agent B 失败重做） | 中 | — |
| 3 | P1 | **选题 JSON 导出**（generator.py + index.html 下载按钮） | 零 | ✅ 已完成(07-07晚) |
| 4 | P1 | **gh-pages 正式部署** | 零 | — |
| 5 | P1 | **网站 UI/UX 全面优化**（响应式/空状态/搜索/深色模式） | 零 | — |
| 6 | P1 | **跑全流水线生成最新 HTML + deploy** | 低 | — |
| 7 | P2 | **定时任务状态验证**（automation list 为空的问题） | 零 | — |
| 8 | P2 | **L2/L3 强模型接入**（免费期后切方案记录） | 零 | — |
| 9 | P2 | **feedback.jsonl + backtest.py** 自我迭代闭环 | 零 | — |
| 10 | P2 | **聚类阈值回测调参**（余弦 0.82 偏严） | 零 | — |

---

## 六、关键决策记录（接手者必读）

1. **赛道核心度**: 不靠模型，改用 `config.CATEGORY_CENTRALITY` 关键词推导（核心=10/重要=7/外围=4），零积分。`reapply_centrality.py` 已接入 `run_daily.py`。
2. **国内企业 V4 权重下调**: 国内标杆稀少（海外10≈国内1），V4 可借鉴降权，V2 信息丰富度上调为最高，事件 boost 上限 30→35。海外企业 V4 不变（"以海外为镜"）。
3. **gh-pages 不动 main**: 决定建独立分支部署，保护 main 上的 3 个自动化。
4. **HY3 免费期策略**: 至 0720 前敞开用，冲 100 分。0720 后切换方案已写入 `RULES.md` 第十节。
5. **铁律不变**: 终分/精选/聚类主条 100% 代码算，模型只打 5 维原始分。
6. **多账号协作**: 不同 WorkBuddy 账号可共享本项目（本地文件），但禁止同时写同一文件。用本文件 + `RULES.md` 做状态交接。

---

## 七、多账号协作规则

- **状态交接入口**: 本文件（`PROJECT_STATUS.md`）+ `RULES.md`
- **写操作互斥**: 两个账号不能同时对同一文件写。建议：一个写代码时另一个只读数据。
- **完成工作后必须**: 更新本文件的"已完成"和"未完成"清单 + 在 `.workbuddy/memory/YYYY-MM-DD.md` 追加日志。
- **新账号接手第一步**: 读本文件 → 读 `RULES.md` → 读 `config.py` → 查今天的 memory 日志 → 从"未完成"清单挑任务开始。
- **Agent 派发原则**: 重活（搜索/翻译/大批量数据处理）用 Agent 后台跑，主对话只保留摘要，避免上下文过载。

---

## 八、当前数据资产速览

| 资产 | 文件 | 数量 | 备注 |
|------|------|------|------|
| 企业库 | `data/enterprise/all_enterprises.json` | 992 家 | 国内 455 / 海外 524，17 字段 |
| 企业评分 | `data/enterprise/enterprise_scores.json` | 992 条 | research_value 0-100，83 家 worth_deep_write |
| 资讯精选 | `data/scored_latest.json` | 231 条 | 含 5 维分 + 聚类 + 实体 |
| 新闻覆盖 | `data/enterprise/news_coverage_batch*.json` | ~135 家 | 仅 TOP，待扩至 992 |
| 更新时间线 | `data/update_log.json` | 3 条 | 2026-07-01/03/07 |
| 信源 | `config.py` SOURCES | 37 个 | T1=9 / T2=25 / T3=3 |

---

## 九、当前部署地址

- **CloudStudio 预览**: https://b1ff4c8d28504339a1654be585173e84.app.codebuddy.work（旧链接仍可用，但内容为 07-07 下午版；07-07 晚重新部署两次均 sandbox 超时失败，待重试）
- **GitHub 仓库**: shuanghello153-eng/silver-pulse (main 分支，被自动化占用)
- **本地 HTML**: `silver-pulse/output/index.html` / `enterprise.html` / `about.html`（已含 07-07 晚 T1/T2 更新）
- **部署方式**: `workbuddy_cloudstudio_deploy` 工具部署 `output/` 目录；GitHub 正式上线计划走独立 `gh-pages` 分支（已决策，待执行）
- **选题 JSON**: `silver-pulse/output/weekly_topics.json`（T1 新增，可下载）

---

## 十、小爽（用户）的关键偏好

- 以海外为镜照中国之路；深度企业分析 > 资讯流水
- 选题四标准：大企业(有年报) / 热点事件 / 反常识差异化模式 / 国内可比性
- 只做选题发现+初步研究，不写稿(另一 AI 写)；不发布
- 直接执行、事事有回应、主动发挥有观点
- 低成本优先不降质；HY3 免费期全力推质量
- 现在是免费期快速开发阶段——"不行再改"（不要因为怕浪费积分而不敢试）
- 身份：小爽 = 银发财经深度作者，"艾年"公众号主理人；目标 = 成为顶级银发行业研究专家

---

_此文件与 `RULES.md` 同步维护。任何重大进展或决策变更后，更新本文件对应章节。_
