import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
db = json.load(open(DB, encoding="utf-8"))
recs = [(e["serial"], e["recommend"]) for e in db if isinstance(e.get("recommend"), str)]
print(f"主库单字符串总数: {len(recs)}")

def _norm(t): return re.sub(r"\s","",t or "")
def _tris(t):
    t=_norm(t); return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _cs(t): return set(_norm(t))
cs=[_cs(r) for s,r in recs]; tr=[_tris(r) for s,r in recs]
inv={}
for i,x in enumerate(tr):
    for g in x: inv.setdefault(g,[]).append(i)
fails=set(); pairs=0
for i in range(len(recs)):
    seen=set()
    for g in tr[i]:
        for j in inv.get(g,[]):
            if j<=i or j in seen: continue
            seen.add(j)
            a,b=cs[i],cs[j]
            if not a or not b: continue
            if len(a&b)/len(a|b)<=0.5: continue
            si,ri=recs[i]; sj,rj=recs[j]
            if ri==rj or C.lcs_len(ri,rj)>=15:
                pairs+=1; fails.add(si); fails.add(sj)
print(f"主库内 R10 雷同对: {pairs}")
print(f"涉及企业数: {len(fails)} ({len(fails)*100/len(recs):.1f}% of 单字符串)")
print(f"干净企业数: {len(recs)-len(fails)}")
