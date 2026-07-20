# -*- coding: utf-8 -*-
import json, sys
b = sys.argv[1]
d = json.load(open('batches_full/'+b, encoding='utf-8'))
for e in d:
    print('='*70)
    print('SERIAL:', e.get('serial'), '| NAME:', e.get('name_cn') or e.get('name'))
    print('TAG:', e.get('tag_l1'), e.get('tag_l2'))
    print('PAYOR:', e.get('payor_model'))
    print('DESC_CN:', e.get('desc_cn'))
    print('SILVER:', e.get('silver_reason'))
    fl = e.get('funding_latest') or {}
    ft = e.get('funding_total') or {}
    print('FUND_LATEST:', fl.get('display') if isinstance(fl,dict) else fl)
    print('FUND_TOTAL:', ft.get('display') if isinstance(ft,dict) else ft)
    hl = e.get('highlights') or []
    for i,h in enumerate(hl):
        print('  HL%d:'%i, h)
    print('SOURCE_DESC(EN):', (e.get('description') or '')[:300])
