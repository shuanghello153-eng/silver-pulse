import json, os, sys, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
db = json.load(open(DB, encoding="utf-8"))
by_serial={e["serial"]:e for e in db}
# 计算干净集
def _norm(t): return re.sub(r"\s","",t or "")
def _tris(t):
    t=_norm(t); return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _cs(t): return set(_norm(t))
recs=[(e["serial"], e["recommend"]) for e in db if isinstance(e.get("recommend"),str)]
cs=[_cs(r) for s,r in recs]; tr=[_tris(r) for s,r in recs]
inv={}
for i,x in enumerate(tr):
    for g in x: inv.setdefault(g,[]).append(i)
fails=set()
for i in range(len(recs)):
    seen=set()
    for g in tr[i]:
        for j in inv.get(g,[]):
            if j<=i or j in seen: continue
            seen.add(j)
            a,b=cs[i],cs[j]
            if not a or not b: continue
            if len(a&b)/len(a|b)<=0.5: continue
            if recs[i][1]==recs[j][1] or C.lcs_len(recs[i][1],recs[j][1])>=15:
                fails.add(recs[i][0]); fails.add(recs[j][0])
clean=[s for s,r in recs if s not in fails]
random.seed(11)
sample=random.sample(clean, 12)
for s in sample:
    e=by_serial.get(s,{})
    name=e.get("name") or e.get("公司名称") or "?"
    biz=e.get("business") or e.get("业务") or e.get("简介") or ""
    comp=e.get("国内竞品") or e.get("竞品") or ""
    rec=e["recommend"]
    print("="*60)
    print(f"[{s}] {name}")
    print(f"  业务/简介: {str(biz)[:120]}")
    print(f"  国内竞品: {str(comp)[:80]}")
    print(f"  recommend({len(rec)}字): {rec}")
