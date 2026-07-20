# -*- coding: utf-8 -*-
"""Dump enterprises of a batch for manual recommend authoring."""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
B = sys.argv[1] if len(sys.argv) > 1 else "batch_src_022.json"
data = json.load(open(os.path.join(HERE, "batches_full", B), encoding="utf-8"))
for e in data:
    s = e.get("serial", "?")
    nm = e.get("name", "")
    rv = e.get("research_value", "")
    dc = (e.get("desc_cn") or "").strip()
    sr = (e.get("silver_reason") or "").strip()
    hl = e.get("highlights") or []
    fd = e.get("funding") or {}
    fdisp = fd.get("display") if isinstance(fd, dict) else ""
    desc = (e.get("description") or "").strip()
    pm = e.get("payor_model", "")
    tags = (e.get("tag_l1") or []) + (e.get("tag_l2") or [])
    print("TAGS:", " / ".join(str(t) for t in tags))
    print("="*70)
    print("SERIAL:", s, "| name:", nm, "| research_value:", rv, "| payor:", pm)
    print("-- desc_cn (len %d):" % len(dc), dc)
    print("-- silver_reason (len %d):" % len(sr), sr)
    if hl:
        print("-- highlights:", " | ".join(str(h) for h in hl))
    if fdisp:
        print("-- funding.display:", fdisp)
    if desc and desc != dc:
        print("-- description (len %d):" % len(desc), desc[:200])
