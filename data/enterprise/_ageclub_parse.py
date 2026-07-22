# -*- coding: utf-8 -*-
"""Parse AgeClub markdown, dedup, and match against all_enterprises.json."""
import json, re, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = r"G:/360MoveData/Users/shuan/Desktop/飞书-选题库-结构化整理/AgeClub企业分类整理_0721_v2-扣子.md"
DB = os.path.join(ROOT, "all_enterprises.json")

def norm(s):
    s = (s or "").lower().strip()
    for ch in ' \t（）()【】[]、，,。.:：;；/／\\-—_·•~～"\'\'':
        s = s.replace(ch, '')
    return s

# ---- parse markdown ----
text = open(SRC, encoding='utf-8').read()
lines = text.split('\n')

entries = []
section = None
section_order = []
for ln in lines:
    s = ln.strip()
    if not s:
        continue
    # section header: starts with ## and contains 适老/养老/银发/板块/补充 etc, but not 校验报告
    if s.startswith('## '):
        if '校验' in s or '分类统计' in s:
            section = None
            continue
        section = s[3:].strip()
        section_order.append(section)
        continue
    if s.startswith('# ') or s.startswith('>') or s.startswith('---') or s.startswith('*'):
        continue
    if s.startswith('共') and '家' in s:  # "共 10 家"
        continue
    # data line contains ｜
    if '｜' not in s:
        continue
    parts = s.split('｜')
    if len(parts) < 4:
        # maybe malformed; try to keep
        continue
    name = parts[0].strip()
    supply = parts[1].strip()
    demand = '｜'.join(parts[2:-1]).strip()
    date = parts[-1].strip()
    if not name:
        continue
    entries.append({
        'name': name,
        'supply': supply,
        'demand': demand,
        'date': date,
        'section': section,
    })

# dedup by norm(name)
seen = {}
deduped = []
for e in entries:
    k = norm(e['name'])
    if k in seen:
        # keep first; could merge supply but skip
        continue
    seen[k] = True
    deduped.append(e)

print("raw parsed lines:", len(entries))
print("after dedup:", len(deduped))

# ---- load DB ----
db = json.load(open(DB, encoding='utf-8'))
print("DB count:", len(db))

# build name map: norm -> list of existing entries
db_by_norm = {}
for ent in db:
    nm = ent.get('name','')
    nn = norm(nm)
    db_by_norm.setdefault(nn, []).append(ent)
    # also name_cn
    nc = ent.get('name_cn','')
    if nc:
        db_by_norm.setdefault(norm(nc), []).append(ent)

# exact match
exact = []
remaining = []
for e in deduped:
    k = norm(e['name'])
    if k in db_by_norm:
        matched = db_by_norm[k][0]
        exact.append({'ageclub': e, 'matched_name': matched.get('name'), 'matched_serial': matched.get('serial')})
    else:
        remaining.append(e)

print("exact match:", len(exact))
print("non-exact (candidates):", len(remaining))

# fuzzy match among remaining
import difflib
fuzzy = []
new_after_fuzzy = []
for e in remaining:
    k = norm(e['name'])
    best = None
    best_ratio = 0
    for nn, lst in db_by_norm.items():
        r = difflib.SequenceMatcher(None, k, nn).ratio()
        if r > best_ratio:
            best_ratio = r
            best = lst[0]
    e['_best_ratio'] = round(best_ratio, 3)
    e['_best_match'] = best.get('name') if best else None
    e['_best_serial'] = best.get('serial') if best else None
    if best_ratio >= 0.80:
        fuzzy.append(e)
    else:
        new_after_fuzzy.append(e)

print("fuzzy (>=0.80):", len(fuzzy))
print("clearly new (<0.80):", len(new_after_fuzzy))

# dump intermediate
out = {
    'entries': deduped,
    'exact': exact,
    'fuzzy': fuzzy,
    'new': new_after_fuzzy,
    'section_order': section_order,
}
with open(os.path.join(ROOT, '_ageclub_intermediate.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# print fuzzy list for review
print("\n=== FUZZY CANDIDATES ===")
for e in fuzzy:
    print(f"  {e['name']}  ~  {e['_best_match']}  ({e['_best_serial']})  r={e['_best_ratio']}")

# print sections distribution
from collections import Counter
sec_count = Counter(e['section'] for e in deduped)
print("\n=== SECTION DISTRIBUTION ===")
for s, c in sec_count.items():
    print(f"  {c:3d}  {s}")
