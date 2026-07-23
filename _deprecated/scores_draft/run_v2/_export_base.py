import json, os
m=json.load(open('manifest.json',encoding='utf-8'))
db=json.load(open('../../data/enterprise/all_enterprises.json',encoding='utf-8'))
by={e['serial']:e for e in db}
keys=['serial','name','name_cn','region','stage','founded','funding_latest','funding_total','investors',
      'payor_model','desc_cn','recommend','business_tags','tag_l1','tag_l2','highlights','events',
      'signal_strength','info_score','diff_score','copy_score','research_value','silver_verdict','silver_reason',
      'website_url','business_tags_role']
os.makedirs('base',exist_ok=True)
for it in m:
    b=it.get('batch')
    if isinstance(b,int) and 14<=b<=27:
        sers=it.get('serials',[])
        out=[]
        for s in sers:
            e=by.get(s)
            if e: out.append({k:e.get(k) for k in keys})
        fn=f'base/batch_{b:03d}_base.json'
        json.dump(out,open(fn,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        print(f'wrote {fn}: {len(out)} entries')
