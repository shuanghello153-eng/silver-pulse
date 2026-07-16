import json

d = json.load(open('data/enterprise/all_enterprises.json'))
m = json.load(open('data/enterprise/_l2_l1.json'))
s = json.load(open('data/enterprise/tag_synonyms.json'))

# 基于企业名常识的合理标签（用户可后续校正）
TAGS = {
    'Agely Care': ['养老机构'],
    'AltoIRA': ['金融理财'],
    'Altoida': ['认知筛查'],
    'Assystel': ['紧急呼叫'],
    'BedHub': ['智能家居'],
    'Caspar.AI': ['可穿戴监测'],
    'Livana Connect': ['陪伴服务'],
    'Lys Therapeutics': ['抗衰'],
    'MapHabit': ['认知训练'],
    'MonSenior': ['养老机构'],
    'MyndYou': ['可穿戴监测'],
    'Ome': ['可穿戴监测'],
    'Optina Diagnostics': ['AI医疗'],
    'Rejuvenate Bio': ['抗衰'],
    'SingFit': ['文娱'],
    'Swissvoice': ['助听器'],
    'Third Eye Health': ['远程医疗'],
    'Vali Health': ['抗衰'],
    'Winterlight Labs': ['认知筛查'],
    'Xray Moov': ['智能硬件'],
}

missing = [t for tags in TAGS.values() for t in tags if t not in m]
print("映射中缺失的标签(需先在_l2_l1注册):", set(missing))
if missing:
    print("⚠️ 中止，请先确认标签存在")
    raise SystemExit(1)

changes = []
for e in d:
    if e['name'] in TAGS and not e.get('tag_l2'):
        new = TAGS[e['name']]
        e['tag_l2'] = new
        nl = set()
        for t in new:
            for p in m.get(t, []):
                nl.add(p)
        e['tag_l1'] = sorted(nl)
        changes.append(f"{e['name']}: -> {new} (L1={e['tag_l1']})")

json.dump(d, open('data/enterprise/all_enterprises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\n已为 {len(changes)} 家新企业补标签：")
for c in changes:
    print("  ", c)
