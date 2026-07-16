#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V21 落库：把 8 个子智能体的研究结果合并回 all_enterprises.json。
用法: python apply_v21_research.py [--apply]
不带 --apply 为 dry-run（只报告，不写）。
"""
import json, sys, os, glob, shutil, datetime
from collections import Counter

base = 'data/enterprise/'
APPLY = '--apply' in sys.argv

d = json.load(open(base + 'all_enterprises.json', encoding='utf-8'))
m = json.load(open(base + '_l2_l1.json', encoding='utf-8'))
valid_l2 = set(m.keys())
by_name = {e.get('name'): e for e in d}

# 载入所有结果
results = []
files = sorted(glob.glob('.tmp/results/result_*.json'))
print('结果文件:', files)
for f in files:
    try:
        arr = json.load(open(f, encoding='utf-8'))
        results += arr
        print(f'  {f}: {len(arr)} 家')
    except Exception as ex:
        print(f'  !! {f} 解析失败: {ex}')

print('\n结果总数:', len(results))

unmatched = []
invalid_tag = []
applied = 0
conf = Counter()
changes = []

for r in results:
    nm = r.get('name')
    e = by_name.get(nm)
    if not e:
        unmatched.append(nm)
        continue
    l2 = r.get('tag_l2') or []
    # 校验标签
    bad = [t for t in l2 if t not in valid_l2]
    if bad:
        invalid_tag.append((nm, bad))
        # 只保留合法的
        l2 = [t for t in l2 if t in valid_l2]
    if not l2:
        # 无有效标签，跳过（保留原标签）
        invalid_tag.append((nm, ['<全部非法或空>']))
        continue
    # 去重
    seen = []
    for t in l2:
        if t not in seen:
            seen.append(t)
    l2 = seen
    conf[r.get('confidence', '?')] += 1
    desc = (r.get('desc_cn') or '').strip()
    old_l2 = e.get('tag_l2')
    if APPLY:
        e['tag_l2'] = l2
        e['tags'] = l2
        if desc:
            e['description'] = desc
            e['desc_cn'] = desc
        # 派生一级
        l1 = []
        for t in l2:
            for x in m.get(t, []):
                if x not in l1:
                    l1.append(x)
        e['tag_l1'] = l1
    applied += 1
    if old_l2 != l2:
        changes.append((nm, old_l2, l2))

print('\n=== 匹配情况 ===')
print('可落库:', applied, '| 未匹配名字:', len(unmatched), '| 含非法标签:', len(invalid_tag))
print('置信度分布:', dict(conf))
if unmatched:
    print('\n未匹配(前30):', unmatched[:30])
if invalid_tag:
    print('\n非法标签(前30):')
    for nm, bad in invalid_tag[:30]:
        print('  ', nm, '->', bad)

if APPLY:
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy(base + 'all_enterprises.json', base + f'backups/all_enterprises_{ts}_pre_v21research.json')
    json.dump(d, open(base + 'all_enterprises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n[已写入] 落库 {applied} 家，标签变更 {len(changes)} 家，backup ts={ts}')
else:
    print(f'\n[DRY-RUN] 若 --apply 将落库 {applied} 家，标签变更 {len(changes)} 家')
