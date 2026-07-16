#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V21 供需对接数据打标落库：只补 tag_l2/tags/tag_l1，不改 desc。
用法: python apply_sd_tags.py [--apply]
"""
import json, sys, glob, shutil, datetime
from collections import Counter

base = 'data/enterprise/'
APPLY = '--apply' in sys.argv

d = json.load(open(base + 'all_enterprises.json', encoding='utf-8'))
m = json.load(open(base + '_l2_l1.json', encoding='utf-8'))
valid_l2 = set(m.keys())
by_name = {e.get('name'): e for e in d}

results = []
for f in sorted(glob.glob('.tmp/sd_results/sdr_*.json')):
    arr = json.load(open(f, encoding='utf-8'))
    results += arr
    print(f'  {f}: {len(arr)} 家')
print('结果总数:', len(results))

unmatched, invalid, applied, conf = [], [], 0, Counter()
for r in results:
    nm = r.get('name')
    e = by_name.get(nm)
    if not e:
        unmatched.append(nm); continue
    l2 = [t for t in (r.get('tag_l2') or []) if t in valid_l2]
    bad = [t for t in (r.get('tag_l2') or []) if t not in valid_l2]
    if bad:
        invalid.append((nm, bad))
    if not l2:
        invalid.append((nm, ['<空或全非法>'])); continue
    seen = []
    for t in l2:
        if t not in seen: seen.append(t)
    l2 = seen
    conf[r.get('confidence', '?')] += 1
    if APPLY:
        l1 = []
        for t in l2:
            for x in m.get(t, []):
                if x not in l1: l1.append(x)
        e['tag_l2'] = l2; e['tags'] = l2; e['tag_l1'] = l1
    applied += 1

print('\n可落库:', applied, '| 未匹配:', len(unmatched), '| 非法/空:', len(invalid))
print('置信度:', dict(conf))
if unmatched: print('未匹配:', unmatched[:30])
if invalid:
    for nm, b in invalid[:30]: print('  非法/空:', nm, b)

if APPLY:
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy(base + 'all_enterprises.json', base + f'backups/all_enterprises_{ts}_pre_sdtag.json')
    json.dump(d, open(base + 'all_enterprises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\n[已写入] 落库 {applied} 家, backup ts={ts}')
else:
    print(f'\n[DRY-RUN] 若 --apply 将落库 {applied} 家')
