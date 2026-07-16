# -*- coding: utf-8 -*-
import json

IN = '_v12_input_TD4.json'
OUT = '_v12_split_TD4.json'

d = json.load(open(IN, encoding='utf-8'))
BIG = ['临终关怀','女性健康','认知症','个人护理','陪伴机器人','护理平台','养老金融','跌倒监测']

# collect in-scope keys and a name->key map for validation
in_keys = {}
key_to_names = {}
for tag in BIG:
    for r in d[tag]:
        k = r['name_cn'] if r.get('name_cn') else r['name']
        in_keys[k] = in_keys.get(k, 0) + 1
        key_to_names.setdefault(k, r['name'])

# ---------------------------------------------------------------
# REASSIGN: key -> list of SPECIFIC L2 tags (no big-tag names)
# ---------------------------------------------------------------
REASSIGN = {
 # ---- 临终关怀 (29) ----
 '慈康生命': ['专业护理'],
 'Empathy': ['金融服务'],
 'Cake': ['金融服务'],
 'Everplans': ['金融服务'],
 'FreeWill': ['金融服务'],
 'GoodTrust': ['金融服务'],
 'Iris Healthcare': ['专业护理'],
 'Vynca': ['金融服务'],
 'After.com': ['殡葬服务'],
 'Compassus': ['专业护理'],
 'Foundation Partners Group': ['殡葬服务'],
 'LifeAfterMe': ['金融服务'],
 'Luminary': ['金融理财'],
 'SCI (Service Corporation International)': ['殡葬服务'],
 'Vitas': ['专业护理'],
 'VyncaCare': ['专业护理'],
 '镰仓新书': ['殡葬服务'],
 'Aveanna Healthcare': ['专业护理'],
 'The Pennant Group': ['专业护理'],
 'Enhabit': ['专业护理'],
 'Artifcts': ['金融理财'],
 'White Orchid Hospice': ['专业护理'],
 'HealthFlex Hospice': ['专业护理'],
 'The Care Team': ['专业护理'],
 'VitalCaring': ['专业护理'],
 'Enzo Health': ['AI医疗'],
 'IO Health': ['AI医疗'],
 'Solace': ['金融理财','陪诊'],
 'Trust & Will': ['金融理财'],

 # ---- 女性健康 (29) ----
 'Sword Health': ['康复医疗'],
 'Pivotal Ventures': ['金融理财'],
 'Alloy': ['更年期'],
 'Bloom Nutrition': ['消费品'],
 'Domma': ['更年期'],
 'Elektra Health': ['更年期'],
 'Evernow': ['更年期'],
 'Gennev': ['更年期'],
 'Grace': ['尿失禁'],
 'Hazel': ['尿失禁','纸尿裤'],
 'Maven Clinic': ['更年期','诊所'],
 'Menolabs': ['更年期'],
 'Midi Health': ['更年期','诊所'],
 'Omena': ['诊所'],
 'Pearl Health': ['更年期'],
 'Stripes Beauty': ['消费品','更年期'],
 'Tia': ['诊所'],
 'Unfabled': ['电商'],
 'Vi Health': ['更年期'],
 'Wile': ['更年期'],
 '八睡眠': ['智能硬件','更年期'],
 'Axena Health': ['康复医疗'],
 'Xella Health': ['体检筛查'],
 'Herself Health': ['诊所'],
 'Uresta': ['尿失禁'],
 'Peppy': ['更年期'],
 'Stella': ['更年期'],
 'Lotus': ['更年期'],
 '伟思医疗': ['康复器械'],

 # ---- 认知症 (27) ----
 '博斯腾': ['认知训练'],
 'AgenT': ['体检筛查'],
 'Alz You Need': ['护理人力'],
 '哺恩养老': ['养老机构'],
 'Actif': ['认知训练'],
 'BrainCheck': ['认知训练'],
 'Carl': ['智能硬件'],
 'Isaac Health': ['认知训练'],
 'Jellydrops': ['消费品'],
 'Linus Health': ['体检筛查'],
 'NeuroNation': ['认知训练'],
 'RETISPEC': ['体检筛查'],
 'Rune Labs': ['AI医疗'],
 'SiftWell Analytics': ['AI医疗'],
 'Thinkie': ['认知训练'],
 'Wesper': ['健康监测'],
 'Zen Sleep': ['心理健康'],
 'Zinnia': ['文娱'],
 'Ivory': ['体检筛查'],
 'Synchron': ['康复医疗'],
 'Leal Therapeutics': ['药品'],
 'Mindr': ['认知训练'],
 'Ceresti': ['护理人力'],
 'Sodalis Senior Living': ['养老机构'],
 '博芮健': ['药品'],
 'CogniFit': ['认知训练'],
 'Neurotrack': ['体检筛查'],

 # ---- 个人护理 (28) ----
 '可靠股份': ['纸尿裤'],
 '上海剪爱': ['上门'],
 '中顺洁柔': ['日用'],
 '可靠': ['纸尿裤'],
 '多呵': ['消费品'],
 '天空树': ['消费品'],
 '彭世': ['家政生活服务'],
 '昱芝夕': ['消费品'],
 '染博士': ['消费品'],
 '海森林': ['假发'],
 '瑞贝卡': ['假发'],
 '章华': ['消费品'],
 '韩愢': ['消费品'],
 '韩金靓': ['消费品'],
 '令羽(肤恩)': ['消费品'],
 '瑞邦生物': ['假发'],
 '彭世修脚': ['家政生活服务'],
 '点可科技': ['智能硬件'],
 '大耳马医学': ['健康监测'],
 'OXO': ['日用'],
 'Nobel Hygiene': ['纸尿裤'],
 'OneSkin': ['长寿科技'],
 '可氏利夫': ['消费品'],
 '乐霂': ['消费品'],
 '韩束': ['消费品'],
 '珀莱雅': ['消费品'],
 '卡唯朵': ['消费品'],
 '不老谜语': ['消费品'],

 # ---- 陪伴机器人 (28) ----
 'Ageless Innovation': ['机器人'],
 'Tombot': ['机器人'],
 'Dorvie': ['家政生活服务'],
 'ElliQ': ['机器人'],
 'Embodied': ['机器人'],
 'Help-full': ['家政生活服务'],
 'joyforall': ['机器人'],
 'Meela': ['文娱'],
 'Naborforce': ['家政生活服务'],
 'Navel': ['机器人'],
 'Pallie AI': ['文娱'],
 'Pyx Health': ['文娱'],
 'Senpai': ['文娱'],
 'NewDays': ['认知训练'],
 'JOY FOR ALL': ['机器人'],
 'Intuition Robotics': ['机器人'],
 'Uniper Care': ['社区'],
 '玄源科技': ['机器人'],
 '江苏艾雨文承': ['机器人'],
 '大象机器人': ['机器人'],
 '萌友智能': ['机器人'],
 '中科源码': ['机器人'],
 '森丽康科技': ['机器人'],
 '分音塔科技': ['智能硬件'],
 'Andromeda Robotics': ['机器人'],
 'Sukoon Unlimited': ['社区'],
 'LOVOT': ['机器人'],
 'Lola Cares': ['文娱'],

 # ---- 护理平台 (28) ----
 'CareLinx': ['护理人力'],
 'Care Continuity': ['专业护理'],
 'CareGuide': ['护理人力'],
 'Carl': ['智能硬件'],
 'Clara Home Care': ['护理人力'],
 'GeoH': ['专业护理'],
 'In-House Health': ['护理人力'],
 'Kismet': ['护理人力'],
 'Koda Health': ['专业护理'],
 'Mable': ['护理人力'],
 'Marta': ['护理人力'],
 'Sensi.AI': ['健康监测'],
 'Swift Medical': ['AI医疗'],
 'VyncaCare': ['专业护理'],
 'Watershed Health': ['专业护理'],
 'Yurtle': ['保险科技'],
 'Homage': ['上门'],
 'Elder': ['护理人力'],
 'Cuideo': ['护理人力'],
 'Empassion Health': ['专业护理'],
 'CareConnectMD': ['专业护理'],
 'Hera': ['专业护理'],
 'LegUp': ['护理人力'],
 'SilverAssist': ['咨询研究'],
 'Age Care Labs': ['上门'],
 'Medflyt': ['护理人力'],
 'SuperCarers': ['护理人力'],
 'Cuidum': ['护理人力'],

 # ---- 养老金融 (26) ----
 'SageWell': ['适老化'],
 '银行＆保险公司': ['金融服务'],
 'Chapter': ['保险科技'],
 'True Link Financial': ['金融服务'],
 '美国银行': ['金融服务'],
 'Eversafe': ['金融服务'],
 '富达投资': ['金融服务'],
 'Golden': ['金融服务'],
 '摩根大通': ['金融服务'],
 '美林证券，美国银行旗下': ['金融服务'],
 '保德信金融': ['金融服务'],
 'Silver Bills': ['金融服务'],
 'Silvur': ['金融理财'],
 'True Link': ['金融服务'],
 '401GO': ['金融理财'],
 'Luminary': ['金融理财'],
 'NewRetirement': ['金融理财'],
 'Nestimate': ['金融理财'],
 'The Helper Bees': ['保险科技'],
 'Solace': ['金融理财','陪诊'],
 'Guaranteed': ['金融理财'],
 'Bright': ['金融理财'],
 'Vestwell': ['金融理财'],
 'Capital Rx': ['保险科技'],
 'Warren': ['金融理财'],
 'Pensionbox': ['金融理财'],

 # ---- 跌倒监测 (26) ----
 '清雷': ['智能硬件'],
 '清雷科技': ['智能硬件'],
 '点可科技': ['智能硬件'],
 'CarePredict': ['健康监测'],
 'Age Bold': ['健身'],
 'SafelyYou': ['健康监测'],
 'Voxela': ['智能硬件'],
 'Phoenix Hipwear': ['服装鞋帽'],
 'Lindera': ['健康监测'],
 'SmartQare': ['智能硬件'],
 'Aloe Care Health': ['智能硬件'],
 'LIBIFY': ['智能硬件'],
 'CARU': ['智能硬件'],
 'ZIBRIO': ['康复器械'],
 'Sage': ['健康监测'],
 'Neursantys': ['康复医疗'],
 'Gardia': ['智能硬件'],
 'Teton.ai': ['智能硬件'],
 'Kinesense': ['智能硬件'],
 'WalkJoy': ['康复器械'],
 'Lifted': ['智能硬件'],
 'Butlr': ['智能硬件'],
 '星纵物联': ['智能硬件'],
 'Medical Guardian': ['智能硬件'],
 'MobileHelp': ['智能硬件'],
 'Nymbl Science': ['健身'],
}

# ---------------------------------------------------------------
# NEW_TAGS
# ---------------------------------------------------------------
NEW_TAGS = {
 '殡葬服务': {
   'l1': '养老服务',
   'members': ['After.com','Foundation Partners Group','SCI (Service Corporation International)','镰仓新书'],
 },
 '假发': {
   'l1': '消费品',
   'members': ['海森林','瑞贝卡','瑞邦生物'],
 },
}

# ---------------------------------------------------------------
# Validate
# ---------------------------------------------------------------
errors = []
forbidden = set(BIG)
# 1. every in-scope key covered
for k in in_keys:
    if k not in REASSIGN:
        errors.append('MISSING reassignment: %r' % k)
# 2. no forbidden big-tag name in values
for k, tags in REASSIGN.items():
    for t in tags:
        if t in forbidden:
            errors.append('FORBIDDEN tag %r in value for %r' % (t, k))
# 3. all REASSIGN keys exist in input
for k in REASSIGN:
    if k not in key_to_names:
        errors.append('REASSIGN key not in input: %r' % k)
# 4. NEW_TAGS members exist & not duplicate existing L2 / already-proposed
exist_l2 = set()
for tag in d:
    exist_l2.add(tag)
already_proposed = set(['健康管理','长护险经办','养老人才培训','美妆护肤','养老膳食','短视频直播','听力验配','遗产规划','睡眠监测'])
for nt, info in NEW_TAGS.items():
    if nt in exist_l2:
        errors.append('NEW_TAG duplicates existing L2: %r' % nt)
    if nt in already_proposed:
        errors.append('NEW_TAG duplicates already-proposed: %r' % nt)
    if info['l1'] not in ['产业资本','养老服务','医疗健康','康复辅具','文娱社交','智能科技','消费品','渠道零售','金融保险','食品营养']:
        errors.append('NEW_TAG %r bad l1: %r' % (nt, info['l1']))
    if len(info['members']) < 3:
        errors.append('NEW_TAG %r has <3 members' % nt)
    for m in info['members']:
        if m not in key_to_names:
            errors.append('NEW_TAG %r member not in input: %r' % (nt, m))

if errors:
    print('VALIDATION ERRORS:')
    for e in errors:
        print(' -', e)
else:
    out = {'REASSIGN': REASSIGN, 'NEW_TAGS': NEW_TAGS}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('OK: wrote', OUT)
    print('REASSIGN entries:', len(REASSIGN))
    print('NEW_TAGS:', {k: len(v['members']) for k,v in NEW_TAGS.items()})
    # tag member counts
    from collections import Counter
    c = Counter()
    for tags in REASSIGN.values():
        for t in tags:
            c[t]+=1
    print('--- resulting tag sizes (top) ---')
    for t,n in c.most_common():
        print(' %s: %d' % (t,n))
