# -*- coding: utf-8 -*-
import json, glob, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C

SERIALS = set()
for b in [52,53,54,55,56,57,58,59]:
    for e in json.load(open(f"batches_full/batch_src_0{b}.json", encoding="utf-8")):
        SERIALS.add(e["serial"])
recs = {}
for f in glob.glob("drafts_v4/draft_*.json"):
    d = json.load(open(f, encoding="utf-8"))
    if d.get("serial") in SERIALS and d.get("recommend"):
        recs[d["serial"]] = d["recommend"]
ks = list(recs)
sets = {k: set(v) for k, v in recs.items()}
lens = {k: len(sets[k]) for k in ks}
# 剪枝：jaccard 上限 = min/max 集合大小
cand = 0
for i in range(len(ks)):
    for j in range(i+1, len(ks)):
        la, lb = lens[ks[i]], lens[ks[j]]
        if la == 0 or lb == 0:
            continue
        if min(la, lb) / max(la, lb) > 0.5:
            cand += 1
print("pairs where jaccard COULD exceed 0.5:", cand, flush=True)
print("total pairs:", len(ks)*(len(ks)-1)//2, flush=True)
