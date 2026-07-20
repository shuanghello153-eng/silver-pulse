# -*- coding: utf-8 -*-
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts_v4")
SERIALS = ['0095','0068','0620','1380','1486','0662','0876','0771','0782','0797',
           '0828','0874','1027','1075','1076','1106','1107','1111','1188','1201']

def load(s):
    p = os.path.join(OUT, "draft_#%s.json" % s)
    return json.load(open(p, encoding="utf-8"))

entries = [load(s) for s in SERIALS]
all_recs = [e.get("recommend") for e in entries]

print("=== GATE (skip R10) ===")
total_pass = 0
results = []
for e in entries:
    issues = check_single.validate(e, others=all_recs, skip={'R10'})
    serial = e.get("serial")
    rc = len(re.sub(r"\s","", e.get("recommend") or ""))
    if issues:
        print(f"\n[{serial}] FAIL (recommend {rc} chars):")
        for it in issues:
            print("   -", it)
        results.append((serial, "FAIL", rc, issues))
    else:
        print(f"[{serial}] PASS (recommend {rc} chars)")
        results.append((serial, "PASS", rc, []))
        total_pass += 1

print("\n=== SUMMARY ===")
print(f"PASS {total_pass}/{len(entries)}")
fails = [r for r in results if r[1]=="FAIL"]
if fails:
    print("FAILING:", [r[0] for r in fails])

# also dump per-serial recommend char count
print("\n=== RECOMMEND CHAR COUNTS ===")
for e in entries:
    rc = len(re.sub(r"\s","", e.get("recommend") or ""))
    print(e.get("serial"), rc)
