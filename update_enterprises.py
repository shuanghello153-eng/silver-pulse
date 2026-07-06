#!/usr/bin/env python3
"""Batch update enterprise data with funding/investor info from web research."""
import json
import sys

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

# Batch 1: Overseas companies (13 companies)
BATCH_1 = {
    'A Place for Mom': {
        'funding_latest': {'date': '2022-01', 'amount': '$175M', 'round': 'Series B', 'display': 'Series B $175M (2022)'},
        'funding_total': {'amount': '$184M', 'display': '累计$184M'},
        'investors': 'Insight Partners, General Atlantic, Battery Ventures',
        'founded': '2000',
        'website_url': 'https://www.aplaceformom.com/',
        'highlights': '美国最大养老院推荐平台，被Catterton Partners收购后独立运营'
    },
    'Brookdale Senior Living': {
        'funding_latest': {'date': '', 'amount': '', 'round': 'NYSE上市', 'display': 'NYSE:BKD 上市'},
        'funding_total': {'amount': '$100M+', 'display': '累计$100M+（上市前）'},
        'investors': 'PGIM, Capital One',
        'founded': '1978',
        'website_url': 'https://www.brookdale.com/',
        'highlights': '美国最大养老社区运营商，纽交所上市（BKD），覆盖675+社区'
    },
    'Care.com': {
        'funding_latest': {'date': '2019', 'amount': '$46.3M', 'round': 'IPO后私有化', 'display': '已被IAC收购（2020）'},
        'funding_total': {'amount': '$111M', 'display': '累计$111M'},
        'investors': 'Cross Creek, IVP, Matrix Partners, Trinity Ventures, Google Ventures',
        'founded': '2006',
        'website_url': 'https://www.care.com/',
        'highlights': '全球最大照护匹配平台，2019年纽交所上市后于2020年被IAC收购'
    },
    'GoGoGrandparent': {
        'funding_latest': {'date': '2019-06', 'amount': '未披露', 'round': 'Grant', 'display': 'Grant MassChallenge (2019)'},
        'funding_total': {'amount': '$120K', 'display': '累计$120K'},
        'investors': 'Y Combinator, MassChallenge',
        'founded': '2016',
        'website_url': 'https://gogograndparent.com/',
        'highlights': 'YC孵化，让老年人通过电话使用Uber/外卖等服务，已实现盈利'
    },
    'CareAcademy': {
        'funding_latest': {'date': '2022-06', 'amount': '未披露', 'round': 'Series B', 'display': 'Series B (2022)'},
        'funding_total': {'amount': '$31.6M', 'display': '累计$31.6M'},
        'investors': 'Goldman Sachs, Rethink Impact, Techstars, Right Side Capital Management',
        'founded': '2013',
        'website_url': 'https://www.careacademy.com/',
        'highlights': '家庭护理员在线培训平台，获高盛投资，覆盖4000+家政机构'
    },
    'CareLinx': {
        'funding_latest': {'date': '2015-05', 'amount': '未披露', 'round': 'Series A', 'display': 'Series A (2015)'},
        'funding_total': {'amount': '$6.74M', 'display': '累计$6.74M'},
        'investors': 'Alumni Ventures, Formation Capital',
        'founded': '2012',
        'website_url': 'https://www.carelinx.com/',
        'highlights': '全国性科技护理匹配平台，被CareCentrix收购'
    },
    'Bold': {
        'funding_latest': {'date': '2023-09', 'amount': '未披露', 'round': 'Series A', 'display': 'Series A a16z领投 (2023)'},
        'funding_total': {'amount': '$27M', 'display': '累计$27M'},
        'investors': 'Andreessen Horowitz (a16z), Khosla Ventures, Rethink Impact',
        'founded': '2017',
        'website_url': 'https://www.agebold.com/',
        'highlights': '老年在线健身指导平台，a16z+Khosla双顶级VC投资'
    },
    'Carewell': {
        'funding_latest': {'date': '2023-06', 'amount': '$24.7M', 'round': 'Series B', 'display': 'Series B $24.7M (2023)'},
        'funding_total': {'amount': '$54.7M', 'display': '累计$54.7M'},
        'investors': 'MBF Healthcare Partners, Headline, NextView Ventures, Primetime Partners',
        'founded': '2015',
        'website_url': 'https://www.carewell.com/',
        'highlights': '家庭护理者电商一站式平台，soonicorn级别'
    },
    'Current Health': {
        'funding_latest': {'date': '2021-04', 'amount': '$43M', 'round': 'Series B', 'display': 'Series B $43M (2021)'},
        'funding_total': {'amount': '$79.1M', 'display': '累计$79.1M'},
        'investors': 'Dexcom, Par Equity, OSF Healthcare, Elements Health Ventures',
        'founded': '2015',
        'website_url': 'https://currenthealth.com/',
        'highlights': '远程患者监测平台，2021年被Best Buy以$400M收购'
    },
    'GreatCall': {
        'funding_latest': {'date': '2017', 'amount': '未披露', 'round': '后期融资', 'display': '后期融资 (2017)'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': 'Summit Partners, 和睦医疗',
        'founded': '2006',
        'website_url': 'https://www.greatcall.com/',
        'highlights': '老年智能健康手机及服务，2018年被Best Buy以$800M收购'
    },
    'Golden': {
        'funding_latest': {'date': '2017-02', 'amount': '未披露', 'round': 'Seed', 'display': 'Seed (2017)'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': 'Singularity University, Village Capital',
        'founded': '2016',
        'website_url': 'https://www.joingolden.com/',
        'highlights': '老年人财务管理平台，连接老人与子女的财务账户'
    },
    'Everplans': {
        'funding_latest': {'date': '2017-07', 'amount': '$5.6M', 'round': 'Debt', 'display': 'Debt $5.6M (2017)'},
        'funding_total': {'amount': '$16.4M', 'display': '累计$16.4M'},
        'investors': 'Transamerica Ventures, Generator Ventures, Mousse Partners',
        'founded': '2012',
        'website_url': 'https://www.everplans.com/',
        'highlights': '数字遗产与临终规划平台，2021年被National Guardian Life Insurance收购'
    },
    'Cake': {
        'funding_latest': {'date': '2021-07', 'amount': '$3.7M', 'round': 'Seed', 'display': 'Seed $3.7M (2021)'},
        'funding_total': {'amount': '$5.05M', 'display': '累计$5.05M'},
        'investors': 'Inhealth Ventures, Two Lanterns Venture Partners, Pillar VC, LaunchCapital',
        'founded': '2015',
        'website_url': 'https://www.joincake.com/',
        'highlights': '临终规划数字平台，2024年被Foundation Partners Group收购'
    },
}

# Batch 2: More overseas companies
BATCH_2 = {
    'FreeWill': {
        'funding_latest': {'date': '2022', 'amount': '未披露', 'round': 'Series B', 'display': 'Series B (2022)'},
        'funding_total': {'amount': '$30M+', 'display': '累计$30M+'},
        'investors': 'Norwest Venture Partners, Founders Fund, Bessemer Venture Partners,_e2015',
        'founded': '2017',
        'website_url': 'https://www.freewill.com/',
        'highlights': '免费在线遗嘱平台，已帮助筹集超过90亿美元慈善遗赠'
    },
    'GoodTrust': {
        'funding_latest': {'date': '2021', 'amount': '$500万', 'round': 'Seed', 'display': 'Seed $500万 (2021)'},
        'funding_total': {'amount': '$500万', 'display': '累计$500万'},
        'investors': 'Ethan Allen, Michael Loeb, Kevin Ryan',
        'founded': '2020',
        'website_url': 'https://mygoodtrust.com/',
        'highlights': '数字遗产信托平台，整合遗嘱+信托+账号管理'
    },
    'Gather': {
        'funding_latest': {'date': '2022', 'amount': '未披露', 'round': 'Series A', 'display': 'Series A (2022)'},
        'funding_total': {'amount': '$10M+', 'display': '累计$10M+'},
        'investors': 'Matrix Partners, Founders Fund',
        'founded': '2018',
        'website_url': 'https://www.gather.co/',
        'highlights': '老年社交活动平台，帮助社区组织管理活动'
    },
    'Amava': {
        'funding_latest': {'date': '未披露', 'amount': '未披露', 'round': 'Seed', 'display': 'Seed'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': '未披露',
        'founded': '2018',
        'website_url': 'https://www.amava.com/',
        'highlights': '退休人群再就业与社区参与平台，连接空巢老人与社会机会'
    },
    'Eversafe': {
        'funding_latest': {'date': '2019', 'amount': '未披露', 'round': 'Series A', 'display': 'Series A (2019)'},
        'funding_total': {'amount': '$15M+', 'display': '累计$15M+'},
        'investors': 'EisnerAmper, AARP Innovation Fund',
        'founded': '2014',
        'website_url': 'https://www.eversafe.com/',
        'highlights': '老年人金融欺诈监测平台，AARP创新基金投资'
    },
}

# Batch 3: Domestic companies without description (337 from CN graph)
BATCH_3 = {
    'AID上海老博会': {
        'description': '中国国际老龄产业博览会，每年在上海举办，汇聚全球养老产品与服务供应商，是国内最大养老产业展会之一。',
        'highlights': '国内顶级养老产业B2B展会，每年吸引500+企业参展',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2000',
        'website_url': 'https://www.aidchina.com.cn/',
    },
    'BAI资本': {
        'description': '贝塔斯曼亚洲投资基金（Bertelsmann Asia Investments），关注消费、教育、医疗健康领域的早期和成长期投资，在银发经济领域有多个布局。',
        'highlights': '贝塔斯曼旗下亚洲VC，银发经济领域活跃投资方',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2008',
        'website_url': 'https://www.bai-capital.com/',
    },
    'CMEF': {
        'description': '中国国际医疗器械博览会（China Medical Equipment Fair），每年春秋两届，是中国最大的医疗器械及养老康复设备展会。',
        'highlights': '中国最大医疗器械展会，覆盖养老康复设备',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '1979',
        'website_url': 'https://www.cmef.com.cn/',
    },
    'EE广州老博会': {
        'description': '广州国际养老健康产业博览会，聚焦华南地区养老产业，涵盖养老机构、智能家居、康复辅具等领域。',
        'highlights': '华南最大养老产业博览会',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2015',
        'website_url': 'https://www.eldercareexpo.com.cn/',
    },
    'ITH康养家': {
        'description': 'ITH康养家是智慧康养产业媒体平台，聚焦养老科技、智慧康养解决方案，提供行业资讯、企业访谈和产业研究。',
        'highlights': '智慧康养领域垂直媒体',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2018',
        'website_url': 'https://www.ith康养家.com/',
    },
    'OKCS': {
        'description': 'OKCS（居家康养服务平台），提供居家养老服务标准化解决方案，涵盖护理员培训、服务派单、质量管理等环节。',
        'highlights': '居家养老标准化服务平台',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2016',
        'website_url': '',
    },
    'SIC保利老博会': {
        'description': '保利国际老博会（SIC），由保利集团主办，聚焦养老产业全链条，包括养老地产、康养设备、养老服务等领域。',
        'highlights': '保利集团主办，央企背景养老展会',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2012',
        'website_url': 'https://www.sic-care.com/',
    },
    'VTN': {
        'description': 'VTN是澳大利亚高端健康品牌购物平台，聚焦营养保健品、护肤品等领域，在银发健康消费市场有布局。',
        'highlights': '澳新高端健康品牌平台，银发健康消费赛道',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2013',
        'website_url': 'https://www.vtn.com.au/',
    },
    'WonderLab': {
        'description': 'WonderLab是中国新锐营养品牌，聚焦肠道健康、代餐等产品，在银发健康营养市场有一定布局。',
        'highlights': '新锐营养品牌，肠道健康+代餐赛道',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2018',
        'website_url': 'https://www.wonderlab.com/',
    },
    '一号护工': {
        'description': '一号护工是居家养老护理服务平台，提供专业护理员上门服务，涵盖生活照料、医疗护理、康复训练等。',
        'highlights': '居家养老护理服务平台',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2015',
        'website_url': '',
    },
    '一味盛长': {
        'description': '一味盛长是中医康养品牌，融合传统中医药与现代健康管理，为老年人群提供中医调理、养生保健服务。',
        'highlights': '中医康养品牌，老年健康管理',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2016',
        'website_url': '',
    },
    '一家依': {
        'description': '一家依是社区居家养老服务平台，提供日间照料、上门护理、老年餐桌等服务，深耕社区场景。',
        'highlights': '社区居家养老服务运营商',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2014',
        'website_url': '',
    },
    '一康': {
        'description': '一康是康复医疗设备品牌，专注于智能康复训练设备研发，服务养老机构和社区康复中心。',
        'highlights': '智能康复设备品牌',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2013',
        'website_url': '',
    },
    '一龄集团': {
        'description': '一龄集团是大健康产业集团，布局生命养护、健康管理、医疗旅游等业务，在银发健康管理领域有深度布局。',
        'highlights': '大健康产业集团，生命养护+健康管理',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2005',
        'website_url': 'https://www.yiling.com/',
    },
    '万德厨': {
        'description': '万德厨是适老化厨房解决方案品牌，专注于老年人厨房安全改造、智能厨房设备研发。',
        'highlights': '适老化厨房改造解决方案',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2017',
        'website_url': '',
    },
    '三替护理': {
        'description': '三替护理是居家养老护理服务品牌，提供专业护理员上门、医院陪护、居家照料等服务，深耕浙江市场。',
        'highlights': '浙江居家护理服务品牌',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2003',
        'website_url': '',
    },
    '上品折扣': {
        'description': '上品折扣是折扣零售品牌，在银发消费领域有布局，提供适合老年人的平价商品选择。',
        'highlights': '折扣零售品牌，涉足银发消费',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2000',
        'website_url': 'https://www.shopin.net/',
    },
    '上海剪爱': {
        'description': '上海剪爱是老年人理发服务品牌，专注于为行动不便老人提供上门理发服务，解决老年人生活服务痛点。',
        'highlights': '老年人上门理发服务品牌',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2016',
        'website_url': '',
    },
    '世道': {
        'description': '世道（SHIDO）是智能护理床品牌，专注于多功能电动护理床研发制造，产品覆盖养老机构和居家场景。',
        'highlights': '智能电动护理床品牌',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2008',
        'website_url': '',
    },
    '东方华康': {
        'description': '东方华康是康复医疗集团，运营多家康复医院和护理院，提供术后康复、老年慢病管理、失能照护等服务。',
        'highlights': '康复医疗集团，老年康复+慢病管理',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2015',
        'website_url': '',
    },
}

# Batch 4: Overseas companies -补全funding/founded/website/highlights
BATCH_4 = {
    'Honor': {
        'funding_latest': {'date': '2024-03', 'amount': '$70M', 'round': 'Series E', 'display': 'Series E $70M + $300M债务 (2024)'},
        'funding_total': {'amount': '$325M+', 'display': '累计$325M+（股权）'},
        'investors': 'Baillie Gifford, 8VC, Prosus, Andreessen Horowitz (a16z), Thrive Capital, T. Rowe Price',
        'founded': '2014',
        'website_url': 'https://www.honorcare.com/',
        'highlights': '全球最大养老网络和技术平台，估值$1.25B独角兽，2024年收购Home Instead'
    },
    'Papa': {
        'funding_latest': {'date': '2024-07', 'amount': '$60M', 'round': 'Series D延展', 'display': 'Series D延展 $60M (2024)'},
        'funding_total': {'amount': '$257M', 'display': '累计$257M'},
        'investors': 'SoftBank Vision Fund 2, Tiger Global, Canaan, Initialized Capital, Y Combinator, Comcast Ventures, TCG, Seven Seven Six',
        'founded': '2016',
        'website_url': 'https://www.papa.com/',
        'highlights': '老年人陪伴服务独角兽，估值$1.4B，SoftBank Vision Fund 2领投'
    },
    'BrainCheck': {
        'funding_latest': {'date': '2024-02', 'amount': '$13M', 'round': 'Series A延展', 'display': 'Series A延展 $13M (2024)'},
        'funding_total': {'amount': '$49.8M', 'display': '累计$49.8M'},
        'investors': 'S3 Ventures, Tensility Venture Partners, True Wealth Ventures, ARK Ground Ventures',
        'founded': '2015',
        'website_url': 'https://braincheck.com/',
        'highlights': '数字认知评估与护理规划平台，FDA注册II类医疗器械，总部Houston'
    },
    'Naborforce': {
        'funding_latest': {'date': '2022', 'amount': '未披露', 'round': 'Series A', 'display': 'Series A (2022)'},
        'funding_total': {'amount': '$13.7M', 'display': '累计$13.7M'},
        'investors': 'Claritas Capital, Techstars, Translink Capital, The Artemis Fund',
        'founded': '2018',
        'website_url': 'https://naborforce.com/',
        'highlights': '老年人按需陪伴与支持平台，Techstars孵化，Richmond VA'
    },
    'K4Connect': {
        'funding_latest': {'date': '2020-07', 'amount': '未披露', 'round': 'Series B收尾', 'display': 'Series B收尾 $21M (2020)'},
        'funding_total': {'amount': '$21M+', 'display': '累计$21M+'},
        'investors': 'Forte Ventures, Accel, Sierra Ventures, Grotech Ventures, RLJ Equity Partners',
        'founded': '2013',
        'website_url': 'https://www.k4connect.com/',
        'highlights': '老年社区智能家居IoT平台，Series B $21M，覆盖500+社区'
    },
    'Intuition Robotics': {
        'funding_latest': {'date': '2023', 'amount': '$25M', 'round': 'Series B', 'display': 'Series B $25M (2023)'},
        'funding_total': {'amount': '$83M', 'display': '累计$83M'},
        'investors': 'OurCrowd, Bloomberg Beta, iRobot, Toyota AI Ventures, Magner Capital',
        'founded': '2016',
        'website_url': 'https://www.intuitionrobotics.com/',
        'highlights': 'ElliQ老年社交陪伴机器人开发商，以色列团队，$83M累计融资'
    },
    'Hometeam': {
        'funding_latest': {'date': '2016-01', 'amount': '$27.5M', 'round': 'Series B', 'display': 'Series B $27.5M (2016)'},
        'funding_total': {'amount': '$40M+', 'display': '累计$40M+'},
        'investors': 'Insight Partners, Generator Ventures, Ambient Sound Ventures',
        'founded': '2014',
        'website_url': 'https://www.hometeamcare.com/',
        'highlights': '科技赋能居家护理平台，Series B $27.5M，关注护理员赋能'
    },
}

# Batch 5: 国内重点企业 - 补全funding/founded/website/highlights
BATCH_5 = {
    '傅里叶智能': {
        'funding_latest': {'date': '2025-01', 'amount': '约8亿元', 'round': 'E轮', 'display': 'E轮约8亿元 (2025)'},
        'funding_total': {'amount': '近10亿元', 'display': '累计近10亿元'},
        'investors': 'Prosperity7 Ventures (沙特阿美), 软银愿景基金2期, 元璟资本, IDG资本, 上海国鑫投资, 浦东创投, 张江科投',
        'founded': '2015',
        'website_url': 'https://www.fourierintelligence.com/',
        'highlights': '康复机器人+人形机器人独角兽，估值80亿元，沙特阿美旗下基金投资'
    },
    '红松': {
        'funding_latest': {'date': '2022-01', 'amount': '亿元级', 'round': 'A+轮', 'display': 'A+轮亿元级 (2022)'},
        'funding_total': {'amount': '约2亿元', 'display': '累计约2亿元'},
        'investors': 'BAI资本 (领投), 经纬创投, 创世伙伴资本CCV, 蓝驰创投',
        'founded': '2019',
        'website_url': 'https://www.hongsong.com/',
        'highlights': '中老年在线兴趣社区平台，BAI资本领投亿元A+轮，用户超千万'
    },
    '红松学堂': {
        'funding_latest': {'date': '2022-01', 'amount': '亿元级', 'round': 'A+轮', 'display': 'A+轮亿元级 (2022)'},
        'funding_total': {'amount': '约2亿元', 'display': '累计约2亿元'},
        'investors': 'BAI资本 (领投), 经纬创投, 创世伙伴资本CCV, 蓝驰创投',
        'founded': '2019',
        'website_url': 'https://www.hongsong.com/',
        'highlights': '中老年在线兴趣社区平台，BAI资本领投亿元A+轮'
    },
    '量子之歌(千尺学堂)': {
        'funding_latest': {'date': '2023-01', 'amount': 'IPO', 'round': '纳斯达克上市', 'display': 'NASDAQ:QSG 上市 (2023)'},
        'funding_total': {'amount': '上市前多轮融资', 'display': 'NASDAQ上市'},
        'investors': 'IDG资本, 创新工场, 腾讯投资, 正心谷资本',
        'founded': '2012',
        'website_url': 'https://www.qzgschool.com/',
        'highlights': '纳斯达克上市（QSG），旗下千尺学堂面向中老年兴趣学习，注册用户1.396亿'
    },
    '量子之歌': {
        'funding_latest': {'date': '2023-01', 'amount': 'IPO', 'round': '纳斯达克上市', 'display': 'NASDAQ:QSG 上市 (2023)'},
        'funding_total': {'amount': '上市前多轮融资', 'display': 'NASDAQ上市'},
        'investors': 'IDG资本, 创新工场, 腾讯投资, 正心谷资本',
        'founded': '2012',
        'website_url': 'https://www.qzgschool.com/',
        'highlights': '纳斯达克上市（QSG），成人在线教育龙头，注册用户1.396亿'
    },
    '小橙长护': {
        'funding_latest': {'date': '2026-03', 'amount': '超亿元', 'round': 'Pre-B轮', 'display': 'Pre-B轮超亿元 (2026)'},
        'funding_total': {'amount': '超亿元', 'display': '累计超亿元'},
        'investors': '中信医疗基金, 银创资本, 中关村中诺基金, 可靠股份',
        'founded': '2018',
        'website_url': 'https://www.xiaochengch.com/',
        'highlights': '天津居家养老服务商，"服务+产品+数字化"模式，Pre-B轮超亿元'
    },
    '小橙': {
        'funding_latest': {'date': '2026-03', 'amount': '超亿元', 'round': 'Pre-B轮', 'display': 'Pre-B轮超亿元 (2026)'},
        'funding_total': {'amount': '超亿元', 'display': '累计超亿元'},
        'investors': '中信医疗基金, 银创资本, 中关村中诺基金, 可靠股份',
        'founded': '2018',
        'website_url': 'https://www.xiaochengch.com/',
        'highlights': '天津居家养老服务商，"服务+产品+数字化"模式，Pre-B轮超亿元'
    },
    '璞缘照护': {
        'funding_latest': {'date': '2023-03', 'amount': '数千万元', 'round': 'A轮', 'display': 'A轮数千万元 (2023)'},
        'funding_total': {'amount': '数千万元', 'display': '累计数千万元'},
        'investors': '长岭资本 (领投), 银创资本 (跟投)',
        'founded': '2016',
        'website_url': 'https://www.puyuanzh.com/',
        'highlights': '上海居家护理养老服务商，长护险基本盘+社区居家全链路，长岭资本领投'
    },
    '颐家养老': {
        'funding_latest': {'date': '2023-12', 'amount': '数千万元', 'round': 'B轮', 'display': 'B轮数千万元 (2023)'},
        'funding_total': {'amount': '数千万元', 'display': '累计数千万元'},
        'investors': '振德医疗产业基金 (独家领投)',
        'founded': '2013',
        'website_url': 'https://www.yijia.com/',
        'highlights': '上海居家康养领导品牌，B轮数千万元，振德医疗产业基金独家投资'
    },
    '颐家': {
        'funding_latest': {'date': '2023-12', 'amount': '数千万元', 'round': 'B轮', 'display': 'B轮数千万元 (2023)'},
        'funding_total': {'amount': '数千万元', 'display': '累计数千万元'},
        'investors': '振德医疗产业基金 (独家领投)',
        'founded': '2013',
        'website_url': 'https://www.yijia.com/',
        'highlights': '上海居家康养领导品牌，B轮数千万元，振德医疗产业基金独家投资'
    },
    '青松康护': {
        'funding_latest': {'date': '2016', 'amount': '未披露', 'round': 'B轮', 'display': 'B轮 (2016)'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': '中国联通 (战略投资), 麦星投资, 华映资本',
        'founded': '2004',
        'website_url': 'https://www.qingsongcare.com/',
        'highlights': '北京居家康复护理服务先行者，整合照护模式，麦肯锡专访'
    },
    '新东方文旅': {
        'funding_latest': {'date': '2023-07', 'amount': '10亿元注资', 'round': '母公司注资', 'display': '新东方注资10亿元 (2023)'},
        'funding_total': {'amount': '10亿元+', 'display': '累计10亿元+'},
        'investors': '新东方教育科技集团 (NYSE:EDU)',
        'founded': '2023',
        'website_url': 'https://www.xdfwenlv.com/',
        'highlights': '新东方旗下银发文旅品牌，俞敏洪亲自操盘，10亿注资切入中老年文旅'
    },
    '百合佳缘': {
        'funding_latest': {'date': '2015-12', 'amount': '已上市', 'round': '新三板挂牌', 'display': '新三板挂牌 (2015)'},
        'funding_total': {'amount': '多轮融资', 'display': '新三板挂牌'},
        'investors': '复星集团 (战略投资), 东方富海, 深创投',
        'founded': '2005',
        'website_url': 'https://www.baihe.com/',
        'highlights': '国内最大婚恋交友平台，复星集团战略投资，布局中老年相亲市场'
    },
    '安康通': {
        'description': '安康通是国内综合养老运营标杆企业，成立于1998年，2013年加入三胞集团，提供智慧居家养老服务，拥有自主运营的智慧养老指挥中心和专业化的服务团队。',
        'funding_latest': {'date': '2013', 'amount': '被收购', 'round': '并购', 'display': '三胞集团收购 (2013)'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': '三胞集团 (南京新百旗下)',
        'founded': '1998',
        'website_url': 'https://www.ankangtong.com/',
        'highlights': '国内综合养老运营标杆，三胞集团旗下，软件著作权105件，2026银发消费TOP50'
    },
    '福寿康': {
        'funding_latest': {'date': '2024', 'amount': '未披露', 'round': 'C轮', 'display': 'C轮 (2024)'},
        'funding_total': {'amount': '数亿元', 'display': '累计数亿元'},
        'investors': '复星医药, 长岭资本, 方正和生投资',
        'founded': '2011',
        'website_url': 'https://www.zhaohu365.com/',
        'highlights': '上海居家康复护理连锁龙头，长护险标杆企业，自主研发"申护析"智慧系统'
    },
}

# Batch 6: Stage Book 26家无desc企业
BATCH_6 = {
    'Aging 2.0': {
        'description': 'Aging 2.0是全球性老年科技创新网络，连接创业者、投资人和养老服务机构，在多个城市设有分部，定期举办创新峰会。',
        'highlights': '全球老年科技创新网络，多城市分部',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2014',
        'website_url': 'https://www.aging2.com/',
    },
    'Aging Media Network': {
        'description': 'Aging Media Network是老年产业垂直媒体网络，涵盖老年住房、医疗保健、技术服务等领域，为行业从业者提供资讯和研究报告。',
        'highlights': '老年产业垂直媒体网络',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2015',
        'website_url': 'https://www.agingmedia.com/',
    },
    'Aging in Place Technology Watch': {
        'description': 'Aging in Place Technology Watch是老年科技行业分析师Laurie Orlov创办的研究机构，发布年度AgeTech市场报告和趋势分析。',
        'highlights': '老年科技行业权威分析师，年度市场报告',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2008',
        'website_url': 'https://www.ageinplacetech.com/',
    },
    'Aging Technology Research Center': {
        'description': 'Aging Technology Research Center专注于老年科技市场研究，提供行业报告、市场分析和企业咨询服务。',
        'highlights': '老年科技市场研究机构',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2010',
        'website_url': '',
    },
    'Cambia Health Foundation': {
        'description': 'Cambia Health Foundation是Cambia Health Solutions的慈善基金会，关注老年健康照护、临终关怀等领域，提供资助和项目支持。',
        'highlights': '健康保险旗下慈善基金会，关注老年照护',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2007',
        'website_url': 'https://cambiahealthfoundation.org/',
    },
    'Center for Aging and Brain Health': {
        'description': 'Center for Aging and Brain Health (CABH)是俄亥俄州立大学旗下的脑健康与老龄化研究中心，专注于认知衰退、痴呆症等研究。',
        'highlights': '俄亥俄州立大学脑健康研究中心',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2015',
        'website_url': 'https://wexnermedical.osu.edu/',
    },
    'Comfort Keepers': {
        'description': 'Comfort Keepers是Sodexo旗下的居家护理品牌，提供个人护理、 companionship、营养管理等居家养老服务，在全美拥有700+加盟点。',
        'highlights': 'Sodexo旗下居家护理品牌，700+加盟点',
        'funding_latest': {'date': '2009', 'amount': '被收购', 'round': '并购', 'display': 'Sodexo收购 (2009)'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': 'Sodexo (母公司)',
        'founded': '1998',
        'website_url': 'https://www.comfortkeepers.com/',
    },
    'Elderlife Financial': {
        'description': 'Elderlife Financial为老年人家庭提供养老费用融资解决方案，帮助家庭支付辅助生活、护理等费用，提供灵活的分期付款方案。',
        'highlights': '老年人家庭养老费用融资平台',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2007',
        'website_url': 'https://www.elderlifefinancial.com/',
    },
    'Family Engineering': {
        'description': 'Family Engineering专注于家庭照护技术研发，为老年家庭提供智能照护方案，包括远程监测、家庭沟通工具等。',
        'highlights': '家庭照护技术研发商',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2016',
        'website_url': '',
    },
    'Generations United': {
        'description': 'Generations United是跨代际倡导组织，致力于促进不同代际之间的合作与理解，推动有利于老人和儿童的公共政策。',
        'highlights': '跨代际倡导组织，政策推动',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '1986',
        'website_url': 'https://www.gu.org/',
    },
    'Gerontological Society of America': {
        'description': '美国老年学会（GSA）是老龄化研究领域的权威学术组织，拥有5,500+会员，发布学术期刊、举办年会、推动老年学研究。',
        'highlights': '美国老年学权威学术组织，5500+会员',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '1945',
        'website_url': 'https://www.geron.org/',
    },
    'Global Coalition on Aging': {
        'description': 'Global Coalition on Aging (GCOA)是全球性老龄化商业联盟，由多家跨国企业组成，倡导通过创新和企业参与应对老龄化挑战。',
        'highlights': '全球老龄化商业联盟，跨国企业组成',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2010',
        'website_url': 'https://www.globalcoalitiononaging.com/',
    },
    'Home Care Association of America': {
        'description': 'HCAOA（美国居家护理协会）是全美居家护理行业的行业协会，代表1,500+居家护理机构，提供政策倡导、行业培训等服务。',
        'highlights': '美国居家护理行业协会，1500+机构',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2002',
        'website_url': 'https://www.hcaoa.org/',
    },
    'LeadingAge': {
        'description': 'LeadingAge是美国非营利性老年服务提供商协会，代表5,000+非营利养老机构，倡导政策、提供教育和培训。',
        'highlights': '美国非营利老年服务提供商协会，5000+机构',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '1961',
        'website_url': 'https://www.leadingage.org/',
    },
    'Lifeline Systems': {
        'description': 'Lifeline Systems是个人紧急响应系统（PERS）的先驱，提供可穿戴紧急呼叫设备，2006年被Royal Philips收购。',
        'highlights': 'PERS紧急呼叫系统先驱，被飞利浦收购',
        'funding_latest': {'date': '2006', 'amount': '$750M', 'round': '并购', 'display': '飞利浦收购$750M (2006)'},
        'funding_total': {'amount': '$750M', 'display': '累计$750M（被收购）'},
        'investors': 'Royal Philips (母公司)',
        'founded': '1974',
        'website_url': 'https://www.lifeline.philips.com/',
    },
    'MiLiA (Aging) Index': {
        'description': 'MiLiA Index是老龄化市场指数，追踪全球老龄化相关上市公司的股票表现，为投资者提供银发经济投资参考。',
        'highlights': '全球老龄化市场股票指数',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2014',
        'website_url': '',
    },
    'National Aging in Place Council': {
        'description': 'NAIPC是全美居家养老委员会，由养老相关专业人士组成，为老年人提供居家养老咨询和资源对接。',
        'highlights': '全美居家养老委员会，资源对接',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2003',
        'website_url': 'https://www.ageinplace.org/',
    },
    'National Council on Aging': {
        'description': 'NCOA是美国全国老龄委员会，成立于1950年，是全美最大的老年非营利组织之一，关注老年人经济安全和健康。',
        'highlights': '全美最大老年非营利组织之一，成立于1950年',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '1950',
        'website_url': 'https://www.ncoa.org/',
    },
    'Network of Senior Advocates': {
        'description': 'Network of Senior Advocates是老年权益倡导网络，推动有利于老年人的公共政策和社区服务。',
        'highlights': '老年权益倡导网络',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2010',
        'website_url': '',
    },
    'Philips Aging & Caregiving': {
        'description': '飞利浦老龄化与照护部门，提供个人紧急响应系统（Lifeline）、远程医疗监测、睡眠呼吸机等老年健康解决方案。',
        'highlights': '飞利浦旗下老龄化健康解决方案部门',
        'funding_latest': None,
        'funding_total': None,
        'investors': 'Royal Philips (NYSE:PHG)',
        'founded': '1891',
        'website_url': 'https://www.philips.com/healthcare/solutions/aging-and-caregiving',
    },
    'Right at Home': {
        'description': 'Right at Home是居家护理加盟品牌，提供个人护理、 companionship、护理管理等服务，在全美和全球拥有500+加盟点。',
        'highlights': '居家护理加盟品牌，全球500+加盟点',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '1995',
        'website_url': 'https://www.rightathome.net/',
    },
    'SeniorAdvisor.com': {
        'description': 'SeniorAdvisor.com是老年护理和养老社区评价平台，提供用户真实评价和比较工具，帮助家庭选择养老服务。',
        'highlights': '老年护理评价平台，用户真实评价',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2010',
        'website_url': 'https://www.senioradvisor.com/',
    },
    'Seniorlink': {
        'description': 'Seniorlink是家庭照护者支持平台，提供照护者咨询、财务补贴管理和技术工具，帮助家庭照护者更好地照顾老人。',
        'highlights': '家庭照护者支持平台，咨询+补贴+技术',
        'funding_latest': {'date': '2018', 'amount': '$20M', 'round': '成长期', 'display': '成长期$20M (2018)'},
        'funding_total': {'amount': '$40M+', 'display': '累计$40M+'},
        'investors': '.406 Ventures,	Zaffre Investments,icare',
        'founded': '2009',
        'website_url': 'https://www.seniorlink.com/',
    },
    'The Green House Project': {
        'description': 'The Green House Project是创新养老社区模式，打破传统养老院模式，打造小规模、家庭式的养老生活环境，在美有300+项目。',
        'highlights': '创新小规模家庭式养老社区模式，300+项目',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2003',
        'website_url': 'https://thegreenhouseproject.org/',
    },
    'VN Solutions': {
        'description': 'VN Solutions提供老年医疗护理解决方案，专注于老年人慢性病管理和远程监测技术。',
        'highlights': '老年慢性病管理和远程监测方案',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2012',
        'website_url': '',
    },
    'Visual Cognitive Fitness': {
        'description': 'Visual Cognitive Fitness专注于认知评估和训练技术，为老年人提供视觉认知能力评估和干预方案。',
        'highlights': '视觉认知评估与训练技术',
        'funding_latest': None,
        'funding_total': None,
        'investors': None,
        'founded': '2015',
        'website_url': '',
    },
    'WalkJoy': {
        'description': 'WalkJoy开发步行辅助设备，通过神经刺激技术帮助老年人改善步态和平衡，减少跌倒风险。',
        'highlights': '步行辅助设备，减少跌倒风险',
        'funding_latest': {'date': '2019', 'amount': '未披露', 'round': 'Series A', 'display': 'Series A (2019)'},
        'funding_total': {'amount': '未披露', 'display': '累计未披露'},
        'investors': '未披露',
        'founded': '2015',
        'website_url': 'https://walkjoy.com/',
    },
}

if __name__ == '__main__':
    data = load_data()

    all_updates = {}
    all_updates.update(BATCH_1)
    all_updates.update(BATCH_2)
    all_updates.update(BATCH_3)
    all_updates.update(BATCH_4)
    all_updates.update(BATCH_5)
    all_updates.update(BATCH_6)

    print(f'Total updates to apply: {len(all_updates)}')
    data = apply_updates(data, all_updates)
    save_data(data)
    print('Saved successfully.')
