# -*- coding: utf-8 -*-
import json, os

IN = r"G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/ageclub_batch4.json"
OUT = r"G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/ageclub_enriched_batch4.json"

with open(IN, encoding="utf-8") as f:
    data = json.load(f)

# Enrichment keyed by exact company name in input.
# Fields: website_url, founded, stage, funding_latest(dict|None),
#         recommend, crunchbase_url, payor_model, tag_l1, tag_l2, _research_notes
ENR = {
"喜悦盛年": {
    "website_url": "",
    "founded": "2016",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "国内领先的银发兴趣教育平台，2016年正式成立，以连锁联营模式在全国47城开出156个校区、覆盖学员超230万；旗下喜悦盛年/盛年文旅/盛年甄选三大子品牌协同发展，已与中国平安、携程等达成“老年大学优质合作伙伴”合作，构建“中老年教育+”跨界融合模式。",
    "payor_model": "C端会员/课程消费 + B端（平安、携程等渠道合作与供应链）",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "品牌主体为广州新晟信息科技有限公司/广州喜悦盛年文化策划有限公司（2025-11-05新设），品牌运营始于2016年；未检索到独立官网。"
},
"EF 海外游学": {
    "website_url": "https://www.ef.com.cn",
    "founded": "2005",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "EF英孚教育为全球知名私人语言教育机构（全球品牌始于1965年），其50+熟龄海外游学产品面向银发群体提供“语言学习+文化旅行”融合体验；国内由英爱孚文化交流咨询（上海）有限公司（2005年成立）运营，依托全球50多所语言学校资源，是高端银发出境游学的重要供给方。",
    "payor_model": "C端学费/游学产品",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "国内运营主体英爱孚文化交流咨询（上海）有限公司成立于2005-09-23；EF全球为私有企业，未融资。"
},
"自由量级（上海）智能科技有限公司": {
    "website_url": "https://web.yinchaoyongxian.com",
    "founded": "2023-07-18",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "2023年成立的AI音乐科技公司，自研“音潮”AI音乐大模型可15秒生成完整歌曲，连续两年担任WAIC官方主题曲创作方；面向普通用户与行业用户提供AI写歌、版权认证与发行服务，可探索AI音乐康养、适老文娱新场景。",
    "payor_model": "C端订阅/创作工具 + B端API与定制配乐",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网为音潮 web.yinchaoyongxian.com；注册资本3亿元，暂无公开融资记录。"
},
"深圳市吉吉鑫实业有限公司": {
    "website_url": "",
    "founded": "2021-06-21",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "深圳企业，2021年成立，公开工商信息显示主营珠宝首饰零售、日用品销售等（曾于2024年从1000万减资至50万）；与平台标注的“线下中老年门店综合体”定位存在差异，建议进一步核实其银发业务主体与品牌。",
    "payor_model": "零售/门店销售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "工商经营范围以珠宝/日用品零售为主，与AgeClub描述‘线下中老年门店综合体’不一致，疑似业务转型或品牌名不同，未检索到官网。"
},
"宁夏音色岁月文化传媒有限公司": {
    "website_url": "",
    "founded": "",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "据平台标注为宁夏中老年声乐社群/文娱机构（线下5000+中老年声乐学员），本次检索未匹配到对应的独立工商主体与官网信息，建议补充准确企业名称与统一社会信用代码以便核验。",
    "payor_model": "社群/课程与活动收费",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "无增量信息：未检索到“宁夏音色岁月文化传媒有限公司”确切工商主体与官网，仅见区域“塞上乐龄大学”等老年文娱动态。"
},
"四川环球假期国际旅行社": {
    "website_url": "",
    "founded": "1993-07-06",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "成立于1993年的老牌旅行社（集体所有制），年服务2万+中老年游客，布局银发旅游与出境游，通过平台化运营连接银发人群与产业资源，是西南地区重要的中老年旅游服务商。",
    "payor_model": "C端旅游产品",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "名称对应“四川环球假期旅行社”（1993-07-06，集体所有制）；另有“四川环球假日国际旅行社有限公司”（2015-12-24），二者不同，未检索到官网。"
},
"中筝文化": {
    "website_url": "https://www.chinazheng.com.cn",
    "founded": "2003-10-28",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2003年成立的北京中筝文化发展有限公司，以古筝艺术为核心，旗下中国古筝学院（袁莎创办）、知音堂等，累计40万+中老年古筝古琴学员；主办“天下筝会”等大型活动，提供线上教育+乐器产销+文化IP综合服务。",
    "payor_model": "课程/乐器销售 + 师资认证与品牌授权",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 www.chinazheng.com.cn；未融资。"
},
"深圳市海外国际旅行社有限公司": {
    "website_url": "http://www.otcsz.com",
    "founded": "1985-03-18",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "创办于1985年的国家特许经营出境游国际旅行社，年组织接待游客超50万人次，高端中老年南北极、出境定制游产品成熟，在深圳设有60多个营业部，本地市占率与品牌力强。",
    "payor_model": "C端旅游产品 + B端批发",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "官网 www.otcsz.com；私营未上市，未融资。"
},
"和爱至美（北京）文化传媒有限公司": {
    "website_url": "",
    "founded": "2014-12-02",
    "stage": "初创期",
    "funding_latest": None,
    "recommend": "2014年成立的北京文化传媒公司（自然人独资，注册资本10万元），据平台定位为中老年文娱IP孵化方向，公开工商与新闻信息有限，建议补充其银发业务的具体产品与运营数据。",
    "payor_model": "IP孵化/内容服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；公开信息有限。"
},
"尚德及象教育": {
    "website_url": "https://www.jixiangedus.com",
    "founded": "2020",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "及象教育2020年由美股上市教育集团核心团队创立，是国内中老年兴趣教育头部在线平台，累计服务超百万家庭、百万级中老年学员；构建“教育+科技+媒体+文旅”生态，师资涵盖清华美院、中央美院等名家，并自研“及象百宝箱”AI学习工具。",
    "payor_model": "C端课程/会员 + 文旅与文创产品",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "官网 www.jixiangedus.com；独立运营，未见对外融资披露。"
},
"山西小鬼闯天涯栏目组": {
    "website_url": "",
    "founded": "2020-06-28",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2020年成立（前身为2007年太原教育电视台“小鬼闯天涯”栏目），打造省级老年春晚、健康直播间等IP，兼具少儿与老年内容运营经验，是区域银发文娱内容服务商。",
    "payor_model": "内容/IP + 活动运营",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "主体为山西小鬼闯天涯文化传媒有限公司（2020-06-28）；未检索到官网。"
},
"寅锦旅行信息咨询（西宁）": {
    "website_url": "",
    "founded": "",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "据平台定位为西宁适老化房车游学、医护配套车队服务商，本次检索未匹配到确切工商主体（疑似与“寅锦/青海寅锦”相关企业无直接对应），建议补充准确企业名称与统一社会信用代码。",
    "payor_model": "C端银发游学/定制游",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "无增量信息：未检索到“寅锦旅行信息咨询（西宁）”确切主体。"
},
"景德镇陶溪川国际旅行社有限公司": {
    "website_url": "http://www.txcgl.cn",
    "founded": "2018-09-04",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2018年成立，景德镇陶文旅控股集团旗下国有文旅企业，主打陶瓷主题研学与银发文旅；2025年陶艺体验课程接待20万人次，并联动“游戏+文旅+城市IP”模式，是“文旅+IP”融合新场景代表。",
    "payor_model": "C端研学/旅游产品（国资平台）",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "国有控股，未融资；官网 www.txcgl.cn。"
},
"贝莱昆明健康产业控股有限公司": {
    "website_url": "",
    "founded": "2022-06-27",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2022年成立（曾用名昆明恋莺企业管理有限公司），布局云南康养旅居、康复与养老服务，经营范围含护理机构服务、康复辅具适配、人体干细胞技术开发等，依托昆明“旅居康养”产业机遇切入银发赛道。",
    "payor_model": "康养/旅居服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "未检索到官网；曾用名昆明恋莺，未融资。"
},
"合肥柏慕年美育学院": {
    "website_url": "",
    "founded": "2025-01-13",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "2025年新成立的合肥中老年高端艺术教育机构（主体为合肥柏慕年教育咨询有限公司），提供形体礼仪、旗袍走秀、朗诵、摄影、绘画、音乐等课程，定位“国内一流中老年美育”。",
    "payor_model": "C端课程/会员",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "2025-01-13成立，注册资本10万，未检索到官网。"
},
"洛阳腾韵阁信息科技有限公司": {
    "website_url": "",
    "founded": "2023-02-17",
    "stage": "初创期",
    "funding_latest": None,
    "recommend": "2023年成立的信息科技公司，据平台定位为国画直播私域团队，公开工商范围含艺术品经营、互联网销售、文艺创作等，建议补充其银发业务的具体规模与佐证信息。",
    "payor_model": "内容电商/私域",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"中科惠泽养老产业投资有限公司": {
    "website_url": "http://www.guatang.com",
    "founded": "2016-03-04",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2016年成立（关联中科惠泽体系始于2004年），以糖生物工程、壳寡糖健康产品为依托，布局养老养生地产、智能养生养老，与中国科学院大连化物所等产学研合作，产品覆盖近300个城市消费者。",
    "payor_model": "健康产品零售 + 养老地产/服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "关联北京中科惠泽糖生物工程技术有限公司（2004年创立，官网 guatang.com）；未融资。"
},
"一诺音乐器（上海）有限公司": {
    "website_url": "http://www.apollodigitalpiano.com",
    "founded": "2022-06-24",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2022年成立，APOLLO钢琴/智能乐器品牌；2026年联合太保家园推出智能乐器康养公开课（K1超级智能吉他、G1电吹管），以适老黑科技切入银发音乐美育与康养文娱渠道。",
    "payor_model": "智能乐器销售 + 康养渠道合作",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "官网 www.apollodigitalpiano.com；未融资。"
},
"苏州启教文化科技有限公司": {
    "website_url": "",
    "founded": "2024-05-21",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "2024年成立的苏州公司，主营中小学社会实践课程与银发旅居课程开发、营地运营，据AgeClub供需对接寻求对接社区、社群、艺术团体及老年大学，是银发旅居课程服务商。",
    "payor_model": "课程开发/营地运营（B端+C端）",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "2024-05-21成立；未检索到官网。"
},
"广西博创智能信息科技有限公司": {
    "website_url": "",
    "founded": "2022-06-15",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "2022年成立于南宁，据AgeClub定位为“老年教育嵌入式社区综合体运营方”，寻求对接老年教育、大健康品牌方，是区域银发社区综合体探索者。",
    "payor_model": "社区综合体运营/课程",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "2022-06-15成立；未检索到官网。"
},
"潮龄俱乐部": {
    "website_url": "",
    "founded": "",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "据平台定位为中老年文旅服务平台，本次检索未匹配到明确独立工商主体（公开信息多指向区域商超银发社群如“潮银俱乐部”或AgeClub平台本身），建议补充运营主体与统一社会信用代码。",
    "payor_model": "文旅/活动服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "无增量信息：未检索到“潮龄俱乐部”独立工商主体。"
},
"北京博学明辨科技有限公司": {
    "website_url": "https://www.babamama.com",
    "founded": "2019-05-17",
    "stage": "天使轮",
    "funding_latest": {"date": "2020-03", "amount": "100万美元", "round": "天使轮", "display": "2020年3月 天使轮 100万美元（多家知名投资机构）"},
    "recommend": "2019年成立（百合网创始人田范江二次创业），旗下“闲趣岛”App专注40+中老年社交、婚恋与兴趣社区，获天使轮100万美元；产品含精准交友匹配、兴趣群聊、在线歌房等，适老化设计，团队约17人。",
    "payor_model": "C端会员/增值服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["相亲"],
    "_research_notes": "官网 www.babamama.com，App xianqudao.com；天使轮2020-03。"
},
"河南人人教育信息咨询有限公司": {
    "website_url": "http://www.rrjywx.com",
    "founded": "2016-03-28",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2016年成立于郑州，主营职业技能与健康管理师等考证培训，据平台定位为康养从业证书培训，服务银发康养产业人才供给，是“银发职业教育”配套服务商。",
    "payor_model": "培训费/考证服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 www.rrjywx.com（另 rrjypx.com）；未融资。"
},
"浙江金颐文化创意有限公司": {
    "website_url": "",
    "founded": "2025-11-26",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "2025年新成立的杭州文化创意公司（主体为杭州金颐文化创意有限公司），经营范围含组织文化艺术交流、旅游策划、健康咨询等，据平台定位服务银发文旅活动；另存在强关联企业“浙江金颐智慧康养有限公司”（wizpathonline.com，AI+养老），建议厘清二者关系。",
    "payor_model": "活动策划/文创服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "名称对应杭州金颐文化创意有限公司（2025-11-26）；关联浙江金颐智慧康养（2024-05-11，AI养老）但非同一主体，未检索到官网。"
},
"乐事艺术学校": {
    "website_url": "http://www.leshiguitar.cn",
    "founded": "2024-01-26",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "武汉千喜乐事艺术学校2024年成立，面向成年人及中老年开展乐器等非传统兴趣培训（吉他等），构建“教育+文创”的中老年艺术学习场景；区域另有“南昌乐的事文化艺术学校（1999年）”同名近似主体，需区分。",
    "payor_model": "C端课程",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "对应武汉市千喜乐事艺术教育培训学校有限责任公司（2024-01-26，官网 leshiguitar.cn）；与南昌乐的事非同一主体。"
},
"英杰之旅": {
    "website_url": "http://www.china-pt.cn",
    "founded": "2005",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "2005年成立的英爱华人地接社（总部伦敦、北京设运作中心），专注英国爱尔兰高端定制旅游，在中国七大城市设分支，累计服务3万+客户，可延展面向高净值银发群体的出境定制游。",
    "payor_model": "C端定制旅游",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "官网 www.china-pt.cn；私有企业，未融资。"
},
"徐报创业投资（江苏）有限公司": {
    "website_url": "",
    "founded": "2022-03-16",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "2022年成立，徐州报业传媒集团（徐州日报社）全资创投平台，注册资本3000万元，布局文化传媒、健康、消费等早期投资，是传统媒体切入银发产业资本运作的代表，可关注其银发赛道被投组合。",
    "payor_model": "国资/集团母基金 + 被投企业",
    "tag_l1": ["文娱社交", "投资机构"], "tag_l2": ["兴趣社群"],
    "_research_notes": "徐州报业传媒集团全资子公司，未对外融资；原tag_l1为文娱社交，补充投资机构标签。"
},
"北京中视志合文化传媒有限公司": {
    "website_url": "http://www.zszhcctv.com",
    "founded": "2018-10-18",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2018年成立，央视一级广告代理（CCTV全频道资源），核心团队专注央视广告20年，服务蒙牛悠瑞奶粉等银发/中老年消费品品牌营销，是银发品牌传播与媒体投放服务商。",
    "payor_model": "B端品牌广告投放",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 www.zszhcctv.com；未融资。"
},
"石家庄憬颐网络技术服务有限公司": {
    "website_url": "",
    "founded": "2025-10-16",
    "stage": "种子期",
    "funding_latest": None,
    "recommend": "2025年新成立的石家庄公司（关联江苏憬颐/泽之泰体系），经营范围覆盖养老服务、健康咨询、物联网设备与可穿戴制造等，定位智慧养老+生活服务综合技术平台，尚处早期。",
    "payor_model": "养老服务/技术平台",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "2025-10-16成立，未检索到官网。"
},
"上海刚刚开始文化传播有限公司": {
    "website_url": "",
    "founded": "",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "据AgeClub披露，公司为一线城市45-60岁人群提供活动/课程/旅行的活动策划方，定位“刚刚开始”的银发生活方式，寻求链接50+高端产品与品牌；本次未检索到独立官网与工商增量信息。",
    "payor_model": "活动/课程/旅行策划（B端+C端）",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "无独立官网/工商增量信息：仅AgeClub供需帖披露业务定位。"
},
"山西新华国旅有限公司": {
    "website_url": "http://www.zgly365.com",
    "founded": "2008",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "山西老牌国际旅行社（2008年成立，太原设10家门店并布局线上电商），主营山西地接、国内游与出境游，可面向银发群体开发康养、红色、文化主题专线，区域品牌力强。",
    "payor_model": "C端旅游产品",
    "tag_l1": ["文娱社交"], "tag_l2": ["旅游"],
    "_research_notes": "官网 www.zgly365.com；另有工商记录显示成立2004-07-28，取平台常用2008年；未融资。"
},
"北京退休青年俱乐部": {
    "website_url": "",
    "founded": "",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "据AgeClub披露，为集旅游、研学、社交、养生于一体的中老年社群平台，寻求外地深入游学交付商；本次检索未匹配到独立工商主体（需与“新东方退休俱乐部”等同类银发社群品牌区分）。",
    "payor_model": "社群/游学活动",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "无增量信息：未检索到“北京退休青年俱乐部”独立工商主体，疑似银发社群品牌。"
},
"金护点教育": {
    "website_url": "http://www.jhdxl.com",
    "founded": "2019-11-29",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2019年成立的成都教育科技公司，品牌“金护点”，主打护理/康养类教育咨询与人才培训，拥有2项教育娱乐类商标，服务银发康养产业的人才供给。",
    "payor_model": "培训费/教育服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "官网 www.jhdxl.com；主体成都金护点教育科技有限公司，未融资。"
},
"北京润生堂化妆品研发有限公司": {
    "website_url": "http://www.bjrunshengtang.cn",
    "founded": "1996-05-24",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "1996年成立的北京化妆品研发企业（品牌“绯诗”染发），具备化妆品生产及第三类医疗器械资质，中老年染发产品曾涉监管通报，属银发个护供应链企业。",
    "payor_model": "C端零售 + 渠道/代工",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 bjrunshengtang.cn（部分平台显示无官网）；未融资；曾因染发产品被监管通报。"
},
"北京幸福益生高新技术有限公司": {
    "website_url": "http://www.bestlife365.org",
    "founded": "2013-10-11",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2013年成立，专注RegeSi再生硅生物材料，推出再生硅牙膏、口腔护理产品，并主办“银龄口腔健康论坛”；为北京市“专精特新”企业，自研材料可应用于骨修复与创面护理，具备银发口腔与创面护理场景。",
    "payor_model": "C端口腔/护理产品 + 材料B端",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 bestlife365.org；曾用名幸福益生（北京）生物科技；未检索到外部融资，疑似自筹。"
},
"长青（中国）日用品有限公司": {
    "website_url": "http://www.cni.com.cn",
    "founded": "1995",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "CNI国际集团（马来西亚）旗下，1995年在山东设立生产基地，2013年获商务部直销牌照，主营营养保健、个人护理等，外资直销体系成熟，产品可覆盖中老年健康消费。",
    "payor_model": "直销零售（会员制）",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "外资直销企业，未引入VC融资；官网 cni.com.cn。"
},
"上海夕昱商贸有限公司": {
    "website_url": "",
    "founded": "2023-05-17",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2023年成立，运营中老年功效个护品牌“昱芝夕（yuzhixi.com）”，聚焦银发人群洗护与肤发护理需求，属新兴银发个护消费品牌。",
    "payor_model": "C端个护零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "品牌官网 yuzhixi.com；公司主体未检索到官网，未融资。"
},
"立白": {
    "website_url": "http://www.liby.com.cn",
    "founded": "1994",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "立白集团1994年创立，主版主体为朝云集团（6601.HK）/立白体系，是国内日化龙头；2025年推出“如沐花海”银发洗衣液，切入适老化家居清洁赛道，渠道与品牌优势明显。",
    "payor_model": "C端日化零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "集团已上市（朝云集团6601.HK）；官网 liby.com.cn。"
},
"火人（北京）科技发展有限公司": {
    "website_url": "http://www.huorenfazhan.com",
    "founded": "2003-07-17",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "2003年成立，主打“双极水”消毒与皮肤护理产品，业务覆盖医用、日化与个护，可服务银发人群的创面护理与日常消毒场景，运营稳健。",
    "payor_model": "C端/医用个护零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 huorenfazhan.com；未融资。"
},
"恒安集团": {
    "website_url": "http://www.hengan.com",
    "founded": "1985-03-16",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "恒安国际（1044.HK）1985年创立，1998年港股上市，是国内卫生用品龙头；旗下“安而康”成人护理系列覆盖纸尿裤、护理垫等，是银发成人失禁护理的主流供给方。",
    "payor_model": "C端成人护理零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "港股上市（1044.HK）；官网 hengan.com。"
},
"北京泽它贸易有限公司（染博士）": {
    "website_url": "http://www.iranboss.com",
    "founded": "2021-07-01",
    "stage": "A轮",
    "funding_latest": {"date": "2021-03", "amount": "未披露", "round": "A轮", "display": "2021年3月 A轮 盛泽资本、达人说等；2019年5月天使轮 红杉中国、险峰长青、至临资本"},
    "recommend": "运营中老年染发品牌“染博士”，2019年5月获红杉中国、险峰长青、至临资本天使轮，2021年3月完成A轮（盛泽资本、达人说等），以“植物/遮盖”定位切入银发染发消费。",
    "payor_model": "C端染发产品零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "主体北京泽它贸易有限公司；官网 iranboss.com；存在天使轮与A轮融资。"
},
"武汉九生堂生物科技股份有限公司": {
    "website_url": "http://www.whjst.com",
    "founded": "1996-10-23",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "1996年成立，专注酶法多肽（多肽健康食品），2014年挂牌新三板（830833），是银发营养保健品研发生产企业，技术积累深厚。",
    "payor_model": "C端营养保健品",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "新三板挂牌（830833）；官网 whjst.com。"
},
"中国纸业投资有限公司": {
    "website_url": "http://www.chinapaper.com.cn",
    "founded": "1988-09-16",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "1988年成立，中国诚通集团全资子公司，主营纸业与供应链；作为成人护理用品（纸尿裤等）上游材料与需求方，是银发护理产业链的重要国资节点。",
    "payor_model": "B端供应链/材料",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "中国诚通全资子公司，未融资；官网 chinapaper.com.cn。"
},
"杭州欧诗漫珠宝": {
    "website_url": "http://www.osm-pearls.com",
    "founded": "1967",
    "stage": "成熟期",
    "funding_latest": None,
    "recommend": "隶属浙江欧诗漫集团（始创1967年），以珍珠饰品与珍珠美妆为主，面向中老年女性群体提供珍珠养颜与饰品消费，品牌历史与渠道积淀深厚。",
    "payor_model": "C端珍珠饰品/美妆",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "集团始创1967年；官网 osm-pearls.com / osm.com.cn；未融资。"
},
"洁柔・老桐学": {
    "website_url": "http://www.zsjr.com",
    "founded": "1999",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "中顺洁柔（002511.SZ，1999年创立）旗下“老桐学”银发方向（2023年设广东老桐学信息科技），布局适龄化终身教育与中老年产业，依托上市日化集团资源切入银发消费与教育。",
    "payor_model": "C端产品/教育",
    "tag_l1": ["文娱社交"], "tag_l2": ["教育"],
    "_research_notes": "母公司中顺洁柔A股上市（002511.SZ）；官网 zsjr.com。"
},
"杭州静博士": {
    "website_url": "http://www.drjing.cn",
    "founded": "2003",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2003年成立，浙江知名美容连锁（40万+会员），布局抗衰、AI美业与健康管理，客群含中高端银发女性，是“美丽健康”银发消费代表。",
    "payor_model": "C端美容/健康管理",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 drjing.cn；未融资。"
},
"河南领澜供应链管理有限公司": {
    "website_url": "http://www.linglansupply.com",
    "founded": "2015-10-09",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2015年成立，主营跨境电商与供应链管理，可为银发消费品（个护、营养品等）提供跨境采购与履约，是银生产业供应链服务商。",
    "payor_model": "B端供应链服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 linglansupply.com；未融资。"
},
"浙江东盛慧谷科技有限公司": {
    "website_url": "http://www.dshuigu.com",
    "founded": "2018-04-27",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2018年成立，打造“东盛慧谷”生命健康产业社区，集研发、孵化、康养服务于一体，引入医疗健康与养老相关企业，是银发健康产业空间运营方。",
    "payor_model": "园区运营/产业服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 dshuigu.com；未融资。"
},
"浦康养老服务促进中心": {
    "website_url": "",
    "founded": "2023-06-14",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2023年成立于上海浦东的民办非企业单位，聚焦养老产业咨询与“浦江银龄”等养老服务，属非营利性银发服务与行业组织。",
    "payor_model": "政府购买服务/行业服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "民办非企业（2023-06-14）；未检索到官网。"
},
"欧比护理用品（佛山）有限公司": {
    "website_url": "http://www.gdobee.com",
    "founded": "2022-04-24",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2022年成立（品牌“欧比”始于2012年），主营成人/银发护理用品，覆盖纸尿裤、护理垫等，是珠三角银发护理消费品牌。",
    "payor_model": "C端成人护理零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 gdobee.com；品牌欧比始于2012；未融资。"
},
"广州黑嘟嘟化妆品有限公司": {
    "website_url": "",
    "founded": "2016-08-25",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2016年成立，主营中老年染发剂等化妆品，以电商与私域渠道触达银发人群，是细分银发个护品牌。",
    "payor_model": "C端染发/个护零售",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"三边科技（上海）有限公司": {
    "website_url": "",
    "founded": "2021-03-30",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2021年成立于上海，主营科技推广与个护相关技术服务，据平台定位涉及银发个护赛道，建议补充其具体产品与运营数据。",
    "payor_model": "技术/个护服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"上海佰孝养老服务有限公司": {
    "website_url": "http://www.shbaixiao.com",
    "founded": "2023-10-19",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2023年成立，专注居家养老与适老化服务，提供上门照护、适老化改造等，是上海区域居家银发服务运营商。",
    "payor_model": "C端居家养老服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 shbaixiao.com；未融资。"
},
"长者之家衡水健康管理有限公司": {
    "website_url": "",
    "founded": "2019-09-20",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2019年成立，定位居家养老与日间照料健康管理，服务河北衡水区域银发人群，属社区嵌入式养老运营商。",
    "payor_model": "C端居家/日间照料",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"吉林省邻里之家康养服务有限公司": {
    "website_url": "http://www.jlllzj.cn",
    "founded": "2018-05-16",
    "stage": "A轮",
    "funding_latest": {"date": "2018", "amount": "未披露", "round": "A轮", "display": "2018年 A轮 原力基金投资"},
    "recommend": "2018年成立，运营“邻里之家”养老机构与社区康养服务，2018年获原力基金投资，是东北区域连锁养老运营代表。",
    "payor_model": "C端机构/社区养老",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 jlllzj.cn；2018年原力基金A轮投资。"
},
"中进宏康医疗科技（上海）有限公司": {
    "website_url": "http://www.xiao-v.net",
    "founded": "2021-09-13",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2021年成立，研发“纳米助浴舱”等适老化助浴设备，面向养老机构与居家提供智能助浴解决方案，切入银发洗浴护理刚需场景。",
    "payor_model": "设备销售/B端+服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 xiao-v.net；未融资。"
},
"广东卡莱雅科技实业有限公司": {
    "website_url": "",
    "founded": "2023-11-29",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2023年成立，由全屋定制向适老化转型的科技实业公司，布局适老化家居与银发空间改造，属银发适老消费制造端。",
    "payor_model": "适老定制/制造",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"首慈康健养老集团": {
    "website_url": "http://www.shouciyanglao.com",
    "founded": "2018-02-27",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2018年成立（集团2015年并购美国养老机构的经验基础），聚焦河南区域养老运营，提供机构养老、社区与居家服务，是中部银发养老连锁代表。",
    "payor_model": "C端机构/社区养老",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 shouciyanglao.com；未融资。"
},
"东原仁知服务集团": {
    "website_url": "http://www.dowellservice.com",
    "founded": "2003",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "东原仁知服务集团（2352.HK）2003年创立，2022年港股上市，以物业服务为基础延伸至社区养老与居家照护，依托社区入口服务银发人群。",
    "payor_model": "物业+养老服务（C端/B端）",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "港股上市（2352.HK，2022）；官网 dowellservice.com。"
},
"医联泰和（北京）健康管理有限公司": {
    "website_url": "http://www.yiliantaihe.cn",
    "founded": "2017-03-14",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2017年成立，主营健康管理与健康咨询，面向中老年群体提供体检、慢病与健康干预服务，是银发健康管理的服务端企业。",
    "payor_model": "C端健康管理服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 yiliantaihe.cn；未融资。"
},
"苏州昆山中老年服务公司": {
    "website_url": "",
    "founded": "",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "据平台标注为苏州昆山的中老年服务机构，本次检索未匹配到确切工商主体（仅见“昆山方缘中老年事务综合服务中心”等近似机构），建议补充准确企业名称。",
    "payor_model": "中老年服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "无增量信息：未检索到“苏州昆山中老年服务公司”确切主体。"
},
"江苏尚满天养老服务有限公司": {
    "website_url": "",
    "founded": "2017-09-14",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2017年成立，南京居家养老服务运营商，提供上门照护、助餐与社区养老支持，是江苏区域银发居家服务代表。",
    "payor_model": "C端居家养老服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"成都瑞式助浴陪诊养老服务有限公司": {
    "website_url": "http://www.ruisy.top",
    "founded": "2025-10-17",
    "stage": "种子期",
    "funding_latest": {"date": "2025", "amount": "未披露", "round": "种子轮", "display": "2025年 种子轮融资（上门助浴/陪诊）"},
    "recommend": "2025年成立，专注上门助浴、陪诊等银发刚需服务，已获种子轮融资，以标准化服务切入居家养老“最后一公里”，模式可复制性强。",
    "payor_model": "C端上门助浴/陪诊",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 ruisy.top；2025年种子轮融资。"
},
"上海茶寿健康管理有限公司": {
    "website_url": "",
    "founded": "2018-05-11",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2018年成立，主营健康管理与养老投资，面向银发人群提供健康干预与康养资源对接，属银发健康投资与运营平台。",
    "payor_model": "健康管理/投资",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
"江苏贤德居养老产业有限公司": {
    "website_url": "",
    "founded": "2024-02-06",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2024年成立（曾由8000万减资至1000万），布局南京康养中心与养老产业，是新兴区域银发康养资产运营方，建议关注其资本变动后的运营稳定性。",
    "payor_model": "C端康养/机构",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；曾大幅减资；未融资。"
},
"慧择保险经纪": {
    "website_url": "https://www.huize.com",
    "founded": "2011-10-14",
    "stage": "已上市",
    "funding_latest": None,
    "recommend": "慧择（HUIZ，2020年纳斯达克上市）2011年成立，是国内互联网保险经纪头部平台，提供重疾、医疗、养老等保险产品，可服务银发人群保障与养老规划需求。",
    "payor_model": "B端佣金/平台服务费",
    "tag_l1": ["金融保险"], "tag_l2": ["保险经纪"],
    "_research_notes": "纳斯达克上市（HUIZ，2020）；官网 huize.com；原tag_l1为文娱社交，调整为金融保险。"
},
"南京天一智慧养老": {
    "website_url": "http://www.tianyi99.com",
    "founded": "2019-07-29",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2019年成立，专注智慧养老与长护险服务，提供居家养老信息化、巡防与护理评估，是江苏区域银发数字化运营代表。",
    "payor_model": "政府/机构智慧养老项目",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 tianyi99.com；未融资。"
},
"海南华研胶原科技股份有限公司": {
    "website_url": "http://www.china-collagen.com",
    "founded": "2005-07-29",
    "stage": "B轮",
    "funding_latest": {"date": "2026-03", "amount": "未披露", "round": "B轮", "display": "2026年3月 B轮 华熙元祐等战略投资"},
    "recommend": "2005年成立，专注鱼胶原蛋白肽等生物活性蛋白研发生产，2026年3月获华熙元祐等战略投资（B轮），产品可服务银发营养与骨关节健康，是银发营养原料龙头。",
    "payor_model": "B端原料 + C端营养品",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "官网 china-collagen.com；2026-03 B轮战略投资。"
},
"深圳市梦马创新智能科技有限公司": {
    "website_url": "",
    "founded": "2025-07-01",
    "stage": "A轮",
    "funding_latest": {"date": "2026-06", "amount": "未披露", "round": "A轮", "display": "2026年6月 A轮 清水湾基金；早期获深圳科创学院出资设立（天使期）"},
    "recommend": "2025年成立，源自深圳科创学院，研发柔性外骨骼与神经交互康复机器人，2026年6月完成A轮（清水湾基金），切入银发康复与助行刚需，技术壁垒高。",
    "payor_model": "康复机器人销售/服务",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；早期获深圳科创学院出资设立，2026-06 A轮清水湾基金。"
},
"南通市数盾保联科技": {
    "website_url": "",
    "founded": "2025-08-01",
    "stage": "已注销",
    "funding_latest": None,
    "recommend": "2025年成立，定位养老数据与健康险系统（关联数盾信息科技），但已于2026年7月决议解散注销，建议关注其关联主体的持续运营情况，谨慎收录。",
    "payor_model": "数据/健康险系统（B端）",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "2025-08-01成立，2026-07-14决议解散（已注销）；未检索到官网。"
},
"深圳市琛源供应链": {
    "website_url": "",
    "founded": "2017-04-05",
    "stage": "成长期",
    "funding_latest": None,
    "recommend": "2017年成立，主营控糖降糖食品与检测设备的供应链服务，年营收约800万、服务5000+客户，是银发慢病（糖尿病）食品与监测的供应链节点。",
    "payor_model": "B端供应链 + C端慢病食品",
    "tag_l1": ["文娱社交"], "tag_l2": ["兴趣社群"],
    "_research_notes": "未检索到官网；未融资。"
},
}

# Normalize keys: input uses Chinese full-width parens in some names.
def norm(s):
    return s.replace("（", "(").replace("）", ")").strip()

enr_norm = {norm(k): v for k, v in ENR.items()}

out = []
n_website = 0
n_funding = 0
n_recommend = 0
missing = []

for rec in data:
    name = rec["name"]
    key = norm(name)
    new = dict(rec)  # preserve all original fields
    if key in enr_norm:
        e = enr_norm[key]
        new["website_url"] = e.get("website_url", "")
        new["founded"] = e.get("founded", "")
        new["stage"] = e.get("stage", "")
        new["funding_latest"] = e.get("funding_latest", None)
        new["recommend"] = e.get("recommend", "")
        new["crunchbase_url"] = e.get("crunchbase_url", "")
        new["payor_model"] = e.get("payor_model", "")
        # tag adjustments only if provided explicitly
        if "tag_l1" in e and e["tag_l1"] is not None:
            new["tag_l1"] = e["tag_l1"]
        if "tag_l2" in e and e["tag_l2"] is not None:
            new["tag_l2"] = e["tag_l2"]
        new["_research_notes"] = e.get("_research_notes", "")
        if e.get("website_url"):
            n_website += 1
        if e.get("funding_latest"):
            n_funding += 1
        if e.get("recommend"):
            n_recommend += 1
    else:
        new["_research_notes"] = "无增量信息"
        missing.append(name)
    out.append(new)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("Total records:", len(out))
print("Website enriched:", n_website)
print("Funding enriched:", n_funding)
print("Recommend enriched:", n_recommend)
print("Missing (no enrichment):", missing)
print("Written to:", OUT)
