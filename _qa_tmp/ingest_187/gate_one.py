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
print("db recs:", len(recs), "cands:", len(cands), flush=True)

c = cands[0]
print("test one:", c.get("name"), flush=True)
try:
    iss = C.validate(c, others=recs)
    print("C.validate ok:", iss, flush=True)
    iss2 = CD.validate_desc(c)
    print("CD.validate_desc ok:", iss2, flush=True)
except Exception:
    traceback.print_exc()
