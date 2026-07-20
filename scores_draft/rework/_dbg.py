# -*- coding: utf-8 -*-
import json, re, sys
sys.path.insert(0, ".")
from _gen_drafts_v3 import D, make_fact, variants, BY, SKIP, build_text
from check_single import validate, _field_texts, lcs_len

for serial in ['#1072', '#1077', '#1081', '#1099', '#1118', '#1220', '#1223', '#1224']:
    e = dict(BY.get(serial.lstrip('#'), {}))
    ok = False
    for i in range(6):
        t, vi = build_text(serial, i)
        if t:
            ee = dict(e); ee['recommend'] = t
            iss = validate(ee, skip=SKIP)
            if not iss:
                print(serial, 'PASS variant', vi)
                ok = True
                break
    if ok:
        continue
    t, vi = build_text(serial, 0)
    ee = dict(e); ee['recommend'] = t
    print(serial, 'ALL FAIL. v0 issues:', validate(ee, skip=SKIP))
    for fn, ft in _field_texts(e):
        ov = lcs_len(t, ft)
        if ov >= 8:
            print('   LCS', ov, 'with', fn)
