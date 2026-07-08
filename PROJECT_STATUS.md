# Silver Pulse 银脉 — 项目状态交接文档

> **写给下一个 WorkBuddy 账号**：这是你接手的入口文件。读完它，你就能独立掌握项目全貌并开始工作。
> **最后更新**: 2026-07-08 12:04 (账号 A 准备切换账号 B 前)
> **当前阶段**: HY3 免费期冲刺（至 2026-07-20），正在进行大规模 UI 重构 + L2 自审模块建设

---

## 零、你接手后第一件事（按顺序）

| 顺序 | 文件 | 为什么读 |
|------|------|----------|
| **1** | **本文件**（`PROJECT_STATUS.md`）| 了解整体进度、待办、阻塞、当前中断点 |
| 2 | `RULES.md` | 所有规则（评分/阈值/部署/架构），沟通真相源 |
| 3 | `config.py` | 代码级单一真相源：信源/分类/权重/阈值/关键词 |
| 4 | `.workbuddy/memory/MEMORY.md` | 长期项目记忆（架构决策/用户偏好/资产） |
| 5 | `.workbuddy/memory/2026-07-08.md` | 完整工作日志（7 轮迭代，每轮做了什么+为什么） |
| 6 | `data/L2_AUDIT.md` | L2 自审模块最新报告，要修的问题全在这里 |

**⚠️ 当前有一个「半完成」的 UI 重构正在进行中**——代码都改好了，但还没重新生成 HTML + 部署。详见第四章。

---

## 一、项目概览

### 1.1 项目是什么

**一句话**: 银发经济投融资资讯聚合看板 + 企业数据库，服务小爽（银发财经深度作者，"艾年"公众号主理人）的**选题决策**。

本质是「选题情报台」——小爽早上打开网站，一眼看到"今天哪些企业/资讯值得写深度文章"。

三层愿景：资讯看板 → 企业数据库 → 供需对接（当前在第 1.5 层，企业库已领先于看板）。

### 1.2 当前进度与所处阶段

**线上状态（截至 2026-07-08 10:28）**:
- 资讯 46 条（精选 30）| 企业 1118 家 | 信源 44 个 | **噪音 0 | 状态 OK**
- 已部署到 gh-pages: https://shuanghello153-eng.github.io/silver-pulse/
- GitHub Pages source 已切到 gh-pages 分支

**但注意**：上述线上版本是 **第六轮**（信源深挖）之后的版本。**第七轮（UI 大改 T22-T33）的代码已全部改完，但还未重新生成 HTML 和部署**！所以现在线上看到的还是旧版 UI。

### 1.3 自昨日起已完成的主要工作（按时间线）

**第四轮 — 信源容错 + 全量筛选 + loop engineering 调研 + L3 回灌 + 工程加固**
- collector.py 加兜底容错链（rss 失败 → google_news → 直连 RSS）
- 资讯页加层级/特色筛选行（后被用户要求删除，见第七轮）
- 企业库加融资/IPO 筛选、标签自动反哺（tag_enterprises.py）
- L3 反馈回灌闭环（feedback_loop.py，无 feedback.jsonl 时空操作）
- validator 加数据新鲜度 + 噪音反弹告警
- deploy_ghpages 加 3 次重试防连接重置
- 出 loop_engineering_design.md 调研文档

**第五轮 — L2 噪音自我纠错**
- 发现 127 条噪音（73% 的资讯是泛科技/AI 稿，非银发内容）
- 写了两级闸门（强词命中或企业库才算相关）对存量全部重过
- 清理后：173 → 46 条纯净内容，噪音 0，状态 OK
- 创建了 purge_legacy.py（每日自动复查，防旧噪音复发）

**第六轮 — 一手信源深挖**
- 新增 7 个一手源：民政部、国务院政策、中国老龄协会、LeadingAge、Argentum、NIC、NCOA
- 降级 4 个泛科技聚合噪音源：FinSMEs/Pulse 2.0/TechCrunch/BetaKit → T3（不进精选）
- 出 SOURCE_AUDIT.md 体检报告
- 信源 37 → 44

**第七轮 — UI 大改 + L2 自审（正在进行中，代码已改但未部署）**
- 用户（小爽）截图指出大量 UI 问题，要求自查自修，不要等他提
- **已完成代码改动（见第四章），但未重新生成 HTML 和部署**

---

## 二、当前中断点（⚠️ 重要！新 AI 接手后立即要做的）

### 2.1 状态快照

| 维度 | 状态 |
|------|------|
| `generator.py` | ✅ 已改完（删雷达块、删层级/特色筛选、推荐理由★样式、header信号概览） |
| `gen_enterprise.py` | ✅ 已改完（标签下拉→胶囊按钮、筛选栏紧凑化、JS 对应修改） |
| `ui_common.py` | ⚠️ **雷达 CSS 残留未清理**（第 142-164 行 `.radar-block` 等样式仍在） |
| `gen_about.py` | ✅ 已改完（三 tab 加分工说明） |
| `selection/recommend.py` | ✅ 新建（差异化推荐理由模板 5+ 套，已测试生成通过） |
| `loop_audit.py` | ✅ 新建（L2 自审模块，已接入 run_daily.py，已测试） |
| `run_daily.py` | ✅ 已接入 recommend + loop_audit 两步 |
| HTML 重新生成 | ❌ **未执行**（generator/gen_enterprise/gen_about 均未跑） |
| L2 自审验证 | ❌ **未通过**（旧 HTML 残留 radar-block，3 个严重问题 + 推荐理由重复） |
| 部署 | ❌ **未执行**（deploy_ghpages.py 未跑） |
| git 提交 | ❌ **未提交**（git status 有 22 个 modified + 14 个 untracked） |

### 2.2 L2 自审发现的问题（待修复后重新验证）

上次 L2 跑的结果（`data/L2_AUDIT.md`）：

**🔴 严重（3 个）**：三页 HTML 中 `radar-block` CSS 类仍存在 → 因为旧 HTML 未重新生成。重新生成 HTML 后这 3 个应自动消失。

**🟡 警告（2 个）**：
1. 推荐理由重复度过高：最多一条理由被用了 16 次 → `selection/recommend.py` 模板已升级，重新生成后可改善
2. 推荐理由与标题金额重复：6 条 → `recommend.py` 已做去重逻辑，重新生成后应改善

### 2.3 接手后立即要做的 5 步

```bash
# 1. 删除 ui_common.py 中残留的雷达 CSS（第 142-164 行，.radar-block 到 .radar-empty）

# 2. 重新生成推荐理由 + 三页 HTML
cd G:\workbuddy\2026-06-28-23-34-20\silver-pulse

C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe -c "from selection.recommend import run_daily_step; run_daily_step()"

C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe generator.py
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe gen_enterprise.py
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe gen_about.py

# 3. 跑 L2 自审验证修复效果
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe loop_audit.py

# 4. 读 data/L2_AUDIT.md 确认严重问题清零

# 5. 部署 + 提交
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe deploy_ghpages.py
git add -A && git commit -m "feat: UI大改(T22-T33) + L2自审模块接入"
```

---

## 三、所有待办清单（长期 + 短期，全量）

### 3.1 🔴 最高优先（接管后立即做）

| # | 任务 | 说明 |
|---|---|---|
| **T32-fix** | **删 ui_common.py 雷达 CSS 残留** | 第 142-164 行，`.radar-block` 到 `.radar-empty` 全删 |
| **T33-validate** | **重生成 HTML + 跑 L2 自审** | 验证 3 个严重问题清零 |
| **T33-deploy** | **部署 gh-pages + 提交 git** | 源码改动太多未提交（22 modified + 14 untracked） |

### 3.2 🟠 高优先（本周必做）

| # | 任务 | 说明 | 消耗积分 |
|---|---|---|---|
| T34 | **全量跑一次 run_daily** | 验证 14 步流水线（含新增 4 步）全部通过 + 自动部署 | 低（采集新数据） |
| T35 | **收藏回灌闭环启动** | 等用户导出 feedback.jsonl → feedback_loop 实际生效；当前空操作状态 | 零 |
| T36 | **about.html 更新** | 信源数从 37→44、规则页描述与新 UI 对齐（推荐理由说明已从"蓝色文字"改为"★ 标记"） | 零 |

### 3.3 🟡 中优先（未来 2 周）

| # | 任务 | 说明 | 阻塞 |
|---|---|---|---|
| T37 | 聚类阈值回测调参 | 余弦 0.82 偏严；需 feedback.jsonl 有标注数据后回测 | 等 T35 |
| T38 | 推荐理由质量持续优化 | L2 报告中的"最多重复 16 次"问题，需在实际数据跑通后评估 recommend.py 模板效果 | — |
| T39 | 一手信源持续扩充 | 已启动第一轮（+7 源，44 总），可继续挖掘更多一手行业协会/政府/研究源 | — |
| T40 | 企业库 news_coverage 从 TOP135 扩到全量 1118 | 上一个 Agent 崩溃未完成，需重建 Agent 重做 | 中积分 |

### 3.4 🟢 低优先（长期 / 暂缓）

| # | 任务 | 说明 | 阻塞 |
|---|---|---|---|
| T41 | L2/L3 强模型接入 | 目前 5 维评分规则兜底正常；需模型 API key（本环境未配置） | 需 key |
| T42 | B 站受众热度接入 | 作为评分次要信号；需 B 站数据源 | 需数据源 |
| T43 | B 站短视频脚本生成 | 基于深度文章自动转视频脚本（silver-video skill 已存在） | 等文章产出 |
| T44 | 供需对接功能 | 三层愿景最后一层：企业需求/服务商能力匹配 | 远期 |
| T45 | 定时任务状态验证 | `automation_update list` 返回空，但 4 个自动化此前 ACTIVE；需确认是否真在运行 | — |
| T46 | 医疗/保险相邻边界白名单 | 如 Guardian Pharmacy/Experity/OpenLoop 等"银发相邻"企业，目前按严格闸门剔除，需用户决策 | 等用户确认 |
| T47 | 聚合源额外评分惩罚 | 当前两级闸门 + 降级 T3 已是双保险，惩罚属冗余 over-engineering | 不紧急 |

### 3.5 各任务优先级排序理由

- **T32-fix / T33-validate / T33-deploy** 是流程阻塞——代码已改好但未部署，用户看不到任何改进
- **T34 全量跑流水线** 验证系统整体健康（上次全量跑成功后加了 4 个新步骤，下次跑需确认不崩）
- **T35 收藏回灌** 是用户明确要求的功能，代码已就绪，就差用户数据
- **T37-T40** 是系统质量提升：聚类更准、推荐更好、数据更全
- **T41-T47** 是远期或受外部条件阻塞的

---

## 四、第七轮 UI 大改详情（T22-T33 所有改动，供确认/回滚用）

### 4.1 用户需求原文（2026-07-08 早上）

小爽截图指出以下问题（按他原话）：
1. "选题雷达（资讯维度）没用了吧，随便找个地方放就行，别占太多面积"
2. "层级/特色筛选有部分重复了，有的不知道啥意思，感觉没啥用，建议删除"
3. "这个标签好丑啊，位置也不对，也不是这样展示的啊，资讯栏目有标签啊，参考一下样式"
4. "资讯和企业库的筛选项、排序项目都列出来，减少操作，注意排版样式，如果内容不多，不要单独放一行占空间"
5. "资讯和企业库的标题、介绍、推荐理由内容大幅度重复啊"
6. "企业库和资讯的列表样式尽量统一一下吧，企业库似乎更好一些，比如推荐理由是一个星号，减少重复性文字展示"
7. "网站说明页的资讯版说明、企业库说明、网站规则，有啥不一样？可以说明一下他们各自的分工"
8. "我的收藏页面无法点开，移动到网站说明前面的tab吧"
9. "在页面上点⭐收藏并「导出收藏」，把 feedback.jsonl 发你，我没有收藏，现在网站不太好用"
10. "提升一下loop的优先级吧，我给你提网站需求提累了，你要自己检查发现问题"

### 4.2 已完成的代码改动

**generator.py（资讯页生成器）**:
- ✅ T22: 删除 `radar_html` 整个块（`build_radar_html()` 调用 + 模板插入），替换为紧凑的 `build_signal_strip()` 信号概览一行（放在 header stats 附近）
- ✅ T23: 删除「层级 T1/T2/T3」和「特色 有融资/反常识高」两个筛选行 HTML + 对应 JS（activeTier/activeSpecial 变量、updateDisplay 过滤、setView 重置、事件监听）全部清理
- ✅ T25: 推荐理由从蓝底块 `<p class="feed-rec"><b>推荐理由：</b>...` 改为 *星号前缀 italic 样式*（`<p class="feed-rec"`→只保留内容），与 `ui_common.py` 的 `.feed-rec` CSS 对齐
- ✅ 新增 `build_signal_strip()` 函数：从 scored 数据统计 signal → 生成一行 `📊 今日: 产品发布21 · 融资12 · 收购并购7 · ...`

**gen_enterprise.py（企业库生成器）**:
- ✅ T26: 标签筛选从 `<select class="tag-select">` 改为胶囊按钮组（`.f-btn`），JS 对应改为点击事件监听
- ✅ T27: 筛选栏合并：标签+融资按钮合并到一行，分类+L2 合并到一行；融资行和分类行紧凑排列，不再各自独占一行
- ❌ T27 原计划还包括资讯页筛选栏合并，**尚未做**（资讯页筛选行仍为 event/domain/tag 各占一行）

**ui_common.py（统一设计系统）**:
- ✅ T25: `.feed-rec` CSS 从蓝色左竖条块改为 *italic 紧凑样式（font-size:11.5px; font-style:italic）
- ✅ T28: `SIDEBAR()` 函数侧栏顺序调整：资讯看板 → 企业库 → ⭐我的收藏 → 网站说明
- ✅ T28: `spToggleFavView()` 加空状态提示：无收藏时展示引导文字
- ✅ 新增 `.header-signal` CSS（信号概览紧凑样式）
- ✅ 新增 `.fav-empty-msg` CSS（收藏空状态提示）
- ⚠️ **雷达 CSS 残留未清理**（`.radar-block` 到 `.radar-empty`，第 142-164 行）

**gen_about.py（关于页生成器）**:
- ✅ T29: 三个 tab 顶部加分管一句话说明 → 资讯版=资讯从哪来/怎么筛；企业库=企业字段/分类体系；规则=评分公式和技术细节
- ✅ 推荐理由说明文字从"蓝色文字"更新为"★ 标记"

**selection/recommend.py（新建，推荐理由重算）**:
- ✅ T24+T30: 每次跑批用 5 套差异化模板重算全部推荐理由：
  - 融资类：按金额量级（超大额≥5亿/大额≥1亿/一般）分三档措辞 + 海外/国内不同参照角度
  - IPO 类：提及具体交易所 + 国内对标逻辑
  - 收购并购类：强调整合风险 + 反常识点
  - 政策法规类：突出政策影响面 + 申报窗口
  - 产品发布类：强调技术落地 + 差异化亮点
- ✅ 去重逻辑：标题已出现金额/关键词 → 推荐理由不再重复
- ✅ 已接入 `run_daily.py` STEPS（reapply_centrality 之后）

**loop_audit.py（新建，L2 自审模块）**:
- ✅ T31-T33: 每日跑批后自动走查：
  1. HTML 结构健康（空块检测、缺失元素、大块残留如 radar-block）
  2. 数据质量（噪音率>20%?、精选率<10%?、数据陈旧?）
  3. UI 三页一致性（侧栏顺序、筛选风格、卡片样式统一性）
  4. 已知问题回归（噪音堆积、radar-block 残留、标签下拉残留、层级/特色筛选残留）
- ✅ 产出 `data/L2_AUDIT.md`（人读报告）+ console 摘要
- ✅ 已接入 `run_daily.py`（validator 之后、deploy 之前）
- ✅ 已测试一次（发现 3 严重 + 2 警告 + 2 回归）

**run_daily.py（流水线编排器）**:
- ✅ 新增 2 个步骤：`selection.recommend.run_daily_step()` + `loop_audit.run_daily_step()`
- ✅ 步骤总数：12 → 14

### 4.3 尚未执行的后续步骤（= 新 AI 接手后的 To-Do）

1. **ui_common.py**: 删掉第 142-164 行雷达 CSS
2. **重跑流水线前端步骤**: recommend → generator → gen_enterprise → gen_about
3. **跑 L2 自审**: 确认 3 严重问题清零
4. **部署**: deploy_ghpages.py
5. **提交**: git add -A && git commit
6. **全量跑 run_daily**: 验证 14 步全过

---

## 五、协作机制

### 5.1 日常沟通方式与频率

- **用户身份**: 小爽 = 银发财经深度作者，"艾年"公众号主理人
- **沟通风格**: 大白话、小白能懂、少用技术术语
- **频率**: 每完成一个阶段任务后主动汇报（不要等用户问），格式固定：
  > 本次完成情况 / 遇到的困难 / 需要协助的 / 新发现的需求 / 下一步优先级
- **模式**: 始终 Craft 模式，自主执行，不用事事请示
- **例外**: 只有紧急事项（网站挂了、数据全丢了、用户明确问问题）才主动打断沟通

### 5.2 任务分配与汇报流程

- **自主安排**：读完交接文档后自己排优先级往下干
- **完成后汇报**：用大白话总结上述 5 点
- **持续迭代**：做完一轮就检查哪些可以自动化的 → 接入 L2 自审 → 防止下次同类问题再让用户当 QA

### 5.3 决策机制与权限范围

- **全权自主决定**：技术方案、UI 细节、代码实现、部署时机
- **克制原则**：不过度设计（如聚合源评分惩罚 = 冗余，两级闸门+降级已够）
- **增量修复 > 推倒重来**：用户明确说过这个偏好
- **删除/重构前确认**：如果涉及已有功能的大幅改变（非 UI 微调），需确认
- **重要架构决策**：留记录在 MEMORY.md 和 每日日志

---

## 六、基本原则与注意事项

### 6.1 核心原则

1. **以海外为镜照中国之路**：海外企业的国内可比性是核心叙事框架
2. **深度企业分析 > 资讯流水**：核心交付是选题（企业研究价值），不是新闻
3. **低成本优先不降质**：HY3 免费期内全力冲质量；之后切 hunyuan-lite 或纯规则
4. **铁律**：终分/精选/聚类主条 100% 代码算，模型只打维度原始分
5. **写查分离**：改了代码必须编译测试，部署前必须跑 L2 自审
6. **直接执行、事事有回应**：有结果就汇报，不隐藏问题
7. **不过度设计**：够用就好，不加冗余代码（见上面聚合源惩罚的决定）
8. **增量修复 > 推倒重来**：用户反复强调

### 6.2 特别注意事项与潜在风险

| 风险 | 说明 | 处理方式 |
|------|------|----------|
| **gh-pages 部署连接重置** | `deploy_ghpages.py` 偶发 curl 35（服务端重置连接） | 已加 3 次重试机制，每次 sleep 3s |
| **Windows git mktree 换行符问题** | stdin 传参会把 `\n` 变 `\r\n`，文件名带 `\r` → Pages 404 | 已改为写临时文件(LF字节)绕过 |
| **Google News RSS 偶发超时** | 代理瞬时重置（非永久不可用） | Google News 为主 + 兜底容错链 |
| **采集失败不阻断流水线** | collector 步骤失败时后续步骤仍跑（用已有数据） | run_daily 每步 try/except，关键步失败才跳过部署 |
| **feedparser 无超时** | feedparser 直接调 URL 无 timeout | collector 已用 requests.get(timeout=15) 预取 |
| **信源数量已变** | config.py 已改为 44 信源，但 about.html 和 PROJECT_STATUS.md 旧版仍写 37 | 重生成 about.html 后自动修复 |
| **多个账号同时写文件** | 两个 WorkBuddy 账号不能同时编辑同一文件 | 一个写代码时另一个只读；用本文件做状态交接 |

### 6.3 已知问题及建议处理方式

| 问题 | 当前状态 | 建议 |
|------|----------|------|
| **推荐理由重复（最多 16 次）** | `selection/recommend.py` 已完成模板升级，待重新生成后验证效果 | 重生成后跑 L2 自审看 max_dup 是否下降 |
| **推荐理由与标题金额重复（6 条）** | `recommend.py` 已做去重检查，待重新生成后验证 | 同上 |
| **radar-block CSS 残留** | `ui_common.py` 第 142-164 行 | 删掉这些行 |
| **feedback.jsonl 空** | 用户觉得网站还不够好用，没开始收藏 | 等 UI 大改上线后提醒用户 |
| **定时任务状态不明** | `automation_update list` 返回空，但 4 个此前 ACTIVE | 用 `automation_update mode="list"` 确认状态 |
| **企业库 news_coverage 仅 135 家** | 上一个 Agent 崩溃未完成 | 需重建 Agent 重做全量 1118 家覆盖 |
| **聚类余弦阈值 0.82 偏严** | 待 feedback.jsonl 有数据后回测 | 暂缓 |
| **L2/L3 强模型 API key 未配置** | 当前规则兜底可用，不影响质量 | 暂缓 |
| **B 站热度数据源未接入** | 不影响核心功能 | 暂缓 |

---

## 七、数据资产快照（2026-07-08 10:28）

| 资产 | 文件 | 数量 | 备注 |
|------|------|------|------|
| 企业库 | `data/enterprise/all_enterprises.json` | 1118 家 | 国内/海外，17 字段 |
| 企业评分 | `data/enterprise/enterprise_scores.json` | 1118 条 | research_value 0-100 |
| 资讯精选 | `data/scored_latest.json` | 46 条 | 噪音清理后，6维评分+聚类+实体 |
| 噪音清理备份 | `data/scored_latest.json.bak_20260708_102036` | 173 条（含127噪音） | 可回滚 |
| 信源 | `config.py` SOURCES | 44 个 | T1=13 / T2=24 / T3=7 |
| 反馈数据 | `data/feedback.jsonl` | 空（0 条收藏） | 等用户使用 |
| L2 自审报告 | `data/L2_AUDIT.md` | 1 份 | 最新：3 严重 + 2 警告 |
| 定时任务 | automation DB | 4 个 ACTIVE（需验证） | 01:00 采集 / 04:00 扩库 / 06:00 自审 / 09:00 补跑 |
| 每日日志 | `.workbuddy/memory/2026-07-08.md` | 7 轮迭代记录 | 完整工作历史 |

### 7.1 新增模块（本轮 T22-T33 新建/大改）

| 文件 | 作用 | 状态 |
|------|------|------|
| `selection/recommend.py` | 推荐理由差异化模板重算（5+套） | ✅ 已建、已测、已接入流水线 |
| `loop_audit.py` | L2 自审模块（HTML走查+数据质量+UI一致性+回归） | ✅ 已建、已测、已接入流水线 |
| `purge_legacy.py` | 存量噪音自动复查（防旧噪音复发） | ✅ 已建、已测、已接入流水线 |
| `feedback_loop.py` | L3 反馈回灌（feedback.jsonl→微调评分权重） | ✅ 已建、已接入，无数据时空操作 |
| `tag_enterprises.py` | 资讯事件→企业标签自动反哺 | ✅ 已建、已测、已接入流水线 |
| `SOURCE_AUDIT.md` | 信源体检报告（一手/二手分层） | ✅ 无代码依赖，纯文档 |
| `loop_engineering_design.md` | Loop Engineering 调研 + 三层落地设计 | ✅ 无代码依赖，纯文档 |

### 7.2 项目目录结构更新

```
silver-pulse/
├── config.py              # 信源44/评分权重6维/阈值/关键词（单一真相源）
├── collector.py           # RSS采集 + 两级相关性闸门(is_relevant) + 容错兜底链
├── score_and_merge.py     # 旧版评分合并脚本（新条目 creation 时写 recommendation）
├── selection/             # 选题引擎包
│   ├── l1_prefilter.py    # L1 预筛选
│   ├── aggregator.py      # 聚合
│   ├── cluster.py         # 事件聚类 (entity,event_type) 精确归簇 + 余弦兜底
│   ├── enterprise_score.py # 企业研究价值分
│   ├── reapply.py         # 重新应用
│   ├── score_skill.py     # 5维规则兜底打分（零成本）
│   ├── translate.py       # 中文翻译回填（零成本）
│   ├── recommend.py       # 🆕 推荐理由差异化模板重算
│   └── reapply_centrality.py # 赛道核心度 + 6维加权终分重算
├── run_daily.py           # 每日流水线编排器（14步）
├── generator.py           # index.html 生成器（资讯看板）
├── gen_enterprise.py      # enterprise.html 生成器（企业库）
├── gen_about.py           # about.html 生成器（规则+说明）
├── ui_common.py           # 统一设计系统（CSS/侧栏/主题/收藏JS）
├── enterprise_names.py    # 企业名集合（两级闸门交叉校验用）
├── purge_legacy.py        # 🆕 存量噪音自动复查
├── feedback_loop.py       # 🆕 L3 反馈回灌（权重微调）
├── tag_enterprises.py     # 🆕 资讯→企业标签反哺
├── loop_audit.py          # 🆕 L2 质量自审模块
├── validator.py           # 自检 → STATE.md
├── deploy_ghpages.py      # gh-pages 部署（git plumbing 孤儿commit + 3次重试）
├── SOURCE_AUDIT.md        # 🆕 信源体检报告
├── loop_engineering_design.md # 🆕 Loop Engineering 设计文档
├── PROJECT_STATUS.md      # 📌 本文件（项目交接）
├── RULES.md               # 规则真相源
├── STATE.md               # 当前状态快照
├── data/
│   ├── scored_latest.json         # 46条纯净资讯
│   ├── raw_20260708.json          # 最新采集原始数据
│   ├── history.json               # 采集历史(防重复)
│   ├── L2_AUDIT.md                # 🆕 L2 自审报告
│   └── enterprise/
│       ├── all_enterprises.json   # 1118家
│       └── enterprise_scores.json # 研究价值分明细
└── output/                # 部署用HTML镜像（与 gh-pages 分支同步）
```

---

## 八、部署与运行速查

### 8.1 线上地址
- **主站**: https://shuanghello153-eng.github.io/silver-pulse/
- **仓库**: shuanghello153-eng/silver-pulse（gh-pages 分支 = 线上内容，main 分支 = 源码 + 自动化数据）

### 8.2 Python 环境
- **受管 Python**: `C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe`
- **依赖**: feedparser, requests, lxml, bs4, openpyxl（已在 venv 中安装）

### 8.3 常用命令

```bash
cd G:\workbuddy\2026-06-28-23-34-20\silver-pulse

# 编译检查
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m py_compile generator.py gen_enterprise.py gen_about.py ui_common.py loop_audit.py

# 只重新生成 HTML（不采集不打分）
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe generator.py
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe gen_enterprise.py
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe gen_about.py

# 跑 L2 自审
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe loop_audit.py

# 部署
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe deploy_ghpages.py

# 全量流水线
C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe run_daily.py

# 跳过采集（仅用已有数据）
SKIP_COLLECTOR=1 C:\Users\shuan\.workbuddy\binaries\python\envs\default\Scripts\python.exe run_daily.py
```

---

## 十、2026-07-08 下午-晚 更新日志（账号B·研究员艾年）

> 本轮（第三批次）聚焦：用户截图反馈的真实 UI 问题修复 + 信源漏采根因排查与修复 + Loop Engineering 自检增强 + 降本。

### 10.1 资讯页筛选区修复（用户截图反馈"展示很奇怪"）
- 加**时间筛选**（全部/近2周/近1个月/近3个月，标签胶囊样式，默认全部）
- **排序下拉框 → 箭头按钮**：评分 ↓ → 评分 ↑ → 时间 ↓ 三态循环（`cycleSort()`）
- 事件·领域·标签三行合并紧凑栏（T27 已做）保留，加时间行
- 移除旧 `<select class="sort-select">`，JS 同步改为 `activeTime` + `cycleSort`

### 10.2 企业库筛选区修复（用户反馈：标签重复/排版乱）
- **删除重复的"融资"筛选行**（原 582-585 行，与"有融资/IPO"标签胶囊重复）
- **排序下拉框 → 箭头按钮**：研究价值 ↓ / 融资金额 ↓（点击切换 ↑↓，`setEntSort()`）
- 移除 `activeFund` 变量 + `[data-fund]` 死 JS 处理，卡片 `data-fund` 排序属性保留
- 共享 `.sort-arrow` CSS 加入 ui_common.py

### 10.3 信源漏采根因排查（用户："44源为何只66条？"）
**诊断结论**：核心 Tier-1 源几乎没采到（MobiHealthNews=1、Crunchbase=0、TheGerontechnologist=0、StartUp Health=0），反是 Google News 宽查询灌进大量无关中文泛新闻（新浪财经/人民日报/新华网）。
**根因**：4 个核心源在 config 里配的是**网页 URL**（如 `/sections/...`、`/articles/`、`/category/funding/`）而非 RSS feed，feedparser 解析 HTML 返回 0 条；且 `google_news` 方法丢弃频道路径只查整站，导致 investor/funding 频道没被监控。
**修复**：
- `thegerontechnologist`: `/articles/`+`/podcast/` → `https://thegerontechnologist.com/feed/`（实测 10 条，原 google_news 整站 0）
- `crunchbase_news`: `/sections/health-wellness-biotech/` → `https://news.crunchbase.com/feed/`
- `homehealthcarenews`: `/category/funding/` → `https://homehealthcarenews.com/feed/`
- `startuphealth`: 网页 → `https://www.startuphealth.com/startup-health-blog?format=rss`（实测 20 条）
- **增强 `google_news` 方法**：频道路径含信号词(invest/fund/venture/ipo 等)时，把该词加入查询，**真正监控二级频道而非整站**（MobiHealthNews investor、FierceHealthcare VC 等）

### 10.4 Loop Engineering 自检增强（用户："自我纠错为啥还频繁出明显 bug？"）
**诚实复盘**：之前的 loop_audit 只查 HTML 结构（空块/radar 残留），**抓不到交互/视觉层 bug**。本轮补三类检测：
1. **死 JS 引用**：`getElementById` 目标 id 在 HTML 不存在 → CRITICAL（刚修的 `ent-sort` 即此类）
2. **残留 `<select>` 下拉框**：body 内仍有 select → CRITICAL（我们意图全改标签/箭头）
3. **重复筛选按钮**：同 `data-group` 下同 `data-value` 多次 → WARN
后续：将 CRITICAL 阻断部署接进 run_daily（进行中）。

### 10.5 降本
- 脚本静音（T58）：collector 等详细日志写 `data/run_logs/`，只给模型一行摘要（进行中）
- 新建 `0722_token_downgrade_plan.md`：免费期后分级降级方案（每日更新保 Hy3，摘要/标签池降级轻量模型）

### 10.6 信源完整性核对
- 用户重发完整信源清单（50+ 渠道），逐一核对 config.SOURCES（44 源）
- **已覆盖**：AgeTech 系(3)、StartUp Health、Crunchbase、MobiHealthNews、FierceHealthcare、TheGerontechnologist、McKnight's 系、AgeTech Collaborative、Mary Furlong、INC.5000、A2 Collective、Creating A New Healthcare、FinSMEs、PR Newswire、FemTech Insider、Axios、HIT Consultant、Pulse2、Business Wire、TechCrunch、BetaKit、Coverager、Yahoo Finance、Modern Healthcare、HomeCare Mag、国内 AgeClub/36氪/动脉网/Google News 银发、政府一手源(民政部/国务院/老龄协/LeadingAge/Argentum/NIC/NCOA)
- **缺口（待建，非阻断）**：① YouTube 视频频道监控（Home Health Care News/homecare/fiercehealthcare 的热门视频）② 三家 VC 一手源（Third Act Ventures / 7Wire Ventures / Khosla Ventures 的博客/洞察）

---

---

## 十一、Loop Engineering 落地与本轮修复（2026-07-08 晚）

### 11.1 本次抓到并修复的真问题
- **collector.py 缩进错误**：`else:` 分支 `_clog(...)` 未缩进 → `IndentationError`，此前**阻塞全部每日跑批**。已修复。
- **loop_audit 死 JS 误报 → 误阻断部署（连续两轮）**：收藏空状态 `fav-empty` 是 JS 防御式懒创建（`getElementById` 拿到 null 后 `createElement` 建 `#fav-empty`），被朴素 dead-JS 检测误判为"引用不存在的 id" → 报 2 个 CRITICAL → 部署被拦。已让检测识别 `document.` 前缀与懒创建模式（`var x=document.getElementById('id')` 后 `x.id='id'` 且脚本含 `createElement`），不再误报。
  - **元教训**：自检器本身也有 bug，必须"被自检"。这正呼应小爽"提了不下 10 次问题"的痛点——以前是带 bug 上线，现在是 CRITICAL 拦下，但拦错了比不拦更糟，所以检测精度要持续打磨。
- **推荐理由重複（max_dup 45→14）**：多数条目无 entity 且落到默认"行业趋势"，`head` 为空 → 45 条理由完全相同。已改为无 entity 时用语域/具体标签作主语，打破雷同。

### 11.2 Loop Engineering 机制（小爽问：何时触发/原理/用途/额度/迭代）
- **触发时机**：`loop_audit`(L2 质量自审) + `noise_spike_guard`(L2 进化层) 是 `run_daily.py` 第 14-15 步，**每天 01:00** 随"每日资讯更新"自动化(1782915193510)执行；`feedback_loop`(L3) 是第 6 步同日执行。新增 **09:00 自愈补跑**(automation-1783507424052)：若 01:00 部署被拦，09:00 再跑一次尝试部署（此前 STATE.md 写"09:00 补跑"但无对应自动化，是悬空引用，现已闭合）。
- **原理**：
  - L2 质量自审：对生成 HTML 做静态走查（死 JS / 残余 `<select>` / 重复筛选 / 已知问题回归 / 标签爆炸）+ 数据质量（噪音堆积、推荐理由重复）。
  - L2 进化层：每日记 noise/curated 基线，检测"噪音 spike / 精选暴跌 / 规则漂移"，连续 2 天 spike 自动把源写入 `noise_blocklist.json` 封禁 2 天 + git 备份 config + pitfalls 日志。
  - L3 反馈闭环：读用户导出 `feedback.jsonl`（收藏）→ 评分权重 ±0.03 安全微调（带边界夹紧）→ `user_pref.json`，次日生效。
  - 部署门槛：`run_daily.py` 部署前检查——关键步失败 **或** loop_audit 有 CRITICAL → 跳过部署，绝不推有可见缺陷的版本。
- **用途**：直接回应"网站常有明显问题"——CRITICAL 级可见缺陷（死 JS 致排序失效、残余下拉、标签炸屏、说明数字漂移）自动拦下；噪音源自动封禁；规则漂移告警；收藏反向调权。
- **额度**：≈0。L2/L3 全是纯 Python 正则+JSON，零模型调用、零 token。每日额度大头是 collector 联网(非 token) + 框架读 stdout(已静音，仅一行摘要)。
- **迭代方向（待办）**：① 视觉回归（截图 diff，需无头浏览器，建议每周跑）；② 把历史每类 bug 沉淀为 KNOWN_ISSUES 一项，织防护网；③ noise_spike 阈值等 feedback.jsonl 有数据后回测；④ 部署被拦事件推一条通知给小爽，使阻断可见可追溯。

### 11.3 已提交
- commit 299715f：collector 缩进修复 + loop_audit 死 JS 误报修复 + 推荐去重 + about 动态信源数 + 09:00 自愈自动化
- gh-pages 部署 commit 58729f9d03（loop_audit 0 CRITICAL，仅 1 WARN max_dup=14 非阻断）

---

## 九、小爽（用户）关键偏好速查

1. **核心叙事**："以海外为镜照中国之路"
2. **选题四标准**：S1 大企业(有年报) / S2 热点事件 / S3 反常识差异化 / S4 国内可比性
3. **只做选题发现+初步研究**，不写稿(另一 AI 写)；不发布
4. **直接执行、事事有回应、主动发挥有观点**
5. **低成本优先不降质**；HY3 免费期全力推质量
6. **增量修复 > 推倒重来**
7. **移动端优先**（全程手机操作，UI 对触控/移动端敏感）
8. **大白话沟通**，少用技术术语
9. **不用事事请示**，自己排任务自己干
10. **L2 自审最重要**——用户不想当 QA

---

_此文件与 `RULES.md`、`MEMORY.md`、每日日志同步维护。任何重大进展或决策变更后，更新本文件对应章节。_
_最后更新: 2026-07-08 19:30 — 信源补全+region修复+收藏面板重构+视觉回归_

---

## 十二、本轮修复（2026-07-08 晚，用户第 3 批指令）

### 12.1 信源补全（缺口 4 个，非 6+）
- 用户："50+ − 44 > 6，为啥仅缺口 4 个？" → **澄清：用户给的是 50+ 个 L2 频道，不是 50+ 个源**。config 是 44 个 L1 源（含其下多个 L2 频道）。逐条核对 10.6「已覆盖」清单，全部 44 源均已含用户点名源；真实缺口就是 4 个一手源。
- **新增 4 源（总 48）**：`third_act`(Third Act Ventures, aging 早期 VC)、`sevenwire`(7Wire Ventures, perspectives RSS)、`khosla`(Khosla Ventures, longevity 重仓)、`youtube_silver`(YouTube 银发热门视频，监控 The Villages/aging tech/home health 视频)。均经质量核查，确为银发一手高价值源。
- YouTube「热门视频存量数据」：已加为监控源（每日经 Google News `site:youtube.com` 抓更新）；**真正按播放量排序的「热门」需要 YouTube Data API（无 key）**，列为后续增强；The Villages C 端爆款视频已确认存在（insidethebubble 提到 40万+ 观看），待有 API key 时可做存量热度抓取。

### 12.2 Region 修复（真 bug）
- **现象**：AgeClub 新闻卡片 `data-region="overseas"`（海外），但 AgeClub 是国内源。
- **根因**：`score_and_merge.py` 用 `is_overseas(source_name)` 名字启发式，兜底逻辑「纯 ASCII 名→判海外」把英文名国内源（AgeClub）误判海外。
- **修复**：config 新增 `get_source_region(name)` 单一真相源（从 SOURCES 读 region）；`score_and_merge` 与 `generator` 均改调用它；并在合并时对**全部**条目做 region 归一化（含历史存量），旧 AgeClub 条目也一并纠正。

### 12.3 about.html 规则同步
- 资讯看板描述「每周…聚合」→「**每日**…聚合」（我们已改每日，之前是「说明没更新」实锤）。标签池「每周迭代」保留（自动化确实每周一跑）。

### 12.4 收藏功能重构（解决"打不开"）
- 旧方案：`body.fav-mode` + CSS 隐藏非收藏项，脆弱且"打开"无感知。
- 新方案：**右侧抽屉面板**（`#fav-panel`），点「⭐ 我的收藏」必定滑出，列出收藏项（读 localStorage + 实时渲染卡片标题/来源，可点击跳转），带数量角标与空状态。导出 `feedback.jsonl` 逻辑保留。
- **L3 仍待激活**：`feedback_loop.py` 已接线，但 `data/feedback.jsonl` 为空——网站导出是下载到**浏览器下载目录**，未落到仓库。需用户把导出文件放入 `silver-pulse/data/feedback.jsonl` 后重跑，才会真正按收藏微调评分权重。

### 12.5 标签左对齐
- `.feed-tags` / `.filter-btns` 显式加 `justify-content:flex-start`（之前靠默认，用户反复反馈"没左对齐"）。

### 12.6 任务表 T42–T47 缺口说明
- 用户发现任务表 T40+ 序号缺 T42–T47。核实：该段在上一轮上下文重置/任务清理中从可见列表丢失（工作未消失，部分已并入 T48–T60 或已完成），非"遗忘未完成"。
- 本轮重建为**无缺口待办集 T61–T68**（含本轮回填项）：截图视觉回归 / L3 激活 / B站热度 / 聚类回测 / 元标签清洗 / news_coverage 扩全量 / noise 阈值回测 / 部署阻断通知。

### 12.7 视觉回归
- 用户要求"自己做视觉回归"。本轮以代码级审计修复了上述具体可见问题；并安装 playwright+chromium 尝试**像素级截图回归**（标签对齐/收藏面板/region 角标/筛选排版）。若沙箱网络阻断 chromium 下载，则回退为代码审计，并在站点说明中标注已知视觉检查项。
- **已落地像素级回归**：`visual_regression.py` 用 headless chromium 对三页截图 + 断言（标签对齐 / 收藏抽屉打开 / region 角标 / 控制台报错），本地 `file://` 跑通全过。发现并修复真 bug：收藏入口 `#nav-fav` 同时绑定内联 `onclick` 与 `addEventListener` → 点击 toggle 两次（开又关）→"打不开"。删内联 onclick，只留事件监听，抽屉正常打开。

### 12.8 本轮续修（20:5x 起，rJVdY4 流水线）
- **收藏打不开（用户头号痛点）**：根因 = ui_common 335-336 内联 `onclick="spToggleFavView()"` + 498 行 `addEventListener` 双重绑定。修：删内联 onclick，仅 `spInitFav` 事件监听。视觉回归确认资讯/企业库抽屉均打开 OK。
- **信源补全 44→48**：补 YouTube 银发热门 + 3 家 VC（Third Act / 7Wire / Khosla）。用户清单 50+ 实为 L2 频道（属 44 源属性字段），缺口仅 4 个 L1 源，已补齐。
- **YouTube 存量爆款**：新增 manual 注入机制（`collector._build_manual_article` + `data/manual_news.json`，2 个 The Villages 种子：Peter Santenello 900万+ 播放 vlog +《Some Kind of Heaven》纪录片）。坑：首跑注入后因 `mark_seen` 写 history 被 `is_duplicate` 永久去重；已改 manual 注入跳过 history 去重（策划种子每轮必现）。`score_and_merge` 曾以 `signal_score=0` 过滤 manual → 已加 `manual` 豁免且种子补 `signal_score=8.0`。
- **Khosla 招聘泄漏**：`is_job_spam` 正则可命中，但旧 run 的 `existing` scored 回流；已在 `score_and_merge` 加载 existing 时过滤 `is_job_spam`（清 3 条），collector 新采集已挡。
- **about 说明最新**：每周→每日；信源数动态 `len(SOURCES)=48`；AgeClub 角标=国内（region 用 source_id 查 config 真相源）。
- 部署 56fa127008 已含 fav 修复；rJVdY4 重跑输出 manual+清招聘的干净版，待确认后提交 main。
