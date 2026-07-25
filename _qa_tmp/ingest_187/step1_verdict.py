# -*- coding: utf-8 -*-
"""步骤1·阶段二 AI 二筛裁决落盘 + 跨批次重复合并 → screened_candidates.json"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

cands = json.load(open('_qa_tmp/ingest_187/raw_candidates.json', encoding='utf-8'))

# AI 二筛裁决（企业库AI 2026-07-26，依据手册 §5.1 阶段二三条准入 + 从严原则）
PENDING = {
    'Transcarent': '自保险雇主健康平台，主用户为在职员工，非银发人群/服务方，判泛医疗',
    'Higi': '社区健康筛查站面向全人群，无老年专属指向',
    'Payactiv': '通用按需发薪（EWA）服务全行业，护理工只是客群之一，判泛金融',
    'Ellipsis Health': '通用语音精神健康筛查，全年龄，无老年专属产品线',
    'Vulcan Augmetics': '肌电假肢面向全年龄残障人群，非老年专属，判泛康复',
}

# 跨批次重复：保留信息更全的一条，note 合并另一条批次来源
DUP_KEEP = {  # name -> 保留哪个批次
    'Sweetch': 'W5以色列_BM日本_企业26家_2026-07-25',      # W5 有更全描述
    'Aidaly': 'W13_B_企业_2026-07-25',                      # W13_B business 更详细
    'Retirable': 'W13_B_企业_2026-07-25',
    'Rosarium Health': 'W13_B_企业_2026-07-25',
    'Homage': 'W11_企业49条_2026-07-25',                     # W11 verified，W9-10 是 lead_unverified
}

seen_dup = {}
out, dropped_dup, pending = [], [], []
for c in cands:
    n = c['name']
    if n in DUP_KEEP:
        if c['batch'] != DUP_KEEP[n]:
            dropped_dup.append((n, c['batch']))
            # 把被丢弃条目的补充信息挂到保留条上（稍后合并）
            seen_dup.setdefault(n, []).append(c)
            continue
    if n in PENDING:
        c['_verdict'] = 'pending_xiaoshuang'
        c['_verdict_reason'] = PENDING[n]
        pending.append(c)
        continue
    c['_verdict'] = 'keep'
    out.append(c)

# 合并重复条目的补充信息
for c in out:
    extras = seen_dup.get(c['name'])
    if extras:
        for e in extras:
            for k in ['funding_raw', 'fund', 'business', 'research_value_raw', 'note_raw']:
                if e.get(k) and e[k] not in (c.get(k) or ''):
                    c[k] = (c.get(k) or '') + (' ||另批(' + e['batch'][:8] + '): ' + str(e[k]) if c.get(k) else str(e[k]))
        c['_merged_from'] = [e['batch'] for e in extras]

json.dump(out, open('_qa_tmp/ingest_187/screened_candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(pending, open('_qa_tmp/ingest_187/pending_xiaoshuang.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('KEEP:', len(out), 'PENDING:', len(pending), 'DUP_DROPPED:', len(dropped_dup))
for n, b in dropped_dup: print('  dup dropped:', n, '<-', b)
