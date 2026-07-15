# -*- coding: utf-8 -*-
"""单标签企业聚类富集：补一个≠现标签的第二标签（横向属性）。跳居家护理。"""
import json, re
AE='data/enterprise/all_enterprises.json'
L2L1='data/enterprise/_l2_l1.json'
data=json.load(open(AE,encoding='utf-8'))
l2l1=json.load(open(L2L1,encoding='utf-8'))
def l1of(t):
    v=l2l1.get(t)
    return v if isinstance(v,list) else ([v] if isinstance(v,str) else [])

# 横向属性规则（高精度，跳过居家护理）
RULES=[
 ('SaaS',     re.compile(r'saas|软件|云平台|数字化平台|管理系统|platform software',re.I)),
 ('AI',       re.compile(r'人工智能|算法|机器学习|大模型|gpt|computer vision|ai驱动|ai技术|ai算法',re.I)),
 ('远程医疗',  re.compile(r'远程|telehealth|telemedicine|线上问诊|virtual care|线上医疗',re.I)),
 ('保险',      re.compile(r'保险|insur|理赔|长护险',re.I)),
 ('智能硬件',  re.compile(r'硬件|传感器|可穿戴|wearable|智能设备|sensor|智能硬件',re.I)),
 ('跌倒监测',  re.compile(r'跌倒|防跌|fall detection|fall risk',re.I)),
 ('慢病管理',  re.compile(r'慢病|慢性病|chronic disease|chronic condition',re.I)),
 ('认知训练',  re.compile(r'认知训练|脑力|认知游戏|brain training|cognitive game|记忆训练',re.I)),
 ('康复器械',  re.compile(r'康复器械|康复设备|康复机器人|康复辅具|外骨骼|理疗设备|rehab equipment|rehab device|rehabilitation device',re.I)),
 ('陪伴社交',  re.compile(r'陪伴|社交|社群|social platform|social network',re.I)),
]
def text(e):
    return ' '.join(str(e.get(k) or '') for k in ['name','name_cn','desc_cn','description','business_model','business_model_cn','category_l2'])

enriched=0
for e in data:
    l2=list(e.get('tag_l2') or [])
    if len(l2)!=1: continue
    cur=l2[0]
    t=text(e)
    for tag,rgx in RULES:
        if tag==cur: continue
        if rgx.search(t):
            e['tag_l2']=l2+[tag]
            nl1=list(e.get('tag_l1') or [])
            for x in l1of(tag):
                if x not in nl1: nl1.append(x)
            e['tag_l1']=nl1
            enriched+=1
            break
single_after=sum(1 for e in data if len(e.get('tag_l2') or [])==1)
print(f"本次富集补标: {enriched} 家")
print(f"单标签企业: {len([e for e in data if len(e.get('tag_l2') or [])==1])} -> {single_after}")
json.dump(data,open(AE,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print("已写回",AE)
PY=''
