# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, ".")
from check_single import validate
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
DBDATA = json.load(open(DB, encoding="utf-8"))
BY = {str(e.get("serial", "")).lstrip("#"): e for e in DBDATA}
OUT = os.path.join(HERE, "drafts_v5")
SKIP = {"R6", "R7", "R8"}

files = [f for f in os.listdir(OUT) if f.startswith("draft_") and f.endswith(".json")]
fail = []
for f in files:
    d = json.load(open(os.path.join(OUT, f), encoding="utf-8"))
    serial = str(d.get("serial", "")).lstrip("#")
    e = dict(BY.get(serial, {}))
    for k in ("recommend",):
        e[k] = d[k]
    iss = validate(e, skip=SKIP)
    if iss:
        fail.append((serial, iss))
print("FILES:", len(files), "RECOMMEND-LEVEL FAIL:", len(fail))
for s, iss in fail:
    print("  ", s, iss)
# 跨企业 R10 复检
recs = [json.load(open(os.path.join(OUT, f), encoding="utf-8")) for f in files]
r10 = []
for r in recs:
    e = dict(BY.get(str(r["serial"]).lstrip("#"), {}))
    e["recommend"] = r["recommend"]
    o = [x["recommend"] for x in recs if x is not r]
    iss = validate(e, others=o, skip=SKIP)
    if any(i.startswith("R10") for i in iss):
        r10.append(r["serial"])
print("R10跨企业冲突:", len(r10), r10)
