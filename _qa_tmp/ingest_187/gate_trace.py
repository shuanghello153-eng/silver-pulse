# -*- coding: utf-8 -*-
import json, sys, os, traceback
ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scores_draft", "rework"))
import check_single as C
import check_description as CD

db = json.load(open("data/enterprise/all_enterprises.json", encoding="utf-8"))
recs = [e["recommend"] for e in db if isinstance(e.get("recommend"), str)]
cands = json.load(open("_qa_tmp/ingest_187/候选_133.json", encoding="utf-8"))

log = open("_qa_tmp/ingest_187/_gate_trace.txt", "w", encoding="utf-8")
fails = {}
for i, c in enumerate(cands):
    log.write(f"{i} {c.get('serial')} {c.get('name')}\n"); log.flush()
    try:
        iss = C.validate(c, others=recs) + CD.validate_desc(c)
        if iss:
            fails[c.get("serial")] = iss
    except Exception:
        log.write("EXC:\n" + traceback.format_exc() + "\n"); log.flush()
        break
log.write(f"\nDONE 通过 {len(cands)-len(fails)}/{len(cands)}\n")
for s, iss in fails.items():
    log.write(f"  {s} {iss}\n")
log.close()
print("done")
