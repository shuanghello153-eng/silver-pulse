# -*- coding: utf-8 -*-
import json, os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
db = json.load(open(os.path.join(ROOT,'all_enterprises.json'),encoding='utf-8'))
inter = json.load(open(os.path.join(ROOT,'_ageclub_intermediate.json'),encoding='utf-8'))

STRONG = ['养老','老年','银发','适老','康养','长者','退休','老龄','老人','养护','助老','长辈',
           '照护','护理','陪诊','慢病','护工','适老化','长护险','康复','营养','保健','失能',
           '空巢','助听','轮椅','护理床','失智','认知','旅居','颐养','医养','健步','中老年',
           '50+','活力老人','失禁','纸尿','拐杖','按摩','助行','外骨骼','药盒','睡眠监测',
           '跌倒','穿戴','智能硬件','护具','理疗','个护','染发','洗护','沐浴','奶粉','肽',
           '视力','口腔','假牙','呼吸机','制氧','雾化','血糖','血压','艾灸','中医','药食','滋补',
           '文娱','老年大学','艺术','社团','展演','研学','婚恋','棋牌','书法','声乐','太极','运动']

def has_signal(name, supply):
    t = name + ' ' + supply
    return any(k in t for k in STRONG)

# ---- exact matches ----
print("="*70)
print("EXACT MATCHES (30):")
print("="*70)
for it in inter['exact']:
    a = it['ageclub']; m = it['matched_name']; ser = it['matched_serial']
    ent = next(e for e in db if e.get('serial')==ser)
    print(f"\n[{ser}] {a['name']}  ==  {m}")
    print(f"   DB l1/l2: {ent.get('tag_l1')} / {ent.get('tag_l2')}")
    print(f"   DB desc: {str(ent.get('description',''))[:90]}")
    print(f"   AGEClub supply: {a['supply'][:90]}")

# ---- new without strong signal ----
print("\n"+"="*70)
print("NEW ENTRIES WITHOUT STRONG SILVER KEYWORD (review for reject):")
print("="*70)
flagged=[]
for e in inter['new']:
    if not has_signal(e['name'], e['supply']):
        flagged.append(e)
        print(f"\n  {e['name']}  [{e['section']}]")
        print(f"     supply: {e['supply'][:110]}")
print(f"\nTOTAL flagged (no strong keyword): {len(flagged)}")
print(f"NEW total: {len(inter['new'])}  -> with signal: {len(inter['new'])-len(flagged)}")
