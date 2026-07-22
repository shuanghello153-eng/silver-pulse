# -*- coding: utf-8 -*-
import json, glob, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_single import validate
recs = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob("drafts_v5/draft_#*.json"))]
print("loaded", len(recs))
others = [r["recommend"] for r in recs]
any_fail = False
for r in recs:
    iss = validate(r, others)
    if iss:
        any_fail = True
        print("R10FAIL", r["serial"], iss)
print("R10 batch check:", "FAIL" if any_fail else "PASS (no cross-enterprise duplication)")
