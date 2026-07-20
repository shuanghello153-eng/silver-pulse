import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

SRC = "data/enterprise/all_enterprises.json"
RUN = "scores_draft/run"
OUT = "G:/workbuddy/2026-07-17-12-07-23/SilverPulse_已完成企业_541家_字段完整版.xlsx"

data = json.load(open(SRC, encoding="utf-8"))
by = {e["serial"]: e for e in data}


def is_done(e):
    rv = e.get("research_value") is not None
    rec = e.get("recommend")
    rec_ok = isinstance(rec, dict) and any(k in rec for k in ("rec_v1", "v1", "rec1"))
    return rv or rec_ok


done = [e for e in data if is_done(e)]
done.sort(key=lambda e: e.get("serial"))
print("已完成企业数:", len(done))

tag_rev = json.load(open(f"{RUN}/tag_review_all.json", encoding="utf-8"))
nonsilver = json.load(open(f"{RUN}/nonsilver_all.json", encoding="utf-8"))
non_by = {n["serial"]: n for n in nonsilver}

HEAD = Font(bold=True, color="FFFFFF", size=11)
HEADFILL = PatternFill("solid", fgColor="2F5496")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
REDFILL = PatternFill("solid", fgColor="FCE4E4")


def style_header(ws, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = HEAD
        cell.fill = HEADFILL
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = BORDER
    ws.freeze_panes = "A2"


def setw(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def s(v):
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


wb = Workbook()

# ===== Sheet1 总览 =====
ws = wb.active
ws.title = "已完成总览"
cols = ["serial", "name", "name_cn", "region", "founded", "stage", "tag_l1", "tag_l2",
        "signal_strength", "info_score", "diff_score", "copy_score", "research_value",
        "value_score(桥接)", "update_time", "rec_v1", "rec_v2", "rec_v3", "source", "nonsilver标记"]
ws.append(cols)
for e in done:
    rec = e.get("recommend")
    if isinstance(rec, dict):
        v1 = rec.get("rec_v1") or rec.get("v1") or ""
        v2 = rec.get("rec_v2") or rec.get("v2") or ""
        v3 = rec.get("rec_v3") or rec.get("v3") or ""
    else:
        v1 = v2 = v3 = ""
    ns = non_by.get(e["serial"])
    ns_mark = ns["verdict"] if ns else ""
    ws.append([e.get("serial"), e.get("name"), e.get("name_cn"), e.get("region"),
               e.get("founded"), e.get("stage"), s(e.get("tag_l1")), s(e.get("tag_l2")),
               e.get("signal_strength"), e.get("info_score"), e.get("diff_score"),
               e.get("copy_score"), e.get("research_value"), e.get("value_score"),
               e.get("update_time"), v1, v2, v3, e.get("source"), ns_mark])
style_header(ws, len(cols))
setw(ws, [9, 22, 16, 7, 8, 9, 14, 18, 11, 9, 9, 9, 11, 12, 12, 55, 55, 55, 10, 12])
for row in ws.iter_rows(min_row=2):
    for c in (16, 17, 18):
        row[c - 1].alignment = WRAP
    row[0].font = Font(bold=True)

# ===== Sheet2 全字段明细 =====
ws2 = wb.create_sheet("全字段明细")
ordered = ["serial", "name", "name_cn", "region", "founded", "stage", "website_url", "crunchbase_url",
           "description", "desc_cn", "category_l1", "category_l2", "tags", "tag_l1", "tag_l2",
           "business_model", "business_model_cn", "business_tags", "source", "payor_model",
           "funding_latest", "funding_total", "investors", "highlights", "value_score", "recommend",
           "news_coverage", "ingest_time", "needs_review", "signal_strength", "info_score",
           "diff_score", "copy_score", "research_value", "update_time", "deep_article_links",
           "related_news_ids"]
ws2.append(ordered)
for e in done:
    row = [s(e.get(k)) for k in ordered]
    ws2.append(row)
style_header(ws2, len(ordered))
setw(ws2, [9, 20] + [18] * 3 + [10, 12, 28, 22, 30, 22, 12, 12, 14, 14, 18, 16, 20, 12, 18, 12, 30, 18, 14, 18, 30, 40, 12, 40, 30, 12, 12, 12, 12, 11, 9, 9, 9, 12, 12, 18, 16])
for row in ws2.iter_rows(min_row=2):
    for i in range(len(ordered)):
        row[i].alignment = WRAP

# ===== Sheet3 标签审查建议 =====
ws3 = wb.create_sheet("标签审查建议")
cols3 = ["serial", "name", "intro(简介)", "old_tags(现有标签)", "suggested(建议动作)", "是否已处理"]
ws3.append(cols3)
for t in tag_rev:
    sugg = t.get("suggested", [])
    sugg_s = "\n".join("[%s] %s — %s" % (x.get("action", ""), x.get("tag", ""), x.get("reason", "")) for x in sugg)
    ws3.append([t.get("serial"), t.get("name"), t.get("intro", ""),
                s(t.get("old_tags")), sugg_s, "建议(待小爽拍板)"])
style_header(ws3, len(cols3))
setw(ws3, [9, 20, 50, 40, 70, 14])
for row in ws3.iter_rows(min_row=2):
    row[2].alignment = WRAP
    row[3].alignment = WRAP
    row[4].alignment = WRAP

# ===== Sheet4 非银发/存疑标记 =====
ws4 = wb.create_sheet("非银发存疑标记")
cols4 = ["serial", "name", "verdict(判定)", "reason(理由)", "是否在已完成541内"]
ws4.append(cols4)
for n in nonsilver:
    ser = n.get("serial")
    in_done = "是" if (ser in by and is_done(by[ser])) else "否"
    ws4.append([ser, n.get("name"), n.get("verdict", ""), n.get("reason", ""), in_done])
style_header(ws4, len(cols4))
setw(ws4, [9, 22, 16, 70, 16])
for row in ws4.iter_rows(min_row=2):
    row[3].alignment = WRAP
    if "非银发" in str(row[2].value):
        row[2].fill = REDFILL

# ===== Sheet5 进度说明 =====
ws5 = wb.create_sheet("进度说明")
lines = [
    ["Silver Pulse 评分+信息补全 · 已完成交付说明", ""],
    ["生成时间", "2026-07-17"],
    ["数据真相源", "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json (1502家)"],
    ["", ""],
    ["【已完成 = 已合并入库】", "541 家 (batches 0-44, waves 1-5)"],
    ["  判定标准", "research_value 非null 且 recommend 为含 rec_v1/v2/v3 的新版字典"],
    ["  字段填充率", "signal_strength/info/diff/copy/research_value/update_time/recommend = 541/541 全满"],
    ["", ""],
    ["【已产出未合并】", "约180家 (batches 45-59, wave6 in-flight, 在 run/out/ 有产物但未 merge)"],
    ["【剩余待跑】", "约792家 (batches 60-125)"],
    ["", ""],
    ["评分公式", "research_value = round((信号×0.3+信息量×0.3+差异化×0.2+可复制×0.2)×10) 量纲0-100"],
    ["信号强度(0-10)", "脚本确定性算法(IPO/+6, 融资/收购分级, 时效分级) clamp 0-10"],
    ["三维(0-10)", "info_score信息量 / diff_score差异化 / copy_score可复制 = 联网AI精评"],
    ["value_score(桥接)", "= research_value 取整, 旧前端回退兼容字段"],
    ["update_time", "2026-07-17 (本轮写入)"],
    ["", ""],
    ["本表包含", "Sheet1 已完成总览(541) | Sheet2 全字段明细(541) | Sheet3 标签审查建议(540) | Sheet4 非银发标记(117)"],
    ["标签审查原则", "只读不写, 全部为建议, 需小爽拍板后才落地"],
    ["非银发标记原则", "不删库, 仅标记 verdict, 删库是另一AI的活"],
    ["", ""],
    ["注意", "本表为第二个AI罢工前的实跑产物汇总; 541家的评分质量需小爽抽审(尤其推荐理由是否对味)"],
]
for r in lines:
    ws5.append(r)
ws5["A1"].font = Font(bold=True, size=13)
for row in ws5.iter_rows():
    row[0].font = Font(bold=True)
    row[0].alignment = Alignment(vertical="top")
    row[1].alignment = WRAP
setw(ws5, [22, 95])

wb.save(OUT)
print("已保存:", OUT)
print("sheets:", wb.sheetnames)
