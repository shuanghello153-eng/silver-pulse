# -*- coding: utf-8 -*-
"""w4-fix: 打印指定 serial 的企业卡关键字段（供撰写 recommend 参考）。
用法：python _w4_card.py 0470 0949 0954 ...
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
db = json.load(open(DB, encoding="utf-8"))
by = {str(x.get("serial", "")).lstrip("#"): x for x in db}

for s in sys.argv[1:]:
    e = by.get(s.lstrip("#"))
    if not e:
        print("=== %s NOT FOUND ===" % s)
        continue
    print("=" * 70)
    print("serial=%s  name=%s  cn=%s  region=%s" % (e.get("serial"), e.get("name"), e.get("name_cn"), e.get("region")))
    print("tags:", e.get("tag_l1"), e.get("tag_l2"))
    print("signal/info/diff/copy/rv:", e.get("signal_strength"), e.get("info_score"), e.get("diff_score"), e.get("copy_score"), e.get("research_value"))
    print("--desc_cn:", e.get("desc_cn"))
    print("--silver_reason:", e.get("silver_reason"))
    print("--description:", e.get("description"))
    hl = e.get("highlights") or []
    for i, h in enumerate(hl):
        print("  highlights[%d]:" % i, h)
    fl = e.get("funding_latest") or {}
    print("--funding_latest.display:", fl.get("display") if isinstance(fl, dict) else fl)
    ft = e.get("funding_total") or {}
    print("--funding_total.display:", ft.get("display") if isinstance(ft, dict) else ft)
    print("--payor_model:", e.get("payor_model"))
    # 当前 draft 里的 recommend
    dp = os.path.join(HERE, "drafts_v4", "draft_%s.json" % e.get("serial"))
    if os.path.exists(dp):
        d = json.load(open(dp, encoding="utf-8"))
        print("**CURRENT DRAFT recommend:**", d.get("recommend"))
    print()
