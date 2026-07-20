# -*- coding: utf-8 -*-
"""Compact field extractor for w4-1. Prints only fields needed to write recommend."""
import json, sys

def cl(s):
    import re
    return len(re.sub(r"\s", "", s or ""))

batch = sys.argv[1]
d = json.load(open(batch, encoding="utf-8"))
for i, e in enumerate(d):
    print("="*70)
    print(f"[{i}] serial={e.get('serial')} name={e.get('name')} cn={e.get('name_cn')}")
    print("tags:", e.get("tag_l1"), e.get("tag_l2"))
    print("region:", e.get("region"))
    print("--desc_cn(%d):"%cl(e.get('desc_cn')), e.get("desc_cn"))
    print("--description:", e.get("description"))
    print("--silver_reason(%d):"%cl(e.get('silver_reason')), e.get("silver_reason"))
    fl = e.get("funding_latest") or {}
    ft = e.get("funding_total") or {}
    fld = fl.get("display") if isinstance(fl, dict) else str(fl)
    ftd = ft.get("display") if isinstance(ft, dict) else str(ft)
    print("--funding_latest.display:", fld)
    print("--funding_total.display:", ftd)
    print("--highlights:", e.get("highlights"))
    print("--payor_model:", e.get("payor_model"))
