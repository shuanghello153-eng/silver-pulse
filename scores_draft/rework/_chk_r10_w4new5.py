# -*- coding: utf-8 -*-
import json, glob, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C

SERIALS = set()
for b in [52,53,54,55,56,57,58,59]:
    data = json.load(open(f"batches_full/batch_src_0{b}.json", encoding="utf-8"))
    for e in data:
        SERIALS.add(e["serial"])

recs = {}
for f in glob.glob("drafts_v4/draft_*.json"):
    d = json.load(open(f, encoding="utf-8"))
    if d.get("serial") in SERIALS and d.get("recommend"):
        recs[d["serial"]] = d["recommend"]

keys = list(recs.keys())
print("my recs:", len(keys), flush=True)
# 预计算字符集合与长度
sets = {k: set(v) for k, v in recs.items()}
lens = {k: len(sets[k]) for k in keys}
bad = []
n = len(keys)
checked = 0
for i in range(n):
    for j in range(i+1, n):
        a, b = keys[i], keys[j]
        la, lb = lens[a], lens[b]
        if la == 0 or lb == 0:
            continue
        # 剪枝：jaccard 上限 = min/ max 集合大小
        if min(la, lb) / max(la, lb) <= 0.5:
            continue
        checked += 1
        ov = C.lcs_len(recs[a], recs[b])
        if ov >= 15:
            sa, sb = sets[a], sets[b]
            ratio = len(sa & sb) / len(sa | sb)
            if ratio > 0.5:
                bad.append((a, b, round(ratio, 2), ov))
print("pairs actually lcs-checked:", checked, flush=True)
print("R10 pairs over 0.5 among my 160:", len(bad), flush=True)
for x in bad[:40]:
    print("  ", x, flush=True)
