# -*- coding: utf-8 -*-
import json, glob, sys, os, re
sys.stderr.write("importing\n"); sys.stderr.flush()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
sys.stderr.write("imported C\n"); sys.stderr.flush()

SERIALS = set()
for b in [52,53,54,55,56,57,58,59]:
    for e in json.load(open(f"batches_full/batch_src_0{b}.json", encoding="utf-8")):
        SERIALS.add(e["serial"])
recs = {}
for f in glob.glob("drafts_v4/draft_*.json"):
    d = json.load(open(f, encoding="utf-8"))
    if d.get("serial") in SERIALS and d.get("recommend"):
        recs[d["serial"]] = re.sub(r"\s", "", d["recommend"])
ks = list(recs)
sys.stderr.write("n=" + str(len(ks)) + "\n"); sys.stderr.flush()

grams = {}
for k in ks:
    s = recs[k]
    if len(s) >= 15:
        grams[k] = set(s[i:i+15] for i in range(len(s)-14))
    else:
        grams[k] = set()
sys.stderr.write("grams built\n"); sys.stderr.flush()

bad = []
checked = 0
n = len(ks)
for i in range(n):
    for j in range(i+1, n):
        a, b = ks[i], ks[j]
        ga, gb = grams[a], grams[b]
        if not ga or not gb or ga.isdisjoint(gb):
            continue
        checked += 1
        sa, sb = set(recs[a]), set(recs[b])
        r = len(sa & sb) / len(sa | sb) if (sa | sb) else 0
        if r > 0.5:
            ov = C.lcs_len(recs[a], recs[b])
            bad.append((a, b, round(r, 2), ov))
sys.stderr.write("loop done\n"); sys.stderr.flush()
print("shared15gram pairs:", checked)
print("R10>0.5 pairs:", len(bad))
for x in bad[:30]:
    print("  ", x)
