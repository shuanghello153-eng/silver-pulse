# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, '.')
import check_single as C

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'batches_full', 'batch_patch_gap.json')
d = json.load(open(SRC, encoding='utf-8'))
by = {x['serial']: x for x in d}

# 载入当前RECS
import importlib.util
spec = importlib.util.spec_from_file_location('wr', os.path.join(HERE, 'write_recommends.py'))
wr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wr)
RECS = wr.RECS
FIXES = wr.FIXES

for serial, rec in RECS.items():
    e = dict(by[serial])
    e['recommend'] = rec
    fix = FIXES.get(serial)
    if fix:
        for k, v in fix.items():
            if v:
                e[k] = v
    errs = C.validate(e, skip={'R10'})
    fd = C._field_texts(e)
    # 只报与字段去重相关的
    rep = [x for x in errs if x.startswith('R-field-dedup')]
    if not rep:
        continue
    print('====', serial)
    for fname, ftext in fd:
        ov = C.lcs_len(rec, ftext)
        if ov >= 8:
            # 找到该子串
            a = rec
            b = ftext
            # 简单定位
            print(f'  [{fname}] LCS={ov}')
            # 打印b中包含的公共片段（取rec里最长匹配）
            # 用滑动窗口在b中找与rec公共最长
            best = ''
            for i in range(len(b)):
                for j in range(i+8, len(b)+1):
                    sub = b[i:j]
                    if sub in a and len(sub) > len(best):
                        best = sub
            print('     重叠片段:', best)
