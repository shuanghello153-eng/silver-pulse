import json, collections, os
BASE = r"g:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise"
ent = json.load(open(os.path.join(BASE, "all_enterprises.json"), encoding="utf-8"))
n = len(ent)
l1c = collections.Counter(); l2c = collections.Counter()
for e in ent:
    for x in (e.get("tag_l1") or []): l1c[x]+=1
    for x in (e.get("tag_l2") or []): l2c[x]+=1

print("企业总数:", n, "| L1数:", len(l1c), "| L2数:", len(l2c))
print("\n=== 全量 L2 标签及企业数（降序）===")
for k,c in l2c.most_common():
    print(f"  {c:4d}  {k}")

print("\n=== Claude 点名标签当前状态 ===")
for t in ["助听辅具","护士派遣","护士上门","数字平台","陪伴社交","陪伴服务","陪伴机器人",
          "远程医疗","远程监护","养老REIT","产业基金","行业媒体","咨询","会展","协会",
          "VC","PE","CVC","投资","媒体","SaaS","AI","助听器","居家护理"]:
    print(f"  {t}: {l2c.get(t,'不存在')} 家" if t in l2c else f"  {t}: 不存在(已合并/删除)")

# 分布区间统计（当前109个L2）
buckets = collections.Counter()
for k,c in l2c.items():
    if c<5: buckets["<5 幽灵"]+=1
    elif c<10: buckets["5-9"]+=1
    elif c<40: buckets["10-39"]+=1
    elif c<80: buckets["40-79"]+=1
    else: buckets[">=80"]+=1
print("\n=== 当前 L2 数量分布 ===")
for b in ["<5 幽灵","5-9","10-39","40-79",">=80"]:
    print(f"  {b}: {buckets[b]} 个")

# 投资/媒体类当前怎么挂的
print("\n=== 当前 产业资本 L1 下的 L2 分布 ===")
cap_l2 = collections.Counter()
cap_members = []
for e in ent:
    if "产业资本" in (e.get("tag_l1") or []):
        for t in (e.get("tag_l2") or []): cap_l2[t]+=1
        cap_members.append(e.get("name") or e.get("name_cn"))
print("产业资本 L1 企业数:", len(cap_members))
for k,c in cap_l2.most_common():
    print(f"  {c:4d}  {k}")

print("\n=== 媒体/研究类 L2 当前分布（跨所有L1）===")
media_l2 = collections.Counter()
for e in ent:
    for t in (e.get("tag_l2") or []):
        if t in ("行业媒体","资讯门户","咨询","会展","协会","研究","展会","媒体"):
            media_l2[t]+=1
for k,c in media_l2.most_common():
    print(f"  {c:4d}  {k}")
