# -*- coding: utf-8 -*-
import json, re, collections

PATH = 'G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json'
with open(PATH, 'r', encoding='utf-8') as f:
    ents = json.load(f)

print("TOTAL:", len(ents))

def l1(e): return e.get('tag_l1') or []
def l2(e): return e.get('tag_l2') or []
def desc(e):
    d = e.get('desc_cn') or e.get('description') or ''
    return d or ''

# ---------- Task 1: 助听器 ----------
print("\n===== TASK1 助听器 (tag_l2 contains 助听器) =====")
ha = [e for e in ents if '助听器' in l2(e)]
print("COUNT:", len(ha))
for e in ha:
    d = desc(e)
    print(f"\n[{e.get('name')}] L1={l1(e)} L2={l2(e)}")
    print("  DESC:", d[:200])

# ---------- Task 2: redundant pairs ----------
print("\n\n===== TASK2 redundant pairs =====")
def setof(tag):
    return [e for e in ents if tag in l2(e)]
pairs = [('助听辅具','助听器'),('护士派遣','护士上门'),('远程监护','远程医疗'),('陪伴社交','陪伴服务')]
for a,b in pairs:
    A=setof(a); B=setof(b)
    an=set(e['name'] for e in A); bn=set(e['name'] for e in B)
    ov=an&bn
    print(f"\n--- {a}({len(A)}) vs {b}({len(B)}) ---")
    print(f"overlap={len(ov)} union={len(an|bn)} coocc_rate_of_A={len(ov)/len(A)*100:.0f}% coocc_rate_of_B={len(ov)/len(B)*100:.0f}%")
    print(f"{a} only: {sorted(an-bn)}")
    print(f"{b} only: {sorted(bn-an)}")
    print(f"both: {sorted(ov)}")

# ---------- Task 3: template pollution ----------
print("\n\n===== TASK3 template pollution (identical desc_cn) =====")
g = collections.defaultdict(list)
for e in ents:
    d = (e.get('desc_cn') or '').strip()
    if d:
        g[d].append(e.get('name'))
dup = {k:v for k,v in g.items() if len(v)>1}
print("num distinct dup-template groups:", len(dup))
for k,v in sorted(dup.items(), key=lambda x:-len(x[1])):
    print(f"\nGROUP size={len(v)}")
    print("  TPL:", k[:160])
    print("  NAMES:", v[:15])
    # check tag_l2 contradiction: are any of these tagged 助听器 only while desc generic?
    for e in ents:
        if e.get('name') in v[:3]:
            print(f"    e.g. {e.get('name')}: L1={l1(e)} L2={l2(e)}")
