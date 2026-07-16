import json, collections, os
BASE = r"g:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise"
ent = json.load(open(os.path.join(BASE, "all_enterprises.json"), encoding="utf-8"))

# 找出重复>=3家的描述组，并打印每组企业的 真实L2标签
desc_groups = collections.defaultdict(list)
for e in ent:
    d = (e.get("description") or "").strip()
    if d:
        desc_groups[d].append(e)

print("=== 可疑重复描述组：成员真实标签抽样 ===\n")
for d, members in sorted(desc_groups.items(), key=lambda x:-len(x[1])):
    if len(members) < 3: 
        continue
    print(f"### 描述组 [{len(members)}家]: {d[:60]}")
    # 统计这组企业实际被打的 L2
    tagcount = collections.Counter()
    for m in members:
        for t in (m.get("tag_l2") or []):
            tagcount[t]+=1
    top = tagcount.most_common(6)
    print("   实际L2标签分布(前6):", ", ".join(f"{k}({v})" for k,v in top))
    # 列出前6个成员的名字+完整L2
    for m in members[:6]:
        nm = m.get("name") or m.get("name_cn") or "?"
        print(f"     - {nm}: {m.get('tag_l2')}")
    print()
