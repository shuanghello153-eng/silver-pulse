# -*- coding: utf-8 -*-
import json, os, re, sys
sys.path.insert(0, ".")
from check_single import lcs_len

DD = "drafts_v4"
recs = {}
for fn in os.listdir(DD):
    if fn.startswith("draft_") and fn.endswith(".json"):
        d = json.load(open(os.path.join(DD, fn), encoding="utf-8"))
        recs[d["serial"]] = d["recommend"]

def norm(s):
    return re.sub(r"\s", "", s)

items = [(s, norm(r)) for s, r in recs.items()]
sets = [(s, set(r)) for s, r in items]

bad = 0
pairs = []
for i in range(len(items)):
    s1, r1 = items[i]
    set1 = sets[i][1]
    for j in range(i + 1, len(items)):
        s2, r2 = items[j]
        set2 = sets[j][1]
        if not set1 or not set2:
            continue
        jr = len(set1 & set2) / len(set1 | set2)
        if jr > 0.5:
            # only now do expensive LCS
            if lcs_len(r1, r2) >= 15:
                bad += 1
                pairs.append((s1, s2, round(jr, 2), lcs_len(r1, r2)))
for p in pairs:
    print("  ", p)
print("R10冲突对:", bad, "| 总草稿", len(items))
