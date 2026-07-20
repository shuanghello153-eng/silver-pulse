# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate, content_len

DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
OUT = os.path.join(HERE, "drafts_v5")

db = json.load(open(DB, encoding="utf-8"))
db_by_serial = {}
for e in db:
    db_by_serial[str(e.get("serial", "")).lstrip("#")] = e

# 本次任务范围：batch_004/005/006 的 36 家
TARGET = {
"#0545","#0546","#0547","#0548","#0550","#0551","#0552","#0553","#0554","#0556",
"#0562","#0563","#0567","#0568","#0569","#0570","#0571","#0572","#0573","#0574",
"#0575","#0576","#0577","#0578","#0579","#0580","#0581","#0582","#0583","#0584",
"#0586","#0587","#0588","#0589","#0590","#0591",
}

# load only target drafts
drafts = []
for fn in os.listdir(OUT):
    if fn.startswith("draft_") and fn.endswith(".json"):
        d = json.load(open(os.path.join(OUT, fn), encoding="utf-8"))
        if str(d.get("serial", "")) in TARGET:
            drafts.append(d)

others = [d.get("recommend", "") for d in drafts if isinstance(d.get("recommend"), str)]

total = 0
passed = 0
fails = {}
for d in drafts:
    serial = d.get("serial", "")
    s = str(serial).lstrip("#")
    ctx = db_by_serial.get(s, {})
    tmp = dict(ctx)
    for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
        if k in d and d[k] is not None:
            tmp[k] = d[k]
    tmp["serial"] = serial
    iss = validate(tmp, others=others)
    total += 1
    if iss:
        fails[serial] = iss
    else:
        passed += 1

print(f"MY TOTAL={total} PASS={passed} FAIL={len(fails)}")
for s, iss in fails.items():
    print(f"  {s}: {iss}")
