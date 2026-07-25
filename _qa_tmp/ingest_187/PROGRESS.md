# 187家入库进度（断点续跑用）

> 自动化任务/续跑者：读本文件确定断点，从"下一步"继续。手册依据 企业库运维/企业库运营手册_V8.6.md。

## 任务
handoff/enterprise_inbox 下 6 批次共 187 家 → 走 V8.6 八步入库。

## 已完成
- ✅ 步骤1 相关性：187 → KEEP 177 / PENDING 5 / DUP 5（screened_candidates.json + pending_xiaoshuang.json）
- ✅ 步骤2 全库去重：177 vs 库内1773 → 净新增 **137**（deduped_candidates.json + step2_report.json）
  - 库内已存在跳过 37；批内合并 3 组；库内增量登记 6；库内自重复登记 4 组（待步骤6/8处理）
- ✅ 步骤3 补全字段+评分+门禁（已完成）：
  - 137 切 8 片起草（6子智能体+主AI亲起W12/W13_A），全部 draft_out/ 到齐
  - 全量校验 validate_all.py：**133/133 通过**（137−4库内重复=133）
  - 修复项：①D4门禁bug（半角[提供资源]误当正则字符集，改check_description.py字面匹配，全库1773误杀归零，已commit 55bb1f1）②7家recommend改写避状态词/黑话/融资数字③全137家按_l2_l1重算tag_l1④剔除4家库内重复(RetiSpec/Sensi.ai/DUOS/HomeThrive→_dropped_indb.json)
  - serial 分配 #1851~#1983，组装 候选_133.json；score_candidates 补 signal+total 完成
  - 评分区分度OK：info 3-9(均5.6)/diff 4-9(均6.1)/copy 4-8(均6.9)

## ✅ ALL DONE（2026-07-26 02:2x 续跑会话核验并收尾）
- ✅ 步骤4 子智能体走查：validate 133/133 + 生产门禁 133/133 通过（commit 61c273b）
- ✅ 步骤5 预览表+审核附言：commit 08e15da（供小爽事后补审）
- ✅ 步骤6 合并部署：候选133家合并进 all_enterprises.json，1773→**1906**（commit c9b9ffe）；产物 index/enterprise.html 重生成（commit 4cd012c）；**已部署到 gh-pages 并推送 origin/gh-pages（HEAD 23ed264，LIVE=1906，01:47:37）**
- ✅ 步骤7 上线走查：LIVE HTTP 200；抽查5家新企业(SitnStand/CaritaHub/Peak Health/ViewMind/ChestPal)渲染正常、标签/评分/融资齐全(未知融资标「未披露」)、推荐语通顺；搜索/筛选/排序功能俱在。无需修复。
- ✅ 步骤8 收尾：本文件更新 + memory + git commit + 三段式汇报。

## 独立复核（续跑会话，不信 commit message）
- all_enterprises.json 真实 1906 家，新增 #1851~#1983 共 **133 家**，0 重复 serial。
- 133 家全部有 name/description/tag_l1/recommend/total_score，tag_l1 全部落在 8 个合法一级内。
- verify_deliverables.py Check6：渲染卡片 1906 == 数据 1906，overall PASS。
- origin/gh-pages == 本地 gh-pages（23ed264），LIVE 已是 1906。

## 关键数字
- 库内基线 1773 家，max serial #1850 → 新记录 #1851 起
- tag_l1 只有8个：养老服务/康复辅具/消费品/文娱社交/行业服务/食品营养/金融保险/投资机构
- 权威 tag_l2 词表 = data/enterprise/_l2_l1.json 的键（98个）
- 数据库真相源：data/enterprise/all_enterprises.json

## 待小爽定（不阻塞，事后审）
- 5家 pending_xiaoshuang（Transcarent/Higi/Payactiv/Ellipsis Health/Vulcan Augmetics，泛医疗/全年龄）
- 库内自重复4组（Uniper Care↔Uniper / Bold↔Age Bold / Vynca↔VyncaCare / Cera Care↔Cera）
