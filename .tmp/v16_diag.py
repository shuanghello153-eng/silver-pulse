import json
from collections import Counter, defaultdict

d = json.load(open('data/enterprise/all_enterprises.json'))

# 完全相同文案聚类
groups = defaultdict(list)
for e in d:
    desc = (e.get('desc_cn') or e.get('description') or '').strip()
    if len(desc) > 15:
        groups[desc].append(e)

# 仅看 >=2 家的组
dup = {k: v for k, v in groups.items() if len(v) >= 2}

out = []
out.append(f"=== 完全相同文案组: {len(dup)} 组, 涉及 {sum(len(v) for v in dup.values())} 家企业 ===\n")

for desc, ents in sorted(dup.items(), key=lambda x: -len(x[1])):
    out.append(f"\n#### 组 [{len(ents)}家] 文案: {desc[:60]}")
    tag_count = Counter()
    for e in ents:
        tag_count.update(e.get('tag_l2', []))
    # 组内标签频次
    freq = sorted(tag_count.items(), key=lambda x: -x[1])
    out.append("  组内标签频次:")
    for t, n in freq:
        pct = '★共性' if n >= max(2, len(ents) * 0.5) else ''
        out.append(f"    {t}: {n}/{len(ents)} {pct}")
    # 列出企业名 + 全部标签
    out.append("  企业明细:")
    for e in ents:
        out.append(f"    - {e['name'][:28]:30} L2={e.get('tag_l2', [])}")

open('.tmp/v16_diag.txt', 'w', encoding='utf-8').write('\n'.join(out))
print("诊断写入 .tmp/v16_diag.txt, 组数:", len(dup))

# 另外统计: 模板企业总体的标签分布 (含短语命中)
TPL = ['面向银发人群', '银发社交与文娱', '相关的服务（如', '专业护理相关的服务',
       '养老辅具与适老化硬件', 'B2B AI/数据驱动', '搭建面向中老年',
       '提供居家照护、专业护理及智慧养老', '主营', '资讯', '平台企业，主营']
def is_tpl(e):
    desc = (e.get('desc_cn') or e.get('description') or '')
    if len(desc) > 40 and desc in groups and len(groups[desc]) >= 2:
        return True
    return any(p in desc for p in TPL)

tpl_ents = [e for e in d if is_tpl(e)]
tc = Counter()
for e in tpl_ents:
    tc.update(e.get('tag_l2', []))
print(f"\n模板短语命中企业: {len(tpl_ents)} 家")
print("这些企业的标签总分布(前25):")
for t, n in tc.most_common(25):
    print(f"  {t}: {n}")
