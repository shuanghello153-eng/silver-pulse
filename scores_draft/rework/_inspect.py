import json, os
from collections import Counter
BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
d = json.load(open(os.path.join(BASE,"data/enterprise/all_enterprises.json"),encoding="utf-8"))
print("TOTAL:", len(d))
print("KEYS:", list(d[0].keys()))

def rtype(e):
    r = e.get("recommend")
    if r is None: return "none"
    if isinstance(r,str): return "str"
    if isinstance(r,dict):
        ks=set(r.keys())
        if {"rec_v1","rec_v2","rec_v3"} <= ks: return "dict3"
        return "dict_other"
    return "other"
c = Counter(rtype(e) for e in d)
print("RECOMMEND FORMAT:", dict(c))

strs = [e for e in d if isinstance(e.get("recommend"),str)]
print("STR count:", len(strs))
tmpl = ["信号偏弱","切入","行业媒体赛道","结合本地资源","宜学其思路"]
tmpl_hits = sum(1 for e in strs if any(t in (e.get("recommend") or "") for t in tmpl))
print("STR templated-hits:", tmpl_hits)

def ln(x): return len(x) if isinstance(x,str) else 0
dc = [ln(e.get("desc_cn","")) for e in d]
print("desc_cn: <80=%d, 80-120=%d, >120=%d, avg=%.1f" % (
    sum(1 for x in dc if x<80), sum(1 for x in dc if 80<=x<=120), sum(1 for x in dc if x>120), sum(dc)/len(dc)))
sr = [ln(e.get("silver_reason","")) for e in d]
print("silver_reason: <30=%d, >=30=%d" % (sum(1 for x in sr if x<30), sum(1 for x in sr if x>=30)))

CANON = {"个人自费","个人自费+政府补贴","个人自费+长护险","个人自费+医保","B端机构采购","B端机构采购+政府付费","B端机构采购+政府/商保支付","政府医保/商保支付","混合支付","不适用（投资机构）","未搜到"}
pm = Counter(e.get("payor_model","") for e in d)
noncanon = sum(v for k,v in pm.items() if k not in CANON)
print("payor distinct=%d, non-canonical=%d" % (len(pm), noncanon))
print("payor top12:", pm.most_common(12))

# scoring fields populated?
for f in ("signal_strength","info_score","diff_score","copy_score","research_value"):
    n = sum(1 for e in d if isinstance(e.get(f),(int,float)))
    print("field %s populated=%d" % (f,n))

flags = [e.get("serial") for e in d if e.get("flag")]
print("DB records with non-empty flag:", len(flags), flags[:10])
