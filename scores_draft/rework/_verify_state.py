import json, os, sys, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
db = json.load(open(DB, encoding="utf-8"))

# 主库 recommend 现状
single=dict_v=empty=other=0
single_serials=[]
for e in db:
    r=e.get("recommend")
    if r is None or (isinstance(r,str) and r.strip()==""):
        empty+=1
    elif isinstance(r,str):
        single+=1; single_serials.append(e["serial"])
    elif isinstance(r,dict):
        dict_v+=1
    else:
        other+=1
print(f"=== 主库 recommend 现状 (共{len(db)}家) ===")
print(f"单字符串(V4正确): {single}")
print(f"三版dict(旧格式错): {dict_v}")
print(f"空/无: {empty}")
print(f"其他: {other}")

# R10 全量探测（只读）
def _norm(t): return re.sub(r"\s","",t or "")
def _tris(t):
    t=_norm(t); return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _cs(t): return set(_norm(t))
recs=[(e["serial"], e["recommend"]) for e in db if isinstance(e.get("recommend"),str)]
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
print(f"\n=== R10 全量探测 ===")
print(f"单字符串总数: {len(recs)}")
print(f"R10雷同对: {pairs}")
print(f"涉及企业(脏): {len(fails)} ({len(fails)*100/len(recs):.1f}%)")
print(f"干净企业: {len(recs)-len(fails)}")

# 保存脏数据清单
with open("_dirty_R10.json","w",encoding="utf-8") as f:
    json.dump({"dirty_serials":sorted(fails),"pairs":pairs,"clean_count":len(recs)-len(fails)}, f, ensure_ascii=False, indent=2)
print(f"\n脏数据清单已存 _dirty_R10.json -> {len(fails)} 家")

# 缺口：主库里非单字符串的（dict/空）即未达标
gap=[e["serial"] for e in db if not (isinstance(e.get("recommend"),str) and e["recommend"].strip()!="")]
print(f"\n=== 缺口(主库无合格recommend) ===")
print(f"共 {len(gap)} 家 (dict {dict_v} + 空 {empty} + 其他 {other})")
with open("_gap_maindb.json","w",encoding="utf-8") as f:
    json.dump(gap, f, ensure_ascii=False, indent=2)
print(f"缺口清单已存 _gap_maindb.json")
