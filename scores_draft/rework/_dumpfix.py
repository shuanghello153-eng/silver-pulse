import json
d=json.load(open('batches_full/batch_patch_gap.json',encoding='utf-8'))
need=['#0638','#0743','#0965','#1335','#1139','#0003','#0083','#0085','#0300','#0716','#0772','#0463','#0474','#0972','#1312','#1334','#0016','#0068','#0175','#0366','#0620','#0629','#0673','#0679','#0684','#0692','#0700','#0739','#0742','#0755','#0763','#0764','#0775','#1348','#1467','#1514','#0672','#0851','#1038','#0919','#0333','#0509','#0806']
by={x['serial']:x for x in d}
for s in need:
    e=by[s]
    print("="*70)
    print("SERIAL",s,"| name",e.get('name'),"| tags",e.get('tag_l1'),e.get('tag_l2'))
    print("desc_cn:",e.get('desc_cn'))
    print("description:",e.get('description'))
    print("silver_reason:",e.get('silver_reason'))
    print("highlights:",e.get('highlights'))
    print("funding_latest:",e.get('funding_latest'))
    print("funding_total:",e.get('funding_total'))
