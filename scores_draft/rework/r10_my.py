# -*- coding: utf-8 -*-
import json, os, re, sys
sys.path.insert(0, ".")
from check_single import lcs_len

DD = "drafts_v4"
# my serials across batches 028-035 (filled in as I go)
MY = set([
    "#0059","#0065","#0092","#0121","#0126","#0127","#0136","#0144","#0152","#0182",
    "#0200","#0277","#0296","#0302","#0336","#0402","#0429","#0487","#0494",
    "#0504","#0507","#0600","#0841","#0843","#0902","#1002","#1010","#1014","#1017",
    "#1022","#1024","#1029","#1030","#1036","#1217","#1234","#1235","#1237","#1238",
])

allrecs = {}
for fn in os.listdir(DD):
    if fn.startswith("draft_") and fn.endswith(".json"):
        d = json.load(open(os.path.join(DD, fn), encoding="utf-8"))
        allrecs[d["serial"]] = d["recommend"]

def norm(s):
    return re.sub(r"\s", "", s)

items = {s: norm(r) for s, r in allrecs.items()}

# only check MY serials against everyone (others included)
mine = [s for s in items if s in MY]
pairs = []
conflicts = 0
for s1 in mine:
    r1 = items[s1]
    set1 = set(r1)
    if not set1:
        continue
    for s2, r2 in items.items():
        if s2 == s1:
            continue
        set2 = set(r2)
        if not set2:
            continue
        jr = len(set1 & set2) / len(set1 | set2)
        if jr > 0.5:
            L = lcs_len(r1, r2)
            if L >= 15:
                conflicts += 1
                pairs.append((s1, s2, round(jr, 2), L))
for p in pairs:
    print("  ", p)
print("MY serials checked:", len(mine), "| R10 conflicts involving mine:", conflicts)
