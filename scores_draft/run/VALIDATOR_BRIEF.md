# 校验员工作手册（独立复核）

你独立复核工人产出的 out JSON，不放水。读 `scores_draft/run/out/batch_NNN_out.json`，并对照 `scores_draft/run/inbox/batch_NNN.json`（看企业原字段，核对 old_tags 是否照抄、分数是否有据）。

逐企业检查：
1. 四个分数都在 0~10 区间；`research_value` = round((signal×0.3+info×0.3+diff×0.2+copy×0.2)×10, 1) 计算正确。
2. `rec_v1/v2/v3` 均非空；**每个版本都覆盖 4 维度**（信号/信息量/差异化/可复制）；三版互不雷同；未复述卡片字段（desc_cn/标签/融资额）；每版≤90 字；无"泛泛而谈/重复啰嗦"的水货。
3. `payor_model`、`business_tags_role`、`silver_verdict` 非空；`update_time`="2026-07-17"。
4. `tag_review` 的 `old_tags` 与 inbox 中企业当前 tag 一致；`suggested` 每条 action/tag/reason 合理、有业务依据。
5. `nonsilver` 仅含 "非银发" 或 "泛医疗擦边" 企业，且 reason 成立；"核心银发" 不得出现在 nonsilver。

输出 JSON 写到 `scores_draft/run/val/batch_NNN_val.json`：
{
  "batch": NNN,
  "checks": [ {"serial":"...","pass":true/false,"issues":["具体问题描述"]} ],
  "overall_pass": true/false
}
只标问题，绝不修改任何数据。对拿不准的标 fail 并说明。
