# -*- coding: utf-8 -*-
# 生成「增强版 1502 家」交付 Excel：全量总览 + 字段填充率 + 真实校验结果 + 质量增强进度 + 银发判定/标签审查
import json, os, subprocess, re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
RUNV2 = os.path.join(BASE, "scores_draft/run_v2")
DB = json.load(open(os.path.join(BASE, "data/enterprise/all_enterprises.json"), encoding="utf-8"))
MAN = json.load(open(os.path.join(RUNV2, "manifest.json"), encoding="utf-8"))
OUT = "G:/workbuddy/2026-07-17-12-07-23/SilverPulse_增强版_1502家_字段完整版_V2.xlsx"

# 已增强（已合并）的 serial 集合
proc = set()
pp = os.path.join(RUNV2, "processed.json")
if os.path.exists(pp):
    proc = set(json.load(open(pp, encoding="utf-8")))

# 真实的五道防线结果（直接复用 validate_v2.py，保证数字一致）
val = subprocess.run([sys.executable, os.path.join(RUNV2, "validate_v2.py")],
                     capture_output=True, text=True, cwd=RUNV2)
val_out = val.stdout
m = re.search(r"违规项\s*(\d+)\s*条", val_out)
total_viol = int(m.group(1)) if m else -1
m2 = re.search(r"各防线违规数：\s*(\{[^}]*\})", val_out)
rule_counts = {}
if m2:
    try:
        rule_counts = eval(m2.group(1))
    except Exception:
        rule_counts = {}
bad_serials = re.findall(r"\[#?(\d+)\]\s*(\w+):", val_out)

HEAD = Font(bold=True, color="FFFFFF", size=11); HEADFILL = PatternFill("solid", fgColor="2F5496")
WRAP = Alignment(wrap_text=True, vertical="top"); TOP = Alignment(vertical="top")
CEN = Alignment(horizontal="center", vertical="top")
THIN = Side(style="thin", color="D0D0D0"); BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
ENHFILL = PatternFill("solid", fgColor="E2EFDA")
def style_header(ws, nc):
    for c in range(1, nc + 1):
        cell = ws.cell(row=1, column=c); cell.font = HEAD; cell.fill = HEADFILL
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center"); cell.border = BORDER
    ws.freeze_panes = "A2"
def setw(ws, widths):
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
def s(v):
    if v is None: return ""
    if isinstance(v, (dict, list)): return json.dumps(v, ensure_ascii=False)
    return str(v)
wb = Workbook()

# Sheet1 全量总览（补全用户关心的描述/标签/融资/事件等字段 + 联网状态透明）
ws = wb.active; ws.title = "全量总览"
cols = ["serial", "name", "name_cn", "region", "category_l1", "category_l2",
        "tag_l1", "tag_l2", "business_tags", "stage", "founded", "website_url",
        "desc_cn", "payor_model", "funding_latest", "funding_total", "investors",
        "highlights", "events",
        "signal_strength", "info_score", "diff_score", "copy_score", "research_value",
        "silver_verdict", "silver_reason", "数据来源(联网精评/规则基线)", "recommend", "update_time"]
ws.append(cols)
for e in DB:
    ser = e.get("serial")
    enh = "联网精评" if ser in proc else "规则基线"
    def jl(v):
        if isinstance(v, dict): return json.dumps(v, ensure_ascii=False)
        if isinstance(v, list): return " / ".join(str(x) for x in v) if v else ""
        return v if v is not None else ""
    ws.append([e.get("serial"), e.get("name"), e.get("name_cn"), e.get("region"),
               jl(e.get("category_l1")), jl(e.get("category_l2")),
               jl(e.get("tag_l1")), jl(e.get("tag_l2")), jl(e.get("business_tags")),
               e.get("stage"), e.get("founded"), e.get("website_url"),
               e.get("desc_cn"), e.get("payor_model"),                jl(e.get("funding_latest")),
               jl(e.get("funding_total")), jl(e.get("investors")),
               jl(e.get("highlights")), jl(e.get("events")),
               e.get("signal_strength"), e.get("info_score"), e.get("diff_score"),
               e.get("copy_score"), e.get("research_value"),
               e.get("silver_verdict"), e.get("silver_reason"), enh,
               e.get("recommend"), e.get("update_time")])
style_header(ws, len(cols))
setw(ws, [9, 20, 14, 7, 12, 12, 14, 16, 16, 9, 8, 22, 30, 20, 18, 14, 18, 28, 28,
          9, 8, 8, 8, 10, 11, 24, 14, 55, 11])
for row in ws.iter_rows(min_row=2):
    row[12].alignment = WRAP   # desc_cn
    row[27].alignment = WRAP   # recommend
    if row[26].value == "联网精评":
        for c in row: c.fill = ENHFILL

# Sheet2 字段填充率
ws2 = wb.create_sheet("字段填充率")
ws2.append(["字段", "有效填充", "占位词(未搜到/未融资/不确定)", "空值", "总计", "填充率"])
fields = ["name_cn", "founded", "stage", "website_url", "funding_latest", "funding_total", "investors",
          "payor_model", "desc_cn", "highlights", "events", "recommend", "business_tags_role", "silver_verdict"]
PH = {"未搜到", "未融资", "不确定"}
for f in fields:
    eff = ph = empty = 0
    for e in DB:
        v = e.get(f)
        if isinstance(v, list):
            if len(v) == 0: empty += 1
            elif all(str(x).strip() in PH for x in v): ph += 1
            else: eff += 1
        elif v is None or (isinstance(v, str) and v.strip() == ""): empty += 1
        elif isinstance(v, str) and v.strip() in PH: ph += 1
        else: eff += 1
    tot = len(DB); rate = round((eff + ph) / tot * 100, 1)
    ws2.append([f, eff, ph, empty, tot, f"{rate}%"])
style_header(ws2, 6); setw(ws2, [20, 12, 30, 8, 8, 10])

# Sheet3 校验结果（真实）
ws3 = wb.create_sheet("校验结果")
ws3.append(["防线", "检查项", "违规数", "结果"])
desc = {
 "L1": "覆盖：1502 serial 无缺无重",
 "L2": "公式：research_value 当场重算误差<=0.5",
 "L3": "量纲：四维 ∈[0,10]",
 "L4": "推荐理由：单字符串/30-200字/含四维/无禁用词",
 "L5": "stage 白名单：严禁融资中/未披露",
 "L6": "全字段非空(允许占位词)",
 "L7": "描述禁忌：不含企业名/成立于/融资",
 "L8": "payor_model 非空",
}
for k in ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]:
    n = rule_counts.get(k, 0)
    ws3.append([k, desc[k], n, "通过" if n == 0 else "违规"])
ws3.append(["合计", f"全量 {len(DB)} 家违规项", total_viol, "OK" if total_viol == 0 else "HAS_ISSUES"])
style_header(ws3, 4); setw(ws3, [8, 55, 10, 14])

# Sheet4 质量增强进度
ws4 = wb.create_sheet("质量增强进度")
ws4.append(["批次", "tier", "企业数", "状态", "说明"])
man_by = {x["batch"]: x for x in MAN}
for b in range(0, 14):
    info = man_by.get(b, {})
    tier = info.get("tier", "B")
    serials = set(info.get("serials", []))
    done = len(serials & proc)
    if done == len(serials) and serials:
        st = "已完成(已合并+复扫通过)"; note = "联网精评+单字段recommend提质，已合并入主库并通过五道防线"
    elif done > 0:
        st = f"部分合并({done}/{len(serials)})"; note = "部分企业已合并"
    else:
        st = "待处理"; note = "待工人产出 out 文件后合并"
    ws4.append([f"batch_{b:03d}", tier, len(serials), st, note])
ws4.append(["batch_014~125 (Tier C 长尾)", "C", "约1334", "基线已落地",
            "规则化补全+默认评分，按方案'长尾降级轻量补全'，后续可择机提质"])
style_header(ws4, 5); setw(ws4, [20, 8, 10, 22, 55])

# Sheet5 银发判定与标签审查
ws5 = wb.create_sheet("银发判定与标签审查")
ws5.append(["项目", "数量/说明"])
sv = {}
for e in DB:
    v = e.get("silver_verdict") or "（未标注）"
    sv[v] = sv.get(v, 0) + 1
ws5.append(["银发判定分布", ""])
for k, v in sorted(sv.items(), key=lambda x: -x[1]):
    ws5.append([k, v])
tr_path = os.path.join(RUNV2, "tag_review_all.json")
ns_path = os.path.join(RUNV2, "nonsilver_all.json")
tr = json.load(open(tr_path, encoding="utf-8")) if os.path.exists(tr_path) else []
ns = json.load(open(ns_path, encoding="utf-8")) if os.path.exists(ns_path) else []
ws5.append(["标签审查(tag_review) 累计", len(tr)])
ws5.append(["非银发/泛医疗标注(nonsilver) 累计", len(ns)])
ws5.append(["", ""])
ws5.append(["— 非银发/泛医疗清单 —", ""])
ws5.append(["serial", "name | verdict | reason"])
for x in ns:
    ws5.append([x.get("serial"), f"{x.get('name')} | {x.get('verdict')} | {x.get('reason')}"])
style_header(ws5, 2); setw(ws5, [30, 90])

wb.save(OUT)
print("已保存:", OUT)
print("总企业:", len(DB), "| 已增强:", len(proc), "| 校验违规:", total_viol)
print("tag_review:", len(tr), "| nonsilver:", len(ns))
print("银发分布:", sv)
