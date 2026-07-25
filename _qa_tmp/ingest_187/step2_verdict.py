# -*- coding: utf-8 -*-
"""步骤2裁决落盘：37 库内重复剔除（6 带增量）、3 保留、3 组批内合并 → deduped_candidates.json"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

cands = json.load(open('_qa_tmp/ingest_187/screened_candidates.json', encoding='utf-8'))

# 与库内重复 → 跳过（AI 裁决 2026-07-26）
LIB_DUPS = {
    'Cala Health': '#0560', 'Alignment Healthcare': '#1243', 'SafelyYou': '#0835',
    'Homage': '#0993', 'Mable': '#0772', 'Vayyar Care (Vayyar Imaging)': '#0895',
    'OrCam': '#0813', 'TytoCare': '#1285', 'Intuition Robotics': '#1041',
    'Uniper': '#1046', 'Voiceitt': '#0906', 'MyndYou': '#1337',
    'August Health': '#0559', 'Bold': '#0494', 'Butlr': '#1268', 'Carewell': '#0500',
    'Empathy': '#0467', 'Livongo': '#0522', 'MedArrive': '#0776', 'Papa': '#0564',
    'CareLinx': '#0499', 'Third Eye Health': '#1348', 'True Link Financial': '#0480',
    'Vesta Healthcare': '#0481', 'Vynca Care': '#0553', 'Wellthy': '#0483',
    'K4Connect': '#0750', 'Season Health': '#0841', 'Trust & Will': '#1292',
    'Aloe Care Health': '#1003', 'Linus Health': '#0765', 'Navel Robotics': '#0795',
    'Steadiwear': '#0868', 'Caredoc 케어닥': '#0654', 'CarePredict': '#0464',
    'Nobi': '#0804', 'Cera': '#1168',
}

# 批内同企业合并：删除方 -> 保留方
INTERNAL_MERGE = {
    'Quo Labs': 'Sam (Quo Labs)',          # W9-W10 條并入 W13_B
    'Helpany': 'Helpany (Paul)',            # W9-W10 lead 并入 W13_B
    'TSUKUI ツクイ': 'ツクイ（Tsukui）',    # W5 并入 W12（W12 校验更全，有退市/私有化信息）
}

# 库内记录增量（步骤6合并时写入，合并前不动全库）
LIB_INCREMENTS = [
    {'serial': '#0895', 'name': 'Vayyar', 'add': {'funding_note': '母公司累计>$300M（2022 $108M Series E，估值>$10亿）——来自W5批次'}},
    {'serial': '#1337', 'name': 'MyndYou', 'add': {'note': '已并入 Arbiter（AgeTech 并购案例）——来自W5批次'}},
    {'serial': '#0481', 'name': 'Vesta Healthcare', 'add': {'note': '信源AI W10 标记 verified_ceased，疑似已停业，待核'}},
    {'serial': '#0772', 'name': 'Mable', 'add': {'website_url': 'https://www.mable.com.au', 'note': '原 mable.com 实测为域名停放页，修正为 .com.au（信源AI W13_B 实测）'}},
    {'serial': '#0795', 'name': 'Navel', 'add': {'website_url': 'https://navelrobotics.com', 'note': '原 navel.com 非该公司官网，修正'}},
    {'serial': '#0993', 'name': 'Homage', 'add': {'note': '与 Infocom 合作拓展日本市场（W9-W10 增量）'}},
]

# 库内存量自重复（本轮不动，登记待处理）
LIB_INTERNAL_DUPS = [
    ['#1046 Uniper Care', '#1184 Uniper', '同为 unipercare.com'],
    ['#0494 Bold', '#0611 Age Bold', '同为 agebold.com'],
    ['#0553 Vynca', '#0910 VyncaCare', '同公司 vynca.com/vyncacare.com'],
    ['#0466 Cera Care', '#1168 Cera', '同公司英国 Cera'],
]

merged_extra = {}
out, dropped = [], []
for c in cands:
    n = c['name']
    if n in LIB_DUPS:
        dropped.append((n, LIB_DUPS[n]))
        continue
    if n in INTERNAL_MERGE:
        merged_extra.setdefault(INTERNAL_MERGE[n], []).append(c)
        continue
    out.append(c)

for c in out:
    extras = merged_extra.get(c['name'])
    if extras:
        for e in extras:
            for k in ['funding_raw', 'fund', 'business', 'research_value_raw', 'note_raw', 'track']:
                if e.get(k) and str(e[k]) not in str(c.get(k) or ''):
                    c[k] = ((c.get(k) or '') + ' ||并(' + e['batch'][:7] + '): ' + str(e[k])).strip(' |')
        c['_merged_internal'] = [e['batch'] for e in extras]

json.dump(out, open('_qa_tmp/ingest_187/deduped_candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'lib_increments': LIB_INCREMENTS, 'lib_internal_dups': LIB_INTERNAL_DUPS,
           'lib_dup_dropped': dropped},
          open('_qa_tmp/ingest_187/step2_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('NET NEW:', len(out), '| LIB DUP DROPPED:', len(dropped), '| INTERNAL MERGED:', len(merged_extra))
