# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate, _ctx_from_db

BATCH = os.path.join(HERE, "batches_score", "batch_25.json")
recs = json.load(open(BATCH, encoding="utf-8"))
for r in recs:
    s = r["serial"]
    if not r.get("_is_v5_already"):
        continue
    ctx = _ctx_from_db(s)
    tmp = dict(ctx)
    tmp["recommend"] = r["current_recommend"]
    tmp["name"] = r.get("name")
    tmp["name_cn"] = r.get("name_cn")
    iss = validate(tmp)
    print(f"{s} ({r.get('name_cn')}): {'PASS' if not iss else iss}")
