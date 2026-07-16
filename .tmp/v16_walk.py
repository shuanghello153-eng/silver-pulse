import json, re
from collections import Counter, defaultdict

d = json.load(open('data/enterprise/all_enterprises.json'))
m = json.load(open('data/enterprise/_l2_l1.json'))

# 模板识别
groups = defaultdict(list)
for e in d:
    desc = (e.get('desc_cn') or e.get('description') or '').strip()
    if len(desc) > 15:
        groups[desc].append(e)
TPL = ['面向银发人群','银发社交与文娱','相关的服务（如','专业护理相关的服务',
       '养老辅具与适老化硬件','B2B AI/数据驱动','搭建面向中老年',
       '提供居家照护、专业护理及智慧养老','主营','资讯','平台企业，主营']
def is_tpl(e):
    desc = (e.get('desc_cn') or e.get('description') or '')
    if len(desc) > 40 and desc in groups and len(groups[desc]) >= 2:
        return True
    return any(p in desc for p in TPL)

# 名字规则（模板企业用）
NAME_RULES = {
    '居家护理': {'real':['护理','照护','护工','家政','康养','医养','养老','孝老','安养','颐养','陪护照料','保姆','助浴','养护','护理院','长护'],
                 'fake':['科技','智能','平台','电子','硬件','系统','软件','数据','互联网','AI','传媒','资讯','金融','保险','医药','医院','诊所','厨','餐','食','修脚','足浴','齿科','用车','出行','服饰','美妆','电商','零售','旅游','文娱','健身','教育','器械','辅具','传感','算法','理赔','设备','产品','方案','研发','制造']},
    '陪伴服务': {'real':['陪伴','照护','护工','家政','养老','孝老','安养','颐养','陪护照料','保姆'],
                 'fake':['诊所','医院','医药','保险','金融','硬件','电子','科技','智能','平台','传媒','资讯','用车','出行','器械','辅具','传感','算法','理赔','电商','零售']},
    '养老机构': {'real':['养老','机构','公寓','养老院','养护','护理院','颐养','康养','CCRC','敬老','托老'],
                 'fake':['科技','电子','硬件','平台','传媒','资讯','金融','保险','医药','医院','诊所','器械','辅具','出行','用车','电商','零售']},
    '兴趣社群': {'real':['社交','社区','兴趣','文娱','合唱','舞蹈','大学','学堂','退休','活动','社群','交友','相亲'],
                 'fake':['诊所','医院','医药','保险','金融','硬件','电子','科技','器械','辅具','传感','算法','理赔','用车','出行','平台','电商','零售']},
    '助听器': {'real':['听力','助听','听觉','声学','耳'],
               'fake':['厨','餐','食','服饰','美妆','护肤','金融','保险','传媒','资讯','旅游','文娱','健身','教育','电商','零售']},
    '助行器': {'real':['助行','轮椅','行动','辅具','康复'],
               'fake':['厨','餐','食','服饰','美妆','护肤','金融','保险','传媒','资讯','旅游','文娱','健身','教育','电商','零售']},
    '可穿戴监测': {'real':['可穿戴','监测','手表','手环','穿戴','体征','健康硬件'],
                   'fake':['厨','餐','食','金融','保险','传媒','资讯','旅游','文娱','教育','服饰','美妆','护肤','诊所','医院','电商','零售']},
    'SaaS': {'real':['SaaS','软件','系统','平台','云','数据','数字化','信息化','科技','智能'],
             'fake':['保险','金融','服饰','美妆','护肤','旅游','文娱','健身','教育','餐饮','食品','硬件','器械','辅具','电商','零售']},
}
# 非模板企业：用真实描述判断服务类标签
SVC_TAGS = ['居家护理','陪伴服务','养老机构','兴趣社群']
SVC_WORDS = ['护理','照护','上门','保姆','助浴','家政','陪伴','社交','兴趣','社区','养老','机构','公寓','敬老','学堂','合唱','舞蹈','交友','相亲','活动']
TECH_WORDS = ['科技','智能','平台','系统','软件','硬件','设备','产品','解决方案','大数据','算法','模型','研发','制造','互联网','数字化','AI','传感','机器人','数据驱动','信息技术']

def fallback(name):
    if any(k in name for k in ['厨','餐','食','食品']): return '营养食品'
    if any(k in name for k in ['科技','智能','电子','数据']): return 'SaaS'
    if any(k in name for k in ['传媒','资讯','媒体']): return '资讯门户'
    if any(k in name for k in ['医药','医院','诊所','健康','医疗']): return '诊所'
    if any(k in name for k in ['金融','保险']): return '保险'
    if any(k in name for k in ['硬件','器械','辅具','传感']): return '智能硬件'
    if any(k in name for k in ['服饰','美妆','护肤']): return '美妆护肤'
    if any(k in name for k in ['旅游','文娱','健身','教育']): return '文娱'
    return None

before = Counter()
for e in d: before.update(e.get('tag_l2', []))

changes = []; zero_fixed = 0
for e in d:
    name = e['name']
    name2 = name.replace('智慧', '智能')  # 智慧养老平台 == 智能平台，按非服务类处理
    orig = list(e.get('tag_l2', []))
    new_l2 = list(orig)
    removed = []
    # 1) 名字规则
    for tag, r in NAME_RULES.items():
        if tag in new_l2 and any(s in name2 for s in r['fake']) and not any(s in name for s in r['real']):
            new_l2.remove(tag); removed.append(tag)
    # 2) 非模板企业：真实描述判断服务类
    if not is_tpl(e):
        desc = (e.get('desc_cn') or e.get('description') or '')
        if any(t in desc for t in TECH_WORDS) and not any(s in desc for s in SVC_WORDS):
            for tag in SVC_TAGS:
                if tag in new_l2:
                    new_l2.remove(tag); removed.append(tag)
    if removed:
        if not new_l2:
            fb = fallback(name2)
            if fb:
                new_l2.append(fb); zero_fixed += 1
                changes.append(f'{name}: {orig} -> {new_l2} [兜底:{fb}]')
            else:
                new_l2 = orig
                changes.append(f'{name}: {orig} -> 保留(无兜底)')
        else:
            changes.append(f'{name}: {orig} -> {new_l2}')
        e['tag_l2'] = new_l2

after = Counter()
for e in d: after.update(e.get('tag_l2', []))

print("=== DRY RUN ===")
for tag in NAME_RULES:
    b=before.get(tag,0); a=after.get(tag,0)
    print(f"  {tag}: {b} -> {a} (减 {b-a})")
print(f"企业总数: {len(d)} | 兜底0标签: {zero_fixed} | 实际改动: {len(changes)}")
print(f"标签种类: {len(before)} -> {len(after)}")
print("\n=== 改动明细 ===")
for c in changes:
    print("  ", c)

# 重算所有企业 L1 并落库
for e in d:
    nl = set()
    for t in e.get('tag_l2', []):
        for p in m.get(t, []):
            nl.add(p)
    e['tag_l1'] = sorted(nl)
json.dump(d, open('data/enterprise/all_enterprises.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\n[已落库] all_enterprises.json 改写 {len(changes)} 家企业标签")
