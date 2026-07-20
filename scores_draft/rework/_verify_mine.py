import json, re, glob
PAYOR_VOCAB=["个人自费","个人自费+政府补贴","个人自费+长护险","个人自费+医保","B端机构采购","B端机构采购+政府付费","B端机构采购+政府/商保支付","政府医保/商保支付","混合支付","不适用（投资机构）","未搜到"]
FORBIDDEN=["复制需结合本地资源","国内宜学其思路而非形态","轻模式易复制，国内创业者可直接借鉴落地","切入XX赛道"]
MY=["#0493","#0565","#0855","#1152","#0602","#0398","#0593","#0594","#0595","#0850","#0012","#0461","#0470","#0949","#0954","#0009","#0011","#0020","#0030","#0038","#0070","#0082","#0086","#0091","#0100","#0129","#0227","#0392","#0394","#0397","#0401","#0436","#0447","#0475","#0495","#0497"]
def overlap(a,b):
    sa,sb=list(a),list(b); common=0; sbc=sb[:]
    for ch in sa:
        if ch in sbc: common+=1; sbc.remove(ch)
    return common/max(len(sa),len(sb)) if max(len(sa),len(sb)) else 0
fails={}
for s in MY:
    f='scores_draft/rework/draft_%s.json'%s
    d=json.load(open(f,encoding='utf-8')); prob=[]
    rec=d.get('recommend') or {}
    v1,v2,v3=rec.get('rec_v1'),rec.get('rec_v2'),rec.get('rec_v3')
    if not all(isinstance(x,str) and x for x in [v1,v2,v3]): prob.append('rec_missing')
    else:
        for v in [v1,v2,v3]:
            if not (40<=len(v)<=90): prob.append('len:%d'%len(v))
        for nm,o in [('o12',overlap(v1,v2)),('o13',overlap(v1,v3)),('o23',overlap(v2,v3))]:
            if o>=0.5: prob.append('%s=%.2f'%(nm,o))
        for v in [v1,v2,v3]:
            for ff in FORBIDDEN:
                if ff in v: prob.append('forbidden')
    desc=d.get('desc_cn') or ''
    if len(desc)<80: prob.append('desc_len:%d'%len(desc))
    if re.match(r'^(是一家|致力于|专注于)',desc): prob.append('desc_start_bad')
    if re.search(r'成立于\d{4}年',desc): prob.append('desc_founded')
    sr=d.get('silver_reason') or ''
    if len(sr)<30: prob.append('silver_len:%d'%len(sr))
    if d.get('payor_model') not in PAYOR_VOCAB: prob.append('payor_not_vocab')
    if d.get('update_time')!='2026-07-18': prob.append('update_time')
    if d.get('serial')!=s: prob.append('serial_mismatch')
    if prob: fails[s]=prob
print('verified',len(MY),'drafts; failures:',len(fails))
for k,v in fails.items(): print(' ',k,'=>',v)
print('ALL PASS' if not fails else 'HAS FAILURES')
