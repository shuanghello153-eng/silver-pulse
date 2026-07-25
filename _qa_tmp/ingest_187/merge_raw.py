# -*- coding: utf-8 -*-
"""汇总 handoff/enterprise_inbox/ 6 个批次为统一候选底稿 raw_candidates.json"""
import json, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

out = []
for f in sorted(glob.glob('handoff/enterprise_inbox/*.json')):
    batch = os.path.basename(f).split('_')[0]
    d = json.load(open(f, encoding='utf-8'))
    comps = d.get('companies') or d.get('enterprises') or []
    for c in comps:
        rec = {
            'batch': os.path.basename(f).replace('.json', ''),
            'name': (c.get('name') or '').strip(),
            'website': c.get('website') or c.get('url') or '',
            'country': c.get('country') or c.get('region') or '',
            'track': c.get('track') or c.get('赛道') or c.get('category_hint') or '',
            'business': c.get('business') or c.get('description') or '',
            'funding_raw': c.get('funding') or '',
            'fund': c.get('fund') or '',
            'status_raw': c.get('status') or '',
            'research_value_raw': c.get('research_value') or '',
            'relevance_raw': c.get('relevance') or '',
            'note_raw': c.get('note') or '',
            'ticker': c.get('证券代码') or '',
        }
        out.append(rec)

# 批内跨批次名称查重（信源AI说过零重叠，复核一遍）
seen = {}
dups = []
for i, r in enumerate(out):
    key = r['name'].lower().strip()
    if key in seen:
        dups.append((r['name'], r['batch'], out[seen[key]]['batch']))
    else:
        seen[key] = i

json.dump(out, open('_qa_tmp/ingest_187/raw_candidates.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('TOTAL:', len(out))
from collections import Counter
print(Counter(r['batch'] for r in out))
print('CROSS-BATCH NAME DUPS:', dups if dups else 'NONE')
empty_web = [r['name'] for r in out if not r['website']]
print('NO WEBSITE:', len(empty_web), empty_web[:10])
