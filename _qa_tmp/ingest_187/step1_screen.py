# -*- coding: utf-8 -*-
"""步骤1·阶段一：强词初筛（复用 config.SILVER_STRONG_KEYWORDS，与 relevance_screener 同源逻辑）
对每个候选拼接 name/track/business/note 文本，命中强词 -> 进 AI 二筛；未命中 -> 列出待 AI 特殊理由判断。
"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import config

strong = [k.lower() for k in config.SILVER_STRONG_KEYWORDS]
cands = json.load(open('_qa_tmp/ingest_187/raw_candidates.json', encoding='utf-8'))

hit, miss = [], []
for c in cands:
    text = ' '.join([c['name'], c['track'], c['business'], c['note_raw'],
                     c['research_value_raw'], c['relevance_raw']]).lower()
    hits = [k for k in strong if k in text]
    c['_kw_hits'] = hits[:6]
    (hit if hits else miss).append(c)

print('HIT:', len(hit), ' MISS:', len(miss))
print('--- 未命中强词（需 AI 特殊理由判断）---')
for c in miss:
    print(f"[{c['batch'][:6]}] {c['name']} | {c['track']} | {c['business'][:80]}")
json.dump(cands, open('_qa_tmp/ingest_187/raw_candidates.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
