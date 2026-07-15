# -*- coding: utf-8 -*-
"""居家护理 同类词净化 + 挂标企业重分类（修正版：L1 用修好的映射重算，不拆字）"""
import json

AE = 'data/enterprise/all_enterprises.json'
L2L1 = 'data/enterprise/_l2_l1.json'

data = json.load(open(AE, encoding='utf-8'))
l2l1 = json.load(open(L2L1, encoding='utf-8'))

# 1) 同类词净化
syn = json.load(open('data/enterprise/tag_synonyms.json', encoding='utf-8'))
KEEP_SYN = {
 '上门照护','上门照护平台','居家/上门护理','居家护理','居家护理服务','居家照护',
 '家庭护理','家庭护理/个人护理','居家护理/家政服务','护理服务','老年护理','长期护理','养老护理'
}
if '居家护理' in syn:
    before = syn['居家护理']
    syn['居家护理'] = [s for s in before if s in KEEP_SYN]
    print(f"同类词 居家护理: {len(before)} -> {len(syn['居家护理'])}, 移除 {len(before)-len(syn['居家护理'])}")
json.dump(syn, open('data/enterprise/tag_synonyms.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)

# 2) 重分类
REMOVE = {
 '如身机器人','老友记','金牌护士','银汤屋','阿福医疗','青鸟软通','天一智慧','厚福医疗',
 'Vesta Healthcare','Vytalize Health','A Place for Mom','Lively','IAC','Clara Home Care',
 'Family First','GeoH','HealthArc','HealthSnap','Helper bees','Lottie','MedArrive',
 'Monogram Health','Sensi.AI','Somatus','Ōmcare','Voize','Nila','NurseBuddy','Nourish Care',
 'eCaring','Aline (Sherpa)','Smartcare','The Helper Bees','麦迪科技','欧圣电气(伊利诺)',
 '中科行智','百善九号','AvevoRx','Zingage','Gladys','WellSky','AlayaCare','ClearCare',
 'Medflyt','CareJoy','Jubo'
}
OVERRIDE = {
 'IAC':     (['养老信息平台'], ['产业资本']),
 'Lively':  (['智能硬件'], ['智能科技']),
 'Voize':   (['AI'], ['智能科技']),
}

def rel1(l2):
    out=[]
    for t in l2:
        v=l2l1.get(t)
        if isinstance(v,list): out+=v
        elif isinstance(v,str): out+=[v]
    return list(dict.fromkeys(out))

by_name = {e['name']: e for e in data}
changed=[]
for name in REMOVE:
    e = by_name.get(name)
    if not e or '居家护理' not in (e.get('tag_l2') or []):
        continue
    if name in OVERRIDE:
        nl2, nl1 = OVERRIDE[name]
    else:
        nl2 = [t for t in (e.get('tag_l2') or []) if t!='居家护理']
        nl1 = rel1(nl2)
        if not nl1:  # 兜底：保留原L1（去掉居家护理）
            nl1 = [x for x in (e.get('tag_l1') or []) if x!='居家护理']
    e['tag_l2']=nl2; e['tag_l1']=nl1
    changed.append((name, nl2, nl1))

print(f"重分类 {len(changed)} 家")
for n,l2,l1 in changed:
    print(f"  {n}: L2={l2} L1={l1}")

hc=[e['name'] for e in data if '居家护理' in (e.get('tag_l2') or [])]
print(f"\n居家护理 剩余: {len(hc)}")
# 损坏检查
bad=[e['name'] for e in data if any(len(x)==1 for x in (e.get('tag_l1') or []))]
print("单字L1损坏企业:", len(bad))
json.dump(data, open(AE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print("已写回", AE)
