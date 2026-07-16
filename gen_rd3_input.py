#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 RD3 拆分输入: 导出当前仍>=20 的二级标签及其成员企业(精简字段)。"""
import json, os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data/enterprise/all_enterprises.json')
OUT = os.path.join(ROOT, 'output/_v12_rd3_input.json')

THRESHOLD = 20

d = json.load(open(DATA, encoding='utf-8'))
es = d if isinstance(d, list) else d.get('enterprises', d.get('data', []))
# 仅保留有 tag_l2 的企业
es = [e for e in es if e.get('tag_l2')]

# 统计二级标签企业数
l2c = Counter()
for e in es:
    for x in e.get('tag_l2', []):
        l2c[x] += 1

big = sorted([k for k, v in l2c.items() if v >= THRESHOLD], key=lambda x: -l2c[x])

# 成员索引: 二级标签 -> [企业]
members = defaultdict(list)
for e in es:
    nc = e.get('name_cn') or e.get('name')
    for x in e.get('tag_l2', []):
        members[x].append({
            'name': nc,
            'name_en': e.get('name', ''),
            'desc_cn': (e.get('desc_cn') or '')[:220],
            'business_model_cn': (e.get('business_model_cn') or '')[:120],
            'tag_l1': e.get('tag_l1', []),
            'tag_l2': e.get('tag_l2', []),
        })

# 现有全部 L2 标签(供 agent 避免重名)
all_l2 = sorted(l2c.keys())
# L1 列表(从 L2->L1 推断: 企业 tag_l1)
l1set = set()
for e in es:
    for x in e.get('tag_l1', []):
        l1set.add(x)
# L1->其下 L2(供 agent 选择归属)
l1_to_l2 = defaultdict(set)
for e in es:
    for l1 in e.get('tag_l1', []):
        for l2 in e.get('tag_l2', []):
            l1_to_l2[l1].add(l2)

payload = {
    'threshold': THRESHOLD,
    'big_tags': [{'tag': t, 'count': l2c[t], 'members': members[t]} for t in big],
    'all_l2_tags': all_l2,
    'l1_list': sorted(l1set),
    'l1_to_l2': {k: sorted(v) for k, v in l1_to_l2.items()},
}

json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"已写出 {OUT}: {len(big)} 个大标签, 共 {sum(l2c[t] for t in big)} 家企业成员")
print("大标签列表:", [f"{t}({l2c[t]})" for t in big])
