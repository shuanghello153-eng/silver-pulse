# -*- coding: utf-8 -*-
"""步骤4 走查：标签分布 / 文案雷同(跨133两两) / 评分区分度 / 地区分布 / 空值抽查。"""
import json, os, re
from collections import Counter
ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
cands = json.load(open(os.path.join(ROOT, "_qa_tmp/ingest_187/候选_133.json"), encoding="utf-8"))
print(f"候选 {len(cands)} 家\n")

# 标签分布
l1c, l2c, regc = Counter(), Counter(), Counter()
for c in cands:
    for a in (c.get("tag_l1") or []): l1c[a]+=1
    for b in (c.get("tag_l2") or []): l2c[b]+=1
    regc[c.get("region","?")]+=1
print("== 一级标签分布 ==")
for k,v in l1c.most_common(): print(f"  {k}: {v}")
print("\n== 二级标签分布(前20) ==")
for k,v in l2c.most_common(20): print(f"  {k}: {v}")
print("\n== 地区分布(前15) ==")
for k,v in regc.most_common(15): print(f"  {k}: {v}")

# 评分
def col(k): return [float(c.get(k)) for c in cands if c.get(k) is not None]
print("\n== 评分区分度 ==")
for k in ("signal_strength","info_score","diff_score","copy_score","total_score"):
    v=col(k)
    if v: print(f"  {k}: min={min(v)} max={max(v)} 均值={sum(v)/len(v):.2f}")

# 文案雷同：跨133两两4-gram Jaccard>0.5 报警
def grams(t):
    t=re.sub(r"\s","",t or "")
    return set(t[i:i+4] for i in range(len(t)-3)) if len(t)>=4 else set()
recs=[(c.get("serial"),c.get("name"),grams(c.get("recommend",""))) for c in cands]
print("\n== 文案雷同(跨133，4-gram Jaccard>0.45) ==")
hits=0
for i in range(len(recs)):
    for j in range(i+1,len(recs)):
        a,b=recs[i][2],recs[j][2]
        if not a or not b: continue
        jac=len(a&b)/len(a|b)
        if jac>0.45:
            print(f"  {recs[i][0]}{recs[i][1]} ~ {recs[j][0]}{recs[j][1]} : {jac:.0%}")
            hits+=1
if not hits: print("  无 (全部<45%)")

# 空关键字段抽查
print("\n== 关键字段空值抽查 ==")
for f in ("name_cn","description","recommend","tag_l1","tag_l2","stage","region"):
    miss=[c.get("serial") for c in cands if not c.get(f)]
    print(f"  {f} 空: {len(miss)} {miss[:5]}")
