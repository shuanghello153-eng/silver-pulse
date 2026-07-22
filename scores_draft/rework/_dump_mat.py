# -*- coding: utf-8 -*-
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as CS
BATCH = os.path.join(HERE, "score_recovery", "batch_05.json")
DB = CS.DB
def ctx(serial):
    d = json.load(open(DB, encoding="utf-8"))
    for e in d:
        if str(e.get("serial","")).lstrip("#") == str(serial).lstrip("#"):
            return e
    return {}
batch = json.load(open(BATCH, encoding="utf-8"))
out = {}
for x in batch:
    ser = x["serial"]
    c = ctx(ser)
    out[ser] = {
        "serial": ser,
        "tag_l1": x.get("tag_l1"), "tag_l2": x.get("tag_l2"),
        "is_listed": x.get("is_listed"), "funding_stage": x.get("funding_stage"),
        "signal_strength": x.get("signal_strength"),
        "name": c.get("name"), "name_cn": c.get("name_cn"),
        "stage": c.get("stage"),
        "desc_cn": (c.get("desc_cn") or "")[:200],
        "highlights": c.get("highlights") or [],
        "funding_latest": (c.get("funding_latest") or {}).get("display") if isinstance(c.get("funding_latest"),dict) else None,
        "funding_total": (c.get("funding_total") or {}).get("display") if isinstance(c.get("funding_total"),dict) else None,
        "current_recommend": x.get("current_recommend"),
    }
json.dump(out, open(os.path.join(HERE,"drafts_v5","_material.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("dumped", len(out))
