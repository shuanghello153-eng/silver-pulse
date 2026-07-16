# -*- coding: utf-8 -*-
import json, collections
PATH = 'G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json'
with open(PATH,'r',encoding='utf-8') as f:
    ents = json.load(f)
def l1(e): return e.get('tag_l1') or []
def l2(e): return e.get('tag_l2') or []
def desc(e): return (e.get('desc_cn') or e.get('description') or '')

# ---- TASK4: 产业资本 mis-entered operational ----
print("===== TASK4 产业资本 with operational l2 =====")
INVEST_MEDIA = {'VC','产业基金','行业媒体','资讯门户','养老咨询','养老信息平台','行业研究','展会','养老社区','研究'}
op = []
for e in ents:
    if '产业资本' in l1(e):
        noninv = [t for t in l2(e) if t not in INVEST_MEDIA]
        if noninv:
            op.append(e)
print("count:", len(op))
for e in op:
    print(f"  {e.get('name')} | L1={l1(e)} | L2={l2(e)} | desc={desc(e)[:90]}")

# ---- TASK5: cross-L1 duplicate L2 ----
print("\n===== TASK5 L2 appearing under >1 L1 =====")
m = collections.defaultdict(set)
for e in ents:
    for t in l2(e):
        for x in l1(e):
            m[t].add(x)
for t, s in sorted(m.items(), key=lambda x:-len(x[1])):
    if len(s)>1:
        print(f"  {t}: {sorted(s)}  (n={sum(1 for e in ents if t in l2(e))})")

# ---- TASK6: basic validation ----
print("\n===== TASK6 validation =====")
zero = [e.get('name') for e in ents if len(l2(e))==0]
print(f"0 L2 count={len(zero)}: {zero}")
over3 = [(e.get('name'), l2(e)) for e in ents if len(l2(e))>3]
print(f">3 L2 count={len(over3)}")
for n,t in over3: print(f"   {n}: {t}")
# internal duplicate
dupin = [(e.get('name'), l2(e)) for e in ents if len(l2(e))!=len(set(l2(e)))]
print(f"internal-dup-L2 count={len(dupin)}")
for n,t in dupin: print(f"   {n}: {t}")
# ghost L2 <5
c = collections.Counter()
for e in ents:
    for t in set(l2(e)): c[t]+=1
ghost = {k:v for k,v in c.items() if v<5}
print(f"ghost L2 (<5) count={len(ghost)}")
for k in sorted(ghost, key=lambda x:ghost[x]):
    print(f"   {k}: {ghost[k]}")

# ---- TASK7: 护工求职/接单 platforms ----
print("\n===== TASK7 护工/护理人力 platforms =====")
kw = ['护工','护理人力','找工作','接单','护理招聘','护理用工','护理员']
for e in ents:
    blob = (e.get('name','')+desc(e)+' '.join(l2(e))).lower()
    if any(k in blob for k in kw):
        print(f"  {e.get('name')} | L1={l1(e)} | L2={l2(e)} | desc={desc(e)[:80]}")

# ---- TASK8: deleted L1 distributions ----
print("\n===== TASK8a 医疗健康 l2 distribution =====")
mh = [e for e in ents if '医疗健康' in l1(e)]
print("total 医疗健康:", len(mh))
c = collections.Counter()
for e in mh:
    for t in l2(e): c[t]+=1
for k,v in c.most_common():
    print(f"   {k}: {v}")

print("\n===== TASK8b 渠道零售 (28) =====")
cr = [e for e in ents if '渠道零售' in l1(e)]
print("total 渠道零售:", len(cr))
for e in cr:
    print(f"  {e.get('name')} | L2={l2(e)} | desc={desc(e)[:70]}")

print("\n===== TASK8c 智能科技 (140) l2 distribution =====")
zc = [e for e in ents if '智能科技' in l1(e)]
print("total 智能科技:", len(zc))
c = collections.Counter()
for e in zc:
    for t in l2(e): c[t]+=1
for k,v in c.most_common():
    print(f"   {k}: {v}")
