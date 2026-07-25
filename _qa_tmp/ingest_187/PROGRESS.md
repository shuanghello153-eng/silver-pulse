# 187家入库进度（断点续跑用）

> 自动化任务/续跑者：读本文件确定断点，从"下一步"继续。手册依据 企业库运维/企业库运营手册_V8.6.md。

## 任务
handoff/enterprise_inbox 下 6 批次共 187 家 → 走 V8.6 八步入库。

## 已完成
- ✅ 步骤1 相关性：187 → KEEP 177 / PENDING 5 / DUP 5（screened_candidates.json + pending_xiaoshuang.json）
- ✅ 步骤2 全库去重：177 vs 库内1773 → 净新增 **137**（deduped_candidates.json + step2_report.json）
  - 库内已存在跳过 37；批内合并 3 组；库内增量登记 6；库内自重复登记 4 组（待步骤6/8处理）
- 🔄 步骤3 补全字段（进行中）：
  - 137 切 8 片放 draft_in/；起草规范 DRAFT_SPEC.md（已修正tag词表为权威98个）
  - W12(11日本介护)+W13_A(1德国长寿) 由主AI亲起 → 已写 draft_out/（含Benesse 2024 EQT MBO退市更正）
  - W11_p1/p2、W9-W10_p1/p2、W13_B、W5 由 6 子智能体并行起草 → 写 draft_out/（进行中）

## 下一步（步骤3收尾）
1. 待 draft_out/ 8 个分片齐全（W11_p1=21/W11_p2=22/W9-W10_p1=19/W9-W10_p2=20/W13_B=25/W5=18/W12=11/W13_A=1 = 137）
2. 跑校验脚本：tag_l2 全在98词表内 / recommend 无禁用词 / 字段完整 / 评分有区分度；不合格项修复
3. 合并8片→分配 serial（从 **#1851** 起顺序）→ 组装 候选_137.json
4. `python scripts/score_candidates.py --candidates 候选_137.json`（补 signal_strength + total_score）
5. `python scores_draft/rework/check_description.py` + `check_single.py` 门禁自测 → 修复
6. 更新本文件标记步骤3完成，进入步骤4

## 关键数字
- 库内基线 1773 家，max serial #1850 → 新记录 #1851 起
- tag_l1 只有8个：养老服务/康复辅具/消费品/文娱社交/行业服务/食品营养/金融保险/投资机构
- 权威 tag_l2 词表 = data/enterprise/_l2_l1.json 的键（98个）
- 数据库真相源：data/enterprise/all_enterprises.json

## 待小爽定（不阻塞，事后审）
- 5家 pending_xiaoshuang（Transcarent/Higi/Payactiv/Ellipsis Health/Vulcan Augmetics，泛医疗/全年龄）
- 库内自重复4组（Uniper Care↔Uniper / Bold↔Age Bold / Vynca↔VyncaCare / Cera Care↔Cera）
