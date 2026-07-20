import json
DB = 'G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json'
data = json.load(open(DB, encoding='utf-8'))
by = {}
for e in data:
    by[str(e.get('serial'))] = e
serials = ['#1105', '#1112', '#1116', '#1117', '#1118', '#1119', '#1120',
           '#1121', '#1122', '#1124', '#1125', '#1126']
for s in serials:
    e = by.get(s)
    if not e:
        print('=== ', s, ' MISSING ===')
        continue
    print('=== ', s, ' name=', e.get('name'), ' | region=', e.get('region'),
          ' | l1=', e.get('tag_l1'), ' | l2=', e.get('tag_l2'))
    print('  desc_cn:', str(e.get('desc_cn'))[:220])
    print('  silver_reason:', str(e.get('silver_reason'))[:180])
    print('  funding_latest:', e.get('funding_latest'), ' | funding_total:', e.get('funding_total'))
    print('  payor_model:', e.get('payor_model'))
    print('  highlights:', e.get('highlights'))
