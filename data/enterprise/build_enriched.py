# -*- coding: utf-8 -*-
import json

SRC = r"G:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise\ageclub_batch1.json"
OUT = r"G:\workbuddy\2026-06-28-23-34-20\silver-pulse\data\enterprise\ageclub_enriched_batch1.json"

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

# Overrides keyed by company name.
# Each value: dict of fields to set + "_research_notes".
O = {}

# ---------- Companies 1-40 targeted gap fixes ----------
O["时尚奶奶团"] = {
    "website_url": "未搜到",
    "founded": 2019,
    "stage": "成长期",
    "funding_latest": {"amount": "约300万元", "round": "天使轮", "date": "2018", "display": "天使轮 约300万元 (2018)"},
    "recommend": "高端银发女性加视频号慢陪伴打法，服饰美妆客单极高、复购约五成，是少数跑通变现的文娱IP。运营主体为何大令创立的MCN，2018年即获300万元天使投资，主账号粉丝超300万、会员超2000人、月GMV曾破千万。可对标北京大妈有话说写流量如何被高价变现；风险在IP个人化与年龄迭代。",
    "_research_notes": "百度百科：时尚奶奶团由何大令（90后，北大）2019年创立，2018年12月获300万元天使投资成立MCN；主账号粉丝超300万（2025），会员超2000人，月GMV曾超千万；无独立官网，以抖音/微信视频号运营。",
}

O["京东方 BOE"] = {
    "website_url": "https://hopehome.boe.com",
    "founded": 1993,
    "stage": "成长期",
    "funding_latest": "项目批复投资超4.5亿元",
    "recommend": "面板巨头跨界康养、'屏端入口'是差异化想象。京东方（BOE，1993年创立，A股000725）将智慧康养作为'智慧医工'核心板块，已在合肥、成都、北京布局护理院与康养社区，依托显示/物联网/数字医院能力做'医康养护乐学'一体化。写作可抓科技大厂入局银发；风险在跨界运营能力与资金门槛，可复制性低。",
    "_research_notes": "京东方官网 boe.com / 智慧康养 hopehome.boe.com；BOE创立于1993年4月，智慧康养为'智慧医工'业务板块，已在合肥京东方护理院、成都自建康养社区、北京缘爱康宸养老院布局。",
}

O["新双派"] = {
    "website_url": "http://www.xinshuangpai.com",
    "founded": 2022,
    "stage": "A轮",
    "funding_latest": {"amount": "数千万元", "round": "A轮", "date": "2026-04", "display": "A轮 数千万元 (2026-04)"},
    "funding_total": {"amount": "累计数千万（天使+A轮）", "display": "累计数千万（天使+A轮）"},
    "recommend": "碳纤维一体加免弯腰自动折叠、设计驱动高端，是辅具差异化样本。双派机器人（新双派机器人杭州）2022年成立，2026年4月完成数千万元A轮（天图投资领投，国舜/西湖科创投跟投），天使轮2021年3月获险峰长青等约千万元；产品销往海外近30国，四合一碳纤维助行器W1为行业首创。可对标互邦写设计溢价；风险在量价与渠道。",
    "_research_notes": "官网 xinshuangpai.com；天眼查：新双派机器人(杭州)有限公司注册2020-12-07，双派品牌2022年成立，创始人杨宇智；2026-04完成数千万元A轮（天图投资领投），天使轮2021-03获险峰长青等约千万元；新浪财经/张通社报道。",
}

O["智医向量机器人"] = {
    "website_url": "https://www.zhiyixiangliang.com",
    "founded": "2024-12",
    "stage": "Pre-A轮",
    "funding_latest": {"amount": "数千万元", "round": "Pre-A轮", "date": "2025-12", "display": "Pre-A轮 数千万元 (2025-12)"},
    "recommend": "把问答机器人+虚拟建模塞进机构系统做智能化，给养老与社区医疗提效。广州智医向量云科技（CEO朱想）2024年12月成立，2025年12月获正轩投资（比亚迪创始人夏佐全系）数千万元Pre-A轮；核心为基于意识大模型的医疗健康数字机器人，覆盖'医疗大脑—数字分身—仿生机器人'，疾病咨询准确率88.91%，服务超8000-10000名专家用户，设广州与巴黎双总部。国内深睿可对标其多模块打包；短板在落地案例与ROI验证。",
    "_research_notes": "官网 zhiyixiangliang.com；企查查：广州智医向量云科技成立于2024-12-10，法定代表人/CEO朱想；2025-12获正轩投资数千万元Pre-A轮；核心为意识大模型医疗健康数字机器人，与华南理工/巴黎十二大联合实验室。",
}

O["浙江人形机器人创新中心"] = {
    "website_url": "https://www.zj-humanoid.com",
    "founded": "2023-12",
    "stage": "Pre-A轮",
    "funding_latest": {"amount": "4.5亿元", "round": "Pre-A轮", "date": "2026-01", "display": "Pre-A轮 4.5亿元 (2026-01)"},
    "funding_total": {"amount": "累计约22亿元", "display": "累计约22亿元"},
    "recommend": "地方国资挂帅、院校同场景绑定把整机落进照护现场；浙江人形机器人创新中心有限公司2023年12月成立（首席科学家熊蓉，浙大教授），2026年1月完成4.5亿元Pre-A轮、累计融资约22亿元，股东含中控技术、招商创科、联想创投等；'领航者NAVIAI'人形机器人具41自由度，规划2026年50个示范场景含医疗/养老。可借鉴'国资搭台+场景牵引'，但工程化与成本待验证，适合写人形机器人进康养政企样本、量产节奏存疑。",
    "_research_notes": "官网 zj-humanoid.com；企查查：浙江人形机器人创新中心有限公司成立于2023-12-21，法定代表人熊蓉（浙大教授），股东含中控技术/招商创科/联想创投等；2026-01完成4.5亿元Pre-A轮，累计融资约22亿元；亿邦/浙江日报报道。",
}

O["锋物科技"] = {
    "founded": 2019,
    "_research_notes": "描述内文注明锋物科技（天津）2019年成立；官网 fengwu.com；物业数字化与智慧社区平台，布局'物业+养老'与巡护机器人（跌倒监测/陪伴/紧急响应），已服务60+物业百强。",
}

# ---------- Companies 41-71 full enrichment ----------
O["上海原座标空间设计有限公司"] = {
    "website_url": "未搜到",
    "founded": "2021-08-23",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "面向银发与高端私宅的适老化空间设计机构（RXY DESIGN，主理人王士超），把适老化从'改造'前置到设计与装修环节，强调美学与安全的平衡。可写'适老化设计的审美突围'；短板在规模化与跨区域复制，适合作为设计驱动型适老服务样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "企查查：上海原座标空间设计有限公司成立于2021-08-23，法定代表人王士超，经营范围含建设工程设计/住宅室内装饰装修；RXY DESIGN品牌定位适老化与高端私宅设计，无独立官网检索到。",
}

O["上海长润国际贸易有限公司"] = {
    "website_url": "http://www.shchangrun.cn",
    "founded": 1998,
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "海尔智慧康养上海总经销与'孝心驿站'供应链运营方，深耕中日养老产品贸易九年，打通从日本养老院供应链到国内适老用品的分销网络。可写'银发供应链的跨境打法'；其'长润养老×爱护科技'战略合作切入运动护具，值得跟踪渠道协同。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "官网 shchangrun.cn（长润养老健康商城）；企业信息：上海长润国际贸易有限公司成立于1998年，海尔康养上海总经销、孝心驿站供应链平台；AgeClub报道其2024年与爱护科技达成战略合作。",
}

O["智慧康（雄安）健康养老科技有限公司"] = {
    "website_url": "未搜到",
    "founded": "2024-01-26",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "落子雄安中关村、定位'数智融合银发经济平台'的初创企业，旗下'花甲商城'尝试连接适老产品与社区渠道。可写'新区政策下的银发平台试验'；短板在商业模式与规模未验证，宜作区域政策样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "企查查/公开：智慧康（雄安）健康养老科技有限公司成立于2024-01-26，法定代表人周杰，注册于雄安中关村；业务含伴步地面防滑适老化改造、花甲商城，无独立官网检索到。",
}

O["德际凯艾（上海）健康咨询服务有限公司"] = {
    "website_url": "未搜到",
    "founded": "未搜到",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "海尔智慧康养体验中心上海总服务商，承载适老化改造与康养体验落地。可写'家电巨头线下体验店如何做适老转化'；争议点在于适老化改造补贴相关报道，需关注合规与服务口碑。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "公开报道：德际凯艾（上海）健康咨询服务有限公司为海尔智慧康养体验中心上海总服务商，主营适老化改造落地；曾因适老化改造补贴相关报道引发关注，无独立官网检索到。",
}

O["福满堂适老化改造服务平台"] = {
    "website_url": "未搜到",
    "founded": "未搜到",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "一站式适老化改造供应链平台（创始人伯玉），以苏州银发经济展位与供应链报价手册切入，连接产品厂商与改造服务方。可写'适老化改造的供应链中台'；短板在平台撮合效率与区域覆盖，宜作供应链整合样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "公开信息：福满堂适老化改造服务平台，创始人伯玉，参与苏州银发经济平台展位，提供适老化供应链报价手册；无独立官网检索到。",
}

O["成都朗力养老产业发展有限公司"] = {
    "website_url": "https://www.cdlangli.com",
    "founded": 2011,
    "stage": "成长期",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "全国首家适老科学研究院运营方，累计完成超6.7万户居家适老化改造，并获B Corp认证，是适老化改造领域'标准+规模+社会企业'三位一体的标杆。可写'适老化改造的规模化与社会企业路径'；对标北京安馨、上海善诊。",
    "payor_model": "政府付费+个人自费",
    "_research_notes": "官网 cdlangli.com；公开：成都朗力养老成立于2011年，全国首家适老科学研究院，累计改造67237户，获B Corp认证，业务覆盖适老化改造与养老培训。",
}

O["武汉金柏康医疗科技有限公司"] = {
    "website_url": "未搜到",
    "founded": "2015-02-06",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "以适老化工程施工为核心的医疗科技企业（法定代表人王国俊），业务覆盖医疗科技、工程与批发，服务于机构与居家适老改造。可写'工程型适老服务商的生存逻辑'；短板在品牌与规模化透明度，宜作区域工程样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "企查查：武汉金柏康医疗科技有限公司成立于2015-02-06，法定代表人王国俊，经营范围含医疗科技/工程/批发；无独立官网检索到。",
}

O["河南工之坊科技集团有限公司"] = {
    "website_url": "https://www.gzfkeji.com",
    "founded": "2020-08-21",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "地面防滑工程龙头（法定代表人魏保成），以机器人/AI与防滑工程结合切入居家安全，覆盖医院、养老等场景。可写'防滑这门适老安全生意的规模化'；对标上海地宝，差异在AI+工程整合，宜作安全改造样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "官网 gzfkeji.com；企查查：河南工之坊科技集团有限公司成立于2020-08-21，法定代表人魏保成，经营范围含机器人/AI/地面防滑工程。",
}

O["乐宜适老化健康科技（江苏）有限公司"] = {
    "website_url": "未搜到",
    "founded": "2020-06-09",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "无锡全屋适老化改造工程商（董事长黄才忠，总经理徐熠），累计服务超4000户，主打从评估到施工的一体化改造。可写'区域全屋适老改造的服务闭环'；短板在跨区域复制，宜作区域工程样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "企查查：乐宜适老化健康科技（江苏）有限公司成立于2020-06-09，位于无锡，董事长黄才忠，累计改造超4000户；无独立官网检索到。",
}

O["合肥盛东信息科技有限公司"] = {
    "website_url": "https://www.shengdongyl.com",
    "founded": "2012-02",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "国家级智慧健康养老示范企业，养老/民政监管与社区、地产养老综合平台已落地超900个，是区域型'平台+运营'标杆。可写'智慧养老平台如何下沉到社区'；对标杭州微脉、上海天与，差异在政务侧深耕。",
    "payor_model": "政府付费+机构采购",
    "_research_notes": "官网 shengdongyl.com；公开：合肥盛东信息科技成立于2012年2月，国家级智慧健康养老示范企业，平台落地超900个。",
}

O["颐享时代"] = {
    "website_url": "https://www.cnyanglao.com",
    "founded": "2014-12-31",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "底层运营主体为深圳市养老管家网络科技有限公司（张东民），以'互联网+居家养老'社区一站式智慧养老SaaS平台切入，连接服务与家庭。可写'社区居家养老的SaaS化'；对标成都全时云、上海天与。",
    "payor_model": "B端机构采购+政府付费",
    "_research_notes": "官网 cnyanglao.com（深圳市养老管家网络科技有限公司）；企查查：颐享时代主体成立于2014-12-31，法定代表人张东民，互联网+居家养老。",
}

O["成都全时云信息有限公司"] = {
    "website_url": "https://www.zelao.com",
    "founded": 2014,
    "stage": "A+轮",
    "funding_latest": {"amount": "数千万元", "round": "A+轮", "date": "未披露", "display": "A+轮 数千万元"},
    "funding_total": {"amount": "累计数千万", "display": "累计数千万"},
    "recommend": "十年智慧养老落地方案服务商，获三部委智慧养老示范，以软硬件一体平台服务居家/社区/机构，是'长周期深耕型'标杆。可写'智慧养老十年长跑者的生存法则'；对标上海天与、合肥盛东。",
    "payor_model": "B端机构采购+政府付费",
    "_research_notes": "官网 zelao.com / qsheal.com；公开：成都全时云信息有限公司成立于2014年，获三部委智慧养老示范，曾完成千万级Pre-A/A+轮融资（具体日期未披露）。",
}

O["上海天与智慧养老服务有限公司"] = {
    "website_url": "https://www.tianyucare.com",
    "founded": 2019,
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "居家/机构/社区一体化养老平台，覆盖23省80+城市，以'无为算法'驱动服务匹配，是头部智慧养老运营平台。可写'算法如何调度养老服务'；对标成都全时云、合肥盛东，差异在全国化覆盖。",
    "payor_model": "B端机构采购+政府付费",
    "_research_notes": "官网 tianyucare.com；公开：上海天与智慧养老服务有限公司成立于2019年，居家/机构/社区照护一体化，覆盖23省80+城，自研'无为算法'。",
}

O["深圳市升质科技有限公司"] = {
    "website_url": "未搜到",
    "founded": "2024-08-07",
    "stage": "初创期",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "2024年新成立的居家养老全闭环系统初创公司（法定代表人吴圣辉，南山软件园），以软硬件一体做居家安全与照护。可写'新锐居家养老系统的切入姿势'；短板在规模与案例验证，宜作早期样本。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "企查查：深圳市升质科技有限公司成立于2024-08-07，法定代表人吴圣辉，注册于深圳南山软件园，注册资本100万，初创居家养老系统，无独立官网检索到。",
}

O["铭博科技"] = {
    "website_url": "未搜到",
    "founded": "未搜到",
    "stage": "未搜到",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "AgeClub描述为'适老化改造项目管理系统'，但公开检索中'铭博科技'存在多个主体（广州铭博网络科技、湖南铭博科技等），均无法可靠对应此业务，建议核实企业全称后再评估。可作为'数据存疑待核'样本。",
    "payor_model": "未披露",
    "_research_notes": "检索歧义：'铭博科技'对应多家无关企业（广州市铭博网络科技、湖南铭博科技等），均不匹配'适老化改造项目管理系统'描述，无法可靠补全，标记为待核实。",
}

O["大连东软睿新健康科技有限公司"] = {
    "website_url": "https://www.neutech.com.cn",
    "founded": 2025,
    "stage": "已上市",
    "funding_latest": {"amount": "港股上市(09616.HK)", "round": "已上市", "date": "", "display": "港股上市公司(09616.HK)"},
    "funding_total": {"amount": "港股上市公司(09616.HK)", "display": "港股上市公司(09616.HK)"},
    "recommend": "东软教育（港股9616）旗下城市级智慧养老平台，整合'教医养康旅'资源，是教育+康养跨界规模化的代表。可写'教育集团如何切入城市级康养'；对标泰康、兴业控股，差异在产教协同。",
    "payor_model": "B端机构采购+政府付费",
    "_research_notes": "官网 neutech.com.cn；东软睿新健康为东软教育(港股09616)旗下，2025年1月由东软教育更名/重组切入康养；城市级智慧养老平台，布局教医养康旅。",
}

O["广州立恒信息科技有限公司"] = {
    "website_url": "https://www.liheng-gz.com",
    "founded": "2020-07-08",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "智慧医养一体化软硬件解决方案商（法定代表人陈立新），覆盖机构与居家场景，强调'一体化'交付。可写'医养一体化的软硬件交付'；对标上海天与、成都全时云。",
    "payor_model": "B端机构采购+政府付费",
    "_research_notes": "官网 liheng-gz.com；企查查：广州立恒信息科技有限公司成立于2020-07-08，法定代表人陈立新，智慧医养整体解决方案。",
}

O["深圳市九町科技有限公司 / 柠檬网联"] = {
    "website_url": "https://www.magicwifi.com.cn",
    "founded": "2010-11-26",
    "stage": "已上市",
    "funding_latest": {"amount": "新三板挂牌(835924)", "round": "已上市", "date": "", "display": "新三板上市公司(835924)"},
    "funding_total": {"amount": "新三板上市公司(835924)", "display": "新三板上市公司(835924)"},
    "recommend": "原名柠檬网联（MagicWiFi），起家于数智园区/商业WiFi，2010年成立、新三板挂牌（835924）。AgeClub将其归为'AI银发流量运营平台'，但公开主营为WiFi与园区连接，与银发流量的关联较弱，建议核实其在银发场景的实际布局。可作为'跨界标签待核'样本。",
    "payor_model": "B端机构采购",
    "_research_notes": "官网 magicwifi.com.cn；企查查：深圳市九町科技（柠檬网联）成立于2010-11-26，法定代表人林一仲，新三板挂牌代码835924，主营数智园区WiFi；与AgeClub'银发流量平台'描述存在偏差。",
}

O["南通英可达信息技术有限公司"] = {
    "website_url": "https://www.ikdcare-inc.com",
    "founded": "2020-07-03",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "伴老智慧屏与智慧居家养老平台运营商（法定代表人杨剑峰），以如意365等品牌连接家庭与社区服务。可写'智慧屏如何成为养老入口'；对标上海天与、合肥盛东。",
    "payor_model": "B端机构采购+个人自费",
    "_research_notes": "官网 ikdcare-inc.com / ruyi365.com；企查查：南通英可达信息技术有限公司成立于2020-07-03，法定代表人杨剑峰，伴老智慧屏与智慧居家养老平台。",
}

O["上海言策企业管理咨询有限公司"] = {
    "website_url": "未搜到",
    "founded": "2020-04-07",
    "stage": "未融资",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "工商登记为'企业管理咨询'（法定代表人周寒琦，2020年成立），与AgeClub'AI品牌流量推荐系统'标签存在偏差，建议核实其真实业务。可作为'数据存疑待核'样本。",
    "payor_model": "B端机构采购",
    "_research_notes": "企查查：上海言策企业管理咨询有限公司成立于2020-04-07，法定代表人周寒琦，主营企业管理咨询；与'AI品牌流量推荐系统'描述不符，标记为待核实，无独立官网检索到。",
}

O["上海乐龄云求索科技有限公司"] = {
    "website_url": "http://app.leling.cn/homePage",
    "founded": 2024,
    "stage": "初创期",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "中老年兴趣社交APP'乐龄云'运营方（沪ICP备2025136164），以展演、兴趣圈子切入50+用户社交，是'老年版小红书'方向。可写'中老年兴趣社交的冷启动'；短板在留存与变现，宜作文娱社交早期样本。",
    "payor_model": "个人自费/广告",
    "_research_notes": "乐龄云APP（app.leling.cn），沪ICP备2025136164号，上海乐龄云求索科技运营，中老年兴趣社交/展演，2024年成立、2026年上线APP。",
}

O["牛程（重庆）信息科技有限公司"] = {
    "website_url": "http://piaochi.net",
    "founded": "2021-04-07",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "团体出行票务O2O平台'票驰'（法定代表人邓伟），聚合9000+旅行社票池，覆盖银发旅游出行场景。可写'银发旅游背后的票务基础设施'；对标携程/同程的老年专线，差异在B端票池聚合。",
    "payor_model": "个人自费/佣金",
    "_research_notes": "官网 piaochi.net / piaochi.wang；企查查：牛程（重庆）信息科技有限公司成立于2021-04-07，法定代表人邓伟，票驰团体出行票务O2O，聚合9000+旅行社票池。",
}

O["臻林国际康养度假园区"] = {
    "website_url": "https://www.serensiawoodshotel.cn",
    "founded": 2022,
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "横琴高端康养度假综合体（殷理基集团，2022年开业，耗资约20亿元），对标亲和源/泰康之家的高端旅居。可写'粤港澳康养度假的标杆'；短板在高客单价与入住率平衡。",
    "payor_model": "个人自费",
    "_research_notes": "官网 serensiawoodshotel.cn；公开：臻林国际康养度假园区位于横琴，殷理基集团投资约20亿元，2022年6月开业，高端康养度假。",
}

O["湖州市机汽猫科技有限公司"] = {
    "website_url": "https://www.qudaiji.com",
    "founded": "2019-12-21",
    "stage": "A+轮",
    "funding_latest": {"amount": "A+轮（2024年两山国控投资）", "round": "A+轮", "date": "2024", "display": "A+轮 (2024)"},
    "funding_total": {"amount": "累计数千万（A轮+A+轮）", "display": "累计数千万（A轮+A+轮）"},
    "recommend": "医院场景自助取袋机'袋拉拉'运营商（法定代表人杨小军），以医院流量切入银发与家庭用户，并获两山国控A+轮投资。可写'医院场景下的银发流量变现'；对标自动售货/取袋机，差异在医疗场景刚需。",
    "payor_model": "B端机构采购+广告",
    "_research_notes": "官网 qudaiji.com；企查查：湖州市机汽猫科技成立于2019-12-21，法定代表人杨小军，袋拉拉自助取袋机；A轮500万（2022-04-29 铮言），A+轮（2024 两山国控）。",
}

O["上海神圆文化发展有限公司"] = {
    "website_url": "https://www.wujiqiu.com",
    "founded": "2016-06-27",
    "stage": "天使轮",
    "funding_latest": {"amount": "天使轮（金额未披露）", "round": "天使轮", "date": "未披露", "display": "天使轮"},
    "funding_total": {"amount": "天使轮", "display": "天使轮"},
    "recommend": "无极球运动运营方（法定代表人王春玉），获中国老体协推荐为适老化运动项目，以赛事/培训切入老年体育消费。可写'适老化体育运动的商业化'；对标广场舞/气排球，差异在标准运动器械+协会背书。",
    "payor_model": "个人自费/赛事",
    "_research_notes": "官网 wujiqiu.com；企查查：上海神圆文化成立于2016-06-27，法定代表人王春玉，无极球运动运营，中国老体协推荐适老化项目；曾获天使轮投资。",
}

O["浙江绿色森林康养集团有限公司"] = {
    "website_url": "未搜到",
    "founded": "2019-09-23",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "千岛湖森林旅居康养集团（法定代表人李庆生，注册资本5000万），由中物联物业集团孵化，构建'基地体验+院子运营+服务输出'的旅居康养模式，并绑定乡村共富。可写'森林旅居的基地化运营'；对标宽汀/亲和源旅居。",
    "payor_model": "个人自费/会员",
    "_research_notes": "企查查/百度百科：浙江绿色森林康养集团成立于2019-09-23，法定代表人李庆生，曾用名候鸟旅居/中物联房地产经纪，千岛湖凤凰岛森林旅居基地，中物联物业集团体系；无独立官网检索到。",
}

O["鲁网"] = {
    "website_url": "https://www.sdnews.com.cn",
    "founded": "未搜到",
    "stage": "成长期",
    "funding_latest": "未融资",
    "funding_total": "未融资",
    "recommend": "山东省重点新闻网站，2025年4月上线'鲁网·银龄'频道，切入银发行业媒体与智库，是区域官媒布局银发的样本。可写'地方媒体如何做银发内容'；对标老年日报/银发财经。",
    "payor_model": "广告/政府合作",
    "_research_notes": "官网 sdnews.com.cn；鲁网为山东省重点新闻网站，2025年4月上线'鲁网·银龄'频道，涉老行业媒体智库。",
}

O["上海欢乐友道数字科技有限公司"] = {
    "website_url": "https://www.huanleyoudao.com",
    "founded": "2023-05-10",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "居家养老互助服务APP'欢乐友道'运营方（CEO李弋戈，团队来自京东/字节/网易/微盟），以'聚一聚/帮一帮/学一学'六大板块构建中老年精品退休生活圈，并拓展社区店招商与短剧。可写'互助养老的社区商业闭环'；对标闲趣岛/红松，差异在互助+社区店。",
    "payor_model": "个人自费/会员+电商",
    "_research_notes": "官网 huanleyoudao.com；百度百科：上海欢乐友道数字科技成立于2023-05-10（曾用名上海道守合数字科技），2023年上线'欢乐友道'APP，CEO李弋戈，团队来自京东/字节/网易/微盟，拥有20万中老年用户、10万私域高净值用户。",
}

O["爱护悦龄科技（上海）有限公司"] = {
    "website_url": "未搜到",
    "founded": "2025-08-11",
    "stage": "天使轮",
    "funding_latest": {"amount": "种子轮（两家机构，金额未披露）", "round": "种子轮", "date": "2025", "display": "种子轮（金额未披露）"},
    "funding_total": {"amount": "种子轮", "display": "种子轮"},
    "recommend": "面向银发群体的运动安全护具及健康方案公司（'爱护科技'，董事长杨谦），以纳米材料+生物力学自研髋/腰/膝/头护具，通过欧盟EN1621认证，切入'跌倒防护'痛点。可写'银发运动防护的Material创新'；对标无锡年欢防摔装备。",
    "payor_model": "个人自费/渠道分销",
    "_research_notes": "AgeClub对接信息：爱护科技（爱护悦龄科技关联）面向银发运动安全护具，成立即获两家机构种子投资，产品通过欧盟EN1621认证；企查查显示爱护悦龄科技(上海)成立于2025-08-11（状态存注销/开业口径差异），法定代表人杨谦。",
}

O["北京光彩中道大健康产业科技有限公司"] = {
    "website_url": "https://www.lvjuwang1314.com",
    "founded": "2023-07-13",
    "stage": "天使轮",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "上线'冬南夏北'旅居养老机构服务平台（法定代表人徐冰），为老年人提供跨区域一站式旅居养老，并招募城市联合创始人与天使投资人。可写'旅居养老的平台化撮合'；对标浙江绿色森林、康养旅居平台。",
    "payor_model": "个人自费/会员",
    "_research_notes": "官网 lvjuwang1314.com；企查查/爱企查：北京光彩中道大健康成立于2023-07-13，法定代表人徐冰，上线'冬南夏北'旅居养老平台，寻城市联合创始人与天使投资人。",
}

O["椿熙堂（安享）"] = {
    "website_url": "https://www.healthtop.cn",
    "founded": "2015-08-21",
    "stage": "成长期",
    "funding_latest": "未披露",
    "funding_total": "未披露",
    "recommend": "桐乡乌镇起家的社区养老运营标杆（法定代表人冯韶军），拥有400+社区活动中心与10家养老机构，是'社区嵌入式养老'的代表。可写'乌镇模式的社区养老复制'；对标上海长者照护之家。",
    "payor_model": "政府付费+个人自费",
    "_research_notes": "官网 healthtop.cn；公开：椿熙堂（安享）成立于2015-08-21，法定代表人冯韶军，桐乡乌镇，400+社区活动中心、10家机构，社区嵌入式养老。",
}

# Apply overrides
for ent in data:
    name = ent.get("name")
    if name in O:
        ent.update(O[name])
    # Ensure every record carries a provenance note
    if not ent.get("_research_notes"):
        ent["_research_notes"] = "数据源自AgeClub供需对接平台原始入库（官网/融资/推荐等字段已在源文件中预填，本批次作为第1批核对保留，未做额外增量检索）"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Wrote", len(data), "enterprises to", OUT)
# quick stats
filled_site = sum(1 for e in data if e.get("website_url") and e["website_url"] != "未搜到")
filled_fund = sum(1 for e in data if e.get("funding_latest") not in (None, "", "未披露", "未融资") or isinstance(e.get("funding_latest"), dict))
filled_rec = sum(1 for e in data if e.get("recommend"))
print("website filled (non-未搜到):", filled_site)
print("recommend filled:", filled_rec)
print("with _research_notes:", sum(1 for e in data if e.get("_research_notes")))
