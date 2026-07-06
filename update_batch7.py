#!/usr/bin/env python3
"""Batch 7: Stage Book 26 companies without description + name fixes."""
import json

DATA_FILE = r'G:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise\all_enterprises.json'

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def apply_updates(data, updates):
    name_map = {}
    for i, e in enumerate(data):
        name_map[e['name']] = i

    updated = 0
    not_found = 0
    for name, upd in updates.items():
        if name in name_map:
            idx = name_map[name]
            for k, v in upd.items():
                data[idx][k] = v
            updated += 1
            print(f'  OK {name}')
        else:
            not_found += 1
            print(f'  MISS {name}')

    print(f'\nUpdated: {updated}, Not found: {not_found}')
    return data

BATCH_7 = {
    'AARP Innovation Labs / AgeTech Collaborative': {
        'description': 'AARP是美国最大的老年人权益倡导组织（3800万会员），其AgeTech Collaborative项目旨在加速老年科技创新生态，连接创业者、投资人和养老服务机构。',
        'highlights': '美国最大老年权益组织(3800万会员)的创新平台',
        'founded': '1958',
        'website_url': 'https://www.aarp.org/agetech/',
    },
    '英国': {
        'description': '此处指英国在银发经济领域的政策与市场环境，英国是全球老龄化程度较高的国家之一，拥有完善的国民医疗服务体系（NHS）和活跃的老年科技创业生态。',
        'highlights': '英国银发经济政策与市场环境参考',
        'founded': '',
        'website_url': '',
    },
    'Aging2.0 Collective': {
        'description': 'Aging2.0 Collective是全球性老年科技创新网络，由Stephen Johnston创立，在全球30+城市设有分部，连接创业者、投资人和养老服务机构，定期举办创新峰会和孵化器项目。',
        'highlights': '全球老年科技创新网络，30+城市分部',
        'founded': '2014',
        'website_url': 'https://www.aging2.com/',
    },
    '亚马逊': {
        'description': 'Amazon（亚马逊）是全球最大的电商和云计算公司，在银发经济领域通过Alexa智能语音助手、AWS云服务和Amazon Care等业务布局老年健康与智慧养老。',
        'highlights': 'Alexa语音助手+AWS云服务布局智慧养老',
        'founded': '1994',
        'website_url': 'https://www.amazon.com/',
    },
    'Apax Partners': {
        'description': 'Apax Partners是全球知名私募股权投资公司，管理资产超过500亿美元，在医疗健康和养老服务领域有多个投资布局。',
        'highlights': '全球PE巨头，医疗健康+养老服务投资布局',
        'founded': '1972',
        'website_url': 'https://www.apax.com/',
    },
    '宝马': {
        'description': 'BMW（宝马）在银发经济领域聚焦老年人出行，通过车内适老化设计、辅助驾驶技术等提升老年驾驶者的安全性和舒适度。',
        'highlights': '车内适老化设计+辅助驾驶技术',
        'founded': '1916',
        'website_url': 'https://www.bmw.com/',
    },
    '美国银行': {
        'description': 'Bank of America（美国银行）在银发经济领域提供退休规划、财富管理、老年金融防欺诈等服务，是全球最大的退休账户管理机构之一。',
        'highlights': '全球最大退休账户管理机构之一',
        'founded': '1904',
        'website_url': 'https://www.bankofamerica.com/',
    },
    '百思买': {
        'description': 'Best Buy（百思买）是全球最大的消费电子零售商，通过收购GreatCall（$800M）和Current Health（$400M）大举进入老年科技和远程医疗市场。',
        'highlights': '收购GreatCall($800M)+Current Health($400M)进入老年科技',
        'funding_latest': {'date': '2021', 'amount': '$400M', 'round': '并购', 'display': '收购Current Health $400M (2021)'},
        'funding_total': {'amount': '$1.2B+', 'display': '累计$1.2B+（老年科技收购）'},
        'investors': 'NYSE:BBY 上市公司',
        'founded': '1966',
        'website_url': 'https://www.bestbuy.com/',
    },
    'Meta': {
        'description': 'Meta（前Facebook）在银发经济领域通过Oculus VR设备为老年人提供社交和认知训练体验，同时研究VR在老年认知衰退干预中的应用。',
        'highlights': 'VR设备用于老年社交和认知训练',
        'founded': '2004',
        'website_url': 'https://www.meta.com/',
    },
    '富达投资': {
        'description': 'Fidelity Investments（富达投资）是全球最大的资产管理公司之一，管理资产超过4万亿美元，在退休规划和养老金融领域是行业标杆。',
        'highlights': '全球最大资产管理公司之一，退休规划标杆',
        'founded': '1946',
        'website_url': 'https://www.fidelity.com/',
    },
    'Greycroft Partners': {
        'description': 'Greycroft Partners是专注早期和成长期投资的VC，在消费科技和医疗健康领域有布局，投资了多个老年科技项目。',
        'highlights': '早期+成长期VC，老年科技投资布局',
        'founded': '2006',
        'website_url': 'https://www.greycroft.com/',
    },
    'Humana / Aetna / UnitedHealth / Cigna': {
        'description': '美国四大健康保险巨头（Humana、Aetna、UnitedHealth、Cigna），在Medicare Advantage市场占据主导地位，是美国老年健康保险市场的核心参与者。',
        'highlights': '美国四大健康保险巨头，Medicare Advantage市场主导',
        'founded': '',
        'website_url': '',
    },
    '摩根大通': {
        'description': 'JPMorgan Chase（摩根大通）是全球最大的金融服务公司之一，通过其Age-Linked投资策略和JPMorgan Asset Management布局银发经济赛道。',
        'highlights': '全球最大金融服务公司之一，银发经济投资布局',
        'founded': '1799',
        'website_url': 'https://www.jpmorganchase.com/',
    },
    '强生': {
        'description': 'Johnson & Johnson（强生）是全球最大的医疗健康公司之一，在老年慢病管理、关节置换、眼科等领域有深度布局，旗下多个产品线直接服务老年人群。',
        'highlights': '全球最大医疗健康公司之一，老年慢病+关节置换+眼科',
        'founded': '1886',
        'website_url': 'https://www.jnj.com/',
    },
    '凯撒医疗': {
        'description': 'Kaiser Permanente（凯撒医疗）是美国最大的非营利性整合医疗体系，服务1200万+会员，在老年健康管理和Medicare Advantage市场占据重要地位。',
        'highlights': '美国最大非营利整合医疗体系，1200万+会员',
        'founded': '1945',
        'website_url': 'https://www.kaiserpermanente.org/',
    },
    'Lululemon': {
        'description': 'Lululemon是全球运动服饰品牌，在银发经济领域通过功能性运动服饰和社区活动鼓励老年人保持积极运动的生活方式。',
        'highlights': '功能性运动服饰，鼓励老年积极运动',
        'founded': '1998',
        'website_url': 'https://www.lululemon.com/',
    },
    '麻省理工学院年龄实验室': {
        'description': 'MIT AgeLab（麻省理工学院年龄实验室）由Joseph Coughlin博士创立，是全球领先的老年科技学术研究机构，研究老龄化与技术的交叉领域。',
        'highlights': '全球领先老年科技学术研究机构，Joseph Coughlin博士创立',
        'founded': '1999',
        'website_url': 'https://agelab.mit.edu/',
    },
    '梅奥诊所': {
        'description': 'Mayo Clinic（梅奥诊所）是美国顶级医疗中心，在老年医学、远程医疗和AI辅助诊断领域处于领先地位，运营多个老年医学研究中心。',
        'highlights': '美国顶级医疗中心，老年医学+远程医疗领先',
        'founded': '1864',
        'website_url': 'https://www.mayoclinic.org/',
    },
    '联邦医疗保险优势计划': {
        'description': 'Medicare Advantage（联邦医疗保险优势计划，又称Part C）是美国政府Medicare的私营化版本，由商业保险公司运营，覆盖超过50%的Medicare受益人（约3100万人）。',
        'highlights': '美国Medicare私营化版本，覆盖3100万+人',
        'founded': '2003',
        'website_url': 'https://www.medicare.gov/',
    },
    '美世咨询': {
        'description': 'Mercer（美世咨询）是全球领先的人力资源咨询公司，在退休规划、养老金管理和员工福利领域是行业标杆，服务全球数百万退休人员。',
        'highlights': '全球领先HR咨询，退休规划+养老金管理标杆',
        'founded': '1945',
        'website_url': 'https://www.mercer.com/',
    },
    'Pivotal Ventures': {
        'description': 'Pivotal Ventures是Melinda French Gates创立的投资和慈善机构，关注女性经济赋权和老年人财务安全，在银发经济领域有战略投资布局。',
        'highlights': 'Melinda French Gates创立，关注老年人财务安全',
        'founded': '2015',
        'website_url': 'https://pivotalventures.org/',
    },
    'Primetime Partners': {
        'description': 'Primetime Partners是专注银发经济（50+人群）的风险投资基金，由Alan Patricof创立，投资了多个老年科技和老年消费项目。',
        'highlights': '专注银发经济VC，Alan Patricof创立',
        'founded': '2020',
        'website_url': 'https://www.primetimepartners.vc/',
    },
    '保德信金融': {
        'description': 'Prudential Financial（保德信金融）是全球最大的金融服务公司之一，在退休金管理、年金和老年财富规划领域是行业领导者。',
        'highlights': '全球最大金融服务公司之一，退休金管理领导者',
        'founded': '1875',
        'website_url': 'https://www.prudential.com/',
    },
    '三星': {
        'description': 'Samsung（三星）在银发经济领域通过智能健康设备、Digital Health平台和适老化电子产品布局老年健康市场，同时在韩国本土市场运营养老服务平台。',
        'highlights': '智能健康设备+适老化电子产品，韩国养老服务平台',
        'founded': '1938',
        'website_url': 'https://www.samsung.com/',
    },
    '斯坦福长寿研究中心': {
        'description': 'Stanford Center on Longevity（斯坦福长寿研究中心）是全球顶级老龄化研究机构，研究长寿社会的金融、健康和生活方式变革，发布影响力很大的年度报告。',
        'highlights': '全球顶级老龄化研究机构，长寿社会研究',
        'founded': '2007',
        'website_url': 'https://longevity.stanford.edu/',
    },
    'Techstars Future of Longevity Accelerator': {
        'description': 'Techstars Future of Longevity是Techstars旗下专注银发经济的加速器项目，每年孵化10+老年科技创业公司，由MetLife基金会赞助。',
        'highlights': 'Techstars银发经济加速器，每年孵化10+公司',
        'founded': '2019',
        'website_url': 'https://www.techstars.com/program/accelerator-future-of-longevity',
    },
    # 修正名称匹配
    'ElliQ': {
        'description': 'ElliQ是以色列Intuition Robotics开发的AI老年社交陪伴机器人，能主动发起对话、提醒服药、推荐活动，已在美国数千家庭部署。由Dor Skuler创立。',
        'highlights': 'AI老年社交陪伴机器人，美国数千家庭部署',
        'funding_latest': {'date': '2023', 'amount': '$25M', 'round': 'Series B', 'display': 'Series B $25M (2023)'},
        'funding_total': {'amount': '$83M', 'display': '累计$83M'},
        'investors': 'OurCrowd, Bloomberg Beta, iRobot, Toyota AI Ventures',
        'founded': '2016',
        'website_url': 'https://elliq.com/',
    },
    'Right At Home': {
        'description': 'Right at Home是居家护理加盟品牌，提供个人护理、companionship、护理管理等服务，在全美和全球拥有500+加盟点。',
        'highlights': '居家护理加盟品牌，全球500+加盟点',
        'founded': '1995',
        'website_url': 'https://www.rightathome.net/',
    },
    'Philips (Lifeline)': {
        'description': '飞利浦Lifeline是个人紧急响应系统（PERS）的先驱品牌，提供可穿戴紧急呼叫设备和24/7紧急响应服务，2006年飞利浦收购Lifeline Systems。',
        'highlights': 'PERS紧急呼叫系统先驱品牌，飞利浦旗下',
        'funding_latest': {'date': '2006', 'amount': '$750M', 'round': '并购', 'display': '飞利浦收购$750M (2006)'},
        'funding_total': {'amount': '$750M', 'display': '累计$750M（被收购）'},
        'investors': 'Royal Philips (NYSE:PHG)',
        'founded': '1974',
        'website_url': 'https://www.lifeline.philips.com/',
    },
}

if __name__ == '__main__':
    data = load_data()
    print(f'Total updates to apply: {len(BATCH_7)}')
    data = apply_updates(data, BATCH_7)
    save_data(data)
    print('Saved successfully.')
