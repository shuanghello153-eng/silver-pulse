# -*- coding: utf-8 -*-
"""从实时 fail_list.json 构建信号降序的重做队列 inbox2/，并生成 rework_reasons.json
（对盘上已存在草稿的 serial 标注缺失维度，供工人精准修正）。"""
import json, os, glob, importlib.util
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
INBOX2 = os.path.join(HERE, "inbox2")
os.makedirs(INBOX2, exist_ok=True)

spec = importlib.util.spec_from_file_location('val', os.path.join(HERE, 'validator.py'))
val = importlib.util.module_from_spec(spec); spec.loader.exec_module(val)
DIMS = {'信号': val.DIM_SIG, '信息': val.DIM_INFO, '差异': val.DIM_DIFF, '复制': val.DIM_COPY}

d = json.load(open(DB, encoding='utf-8'))
by = {int(str(e.get('serial', '#0')).lstrip('#')): e for e in d}
sig_of = lambda s: by[s].get('signal_strength') if isinstance(by.get(s, {}).get('signal_strength'), (int, float)) else 0

fails = json.load(open(os.path.join(HERE, 'fail_list.json'), encoding='utf-8'))['fails']
fser = [int(s) for s in fails.keys()]
fser.sort(key=lambda s: -sig_of(s))

# 批处理
B = 12
batches = [fser[i:i+B] for i in range(0, len(fser), B)]
for i, b in enumerate(batches):
    with open(os.path.join(INBOX2, f"batch_{i:03d}.txt"), 'w', encoding='utf-8') as f:
        for s in b:
            f.write(f"{s}\n")

# rework_reasons：盘上已有草稿的标注缺失维度
reasons = {}
for fp in glob.glob(os.path.join(HERE, 'draft_#*.json')):
    s = int(os.path.basename(fp).split('_#')[1].split('.')[0])  # draft_#XXXX.json
    dr = json.load(open(fp, encoding='utf-8'))
    r = dr.get('recommend')
    if isinstance(r, dict):
        txt = ' '.join(r.get(k, '') or '' for k in ('rec_v1', 'rec_v2', 'rec_v3'))
        missing = [n for n, kws in DIMS.items() if not any(k in txt for k in kws)]
        reasons[s] = {'missing_dims': missing, 'prev_issues': fails.get(str(s), [])}
json.dump(reasons, open(os.path.join(HERE, 'rework_reasons.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)

print(f"失败总数: {len(fser)} | 批次: {len(batches)} (每批{B})")
print(f"已标注重做原因(盘上有旧草稿): {len(reasons)} 家")
print("最高信号批次前5:", [(s, sig_of(s)) for s in fser[:5]])
print("最低信号批次后5:", [(s, sig_of(s)) for s in fser[-5:]])
