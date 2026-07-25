# -*- coding: utf-8 -*-
"""合并 draft_out/ 全部分片，按分片名+原顺序拼接，分配 serial(#1851起)，
   清理临时字段(_srcfile/_status_raw/_note_raw)，输出 候选_133.json。"""
import json, os, glob, re

ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
HERE = os.path.join(ROOT, "_qa_tmp", "ingest_187")

# 确认库内 max serial
db = json.load(open(os.path.join(ROOT, "data/enterprise/all_enterprises.json"), encoding="utf-8"))
mx = 0
for e in db:
    m = re.search(r"(\d+)", str(e.get("serial", "")))
    if m: mx = max(mx, int(m.group(1)))
print(f"库内 max serial = #{mx:04d}，新记录从 #{mx+1:04d} 起")

records = []
for fp in sorted(glob.glob(os.path.join(HERE, "draft_out", "*.json"))):
    for r in json.load(open(fp, encoding="utf-8")):
        records.append(r)
print(f"合并 {len(records)} 家")

TMP_FIELDS = ("_srcfile", "_status_raw", "_note_raw")
nxt = mx + 1
for r in records:
    r["serial"] = f"#{nxt:04d}"
    nxt += 1
    for k in TMP_FIELDS:
        r.pop(k, None)

out = os.path.join(HERE, "候选_133.json")
json.dump(records, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"已写 {out}（serial #{mx+1:04d} ~ #{nxt-1:04d}）")
