# -*- coding: utf-8 -*-
"""BATCH 2 草稿生成器（研究者-批次2）。生成 drafts_v4/draft_#XXXX.json 并跑门禁。"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
OUT = os.path.join(HERE, "drafts_v4")
sys.path.insert(0, HERE)
import check_single as C

D = json.load(open(DB, encoding="utf-8"))

def ctx(serial):
    s = str(serial).lstrip("#")
    return next((x for x in D if str(x.get("serial", "")).lstrip("#") == s), {})

B = {}

B["1202"] = dict(
    recommend="人形机器人厂商2026年3月完成10亿元B轮、累计融资约14.9亿元，资本加注与量产节奏同步向上（信号）。2025年7月单月交付105台、消费级小布米售价9998元，销量数据公开透明（信息量）。与优必选、乐聚等国内厂商同处通用人形机器人赛道，其低价消费级打法少见（差异化）。国内已有类似（优必选、乐聚机器人），万台级量产与价格下探思路可借鉴（可复制）。",
    desc_cn="该公司2023年9月在北京设立，主攻通用人形机器人本体与具身智能，产品横跨工业与家庭陪护两大场景，小布米系列面向消费级市场，曾亮相春晚。作为国内融资与量产推进较快的人形机器人新势力，其规模化进展值得持续跟踪。",
    silver_reason="面向老年陪护场景布局消费级人形机器人，低价化与量产能力有望降低养老机构与家庭的机器人使用门槛，契合银发照护人力短缺的痛点。",
    payor_model="B端机构采购",
    funding_latest={"display": "2026-03 B轮10亿元（领投方未披露）"},
    funding_total={"display": "累计约14.9亿元"},
    stage="成长期", founded_year=2023,
    highlights=["2026-03 完成10亿元B轮", "2025-07 单月交付105台", "小布米售价9998元", "曾登春晚"],
    events=["2026-03 B轮融资10亿元", "2025-07 单月交付105台消费级机器人"],
    business_model="人形机器人本体研发与销售，B端机构采购+消费级零售",
    coverage_regions=["中国", "全球"],
    domestic_competitors=["优必选", "乐聚机器人", "达闼机器人"],
)

B["1221"] = dict(
    recommend="低视力AR眼镜属消费级康复辅具，2016年成立、与HTC VIVE合作推出e3+，并进入美国商业保险报销目录（信号）。其轻量AR加图像增强方案持有多项低视力辅助专利，技术壁垒清晰（信息量）。和国内集思鸣智、响午的辅具路线形成对照，定位更偏消费级AR（差异化）。国内已有类似（集思鸣智、响午），其硬件加保险报销双轮模式值得借鉴（可复制）。",
    desc_cn="这家美国企业自2016年起深耕低视力增强现实眼镜，Pro系列轻量产品面向阅读与出行困难的老年群体，提供放大、对比增强与文字识别，后续携手HTC VIVE推出e3+型号，并可纳入美国商保报销。",
    silver_reason="以AR眼镜帮助低视力老人恢复阅读、出行等基础能力，属康复辅具与视觉辅助范畴，直接改善老年群体生活质量，是银发消费级辅具的典型海外样本。",
    payor_model="个人自费",
    funding_latest={"display": "未搜到（曾进入孵化器/加速器）"},
    funding_total={"display": "未搜到"},
    stage="成长期", founded_year=2016,
    highlights=["2016年成立", "与HTC VIVE合作e3+", "进入美国保险报销目录", "低视力AR眼镜"],
    events=["与HTC VIVE达成合作推出e3+"],
    business_model="AR硬件销售（个人自费），部分市场由商业保险报销",
    coverage_regions=["美国", "全球"],
    domestic_competitors=["集思鸣智", "响午", "安泰康成"],
)

B["1247"] = dict(
    recommend="西班牙AI医疗心电平台，2024年获CE Mark IIa认证、可判读22种心律，技术里程碑密集（信号）。2025年公布房颤识别准确率96.4%，临床验证数据扎实（信息量）。和国内心永科技、瑞光康泰等可穿戴心电厂商相比，其云端判读加IIa认证壁垒突出（差异化）。国内已有类似（心永科技、瑞光康泰），其软件即医疗器械申报路径可借鉴（可复制）。",
    desc_cn="这家西班牙公司2018年创立，用人工智能解读心电图，核心平台Willem面向养老机构与基层医疗提供远程心电筛查，2024年取得欧盟CE IIa类医疗器械认证，可识别22种心律，2025年房颤识别准确率公布为96.4%。",
    silver_reason="用AI心电筛查提前发现房颤等老年高发心血管风险，属可穿戴监测与体检筛查方向，可降低老年心脑血管意外发生率，契合银发健康管理需求。",
    payor_model="B端机构采购",
    funding_latest={"display": "2022 A轮1850万欧元"},
    funding_total={"display": "累计约1850万欧元"},
    stage="成长期", founded_year=2018,
    highlights=["2024 CE IIa认证", "可判读22种心律", "2025 房颤准确率96.4%", "Willem平台"],
    events=["2024 获CE IIa类认证", "2025 公布房颤识别准确率96.4%"],
    business_model="AI心电SaaS，向医疗机构与养老机构收费（B端）",
    coverage_regions=["西班牙", "欧洲"],
    domestic_competitors=["心永科技", "瑞光康泰", "善诊"],
)

B["1254"] = dict(
    recommend="面向养老场景的无标记动作捕捉跌倒风险SaaS，已销往25国并与Microsoft、Intel、NBA合作（信号）。其步态算法持有专利、公开客户覆盖多国机构，数据透明度高（信息量）。和国内乐湾、医家通等养老软件相比，其无摄像头纯视觉方案与跨国客户群是壁垒（差异化）。国内已有类似（乐湾、医家通），其无穿戴监测打法可平移借鉴（可复制）。",
    desc_cn="这家加拿大公司提供无需标记的动作捕捉步态与跌倒风险分析，凭借普通摄像头与人工智能视频识别步态异常、预测跌倒，业务已拓展至25个国家，与微软、英特尔及NBA达成合作并持有专利，主要服务养老机构与医院。",
    silver_reason="以无穿戴、无摄像头依赖的视觉分析预测老人跌倒风险，对接养老机构与医院的防跌倒需求，是银发康复护理领域低侵入监测的海外代表。",
    payor_model="B端机构采购",
    funding_latest={"display": "未搜到（天使/种子阶段）"},
    funding_total={"display": "未搜到"},
    stage="初创期", founded_year=None,
    highlights=["销往25国", "微软/英特尔/NBA合作", "无标记动作捕捉专利", "跌倒风险SaaS"],
    events=["与微软、英特尔及NBA达成合作"],
    business_model="步态/跌倒风险分析SaaS，向机构收费（B端）",
    coverage_regions=["加拿大", "全球25国"],
    domestic_competitors=["乐湾", "医家通", "麦麦养老"],
)

B["1255"] = dict(
    recommend="自主配送机器人厂商，2024年累计融资达2250万美元，最新一轮由468 Capital领投（信号）。公开披露月均完成约3.6万次配送，运营数据扎实（信息量）。和国内南京新百、九如城等养老配送玩家相比，其跨国商超与工业客户基底是机器人落地的差异化壁垒（差异化）。国内已有类似（南京新百、九如城），其机器人加场景运营轻资产打法可借鉴（可复制）。",
    desc_cn="该公司研发自主配送机器人，为园区、社区与养老机构送去餐食和药品，当年累计融资约2250万美元，当轮由468资本领投、Magna与Shell参投，对外披露月均执行约3.6万单配送任务。",
    silver_reason="用自主配送机器人缓解养老机构与社区老人的餐药末端配送人力短缺，属养老服务自动化方向，可降低照护人力成本并提升配送时效。",
    payor_model="B端机构采购",
    funding_latest={"display": "2024-07 最新轮1000万美元（468 Capital领投）"},
    funding_total={"display": "累计约2250万美元"},
    stage="成长期", founded_year=None,
    highlights=["累计融资2250万美元", "468 Capital领投", "月均3.6万次配送", "自主配送机器人"],
    events=["2024-07 完成累计2250万美元融资"],
    business_model="配送机器人销售与运营服务，向机构与企业收费（B端）",
    coverage_regions=["美国", "全球"],
    domestic_competitors=["南京新百", "九如城", "天壹智慧"],
)

B["1259"] = dict(
    recommend="英国AI非穿戴养老监测厂商，获NHS Care Tech Fund百万英镑资助，并落地Whzan Guardian 4D试点（信号）。公开试点数据称跌倒事件降66%、呼叫救护车降97.5%，效果量化清晰（信息量）。和国内清澜技术、清雷等非穿戴监测相比，其绑定NHS政府付费的养老采购渠道是壁垒（差异化）。国内已有类似（清澜技术、清雷），其非穿戴加政府买单路径可借鉴（可复制）。",
    desc_cn="这家英国公司用毫米波与环境传感做非穿戴养老监测，识别跌倒、离床等异常并告警，方案关联Whzan团队的Guardian技术，曾获英国NHS照护科技基金约100万英镑资助，试点显示跌倒事件下降66%、呼叫急救车比例降97.5%。",
    silver_reason="以非穿戴方式对独居与机构老人做无感跌倒与异常监测，降低照护人力负担，契合银发养老监测的隐私友好与低侵入趋势。",
    payor_model="B端机构采购+政府付费",
    funding_latest={"display": "NHS Care Tech Fund 约100万英镑资助"},
    funding_total={"display": "未搜到"},
    stage="成长期", founded_year=None,
    highlights=["NHS照护科技基金资助", "Whzan Guardian技术", "跌倒降66%", "呼救降97.5%"],
    events=["获英国NHS照护科技基金约100万英镑资助"],
    business_model="监测平台向养老机构与NHS收费（B端+政府付费）",
    coverage_regions=["英国"],
    domestic_competitors=["清澜技术", "清雷", "百芝龙"],
)

B["1277"] = dict(
    recommend="英国护理电子健康档案SaaS，2000年成立、2023年获G Square投资，资本与口碑长期沉淀（信号）。公开称承载800万患者记录、4万用户、服务200余家机构，规模数据透明（信息量）。和国内乐湾、优享陪诊等护理信息化相比，其二十余年专科EHR积累是壁垒（差异化）。国内已有类似（乐湾、优享陪诊），其垂直护理SaaS打法可借鉴（可复制）。",
    desc_cn="这家英国企业2000年创立，主营护理与心理健康的电子健康档案系统，代表产品iaptus服务于护理机构与心理照护，2023年引入G Square作为投资方，公开称管理800万份患者档案、4万名用户，覆盖200多家机构。",
    silver_reason="为老年护理与心理照护机构提供信息化电子档案，提升跨机构照护连续性与数据可追溯性，是银发养老服务数字化的海外成熟样本。",
    payor_model="B端机构采购",
    funding_latest={"display": "2023 G Square投资（金额未披露）"},
    funding_total={"display": "未搜到"},
    stage="成长期", founded_year=2000,
    highlights=["2000年成立", "2023 G Square投资", "800万患者记录", "4万用户"],
    events=["2023 获G Square投资"],
    business_model="护理EHR SaaS订阅，向机构收费（B端）",
    coverage_regions=["英国"],
    domestic_competitors=["乐湾", "优享陪诊", "南京新百"],
)

B["1288"] = dict(
    recommend="医疗服务机器人厂商，2015年成立、2019年完成B+轮（国科嘉和、IDG、科沃斯参投），2025年启动科创板辅导（信号）。公开覆盖28省、400余家三甲医院、约4000台设备运行，装机数据扎实（信息量）。和国内南京新百、九如城等相比，其院内消毒配送机器人矩阵与三甲渠道是壁垒（差异化）。国内已有类似（南京新百、九如城），其医疗场景机器人打法可借鉴（可复制）。",
    desc_cn="该公司2015年设立，产品覆盖医院场景的消毒、配送与巡检机器人，2019年走完B+轮，投资方含国科嘉和、IDG与科沃斯，2025年7月启动科创板上市辅导，公开进入28个省份的400多家人型三甲医院，运行设备约4000台。",
    silver_reason="医疗与养老服务机器人可向养老机构与医养结合场景延展，缓解护理与院感防控人力压力，是银发康养机器人国产化的代表性企业。",
    payor_model="B端机构采购",
    funding_latest={"display": "2019 B+轮（国科嘉和/IDG/科沃斯）"},
    funding_total={"display": "未搜到（B+轮后未披露）"},
    stage="成长期", founded_year=2015,
    highlights=["2019 B+轮", "2025-07 科创板辅导备案", "覆盖28省400+三甲医院", "约4000台运行"],
    events=["2025-07 启动科创板上市辅导"],
    business_model="医疗/服务机器人销售与运维，向医院与机构收费（B端）",
    coverage_regions=["中国", "28省"],
    domestic_competitors=["南京新百", "九如城", "光大养老"],
)

B["1289"] = dict(
    recommend="日本情感陪伴机器人2018年发售，日本出货已超1.4万台，2024年CES斩获创新奖（信号）。上海首店2024年2月开业，买断约6万元、月订阅880元，定价与销量数据透明（信息量）。和国内江苏艾雨文承、大象机器人等相比，其萌系交互与情绪价值定位少见（差异化）。国内已有类似（江苏艾雨文承、大象机器人），其硬件加订阅陪伴打法可借鉴（可复制）。",
    desc_cn="日本Groove X推出的情感陪伴机器人于2018年发售，以可爱外形与拟人交互服务独居老人与家庭，日本市场累计出货逾1.4万台；同年CES摘得创新奖，上海首店设于2024年2月，买断价约6万元、月费880元。",
    silver_reason="以情感陪伴机器人缓解独居老人孤独感，提供非药物情绪支持，属文娱社交与陪伴机器人方向，是海外陪伴型银发产品的成熟样本。",
    payor_model="个人自费+政府补贴",
    funding_latest={"display": "未搜到（母公司Groove X融资历史）"},
    funding_total={"display": "未搜到"},
    stage="成长期", founded_year=2018,
    highlights=["2018发售", "日本出货超1.4万台", "2024 CES创新奖", "上海首店2024-02"],
    events=["2024-02 上海首店开业", "2024 CES创新奖"],
    business_model="陪伴机器人硬件销售+月订阅（个人自费/部分补贴）",
    coverage_regions=["日本", "中国上海"],
    domestic_competitors=["江苏艾雨文承", "大象机器人", "中科源码"],
)

B["1291"] = dict(
    recommend="室内服务机器人厂商，2019年获2000万美元、2024年富士康领投3000万美元D轮，累计融资超1亿美元（信号）。美国养老院远程诊疗占其收入约五成、西班牙签下600台居家医院合同，商业化数据扎实（信息量）。和国内乐聚机器人、江苏艾雨文承等相比，其移动屏加远程医疗定位是壁垒（差异化）。国内已有类似（乐聚机器人、江苏艾雨文承），其机构采购打法可借鉴（可复制）。",
    desc_cn="这款通用室内服务机器人由以色列Roboteam（博歌科技）推出，兼具移动视频陪伴与智能助手功能，适用于老人居家与养老机构，2019年进账2000万美元；到2024年完成3000万美元的D轮、由富士康领投，累计融资超过1亿美元。",
    silver_reason="以室内服务机器人承接老人居家远程诊疗与陪伴，连接医疗资源与家庭场景，属文娱社交与陪伴服务方向的银发智能化产品。",
    payor_model="B端机构采购",
    funding_latest={"display": "2024 D轮3000万美元（富士康领投）"},
    funding_total={"display": "累计超1亿美元"},
    stage="成长期", founded_year=2019,
    highlights=["2019 获2000万美元", "2024 富士康领投D轮3000万", "美国养老院远程诊疗占收入约50%", "西班牙600台合同"],
    events=["2024 富士康领投3000万美元D轮"],
    business_model="服务机器人销售+远程诊疗服务，向机构收费（B端）",
    coverage_regions=["以色列", "美国", "西班牙"],
    domestic_competitors=["乐聚机器人", "江苏艾雨文承", "大象机器人"],
)

B["1299"] = dict(
    recommend="云端机器人厂商，2015年成立、累计融资超50亿元、2023年C轮超10亿元，曾处赛道头部（信号）。但2024年起频现欠薪裁员、成被执行人，2025年总部人去楼空，经营数据急转（信息量）。和国内优必选、乐聚机器人相比，其云端大脑重资产路线风险暴露、由盛转衰（差异化）。国内已有类似（优必选、乐聚机器人），其重云端架构的教训值得警醒与对标（可复制）。",
    desc_cn="这家云端智能机器人公司2015年成立，曾以云端大脑加本体模式位居服务机器人头部，累计融资超过50亿元，至2023年C轮突破10亿元；但2024年起出现欠薪裁员、被列为被执行人，到2025年总部已人去楼空并转至香港合资运营。",
    silver_reason="云端服务机器人曾计划切入养老陪护与导诊场景，但其由盛转衰的历程揭示了重资产云端架构的现金流风险，是银发机器人赛道的重要警示样本。",
    payor_model="B端机构采购",
    funding_latest={"display": "2023 C轮超10亿元"},
    funding_total={"display": "累计超50亿元"},
    stage="收缩/风险", founded_year=2015,
    highlights=["累计融资超50亿元", "2023 C轮超10亿元", "2024 欠薪裁员被执行人", "2025 总部人去楼空"],
    events=["2024 欠薪裁员、被列为被执行人", "2025 总部人去楼空转香港合资"],
    business_model="云端机器人销售（B端），目前经营承压",
    coverage_regions=["中国", "香港"],
    domestic_competitors=["优必选", "乐聚机器人", "达闼机器人"],
)

B["1316"] = dict(
    recommend="英国AI电话陪伴创业，2023年成立、2024年5月获SFC Capital约25万英镑种子投资（信号）。其用怀旧疗法加语音交互做独居老人陪伴，公开资料透明但营收尚早（信息量）。和国内心智青、美好盛年等长辈文娱相比，其轻量语音加怀旧疗法定位少见（差异化）。国内已有类似（心智青、美好盛年），其低成本的AI电话陪伴打法可借鉴（可复制）。",
    desc_cn="这家英国利物浦创业公司（隶属Leaf AI）2023年成立，2024年5月引入SFC的25万英镑种子资金，通过AI电话与怀旧疗法为独居老人提供对话式陪伴和认知刺激，属于轻量语音情感服务。",
    silver_reason="以低成本AI电话陪伴缓解独居老人孤独与认知退化，属文娱社交与陪伴服务方向，为银发精神慰藉提供可规模化的轻量方案。",
    payor_model="个人自费",
    funding_latest={"display": "2024-05 Pre-Seed 约25万英镑（SFC Capital）"},
    funding_total={"display": "累计约25万英镑"},
    stage="初创期", founded_year=2023,
    highlights=["2023成立", "2024-05 Pre-Seed 25万英镑", "AI电话陪伴", "怀旧疗法"],
    events=["2024-05 获SFC Capital约25万英镑种子投资"],
    business_model="AI陪伴订阅服务（个人自费）",
    coverage_regions=["英国"],
    domestic_competitors=["心智青", "美好盛年", "美篇"],
)

B["1323"] = dict(
    recommend="央企旗下银发旅游品牌于2024年12月正式发布，巨头入局信号明确（信号）。依托集团旅行酒店景区资源，面向3.93亿活力老人、对应8.3万亿银发经济大盘，市场数据清晰（信息量）。和国内一龄集团、共比邻等相比，其央企资源加全产业链是稀缺壁垒（差异化）。国内已有类似（一龄集团、共比邻），其旅游加康养旅居打法可借鉴（可复制）。",
    desc_cn="这是中国旅游集团推出的银发游与康养旅居专业品牌，2024年12月29日对外发布，面向50岁以上人群提供旅游加康养旅居产品，依托集团在旅行、酒店与景区方面的资源，主打活力老人的康养文旅路线。",
    silver_reason="面向活力老人提供旅游与康养旅居服务，切入银发文旅这一高速增长的消费场景，是央企资源型巨头布局银发经济的标志性样本。",
    payor_model="个人自费",
    funding_latest={"display": "未搜到（央企内部孵化品牌）"},
    funding_total={"display": "未搜到"},
    stage="初创期", founded_year=2024,
    highlights=["2024-12-29 品牌发布", "央企中国旅游集团旗下", "银发康养旅游", "活力老人3.93亿"],
    events=["2024-12-29 品牌正式发布"],
    business_model="银发旅游与康养旅居产品销售（个人自费）",
    coverage_regions=["中国"],
    domestic_competitors=["一龄集团", "共比邻", "美好盛年"],
)

B["1337"] = dict(
    recommend="AI医疗语音认知监测厂商，2016年成立、2024年9月获WindRose战略投资，累计融资约1230万美元（信号）。其Eleanor语音引擎通过分析通话语调变化筛查认知症，临床合作数据逐步公开（信息量）。和国内远也、云芯信息等相比，其非侵入语音biomarker路线少见（差异化）。国内已有类似（远也、云芯信息），其语音加认知筛查的低门槛医疗打法可借鉴（可复制）。",
    desc_cn="这家纽约公司2016年创立，用人工智能语音分析识别认知症与神经退行风险，核心产品Eleanor通过通话语调与语言特征变化做远程筛查，2024年9月拿到WindRose的战略投资支持，累计融资规模约1230万美元。",
    silver_reason="以非侵入的语音分析早期识别老年认知症，属可穿戴监测与认知筛查方向，可显著提前干预窗口，契合银发脑健康管理的迫切需求。",
    payor_model="B端机构采购",
    funding_latest={"display": "2024-09 战略投资（WindRose）"},
    funding_total={"display": "累计约1230万美元"},
    stage="成长期", founded_year=2016,
    highlights=["2016成立", "2024-09 WindRose战略投资", "Eleanor语音引擎", "认知症筛查"],
    events=["2024-09 获WindRose战略投资"],
    business_model="语音认知监测SaaS，向医疗机构与支付方收费（B端）",
    coverage_regions=["美国", "纽约"],
    domestic_competitors=["远也", "云芯信息", "博博科技"],
)

B["1342"] = dict(
    recommend="法国家庭护理与陪伴服务商，公开融资与运营数据较少，信号主要来自欧洲银发照护政策红利（信号）。可查资料显示其聚焦居家护理与情感陪伴，但用户规模与营收尚未披露（信息量）。和国内小橙、易得康、福寿康等相比，其法式居家护理模式定位清晰（差异化）。国内已有类似（小橙、易得康、福寿康），其护理加陪伴社区化打法可借鉴（可复制）。",
    desc_cn="这家法国企业专注老年人家庭护理与陪伴服务，业务落在居家场景的护理员上门与情感陪伴，公开资料有限，融资规模与运营数据尚未对外披露，主要依托欧洲银发照护体系与政策环境开展业务，可作为法式居家照护的观察样本。",
    silver_reason="面向居家老人提供护理与陪伴服务，对接社区居家养老这一银发核心场景，是法式居家照护模式的海外观察样本，国内已有成熟对标。",
    payor_model="个人自费+政府补贴",
    funding_latest={"display": "未搜到"},
    funding_total={"display": "未搜到"},
    stage="未搜到", founded_year=None,
    highlights=["法国家庭护理与陪伴", "居家护理场景", "资料有限"],
    events=[],
    business_model="居家护理与陪伴服务（个人自费+政府补贴）",
    coverage_regions=["法国"],
    domestic_competitors=["小橙", "易得康", "福寿康"],
)

B["1346"] = dict(
    recommend="法国养老EHPAD非药物语音AI厂商，2024年获SilverEco提名，凭自动电话干预缓解认知症行为障碍、减少神经阻滞剂使用（信号）。公开资料有限，其向养老机构输出的语音关怀模块尚缺规模数据（信息量）。和国内江苏艾雨文承、中科源码等相比，其非药物加自动呼叫定位少见（差异化）。国内已有类似（江苏艾雨文承、中科源码），其减药化语音陪伴养老打法可借鉴（可复制）。",
    desc_cn="这家法国公司面向EHPAD养老机构提供非药物语音AI，通过自动电话与语音交互缓解认知症老人的行为障碍、减少精神类药物使用，曾摘得SilverEco奖项提名，对外运营数据有限。",
    silver_reason="以非药物、自动语音干预改善认知症老人行为与情绪，降低精神类药物依赖，属文娱社交与陪伴服务方向的银发照护创新。",
    payor_model="B端机构采购",
    funding_latest={"display": "未搜到（获SilverEco提名）"},
    funding_total={"display": "未搜到"},
    stage="未搜到", founded_year=None,
    highlights=["法国EHPAD语音AI", "2024 SilverEco提名", "非药物行为干预", "减神经阻滞剂"],
    events=["2024 获SilverEco奖项提名"],
    business_model="语音关怀模块向养老机构收费（B端）",
    coverage_regions=["法国"],
    domestic_competitors=["江苏艾雨文承", "中科源码", "大象机器人"],
)

B["1347"] = dict(
    recommend="养老场景智能家居照护厂商，2017年成立、累计融资约1000万美元，资本节奏平稳（信号）。其无穿戴无摄像头方案已积累1500亿数据点、可检20项健康指标，并在Arcadia等社区部署，数据扎实（信息量）。和国内锋物科技、奥佳华等相比，其WiFi雷达非侵入传感是壁垒（差异化）。国内已有类似（锋物科技、奥佳华），其智能家居加健康传感打法可借鉴（可复制）。",
    desc_cn="这家加州Palo Alto企业2017年创立，做养老社区的智能家居照护平台，采用无穿戴、无摄像头的WiFi与毫米波雷达传感，检测跌倒、睡眠、呼吸等约20项健康指标，已沉淀1500亿级数据点并在Arcadia、Shellpoint等社区落地，潜在报销约150美元每人每月。",
    silver_reason="以隐私友好的无摄像头传感为养老社区与居家老人提供健康与环境监测，属智能家居与消费品方向，可非侵入地提升照护安全。",
    payor_model="B端机构采购",
    funding_latest={"display": "累计融资约1000万美元（种子及后续轮）"},
    funding_total={"display": "累计约1000万美元"},
    stage="成长期", founded_year=2017,
    highlights=["2017成立", "累计融资约1000万美元", "1500亿数据点", "可检20项健康指标"],
    events=["已在Arcadia、Shellpoint等社区部署"],
    business_model="智能家居健康传感平台，向社区与机构收费（B端）",
    coverage_regions=["美国", "Palo Alto"],
    domestic_competitors=["锋物科技", "奥佳华", "旅睡智家"],
)

B["1358"] = dict(
    recommend="上海新设机器人公司，2025年9月成立，实缴资本500万元，尚无公开运营数据（信号）。工商范围覆盖工业与服务消费机器人，但用户与营收暂未披露，信息量偏弱（信息量）。和国内初新养老、春树养老等相比，其刚起步、尚无成型机器人养老打法（差异化）。国内已有类似（初新养老、春树养老），其新设入局动作可作早期观察样本（可复制）。",
    desc_cn="这家上海机器人企业于2025年9月5日注册，法定代表人为余亚舟，注册资本500万元，经营范围包括工业机器人、服务消费机器人及智能控制系统，目前公开的产品与运营信息很少，处于早期起步阶段。",
    silver_reason="新设主体将服务消费机器人列为经营范围，潜在指向养老与社区服务机器人方向，但目前尚无实质银发业务落地，宜作早期观察样本。",
    payor_model="B端机构采购",
    funding_latest={"display": "未搜到"},
    funding_total={"display": "未搜到"},
    stage="初创期", founded_year=2025,
    highlights=["2025-09-05 成立", "注册资本500万元", "经营范围含服务消费机器人", "早期起步"],
    events=["2025-09-05 公司注册成立"],
    business_model="机器人研发与销售（规划中，B端）",
    coverage_regions=["中国", "上海"],
    domestic_competitors=["初新养老", "春树养老", "安养养老"],
)

B["1372"] = dict(
    recommend="银发防护穿着类服装鞋帽创业，主打面向帕金森与阿尔茨海默老人的智能防摔马甲，集成跌倒气囊与定位芯片（信号）。公开资料有限，其工服美防摔马甲尚无明确销量与融资披露，信息量偏弱（信息量）。和国内令羽、响午、爱风尚等银发服装相比，其气囊防护定位少见（差异化）。国内已有类似（令羽、响午、爱风尚），其防护穿着加传感打法可借鉴（可复制）。",
    desc_cn="这一方向主打银发防护穿着，为帕金森及阿尔茨海默群体设计智能防摔马甲，内置跌倒气囊与定位芯片，关联北京通州工服美防摔马甲及清华相关技术团队，公开工商与运营资料有限。",
    silver_reason="以防摔马甲等防护穿着产品降低老年跌倒伤害，属服装鞋帽与防护穿着方向的银发安全技术，直接对应高龄老人跌倒高发的痛点。",
    payor_model="个人自费",
    funding_latest={"display": "未搜到"},
    funding_total={"display": "未搜到"},
    stage="未搜到", founded_year=None,
    highlights=["智能防摔马甲", "跌倒气囊+定位芯片", "面向帕金森/阿尔茨海默老人", "资料有限"],
    events=[],
    business_model="防护穿着硬件销售（个人自费）",
    coverage_regions=["中国", "北京"],
    domestic_competitors=["令羽", "响午", "爱风尚"],
)

B["1389"] = dict(
    recommend="微型医疗科技类公司，2017年成立、注册资本仅数万元，做二类医疗器械与保健品推广，定位长寿抗衰与亚健康干预（信号）。公开资料显示其做二类医疗器械批发与保健品推广，但营收与用户规模未披露，信息量偏弱（信息量）。和国内时光派、森美等抗衰机构相比，其偏渠道推广、研发壁垒有限（差异化）。国内已有类似（时光派、森美），其医疗加保健品轻资产打法可借鉴（可复制）。",
    desc_cn="这家长沙微型医药科技公司2017年设立，注册资本披露存在分歧（天眼查5万元、BOSS直聘20万元），主营医学研究、二类医疗器械批发、亚健康干预与保健品推广，库内标签为长寿抗衰，实际业务更偏医药健康产品的渠道销售。",
    silver_reason="该公司切入长寿抗衰消费赛道，以保健品与二类器械的渠道分销为主，研发属性偏弱，是银发抗衰领域轻资产运营的小微样本。",
    payor_model="个人自费",
    funding_latest={"display": "未搜到"},
    funding_total={"display": "未搜到"},
    stage="初创期", founded_year=2017,
    highlights=["2017成立", "注册资本披露分歧(5万/20万)", "二类医疗器械批发", "保健品推广"],
    events=[],
    business_model="医疗器械与保健品渠道推广（个人自费）",
    coverage_regions=["中国", "长沙"],
    domestic_competitors=["时光派", "森美", "yooLab"],
)

# ---- 写入 + 门禁 ----
results = []
for serial, data in B.items():
    e = ctx(serial)
    draft = {"serial": "#" + serial}
    draft.update(data)
    fp = os.path.join(OUT, "draft_#%s.json" % serial)
    json.dump(draft, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    merged = dict(e)
    for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
        if k in draft and draft[k] is not None:
            merged[k] = draft[k]
    iss = C.validate(merged, others=None, skip={"R10"})
    rec_len = C.content_len(draft.get("recommend", ""))
    results.append((serial, rec_len, iss))
    print("#%s recommend字数=%d 门禁=%s" % (serial, rec_len, "PASS" if not iss else iss))

print("\n=== 汇总 ===")
fail = [r for r in results if r[2]]
print("总计 %d 家 | PASS %d | FAIL %d" % (len(results), len(results) - len(fail), len(fail)))
for s, n, iss in fail:
    print("  FAIL #%s: %s" % (s, iss))
