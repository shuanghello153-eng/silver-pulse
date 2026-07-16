#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V21 结构调整（原子）：
1) 新增二级「长寿抗衰」→ 一级 消费品
2) 合并 远程监护 → 远程护理（养老服务内）
3) 合并 垂直电商 → 电商（消费品内）
同步 all_enterprises.json / _l2_l1.json / tag_synonyms.json / config.py(ENTERPRISE_CATEGORIES 重建)
"""
import json, re, os, shutil, ast, datetime

base = 'data/enterprise/'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
os.makedirs(base + 'backups', exist_ok=True)
shutil.copy(base + 'all_enterprises.json', base + f'backups/all_enterprises_{ts}_pre_v21.json')
shutil.copy('config.py', base + f'backups/config_{ts}_pre_v21.py')

d = json.load(open(base + 'all_enterprises.json', encoding='utf-8'))
m = json.load(open(base + '_l2_l1.json', encoding='utf-8'))
syn = json.load(open(base + 'tag_synonyms.json', encoding='utf-8'))

# ---------- 1. 映射表 ----------
m['长寿抗衰'] = ['消费品']
m.pop('远程监护', None)
m.pop('垂直电商', None)

# ---------- 2. 同类词 ----------
def add_syn(canon, *words):
    lst = syn.get(canon, [])
    for w in words:
        if w != canon and w not in lst:
            lst.append(w)
    syn[canon] = lst
add_syn('远程护理', '远程监护')
add_syn('电商', '垂直电商')
add_syn('长寿抗衰', '抗衰', '长寿', '抗老', '逆龄', 'longevity', 'anti-aging', '抗衰老', '长寿医学')
syn.pop('远程监护', None)
syn.pop('垂直电商', None)

# ---------- 3. 数据变更 ----------
REPLACE = {'远程监护': '远程护理', '垂直电商': '电商'}
LONG_DRUG = {'NewLimit', 'Jocasta Neuroscience', 'BioAge Labs', 'Unity Biotechnology',
             'Retro Biosciences', 'Life Biosciences', 'Avaí Bio', 'Seraphina Therapeutics (fatty15)'}
LONG_ADD = {'OneSkin', '卡唯朵', '不老谜语', '森美', 'Generation Lab', 'InsideTracker',
            'Function Health', 'Fountain Life', 'Biopeak', 'Blue Longevity Clinic'}

cnt_merge = 0
cnt_long = 0
for e in d:
    l2 = e.get('tag_l2') or []
    nl2 = []
    for t in l2:
        t2 = REPLACE.get(t, t)
        if t2 != t:
            cnt_merge += 1
        if t2 not in nl2:
            nl2.append(t2)
    nm = e.get('name', '')
    if nm in LONG_DRUG:
        nl2 = [('长寿抗衰' if t == '药品' else t) for t in nl2]
        if '长寿抗衰' not in nl2:
            nl2.append('长寿抗衰')
        cnt_long += 1
    if nm in LONG_ADD:
        if '长寿抗衰' not in nl2:
            nl2.append('长寿抗衰')
        cnt_long += 1
    seen = []
    for t in nl2:
        if t not in seen:
            seen.append(t)
    e['tag_l2'] = seen
    e['tags'] = seen
    l1 = []
    for t in seen:
        for x in m.get(t, []):
            if x not in l1:
                l1.append(x)
    e['tag_l1'] = l1

# ---------- 写回 ----------
json.dump(d, open(base + 'all_enterprises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump(m, open(base + '_l2_l1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump(syn, open(base + 'tag_synonyms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- 重建 config.ENTERPRISE_CATEGORIES ----------
L1_ORDER = ['养老服务', '康复辅具', '消费品', '文娱社交', '食品营养', '行业服务', '金融保险', '投资机构']
by_l1 = {x: [] for x in L1_ORDER}
for l2, l1s in m.items():
    for l1 in l1s:
        if l1 in by_l1 and l2 not in by_l1[l1]:
            by_l1[l1].append(l2)
for k in by_l1:
    by_l1[k] = sorted(by_l1[k])
lines = ['ENTERPRISE_CATEGORIES = {']
for l1 in L1_ORDER:
    lines.append(f'  "{l1}": [')
    for l2 in by_l1[l1]:
        lines.append(f'    "{l2}",')
    lines.append('  ],')
lines.append('}')
newblock = '\n'.join(lines)
src = open('config.py', encoding='utf-8').read()
src2 = re.sub(r'ENTERPRISE_CATEGORIES\s*=\s*\{.*?\n\}', newblock, src, count=1, flags=re.S)
ast.parse(src2)
open('config.py', 'w', encoding='utf-8').write(src2)

# ---------- 汇总 ----------
from collections import Counter
l2c = Counter()
for e in d:
    for t in e.get('tag_l2') or []:
        l2c[t] += 1
print('合并改写次数:', cnt_merge, '| 长寿抗衰赋值:', cnt_long)
print('远程护理:', l2c.get('远程护理'), '| 远程监护(应无):', l2c.get('远程监护'))
print('电商:', l2c.get('电商'), '| 垂直电商(应无):', l2c.get('垂直电商'))
print('长寿抗衰:', l2c.get('长寿抗衰'))
print('二级总数:', len(l2c), '| 一级映射条目:', len(m))
print('config ENTERPRISE_CATEGORIES 各一级二级数:', {k: len(v) for k, v in by_l1.items()})
print('backup ts:', ts)
