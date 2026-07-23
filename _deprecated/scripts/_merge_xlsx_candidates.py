# -*- coding: utf-8 -*-
"""合并两个采集智能体的候选 JSON + 第二张表(达旦无极)的真实行，
做跨part去重 + 二次比对企业库，产出最终 _xlsx_candidates.json 供 _ingest_xlsx.py 入库。
不修改 all_enterprises.json（入库由 _ingest_xlsx.py 完成）。
"""
import json, re, copy

REPO = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
EP = f"{REPO}/data/enterprise/all_enterprises.json"
XLSX = "G:/360MoveData/Users/shuan/Desktop/飞书-选题库-结构化整理/艾年·养老行业供需对接.xlsx"
OUT = f"{REPO}/_xlsx_candidates.json"

SUFFIX = ["公司","有限公司","股份有限公司","集团股份有限公司","集团","科技","技术","有限",
          "有限合伙","企业","合伙企业","网络","信息","智能","股份","控股","有限公司)"]

def norm(s):
    return (s or "").strip().lower()

def core(s):
    s = norm(s)
    for suf in SUFFIX:
        if s.endswith(suf) and len(s) > len(suf):
            s = s[:-len(suf)]
    return s

# ---- 读取现有企业库名称 ----
ents = json.load(open(EP, encoding="utf-8"))
lib_norm = {norm(e.get("name","")) for e in ents if e.get("name")}
lib_core = {core(e.get("name","")) for e in ents if e.get("name")}

# ---- 读取两个采集part ----
parts = []
for p in ["_xlsx_candidates_partA.json","_xlsx_candidates_partB.json"]:
    try:
        parts.extend(json.load(open(f"{REPO}/{p}", encoding="utf-8")))
    except FileNotFoundError:
        print("WARN: missing", p)

# ---- 处理第二张表真实行(跳过测试) ----
import openpyxl
wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
for ws in wb.worksheets:
    if ws.title.startswith("新提交者"):
        continue  # 主表已由采集智能体处理
    rows = list(ws.iter_rows(values_only=True))
    hdr = None; hrow = None
    for i, r in enumerate(rows):
        if any(c is not None for c in r):
            hdr = r; hrow = i; break
    hmap = {str(h).strip(): idx for idx, h in enumerate(hdr)}
    def get(row, key):
        for k, v in hmap.items():
            if key in k:
                return row[v] if v < len(row) else None
        return None
    for row in rows[hrow+1:]:
        name = norm(get(row, "公司名称") or get(row, "姓名"))
        if not name or name == "测试":
            continue
        biz = get(row, "业务介绍") or get(row, "业务详情") or ""
        supply = get(row, "提供") or ""
        demand = get(row, "需要") or ""
        desc = (biz or "").strip()
        if supply or demand:
            desc += f"\n【提供资源】{supply}\n【需求资源】{demand}"
        parts.append({
            "name": get(row, "公司名称") or get(row, "姓名"),
            "region": "国内",
            "category_l1": "养老服务",       # 达旦无极=认知症情感陪伴数字人 -> 养老服务/认知症(待校验)
            "category_l2": "认知症",
            "description": desc,
            "website_url": "",
            "founded": "未披露",
            "stage": "未披露",
            "investors": "未披露",
            "funding_latest": {"date":"未披露","amount":"未披露","round":"未披露","display":"未披露"},
            "funding_total": {"amount":"未披露","display":"未披露"},
            "tags": [],
            "source": "飞书供需对接表",
            "business_model": "认知症数字人SaaS/SDK授权",
            "business_model_cn": "认知症情感陪伴数字人系统，SaaS与SDK接入"
        })

# ---- 合并去重 ----
seen_norm = set(); seen_core = set()
final = []
skipped_dup = []
for c in parts:
    nm = norm(c.get("name",""))
    if not nm:
        continue
    cr = core(c.get("name",""))
    if nm in lib_norm or cr in lib_core:
        skipped_dup.append((c.get("name",""), "已在企业库"))
        continue
    if nm in seen_norm or cr in seen_core:
        skipped_dup.append((c.get("name",""), "xlsx内部重复"))
        continue
    seen_norm.add(nm); seen_core.add(cr)
    final.append(c)

json.dump(final, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"合并完成：采集part合计 {len(parts)} 条 -> 去重后候选 {len(final)} 条；跳过 {len(skipped_dup)} 条")
for s in skipped_dup:
    print("  跳过:", s)
