# -*- coding: utf-8 -*-
import json, sys
DB = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json"
serials = sys.argv[1:]
d = json.load(open(DB, encoding="utf-8"))
by = {str(e.get("serial", "")): e for e in d}
for s in serials:
    e = by.get(s)
    if not e:
        print("=== %s NOT FOUND ===" % s)
        continue
    print("=== %s | %s (%s) | %s | %s" % (e.get("serial"), e.get("name"), e.get("name_cn"), e.get("region"), e.get("business_model_cn")))
    print("tags: %s / %s" % (e.get("tag_l1"), e.get("tag_l2")))
    print("funding_latest: %s" % (e.get("funding_latest") or {}).get("display"))
    print("funding_total: %s" % (e.get("funding_total") or {}).get("display"))
    evs = e.get("events") or []
    def _ev(x):
        if isinstance(x, dict):
            return "%s:%s" % (x.get("date"), x.get("text"))
        return str(x)
    print("events: " + " ; ".join(_ev(x) for x in evs[:6]))
    print("desc_cn: %s" % e.get("desc_cn"))
    print("highlights: " + " | ".join(e.get("highlights") or []))
    print("silver_reason: %s" % e.get("silver_reason"))
    print("payor: %s" % e.get("payor_model"))
    print("")
