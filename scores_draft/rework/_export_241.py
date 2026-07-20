# -*- coding: utf-8 -*-
"""导出 241 家'无#命名、被合并脚本漏掉'的草稿企业全字段到 Excel，供人工校验。"""
import json, glob, os, re
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data", "enterprise", "all_enterprises.json")
DRAFTS = os.path.join(HERE, "drafts_v4")

DB = json.load(open(DB_PATH, encoding="utf-8"))
DBI = {e.get("serial"): e for e in DB}

def norm(s):
    return re.sub(r"\D", "", str(s or ""))
DBI_NUM = {norm(e.get("serial")): e for e in DB}

# 读所有草稿，按 带# / 不带# 分类
all_files = sorted(glob.glob(os.path.join(DRAFTS, "*.json")))
hash_files = [f for f in all_files if "#" in os.path.basename(f)]
nohash_files = [f for f in all_files if "#" not in os.path.basename(f)]

def load(f):
    try:
        return json.load(open(f, encoding="utf-8"))
    except Exception:
        return None

# 带#草稿覆盖的serial（数字归一）
hash_serials = set()
for f in hash_files:
    j = load(f)
    if not j: continue
    s = j.get("serial") or j.get("企业序号")
    if s: hash_serials.add(norm(s))

# 241 无#草稿
rows = []           # 每行 = 一家无#草稿企业
only_nohash = 0     # 仅无#版本存在（会永久丢失）
also_hash = 0       # 也有#版本（重复）
for f in nohash_files:
    j = load(f)
    if not j: continue
    ser = j.get("serial") or j.get("企业序号")
    ns = norm(ser)
    dbrec = DBI.get(ser) or DBI_NUM.get(ns) or {}
    is_unique = ns not in hash_serials
    if is_unique: only_nohash += 1
    else: also_hash += 1
    rows.append({
        "file": os.path.basename(f),
        "serial": ser,
        "unique": "是（只有这一份，漏掉即永久丢失）" if is_unique else "否（另有#版本）",
        "draft": j,
        "db": dbrec,
    })

# 汇总所有出现过的字段（主库 + 草稿）
db_fields = []
for e in DB:
    for k in e.keys():
        if k not in db_fields: db_fields.append(k)

# Excel
wb = Workbook()
ws = wb.active
ws.title = "241家被漏草稿"

# 表头：文件名 / serial / 是否唯一 / 草稿推荐理由 / 主库现有推荐理由 / 然后所有主库字段
head = ["草稿文件名", "企业序号", "是否唯一(漏掉后果)", "【草稿】推荐理由(写好但没合并)", "【主库现状】推荐理由"]
head += [f"主库·{k}" for k in db_fields]
ws.append(head)

hdr_fill = PatternFill("solid", fgColor="2F5597")
hdr_font = Font(color="FFFFFF", bold=True, size=10)
for c in range(1, len(head)+1):
    cell = ws.cell(row=1, column=c)
    cell.fill = hdr_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def cellval(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return v

# 排序：唯一的排前面
rows.sort(key=lambda r: (0 if "是" in r["unique"] else 1, norm(r["serial"])))
for r in rows:
    draft_rec = r["draft"].get("recommend") or r["draft"].get("推荐理由") or ""
    db_rec = r["db"].get("recommend", "")
    line = [r["file"], r["serial"], r["unique"], cellval(draft_rec), cellval(db_rec)]
    for k in db_fields:
        line.append(cellval(r["db"].get(k, "")))
    ws.append(line)

# 列宽
widths = {1: 18, 2: 10, 3: 22, 4: 55, 5: 40}
for i in range(1, len(head)+1):
    ws.column_dimensions[get_column_letter(i)].width = widths.get(i, 22)
ws.freeze_panes = "C2"
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.alignment = Alignment(vertical="top", wrap_text=True)

out = os.path.join(HERE, "241家被漏草稿_全字段核验.xlsx")
wb.save(out)
print("SAVED:", out)
print("241无#草稿总数:", len(rows))
print("  其中唯一(漏掉即永久丢失):", only_nohash)
print("  其中另有#版本(重复):", also_hash)
print("字段列数(主库):", len(db_fields))
