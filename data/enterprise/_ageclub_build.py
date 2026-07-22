# -*- coding: utf-8 -*-
"""Build ageclub_new_entries.json from parsed intermediate + curation decisions."""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
inter = json.load(open(os.path.join(ROOT, '_ageclub_intermediate.json'), encoding='utf-8'))
db = json.load(open(os.path.join(ROOT, 'all_enterprises.json'), encoding='utf-8'))
DB_BY_SER = {e.get('serial'): e for e in db}

# ---------------- curation decisions ----------------
# fuzzy -> merged into existing serial (same entity, do NOT add as new)
MERGE = {
    '无锡年欢科技公司': '#1456',
    '太素方舟（北京）生物科技有限公司': '#1400',
    '江苏享佳健康': '#0080',
    '湖北优唐健康管理有限责任公司': '#1507',
    '浙江老范科技有限公司': '#1517',
}

# new entries to reject (non-company / non-silver per silver-signal rule)
REJECT = {
    '中国人生科学学会': '行业协会（非企业产品主体）',
    '佛山市南海区养老服务业协会': '行业协会（非企业产品主体）',
    '广西中小企业经济互助商会 / 广西桂派旗袍文旅': '商会+旗袍泛女性社群，无明确50+定位',
    '北京服装学院': '高校科研机构（非企业产品主体）',
    '中科极地抗衰老技术研究院': '研究院/泛抗衰（非标准企业主体，属泛再生医学）',
    '湖北广播电视台电视综合频道': '综合电视台（泛融媒体，银发仅子板块）',
    '合肥通鼎文化传媒有限公司': '纯广告大屏置换（泛融媒体，无银发产品）',
}

# exact-match supplement suggestions (AgeClub has more detailed/updated info)
EXACT_SUPPLEMENTS = {
    '福建百龄康养产业发展集团有限公司': 'AgeClub最新显示其在运营养老机构已增至12家（库内记录为11家），建议更新规模数据。',
    '上海地宝防滑防护科技有限公司': 'AgeClub补充其产品矩阵含无障碍扶手、淋浴辅具，建议在描述中增补具体适老辅具品类。',
    '江西哦咔科技有限公司': 'AgeClub显示其正采购认知症养老空间设计团队，说明业务延伸至认知症专区设计，建议补充。',
    '时尚奶奶团': 'AgeClub称其拥有100个中老年IP矩阵（库内仅述粉丝规模），建议补充IP矩阵化运营模式。',
    '浙江三网科技股份有限公司': 'AgeClub列明其养老硬件含定位手环、防跌倒报警器，建议补充硬件品类细节。',
    '美适浴（上海）卫浴有限公司': 'AgeClub强调“100%防摔倒适老开门浴缸”，建议补充产品安全性卖点。',
}

# ---------------- section -> (l1, l2) mapping with keyword overrides ----------------
def assign_tags(section, name, supply):
    t = name + ' ' + supply
    # default by section
    if '二、适老化改造' in section:
        return ['养老服务'], ['适老化']
    if '七、智慧养老平台' in section:
        return ['养老服务'], ['养老信息平台']
    if '八、社区' in section:
        if '机构' in supply or 'CCRC' in supply or '养老院' in supply:
            return ['养老服务'], ['养老机构']
        if '适老化' in supply:
            return ['养老服务'], ['适老化']
        return ['养老服务'], ['居家护理']
    if '一、营养食品' in section:
        if '保险' in supply or '金融' in supply or '康养社区' in supply:
            return ['金融保险'], ['保险']
        return ['食品营养'], ['营养食品']
    if '十、老年教育' in section:
        return ['文娱社交'], ['教育']
    if '十一、医疗问诊' in section:
        if '餐饮' in supply or '餐' in supply:
            return ['养老服务'], ['养老膳食']
        if '保健' in supply or '营养' in supply or '肽' in supply:
            return ['消费品'], ['保健品']
        return ['康复辅具'], ['远程医疗']
    if '五、智能硬件' in section:
        return ['康复辅具'], ['智能硬件']
    if '十三、旅居基地' in section:
        if '地产' in supply or '物业' in supply or '开发' in supply or '投资' in supply:
            return ['养老服务'], ['康养地产']
        return ['文娱社交'], ['旅游']
    if '三、适老家具' in section:
        if '卫浴' in supply:
            return ['养老服务'], ['适老化']
        if '床垫' in supply or '床' in supply:
            return ['康复辅具'], ['护理床']
        return ['康复辅具'], ['护理床']
    if '十二、家电、助听器' in section:
        if '助听' in supply:
            return ['康复辅具'], ['助听器']
        return ['消费品'], ['智能家居']
    if '四、康复医疗器械' in section:
        if '助听' in supply:
            return ['康复辅具'], ['助听器']
        return ['康复辅具'], ['康复器械']
    if '六、智能护理机器人' in section:
        if '陪护' in supply or '陪伴' in supply:
            return ['康复辅具'], ['陪伴机器人']
        return ['康复辅具'], ['机器人']
    if '板块 1' in section or section.startswith('板块 1'):
        return ['消费品'], ['服装鞋帽']
    if '板块 4' in section:
        if '旅游' in supply or '旅居' in supply or '研学' in supply or '游学' in supply:
            return ['文娱社交'], ['旅游']
        if '教育' in supply or '课程' in supply or '大学' in supply:
            return ['文娱社交'], ['教育']
        if '婚恋' in supply or '相亲' in supply:
            return ['文娱社交'], ['相亲']
        if '社团' in supply or '社群' in supply or '社交' in supply or '交友' in supply:
            return ['文娱社交'], ['兴趣社群']
        return ['文娱社交'], ['兴趣社群']
    if '板块 3' in section:
        if '纸尿' in supply or '失禁' in supply:
            return ['消费品'], ['纸尿裤']
        if '失禁' in supply or '尿失禁' in supply:
            return ['消费品'], ['尿失禁']
        if '美妆' in supply or '护肤' in supply or '卸妆' in supply or '妆' in supply:
            return ['消费品'], ['美妆护肤']
        if '染发' in supply or '洗发' in supply or '沐浴' in supply or '洗护' in supply or '个护' in supply:
            return ['消费品'], ['个人护理']
        return ['消费品'], ['个人护理']
    if '板块 5' in section:
        if '机构' in supply or '养老院' in supply:
            return ['养老服务'], ['养老机构']
        if '适老化' in supply:
            return ['养老服务'], ['适老化']
        return ['养老服务'], ['居家护理']
    if '板块 6' in section:
        if '保险' in supply or '金融' in supply:
            return ['金融保险'], ['保险']
        if '营养' in supply or '食品' in supply or '保健' in supply or '肽' in supply:
            return ['食品营养'], ['营养食品']
        if '智能' in supply or '科技' in supply or '软件' in supply or '硬件' in supply:
            return ['康复辅具'], ['智能硬件']
        return ['行业服务'], ['养老软件']
    if '板块 2' in section:
        if '卫浴' in supply or '浴缸' in supply:
            return ['养老服务'], ['适老化']
        if '茶' in supply:
            return ['食品营养'], ['营养食品']
        return ['消费品'], ['智能家居']
    if '补充 - 银发文娱旅游' in section:
        return ['文娱社交'], ['旅游']
    if '补充 - 银发消费' in section:
        if '保健' in supply or '营养' in supply or '肽' in supply or '奶粉' in supply or '食品' in supply:
            return ['食品营养'], ['营养食品']
        if '美妆' in supply or '护肤' in supply or '个护' in supply or '洗护' in supply:
            return ['消费品'], ['个人护理']
        if '氢' in supply or '水' in supply or '器械' in supply or '设备' in supply:
            return ['康复辅具'], ['医疗器械']
        return ['消费品'], ['营养食品']
    if '补充 - 其他' in section:
        if '软件' in supply or '系统' in supply or '直播' in supply:
            return ['行业服务'], ['养老软件']
        if '设备' in supply or '穿戴' in supply or '监测' in supply:
            return ['康复辅具'], ['智能硬件']
        return ['行业服务'], ['']
    if '补充 - 银发智能科技' in section:
        return ['康复辅具'], ['智能硬件']
    if '补充 - 养老服务' in section:
        if '设计' in supply:
            return ['养老服务'], ['适老化']
        if '机构' in supply or '养老院' in supply:
            return ['养老服务'], ['养老机构']
        return ['养老服务'], ['居家护理']
    if '补充 - 银发医疗健康' in section:
        if '助听' in supply:
            return ['康复辅具'], ['助听器']
        if '慢病' in supply or '糖尿病' in supply:
            return ['康复辅具'], ['慢病管理']
        if '康复' in supply:
            return ['康复辅具'], ['康复医疗']
        if '视觉' in supply or '眼' in supply:
            return ['康复辅具'], ['视觉辅助']
        return ['康复辅具'], ['健康管理']
    if '补充 - 银发流量媒体' in section:
        if '电视' in supply or '广播' in supply or '媒体' in supply:
            return ['行业服务'], ['行业媒体']
        return ['行业服务'], ['资讯门户']
    if '九、银发流量' in section:
        if '文旅' in supply or '旅居' in supply or '旅游' in supply or '研学' in supply or '游学' in supply:
            return ['文娱社交'], ['旅游']
        if '电视' in supply or '广播' in supply or '媒体' in supply or '栏目' in supply or '杂志' in supply:
            return ['行业服务'], ['行业媒体']
        if '私域' in supply or '直播' in supply or '电商' in supply or '流量' in supply or '社群' in supply or '渠道' in supply:
            return ['行业服务'], ['养老信息平台']
        return ['行业服务'], ['']
    # fallback
    return ['行业服务'], ['']


def region_of(name, supply):
    if name in ('索尼半导体',) or '索尼' in name:
        return '海外'
    if '英杰之旅' in name:  # 英国熟龄游学定制服务
        return '海外'
    return '国内'


def make_description(name, supply, demand):
    s = supply.strip()
    # sentence 1: what they do
    desc = f"{name}：{s}。"
    # sentence 2: who they serve / how they monetize (inferred only from explicit hints)
    hints = (supply + ' ' + demand)
    if any(k in hints for k in ['招商', '代理', '渠道', '加盟', '分销', '集采', '合伙', '供货', '经销']):
        desc += "公司主要通过渠道招商、代理分销与产业链上下游合作拓展市场。"
    elif any(k in hints for k in ['研发', '生产', '制造', '工厂', '源头', '厂家', ' OEM', 'ODM']):
        desc += "以自主研发与生产制造为核心，面向B端机构与终端银发消费群体提供产品与服务。"
    elif any(k in hints for k in ['平台', '系统', '软件', 'SaaS', '运营', '服务']):
        desc += "通过平台化运营与软硬件服务，连接银发人群、服务机构与产业资源。"
    else:
        desc += "面向银发人群及相关养老服务机构提供产品与服务。"
    return desc


# ---------------- assemble ----------------
new_entries = []
rejected = []

def add_entry(e, note=''):
    nm = e['name']
    l1, l2 = assign_tags(e['section'], nm, e['supply'])
    l2 = [x for x in l2 if x]
    entry = {
        'name': nm,
        'region': region_of(nm, e['supply']),
        'tag_l1': l1,
        'tag_l2': l2,
        'tags': [],
        'description': make_description(nm, e['supply'], e['demand']),
        'recommend': '',
        'source': 'AgeClub供需对接',
        'website_url': '',
        'crunchbase_url': '',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '',
        'stage': '',
        'payor_model': '',
    }
    new_entries.append(entry)

# 1) clearly-new (307)
for e in inter['new']:
    nm = e['name']
    if nm in REJECT:
        rejected.append({'name': nm, 'reason': REJECT[nm]})
        continue
    add_entry(e)

# 2) fuzzy -> merges are skipped; distinct fuzzy -> new
merged_count = 0
for e in inter['fuzzy']:
    nm = e['name']
    if nm in MERGE:
        merged_count += 1
        continue
    if nm in REJECT:
        rejected.append({'name': nm, 'reason': REJECT[nm]})
        continue
    add_entry(e)

# 3) exact-match supplements
exact_supps = []
for it in inter['exact']:
    nm = it['ageclub']['name']
    if nm in EXACT_SUPPLEMENTS:
        ser = it['matched_serial']
        ent = DB_BY_SER.get(ser, {})
        exact_supps.append({
            'name': nm,
            'existing_tags': (ent.get('tag_l1') or []) + (ent.get('tag_l2') or []),
            'suggested_description_addition': EXACT_SUPPLEMENTS[nm],
        })

# ---------------- summary ----------------
summary = {
    'total_parsed': inter['entries'].__len__(),
    'after_dedup': len(inter['entries']),
    'exact_match': len(inter['exact']),
    'fuzzy_match': len(inter['fuzzy']),
    'fuzzy_resolved': {'merged': merged_count, 'new': len(inter['fuzzy']) - merged_count},
    'after_silver_signal_filter': len(new_entries),
    'rejected': rejected,
    'final_new_entries': len(new_entries),
}

out = {
    'summary': summary,
    'exact_match_supplements': exact_supps,
    'new_entries': new_entries,
}

OUT = os.path.join(ROOT, 'ageclub_new_entries.json')
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("WROTE", OUT)
print(json.dumps(summary, ensure_ascii=False, indent=2))
print("\nrejected count:", len(rejected))
for r in rejected:
    print("  -", r['name'], "::", r['reason'])
print("\nexact supplements:", len(exact_supps))
for s in exact_supps:
    print("  -", s['name'])
