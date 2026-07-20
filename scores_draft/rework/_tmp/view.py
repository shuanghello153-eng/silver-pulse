import json, sys
out = json.load(open('scores_draft/rework/_tmp/extracted_120.json', encoding='utf-8'))
serials = sys.argv[1:]
if not serials:
    serials = list(out.keys())
for s in serials:
    if s not in out:
        print('=== %s NOT FOUND ===' % s)
        continue
    e = out[s]
    def g(k):
        return e.get(k, '')
    print('=' * 60)
    print('serial:', s, '| name:', g('name'), '| name_cn:', g('name_cn'))
    print('cat:', g('category_l1'), '/', g('category_l2'))
    print('tags:', g('tags'), '| tag_l1:', g('tag_l1'), '| tag_l2:', g('tag_l2'))
    print('founded:', g('founded'), '| funding_latest:', g('funding_latest'), '| funding_total:', g('funding_total'))
    print('investors:', g('investors'))
    print('desc_cn:', g('desc_cn'))
    print('business_model_cn:', g('business_model_cn'))
    print('website:', g('website_url'))
    print('payor:', g('payor_model'), '| silver_verdict:', g('silver_verdict'))
    print('OLD recommend:', g('recommend'))
