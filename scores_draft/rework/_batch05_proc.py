# -*- coding: utf-8 -*-
"""Batch05 processor: keep-vs-rewrite decision + scoring helper (analysis only)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as CS

BATCH = os.path.join(HERE, "score_recovery", "batch_05.json")
DB = CS.DB

def ctx(serial):
    if not os.path.exists(DB):
        return {}
    d = json.load(open(DB, encoding="utf-8"))
    for e in d:
        if str(e.get("serial", "")).lstrip("#") == str(serial).lstrip("#"):
            return e
    return {}

batch = json.load(open(BATCH, encoding="utf-8"))
print(f"total={len(batch)}")
pass_n = 0
fail_n = 0
for x in batch:
    ser = x["serial"]
    rec = x.get("current_recommend") or ""
    c = ctx(ser)
    tmp = dict(c)
    for k in ("recommend", "desc_cn", "highlights", "stage", "funding_latest", "funding_total"):
        if k in x and x[k] is not None:
            tmp[k] = x[k]
    tmp["recommend"] = rec
    iss = CS.validate(tmp)
    cl = CS.content_len(rec)
    if iss:
        fail_n += 1
        print(f"FAIL {ser} len={cl} :: {iss}")
    else:
        pass_n += 1
print(f"\nGATE: pass={pass_n} fail={fail_n}")
