# -*- coding: utf-8 -*-
import json, sys, os, collections
ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scores_draft", "rework"))
import enterprise_build as EB

cands = json.load(open("_qa_tmp/ingest_187/候选_133.json", encoding="utf-8"))
passed, failures = EB.run_gates(cands)
print(f"生产门禁自测：{passed}/{len(cands)} 通过")
cnt = collections.Counter()
for s, iss in failures.items():
    for x in iss:
        cnt[x.split(":")[0].split("[")[0]] += 1
print("失败类型分布:", dict(cnt))
for s, iss in list(failures.items())[:20]:
    print("  #" + str(s), iss)
