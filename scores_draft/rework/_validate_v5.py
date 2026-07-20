# -*- coding: utf-8 -*-
"""独立校验 drafts_v5：不信任工人自测。全量跑 check_single(R1-R10含R6/R7/R8) + 内部R10。
用法: python _validate_v5.py [--scope batches]  （默认全量 drafts_v5）
"""
import json, os, re, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB_PATH = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DRAFTS_DIR = os.path.join(HERE, "drafts_v5")

db = json.load(open(DB_PATH, encoding="utf-8"))
db_idx = {str(e.get("serial","")).lstrip("#"): e for e in db}

files = sorted(glob.glob(os.path.join(DRAFTS_DIR, "draft_*.json")))
by_serial = defaultdict(list)
for fp in files:
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue
    s = str(d.get("serial","")).lstrip("#")
    by_serial[s].append(d)

print(f"drafts_v5 文件数: {len(files)} | 去重 serials: {len(by_serial)}")

# 全量单企业校验（含 R6/R7/R8 + R10跳过先）
full_pass = {}
full_fail = {}
for s, lst in by_serial.items():
    best = max(lst, key=lambda d: C.content_len(d.get("recommend") or ""))
    entry = db_idx.get(s)
    if not entry:
        full_fail[s] = ["库中未找到"]
        continue
    ctx = dict(entry)
    ctx["recommend"] = best.get("recommend")
    for k in ("desc_cn","silver_reason","payor_model"):
        if k in best and best[k]:
            ctx[k] = best[k]
    errs = C.validate(ctx, others=None, skip={"R10"})
    if errs:
        full_fail[s] = errs
    else:
        full_pass[s] = best

print(f"全量(含R6/R7/R8) PASS: {len(full_pass)} | FAIL: {len(full_fail)}")

# recommend-only 口径（R6/R7/R8 不阻塞）
REC_SKIP = {"R10","R6","R7","R8"}
rec_pass = {}
rec_fail = {}
for s, lst in by_serial.items():
    best = max(lst, key=lambda d: C.content_len(d.get("recommend") or ""))
    entry = db_idx.get(s)
    if not entry:
        rec_fail[s] = ["库中未找到"]
        continue
    ctx = dict(entry)
    ctx["recommend"] = best.get("recommend")
    for k in ("desc_cn","silver_reason","payor_model"):
        if k in best and best[k]:
            ctx[k] = best[k]
    errs = C.validate(ctx, others=None, skip=REC_SKIP)
    if errs:
        rec_fail[s] = errs
    else:
        rec_pass[s] = best

print(f"recommend-only PASS: {len(rec_pass)} | FAIL: {len(rec_fail)}")

# 失败原因
rc = Counter()
for s,errs in rec_fail.items():
    for e in errs:
        rc[e.split(":")[0].split("（")[0]] += 1
print("recommend FAIL 原因:", dict(rc))

# 内部 R10（recommend-only 合格者互比）
recs = [(s, rec_pass[s].get("recommend","")) for s in rec_pass if isinstance(rec_pass[s].get("recommend"),str)]
n=len(recs)
def _norm(t): return re.sub(r"\s","",t or "")
def _tri(t):
    t=_norm(t); return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _cs(t): return set(_norm(t))
cs=[_cs(r) for s,r in recs]; tris=[_tri(r) for s,r in recs]
inv={}
for i,tr in enumerate(tris):
    for g in tr: inv.setdefault(g,[]).append(i)
r10=set(); checked=0
for i in range(n):
    seen=set()
    for g in tris[i]:
        for j in inv.get(g,[]):
            if j<=i or j in seen: continue
            seen.add(j)
            sa,sb=cs[i],cs[j]
            if not sa or not sb: continue
            if len(sa&sb)/len(sa|sb)<=0.5: continue
            checked+=1
            si,ri=recs[i]; sj,rj=recs[j]
            if ri==rj: r10.add(si); r10.add(sj)
            elif C.lcs_len(ri,rj)>=15: r10.add(si); r10.add(sj)
print(f"内部R10 比对 {checked} 对 | 雷同 {len(r10)} 家")

final_rec_pass = [s for s in rec_pass if s not in r10]
print(f"最终 recommend 合格(可合并): {len(final_rec_pass)}")

# 保存
out = {
  "final_rec_pass": sorted(final_rec_pass, key=lambda x:int(x)),
  "rec_fail": {k:rec_fail[k] for k in sorted(rec_fail, key=lambda x:int(x))},
  "full_fail_count": len(full_fail),
  "full_fail": {k:full_fail[k] for k in sorted(full_fail, key=lambda x:int(x))},
}
json.dump(out, open(os.path.join(HERE,"_v5_validation.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n已存 _v5_validation.json")
