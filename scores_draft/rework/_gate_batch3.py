# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '.')
from check_single import validate

HERE = os.path.dirname(os.path.abspath(__file__))
DV = os.path.join(HERE, "drafts_v4")
SERIALS = ["1392","1400","1402","1415","1416","1433","1440","1441","1454",
           "1479","1484","1488","1500","1501","1503","1516","0631","0036","1333","1356"]

all_fail = {}
for s in SERIALS:
    fp = os.path.join(DV, f"draft_#{s}.json")
    if not os.path.exists(fp):
        print(f"#{s}: MISSING FILE"); continue
    e = json.load(open(fp, encoding="utf-8"))
    iss = validate(e, others=None, skip={'R10'})
    if iss:
        all_fail[s] = iss
        print(f"#{s}: FAIL {iss}")
    else:
        print(f"#{s}: PASS  (recommend {len(''.join(e.get('recommend','').split()))}字)")

print("\n==== SUMMARY ====")
print(f"TOTAL {len(SERIALS)} | PASS {len(SERIALS)-len(all_fail)} | FAIL {len(all_fail)}")
