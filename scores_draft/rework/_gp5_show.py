# -*- coding: utf-8 -*-
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))

def main():
    arg = sys.argv[1]
    # arg is either a batch file path or a list of serials
    serials = []
    if arg.endswith(".json"):
        serials = json.load(open(arg, encoding="utf-8"))
    else:
        serials = arg.split(",")
    db = json.load(open(DB, encoding="utf-8"))
    by = {}
    for e in db:
        by[str(e.get("serial",""))] = e
    out = {}
    for s in serials:
        s = s.strip()
        e = by.get(s)
        if not e:
            out[s] = {"__missing__": True}
            continue
        rec = {
            "serial": e.get("serial"),
            "name": e.get("name"),
            "name_cn": e.get("name_cn"),
            "business": e.get("business"),
            "desc_cn": e.get("desc_cn"),
            "tag_l1": e.get("tag_l1"),
            "tag_l2": e.get("tag_l2"),
            "tag_l3": e.get("tag_l3"),
            "funding_latest": e.get("funding_latest"),
            "funding_total": e.get("funding_total"),
            "domestic": e.get("domestic_competitors") or e.get("国内竞品") or e.get("competitors_cn"),
            "silver_reason": e.get("silver_reason"),
            "payor_model": e.get("payor_model"),
            "highlights": e.get("highlights"),
        }
        out[s] = rec
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
