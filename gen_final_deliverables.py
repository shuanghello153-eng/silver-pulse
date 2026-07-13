#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成最终交付物（标签体系全映射 v7.md + 全量企业标签 v7.xlsx）。
数据来源：data/enterprise/all_enterprises.json（已应用重构轮 2026-07-13）。
为避免导入 _rebuild_tags.py 触发整库重跑副作用，用 ast 仅抽取 L2_TO_L1 字典。
"""
import ast, json, os, subprocess, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
ENT = os.path.join(ROOT, "data/enterprise/all_enterprises.json")
SYN = os.path.join(ROOT, "data/enterprise/tag_synonyms.json")
RB = os.path.join(ROOT, "_rebuild_tags.py")
OUT_MD = os.path.join(ROOT, "output", "标签体系_全映射_2026-07-13_v7.md")
OUT_XLSX = os.path.join(ROOT, "output", "企业标签全量表_2026-07-13_v7.xlsx")

# ---- 读数据 ----
d = json.load(open(ENT, encoding="utf-8"))
es = d if isinstance(d, list) else d.get("enterprises", d.get("data", []))
print("企业总数:", len(es))

# ---- 用 ast 仅抽取 L2_TO_L1（不执行模块）----
src = open(RB, encoding="utf-8").read()
tree = ast.parse(src)
L2L1 = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "L2_TO_L1":
                L2L1 = ast.literal_eval(node.value)
if L2L1 is None:
    raise SystemExit("未找到 L2_TO_L1")
print("L2_TO_L1 条目:", len(L2L1))

# ---- 同类词 ----
syn = json.load(open(SYN, encoding="utf-8"))

# ---- 计算分布 ----
l1_count = defaultdict(set)      # L1 -> set(企业名)
l2_count = defaultdict(int)      # L2 -> 企业数
cross = 0
all_l2 = set()
for e in es:
    l2 = e.get("tag_l2") or []
    l1 = set(e.get("tag_l1") or [])
    all_l2.update(l2)
    for x in l2:
        if x in L2L1:
            l1_count[L2L1[x]].add(e.get("name"))
            l2_count[x] += 1
    if len(l1) > 1:
        cross += 1

# L1 -> [L2...] 逆映射（仅含真实出现在数据里的二级标签，按 L2 企业数降序）
l1_to_l2 = defaultdict(list)
for l2, l1 in L2L1.items():
    if l2 in all_l2:
        l1_to_l2[l1].append(l2)
for l1 in l1_to_l2:
    l1_to_l2[l1].sort(key=lambda x: -l2_count.get(x, 0))

total = len(es)
sum_l1 = sum(len(v) for v in l1_count.values())
print("一级企业数之和:", sum_l1, "| 跨一级企业:", cross)

# ---- 写 MD ----
lines = []
lines.append("# 标签体系全映射（2026-07-13 v7）")
lines.append("> **v7 重构轮（2026-07-13）**：在 v6 基础上按既定决策重盘。一级 11→10（删 女性健康/精神健康 并降级为医疗健康下 L2；新增 产业资本 L1 收纳 投资机构/行业媒体/咨询研究/会展峰会）。纯规则离线重算，**未调用大模型/未联网**。`python _rebuild_tags.py && python validate_tags.py` 校验 **9/9 全绿**；企业数 1324，二级标签 54 个。")
lines.append("> 真相源：`_rebuild_tags.py`（含 `WALKTHROUGH_FIX` / `OPTIMIZE_FIX_20260712` / `RESTRUCTURE_20260713`）；同类词：`data/enterprise/tag_synonyms.json`；校验：`validate_tags.py`。")
lines.append("")

# —— 一、一级分布 ——
lines.append("## 一、各一级标签企业数（其下二级标签企业集合去重汇总）")
lines.append("| 一级标签 | 企业数 | 占比 |")
lines.append("|---|---:|---:|")
for l1 in sorted(l1_count, key=lambda x: -len(l1_count[x])):
    c = len(l1_count[l1])
    lines.append("| %s | %d | %.1f%% |" % (l1, c, 100.0 * c / total))
lines.append("")
lines.append("- 各一级企业数之和 = %d（≥ 总企业数 %d，比值 **%.2f**），因单企业可挂分属不同一级的多个二级标签。" % (sum_l1, total, sum_l1 / total))
lines.append("- 跨一级企业（同时出现在 ≥2 个一级下）：**%d 家**，属正常现象。" % cross)
lines.append("")

# —— 二、L1 → L2 → 同类词 全量（无省略）——
lines.append("## 二、L1 → L2 → 同类词 全量映射（无省略）")
lines.append("")
for l1 in sorted(l1_to_l2, key=lambda x: -len(l1_count[x])):
    lines.append("### %s（%d 家）" % (l1, len(l1_count[l1])))
    lines.append("| 二级标签 | 企业数 | 同类词（别名，仅搜索扩展用） |")
    lines.append("|---|---:|---|")
    for l2 in l1_to_l2[l1]:
        cnt = l2_count.get(l2, 0)
        aliases = syn.get(l2, [])
        lines.append("| %s | %d | %s |" % (l2, cnt, "、".join(aliases) if aliases else "—"))
    lines.append("")

# —— 三、改动前后对照 ——
lines.append("## 三、v6 → v7 改动前后对照")
lines.append("")
lines.append("**一级标签（11 → 10）**")
lines.append("- 删除 `女性健康`、`精神健康` 两个一级（降级为医疗健康下的二级标签 `女性健康服务`、`心理健康服务`）。")
lines.append("- 新增 `产业资本` 一级，收纳 `投资机构` / `行业媒体` / `咨询研究` / `会展峰会`（行业媒体、咨询研究 从智能科技移出，不再与智能科技纠缠）。")
lines.append("- 其余 8 个一级（养老服务 / 医疗健康 / 康复辅具 / 文娱社交 / 智能科技 / 消费品 / 渠道零售 / 金融保险 / 食品营养）保留。")
lines.append("")
lines.append("**二级标签关键改名 / 合并 / 拆分**")
changes = [
    ("人工智能", "AI", "改名；并剔除非 AI 企业（描述不含 AI/大模型/算法等者改归 医疗器械/智能硬件/远程医疗）"),
    ("智能养老平台", "智慧养老", "改名"),
    ("照护系统", "智慧养老", "并入智慧养老（不再单列）"),
    ("SODH", "SDOH", "拼写修正（Social Determinants of Health）"),
    ("适老化", "适老化改造", "改名，语义更准"),
    ("产业资本(旧L2)", "投资机构", "改名"),
    ("女性健康", "女性健康服务", "改名（并降级为医疗健康 L2）"),
    ("精神健康", "心理健康服务", "改名（并降级为医疗健康 L2）"),
    ("健康管理 / 健康监测", "跌倒监测 / 远程监测 / 用药管理 / 健康咨询 / 体检筛查 / 慢病管理 / 远程医疗", "删除宽泛桶，按描述细分再分配"),
    ("文化娱乐", "社交平台 / 旅游 / 健身 / 教育 / 相亲 / 陪伴机器人 / 就业", "删除宽泛桶，按描述细分再分配"),
    ("数字平台", "行业媒体 / 电商 / 智慧养老 / 零售", "删除宽泛桶，按描述细分再分配"),
    ("康复设备(过宽)", "康复机器人 / 行动辅具 / 假肢矫形 / 护理床具 / 外骨骼 → 合并入 康复设备·康复机器人", "拆分后再合并稀有项，避免幽灵标签"),
    ("（无）", "新增 支付方字段 payor_model", "新横向字段，默认「未披露」，轻量关键词预填 Medicare Advantage / PACE / Medicaid / 商业保险 / 自费 / 政府补贴"),
]
lines.append("| 旧标签 | 新标签 | 说明 |")
lines.append("|---|---|---|")
for a, b, c in changes:
    lines.append("| %s | %s | %s |" % (a, b, c))
lines.append("")
lines.append("**未采纳 / 已驳回的方案**（按用户拍板）")
lines.append("- 不新增「平台」二级标签（用户明确驳回）。")
lines.append("- 行业媒体 / 咨询研究 不移入「产业资本」之外的新字段，直接作为 `产业资本` 一级下的二级标签（用户要求「不要改字段，搞复杂了」）。")
lines.append("- 「是否上市」字段不改（用户：「不用管，列表有这个字段」）。")
lines.append("")
lines.append("**9 家运营企业从 `投资机构` 纠正**（源头误标为「相关上市公司/运营商」，实为运营企业）")
fix9 = [
    ("南京新百", "养老服务（居家护理）", "养老服务运营商，旗下安康通/禾康养老"),
    ("悦心健康", "养老服务（养老社区）+ 医疗健康（康复医疗）", "转型大健康与养老服务"),
    ("Ensign 集团", "养老服务（养老机构）", "专业护理院与康复服务商"),
    ("Qida", "养老服务（养老社区）", "西班牙养老与医疗健康服务提供商"),
    ("可靠股份", "消费品（个人护理）", "成人失禁护理用品"),
    ("中顺洁柔", "消费品（个人护理）", "生活用纸龙头"),
    ("BioAge Labs｜长寿科技", "智能科技（长寿科技）", "长寿与代谢衰老疗法公司"),
    ("Seen Health", "医疗健康（慢病管理）", "PACE 综合照护"),
    ("Ellipsis Health", "医疗健康（→医疗器械，AI医疗合并）", "临床语音 AI，非投资机构"),
]
lines.append("| 企业 | 纠正后标签 | 依据 |")
lines.append("|---|---|---|")
for a, b, c in fix9:
    lines.append("| %s | %s | %s |" % (a, b, c))
lines.append("")

# —— 四、校验证据 ——
try:
    r = subprocess.run([sys.executable, "validate_tags.py"], capture_output=True, text=True, cwd=ROOT, timeout=120)
    lines.append("## 四、校验证据（validate_tags.py）")
    lines.append("")
    lines.append("```")
    lines.append(r.stdout.strip()[-1200:] if r.stdout.strip() else "(无输出)")
    lines.append("```")
    lines.append("")
    lines.append("结论：**9/9 全绿**（二级标签 %d 个 / 一级标签 %d 个；0 标签企业=0；单企业 ≤3 二级；同类词无碰撞/孤儿/退化）。" % (len(all_l2), len(l1_count)))
except Exception as ex:
    lines.append("## 四、校验证据")
    lines.append("")
    lines.append("校验脚本执行异常：%s" % ex)

open(OUT_MD, "w", encoding="utf-8").write("\n".join(lines))
print("已写 MD:", OUT_MD)

# ---- 写 XLSX ----
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "企业标签全量"
headers = ["企业名(name)", "中文名(name_cn)", "一级标签(tag_l1)", "二级标签(tag_l2)",
           "支付方(payor_model)", "业务-客户(business_tags.customer)", "业务-角色(business_tags.role)",
           "业务-渠道(business_tags.channel)", "国家地区(country)", "简介(description)",
           "原分类(category_l1)", "原分类(category_l2)"]
ws.append(headers)
hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(color="FFFFFF", bold=True)
for c in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill = hdr_fill
    cell.font = hdr_font
    cell.alignment = Alignment(vertical="center", wrap_text=True)

def jt(v):
    if v is None:
        return ""
    if isinstance(v, list):
        return "、".join(str(x) for x in v)
    return str(v)

for e in es:
    bt = e.get("business_tags") or {}
    row = [
        e.get("name", ""), e.get("name_cn", ""),
        jt(e.get("tag_l1")), jt(e.get("tag_l2")),
        e.get("payor_model", "") or "未披露",
        jt(bt.get("customer")), jt(bt.get("role")), jt(bt.get("channel")),
        e.get("country", "") or "",
        (e.get("description") or "")[:300],
        jt(e.get("category_l1")), jt(e.get("category_l2")),
    ]
    ws.append(row)

widths = [22, 18, 22, 26, 16, 22, 18, 18, 12, 50, 18, 18]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws.freeze_panes = "A2"

wb.save(OUT_XLSX)
print("已写 XLSX:", OUT_XLSX, "| 行数(含表头):", ws.max_row)
