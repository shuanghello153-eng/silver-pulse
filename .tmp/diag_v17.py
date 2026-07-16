import json, collections, os

BASE = r"g:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise"
ent = json.load(open(os.path.join(BASE, "all_enterprises.json"), encoding="utf-8"))
syn = json.load(open(os.path.join(BASE, "tag_synonyms.json"), encoding="utf-8"))
l2l1 = json.load(open(os.path.join(BASE, "_l2_l1.json"), encoding="utf-8"))

n = len(ent)
print("=== 总览 ===")
print("企业总数:", n)

# L1 / L2 计数
l1c = collections.Counter()
l2c = collections.Counter()
per_ent_l2 = []
for e in ent:
    t1 = e.get("tag_l1") or []
    t2 = e.get("tag_l2") or []
    for x in t1: l1c[x]+=1
    for x in t2: l2c[x]+=1
    per_ent_l2.append(len(t2))

print("一级标签数:", len(l1c))
print("二级标签数:", len(l2c))
print("平均每企业二级数: %.2f" % (sum(per_ent_l2)/n))
print("单标签企业数:", sum(1 for x in per_ent_l2 if x==1))
print("双标签企业数:", sum(1 for x in per_ent_l2 if x==2))
print("三标签企业数:", sum(1 for x in per_ent_l2 if x==3))
print("0标签企业数:", sum(1 for x in per_ent_l2 if x==0))

print("\n=== 一级标签及企业数 ===")
for k,v in l1c.most_common():
    print(f"  {v:4d}  {k}")

print("\n=== 二级标签 >=40 的大桶（全部列出企业数）===")
big = [(c,k) for k,c in l2c.items() if c>=40]
for c,k in sorted(big, reverse=True):
    print(f"  {c:4d}  {k}")
print(">=40 标签总数:", len(big))

print("\n=== 二级标签 20-39 的中桶 ===")
mid = [(c,k) for k,c in l2c.items() if 20<=c<40]
for c,k in sorted(mid, reverse=True):
    print(f"  {c:4d}  {k}")
print("20-39 标签总数:", len(mid))

print("\n=== 二级标签 <=2 的幽灵标签 ===")
ghost = [(c,k) for k,c in l2c.items() if c<=2]
for c,k in sorted(ghost):
    print(f"  {c:4d}  {k}")
print("<=2 标签总数:", len(ghost))

print("\n=== 疑似污染1：二级标签名 与 一级标签名 重名 ===")
l1set = set(l1c.keys())
for k in l2c:
    if k in l1set:
        print(f"  !! {k} 既是二级({l2c[k]}家)又是一级")

print("\n=== 疑似污染2：同描述文案（模板污染残留）===")
desc_groups = collections.defaultdict(list)
for e in ent:
    d = (e.get("description") or "").strip()
    if d:
        desc_groups[d].append(e.get("name") or e.get("name_cn") or "?")
dup = {d:ns for d,ns in desc_groups.items() if len(ns)>=3}
print("重复>=3家的描述文案组数:", len(dup))
total_in_dup = sum(len(v) for v in dup.values())
print("这些组覆盖企业总数:", total_in_dup)
for d,ns in sorted(dup.items(), key=lambda x:-len(x[1]))[:8]:
    print(f"\n  [{len(ns)}家] {d[:50]}")
    print("    ", " / ".join(ns[:12]))

print("\n=== 同类词(synonyms) 指向不存在标签的情况 ===")
valid = set(l2c.keys())
orphan = 0
for canon, syns in syn.items():
    if canon not in valid:
        orphan += 1
        if orphan<=20:
            print(f"  canon不存在: {canon}  -> {syns[:5]}")
print("指向不存在canon的同类词组数:", orphan)

print("\n=== L1/L2 映射(_l2_l1.json) 与 实际数据不一致检查 ===")
# 数据中出现的 L2 是否在 _l2_l1 有记录
data_l2 = set(l2c.keys())
map_l2 = set(l2l1.keys())
missing_in_map = data_l2 - map_l2
extra_in_map = map_l2 - data_l2
print("数据有但映射缺失的L2数:", len(missing_in_map))
for k in list(missing_in_map)[:20]:
    print("  缺失映射:", k)
print("映射有但数据无的L2数(死映射):", len(extra_in_map))
for k in list(extra_in_map)[:20]:
    print("  死映射:", k)
