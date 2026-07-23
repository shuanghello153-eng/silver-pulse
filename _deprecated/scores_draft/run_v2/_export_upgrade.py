import json
keys=['serial','name','name_cn','region','stage','founded','funding_latest','funding_total','investors',
      'payor_model','desc_cn','recommend','business_tags','tag_l1','tag_l2','highlights','events',
      'signal_strength','info_score','diff_score','copy_score','research_value','silver_verdict','silver_reason',
      'website_url','business_tags_role']
for b in range(3,14):
    fn=f'out/batch_{b:03d}_out.json'
    try:
        d=json.load(open(fn,encoding='utf-8'))
        ents=d.get('enterprises',d)
        out=[{k:e.get(k) for k in keys} for e in ents]
        ufn=f'base/batch_{b:03d}_upgrade.json'
        json.dump(out,open(ufn,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        print(f'{ufn}: {len(out)} entries')
    except Exception as ex:
        print(f'{fn}: MISSING ({ex})')
