# -*- coding: utf-8 -*-
import json, re, os

INFILE = "/g/workbuddy/2026-06-28-23-34-20/silver-pulse/output/_v12_input_TD3.json"
OUTFILE = "/g/workbuddy/2026-06-28-23-34-20/silver-pulse/output/_v12_split_TD3.json"

with open(INFILE, encoding="utf-8") as f:
    data = json.load(f)

INSCOPE = ["健康监测","AI","智能硬件","养老机构","营养食品","适老化改造","文娱","专业护理","机器人","医疗器械"]

AVAILABLE = set(["认知训练","陪诊","AI医疗","SDOH","SODH","药品","康复医疗","跌倒监测","健康监测",
"用药管理","体检筛查","心理健康","女性健康","更年期","诊所","专业护理","养老机构","适老化",
"远程护理","护理人力","上门","旅居养老","康养地产","家政生活服务","外骨骼","康复器械","康复机器人",
"助行器","假肢矫形","护理床具","听力训练","轮椅","护理床","服装鞋帽","个人护理","眼镜","助听器",
"智能硬件","日用","老年产品","消费品","尿失禁","纸尿裤","旅游","教育","健身","相亲","文娱","时间银行",
"社区","会员俱乐部","陪伴机器人","就业","保险科技","金融理财","金融服务","机器人","长寿科技","行业媒体",
"咨询研究","会展峰会","渠道零售","渠道","零售","电商"])

# The 10 in-scope big tags are umbrellas to dissolve -> never allowed as reassignment targets
UMBRELLAS = set(INSCOPE)
TARGET = AVAILABLE - UMBRELLAS

# map non-available but meaningful tag_l2 tokens -> available target
TOKEN_MAP = {
    "慢病管理":"远程护理","智慧养老":"适老化","居家护理":"上门","康复设备":"康复器械",
    "投资机构":None,"平台":None,"保险":"保险科技","临终关怀":"专业护理","康复医疗":"康复医疗",
    "药品":"药品","认知训练":"认知训练","跌倒监测":"跌倒监测","用药管理":"用药管理",
    "体检筛查":"体检筛查","远程护理":"远程护理","心理健康":"心理健康","助听器":"助听器",
    "适老化":"适老化","专业护理":"专业护理","养老机构":"养老机构",
}

# ---- keyword rules (text -> available tag) ; applied when no override ----
RULES = [
    (r"跌倒|防跌|fall|防摔倒", "跌倒监测"),
    (r"用药|服药|药物|medication|处方|吃药", "用药管理"),
    (r"筛查|早筛|screening|体检|影像筛查|骨质疏松|眼科筛查|视网膜|帕金森筛查|眼动", "体检筛查"),
    (r"远程护理|远程患者|remote patient|RPM|telecare|远程监测|远程医疗|虚拟护理|居家医疗|远程照护|远程看护", "远程护理"),
    (r"心理|抑郁|焦虑|mental|痴呆症.*心理|孤独|陪伴", "心理健康"),
    (r"助听器|hearing|airpods|听力", "助听器"),
    (r"眼镜|视觉增强|低视力|黄斑|retina|ar头显|视力|电子眼镜|视觉", "眼镜"),
    (r"认知|cognitive|脑健康|记忆|痴呆|阿尔茨海默|帕金森|neuro|认知训练|数字疗法|vr康复|脑机|bc机", "认知训练"),
    (r"康复医疗|康复医院|rehab|术后康复|神经调控|物理治疗|康复理疗|康复评定|康复机器人", "康复医疗"),
    (r"康复器械|康复设备|康复评定设备|家用医疗|监护监测|医疗器械|医疗设备|植入物|骨科", "康复器械"),
    (r"康复机器人|rehab robot|康养机器人", "康复机器人"),
    (r"外骨骼|exoskeleton", "外骨骼"),
    (r"助行器|walker|代步车|代步", "助行器"),
    (r"轮椅|wheelchair", "轮椅"),
    (r"护理床|病床|icu床|床具", "护理床"),
    (r"护理床具|床垫", "护理床具"),
    (r"假肢|矫形|prosthesis|关节置换", "假肢矫形"),
    (r"陪诊|陪同就医|就医陪", "陪诊"),
    (r"ai医疗|医疗ai|ai诊断|影像诊断|辅助诊断|ai医学|医疗人工智能|数字病理|临床ai|医疗大模型", "AI医疗"),
    (r"保险|insurance|medicare|claims|理赔|健康计划|付款人|payer|事先授权|福利|保费", "保险科技"),
    (r"金融|financ|理财|财富", "金融理财"),
    (r"长寿|longevity|抗衰老|aging|健康老龄化", "长寿科技"),
    (r"媒体|资讯|行业媒体|内容平台|数据服务|报告|研究机构|展会", "行业媒体"),
    (r"咨询|智库|策划|顾问|资源对接|产业园", "咨询研究"),
    (r"会展|峰会|expo|论坛", "会展峰会"),
    (r"电商|零售|渠道|商城|门店|商店|marketplace|订阅服务|dtc", "零售"),
    (r"适老化|无障碍|扶手|防滑|改造|家居|家具|建材|楼梯|升降|紧急呼叫|呼叫|telecare", "适老化"),
    (r"上门|到家|home visit|护士上门|护工上门|居家护理|居家照护|居家服务", "上门"),
    (r"家政|家务|保洁|生活照料|交通接送|陪诊|做饭|送餐", "家政生活服务"),
    (r"护理服务|护工|护理员|医疗护理|专业护理|照护服务|护理平台|长期护理|安宁疗护|临终|护理院|护理机构", "专业护理"),
    (r"旅居|旅游|travel|候鸟|度假|游学", "旅游"),
    (r"康养地产|地产|reits|reit|养老社区|ccrc|康养|物业|地产开发", "康养地产"),
    (r"会员|俱乐部|club|社群|社区活动|兴趣社区|聚乐部", "会员俱乐部"),
    (r"教育|课程|培训|大学|学习|school|老年大学", "教育"),
    (r"健身|运动|锻炼|exercise|广场舞", "健身"),
    (r"相亲|婚恋|dating", "相亲"),
    (r"短视频|视频|社交|直播|娱乐|兴趣|内容平台|文娱", "会员俱乐部"),
    (r"时间银行", "时间银行"),
    (r"就业|再就业|职业|招聘|工作", "就业"),
    (r"机器人|robot", "陪伴机器人"),
    (r"陪伴|companion|情感|陪护|海豹", "陪伴机器人"),
    (r"硬件|设备|手环|戒指|手表|传感器|监测仪|床垫|智能产品|穿戴", "老年产品"),
    (r"消费品|消费|品牌|产品|补充剂|营养|膳食|食品|羊奶|奶粉", "消费品"),
    (r"日用|厨房|烹饪|马桶|家居日", "日用"),
    (r"按摩|艾灸|个人护理|健康硬件", "个人护理"),
    (r"服装|鞋|帽|衣", "服装鞋帽"),
    (r"尿|失禁|纸尿裤|尿布", "纸尿裤"),
    (r"女性|更年期|women|妇科|乳腺|潮热", "女性健康"),
    (r"更年期|menopause", "更年期"),
    (r"药品|制药|pharma|处方", "药品"),
    (r"诊所|clinic", "诊所"),
    (r"sdoh|社会决定|social determinant", "SDOH"),
]

# ---- curated overrides (key -> [tags]) for ambiguous / big-tech / multi-big cases ----
OVERRIDES = {
    # 健康监测 members
    "百芝龙": ["跌倒监测","适老化"],
    "享睡": ["老年产品"],
    "享睡Sleepace": ["老年产品"],
    "星巡智能": ["适老化"],
    "兆观智能": ["体检筛查"],
    "Current Health": ["远程护理"],
    "Aktiia": ["康复器械"],
    "Apple": ["助听器"],
    "CardioSignal": ["体检筛查"],
    "Cloud DX": ["远程护理"],
    "CoachCare": ["远程护理"],
    "HealthArc": ["远程护理"],
    "Hyfe AI": ["体检筛查"],
    "Metyos": ["康复器械"],
    "MindMics": ["康复器械"],
    "Modivcare": ["上门","远程护理"],
    "OneStep": ["康复器械"],
    "SafelyYou": ["跌倒监测"],
    "Sava": ["康复器械"],
    "SomaReality": ["认知训练"],
    "Vayyar": ["跌倒监测"],
    "Videra Health": ["心理健康"],
    "Voxela": ["跌倒监测"],
    "Best Buy Health": ["远程护理"],
    "Clairvoyant Networks": ["远程护理"],
    "DNX": ["远程护理"],
    "GrandCare Systems": ["适老化"],
    "Cooey Health": ["远程护理"],
    "Sensi": ["跌倒监测"],
    "Sensara": ["跌倒监测"],
    "Wanda Health": ["远程护理"],
    "Percipio Health": ["远程护理"],
    "Cherish": ["跌倒监测"],
    "Cera｜英国居家医疗AI": ["上门","远程护理"],
    "中科华意": ["康复医疗","认知训练"],
    "Idoven": ["体检筛查"],
    "Kraydel": ["跌倒监测"],
    "Tunstall": ["适老化"],
    "Lifted": ["跌倒监测"],
    "Watcherr": ["跌倒监测"],
    "lyflynks": ["用药管理","上门"],
    # 智能硬件 members
    "作为科技": ["跌倒监测"],
    "倍轻松": ["个人护理"],
    "兆观": ["老年产品"],
    "博博科技": ["跌倒监测"],
    "唯艾": ["个人护理"],
    "心永科技": ["康复器械"],
    "达旦无极": ["跌倒监测"],
    "唯艾科技": ["个人护理"],
    "苗米科技": ["跌倒监测"],
    "Inspiren": ["跌倒监测"],
    "亚马逊": ["零售","渠道零售"],
    "宝马": ["消费品"],
    "Meta": ["认知训练"],
    "GreatCall": ["适老化"],
    "三星": ["消费品"],
    "6Degrees": ["老年产品"],
    "AceAge": ["用药管理"],
    "Embr Labs": ["个人护理"],
    "HiDO": ["用药管理"],
    "Kalogon": ["护理床具"],
    "Lilli": ["远程护理"],
    "Lotus Ring": ["老年产品"],
    "Nobi": ["跌倒监测"],
    "Toi Labs": ["老年产品"],
    "ŌURA": ["老年产品"],
    "Philips (Lifeline)": ["适老化"],
    "Orion": ["老年产品"],
    "Eight Sleep": ["老年产品","女性健康"],
    "ONSCREEN": ["适老化"],
    "Brava": ["日用"],
    "GrandPad": ["老年产品"],
    "PalCare": ["适老化"],
    "Haelo": ["跌倒监测"],
    "九为健康": ["药品"],
    "京东方 BOE": ["适老化"],
    "松延动力": ["陪伴机器人"],
    # AI members
    "清澜技术": ["适老化"],
    "甲子科技": ["适老化"],
    "Lyft Health": ["家政生活服务"],
    "IBM": ["AI医疗"],
    "Alaffia Health": ["保险科技"],
    "Anatomy Financial": ["保险科技"],
    "Citizen Health": ["AI医疗"],
    "Cohere Health": ["保险科技"],
    "Credo Health": ["保险科技"],
    "Daffodil Health": ["保险科技"],
    "DigitalOwl": ["保险科技"],
    "Friendi.fi": ["AI医疗"],
    "Infinitus Systems": ["AI医疗"],
    "Miihealth": ["AI医疗"],
    "Somnee": ["AI医疗"],
    "SpinSci": ["AI医疗"],
    "Thoughtful AI": ["保险科技"],
    "Thrive AI Health": ["AI医疗"],
    "Together by Renee": ["保险科技","用药管理"],
    "Two Chairs": ["心理健康"],
    "Voiceitt": ["AI医疗"],
    "Duos": ["保险科技"],
    "Google Gemini AI 健康教练": ["AI医疗"],
    "Hippocratic AI": ["AI医疗"],
    "Care Daily": ["远程护理"],
    "Jona": ["AI医疗"],
    "新奈医疗": ["AI医疗"],
    "智医向量": ["AI医疗"],
    "Zingage": ["上门"],
    "Gladys": ["上门"],
    "Cadence": ["远程护理"],
    "Enzo Health": ["上门"],
    "Callie Care": ["陪伴机器人"],
    "Neurable": ["认知训练"],
    "深睿医疗": ["AI医疗"],
    "阶梯医疗": ["AI医疗","康复医疗"],
    "AIM": ["AI医疗","体检筛查"],
    "Jubo": ["远程护理"],
    # 养老机构 members
    "南京新百": ["专业护理"],
    "织生科技": ["认知训练"],
    "集思鸣智": ["认知训练"],
    "鹤灵医疗": ["认知训练"],
    "东方华康": ["康复医疗","专业护理"],
    "和家健脑": ["认知训练"],
    "康语轩": ["专业护理"],
    "美邸中国": ["专业护理"],
    "脑动极光": ["认知训练"],
    "虚之实": ["认知训练","康复医疗"],
    "记忆家": ["专业护理"],
    "松龄护老": ["专业护理"],
    "复星保德信颐养": ["康养地产"],
    "厚福医疗": ["护理床"],
    "天佑安康": ["咨询研究","旅居养老"],
    "Athulya Senior Care": ["专业护理"],
    "Rippl Care": ["心理健康"],
    "A Place for Mom": ["咨询研究"],
    "Brookdale Senior Living": ["专业护理"],
    "Hebrew Senior Life": ["专业护理"],
    "Riverspring Living": ["专业护理"],
    "Artis Senior Living": ["专业护理"],
    "Brightview Senior Living": ["专业护理"],
    "Log my Care": ["咨询研究"],
    "Lottie": ["咨询研究"],
    "SeniorHousingLiving": ["咨询研究"],
    "Welbi": ["专业护理"],
    "Altek Corporation": ["跌倒监测"],
    "Pansy Homecare": ["上门"],
    "Lizzy Care": ["上门"],
    "The Ensign Group": ["专业护理"],
    "LTC Properties": ["康养地产"],
    "Clariane": ["专业护理"],
    "Emeis (Orpea)": ["专业护理"],
    "OnShift": ["护理人力"],
    "PARO": ["陪伴机器人"],
    # 营养食品 members
    "WonderLab": ["消费品"],
    "养乃世家": ["消费品"],
    "冬泽": ["消费品"],
    "yooLab": ["电商"],
    "维小饭": ["电商"],
    "玛土撒拉": ["消费品"],
    "麦孚营养": ["消费品"],
    "冬泽特医": ["消费品"],
    "优生活羊奶": ["消费品"],
    "Air Protein": ["消费品"],
    "Bioniq": ["电商"],
    "Bobbie": ["消费品"],
    "ByHeart": ["消费品"],
    "Day Two": ["电商"],
    "DiningRD": ["消费品"],
    "Foodsmart": ["电商"],
    "Huel": ["消费品"],
    "Mealogic": ["消费品"],
    "Mend": ["电商"],
    "Modify Health": ["电商"],
    "Nourish": ["电商"],
    "NourishedRx": ["电商"],
    "PurFoods": ["消费品"],
    "RxDiet": ["电商"],
    "YgEia3": ["消费品"],
    "Healthnix": ["电商"],
    "Miils": ["电商"],
    "澳维诺": ["消费品"],
    "好健康 goodhealth": ["消费品"],
    "因你 inne": ["消费品"],
    "Seraphina Therapeutics (fatty15)": ["消费品"],
    "Mom's Meals": ["消费品"],
    "Silver Cuisine": ["消费品"],
    "Magic Kitchen": ["消费品"],
    "Kate Farms": ["消费品"],
    "脂代科技": ["消费品"],
    # 适老化改造 members
    "特霍芬": ["适老化"],
    "万德厨": ["适老化"],
    "中匠福": ["适老化"],
    "云芯信息": ["适老化"],
    "佛山建泰": ["适老化"],
    "佛山永爱": ["适老化"],
    "台格": ["适老化"],
    "和乐春晖": ["适老化"],
    "嘉年乐": ["适老化"],
    "天华设计": ["适老化"],
    "安馨康养": ["适老化"],
    "志贺康养": ["适老化"],
    "悠幸": ["适老化"],
    "救救帮": ["适老化"],
    "来邦科技": ["适老化"],
    "栖城设计": ["适老化"],
    "沐恒实业": ["适老化"],
    "爱牵挂": ["适老化"],
    "盛通养老": ["适老化"],
    "福康通": ["适老化"],
    "遇禾规划": ["适老化"],
    "甲子科技(甲子养老)": ["适老化"],
    "小咖云": ["咨询研究"],
    "101 Mobility": ["适老化"],
    "K4Connect": ["适老化"],
    "Steadiwear": ["康复器械"],
    "大和房屋工业 (Daiwa House)": ["适老化"],
    "积水房屋 (Sekisui House)": ["适老化"],
    "Stannah": ["适老化"],
    "Doro": ["适老化"],
    "华康岛": ["适老化"],
    "伊维养老": ["适老化"],
    # 文娱 members
    "小年糕": ["会员俱乐部"],
    "彩视": ["会员俱乐部"],
    "闲趣岛": ["旅游","会员俱乐部"],
    "乐龄圈": ["会员俱乐部"],
    "半月浮生": ["会员俱乐部"],
    "就爱广场舞": ["会员俱乐部"],
    "心乐空间": ["会员俱乐部"],
    "摩登银龄": ["会员俱乐部"],
    "时尚奶奶团": ["会员俱乐部"],
    "晶彩人生": ["会员俱乐部"],
    "最美芳华": ["会员俱乐部"],
    "爱风尚": ["会员俱乐部"],
    "票圈视频": ["会员俱乐部"],
    "糖豆": ["会员俱乐部"],
    "老柚": ["会员俱乐部"],
    "舞动时代": ["会员俱乐部"],
    "退休俱乐部": ["会员俱乐部"],
    "遇见美好": ["会员俱乐部"],
    "银彩聚乐部": ["会员俱乐部"],
    "链老网": ["教育","会员俱乐部"],
    "锣钹科技": ["会员俱乐部"],
    "鹏翼时代": ["会员俱乐部"],
    "现名 CoGenerate": ["就业"],
    "Netflix": ["行业媒体"],
    "AgeWell Global": ["会员俱乐部"],
    "Clever Care Health Plan": ["保险科技"],
    "NeoSilver": ["会员俱乐部"],
    "Seniorworld": ["会员俱乐部"],
    "Uniper": ["会员俱乐部"],
    "The Joy Club": ["会员俱乐部"],
    "Clyx": ["会员俱乐部"],
    # 专业护理 members
    "抚理健康": ["上门"],
    "一号护工": ["上门"],
    "医护到家": ["上门"],
    "小柏家护": ["上门"],
    "戴恩": ["上门"],
    "擎浩护理": ["上门"],
    "智宇孝老": ["上门"],
    "柏老汇": ["上门"],
    "泰康安宁疗护": ["上门"],
    "泰心康护": ["上门"],
    "爱侬养老": ["上门"],
    "福寿家": ["上门"],
    "立奇电子": ["上门"],
    "老友记": ["上门"],
    "金牌护士": ["上门"],
    "银汤屋": ["上门"],
    "阿福医疗": ["上门"],
    "青鸟软通": ["上门"],
    "小橙长护": ["上门","康复医疗"],
    "Home Instead": ["上门"],
    "Geri Care": ["上门","康复医疗"],
    "Papa": ["家政生活服务"],
    "hellocare.ai": ["远程护理"],
    "LHC Group": ["上门"],
    "eCaring": ["护理人力"],
    "Aline (Sherpa)": ["护理人力"],
    "Smartcare": ["护理人力"],
    "IntellaTriage": ["远程护理"],
    "Cera｜英国居家医疗AI": ["上门","远程护理"],
    # 机器人 members
    "优必选": ["陪伴机器人","康复机器人"],
    "ForSight Robotics": ["康复医疗"],
    "Labrador Systems": ["陪伴机器人"],
    "Amba": ["护理人力"],
    "Labrador": ["陪伴机器人"],
    "Diligent Robotics": ["陪伴机器人"],
    "乐聚机器人": ["陪伴机器人"],
    "麦迪科技": ["康复机器人","陪伴机器人"],
    "达闼机器人": ["陪伴机器人"],
    "欧圣电气": ["尿失禁"],
    "中科行智": ["陪伴机器人"],
    "中科源码": ["陪伴机器人"],
    "森丽康科技": ["陪伴机器人"],
    "腾讯 Robotics X": ["陪伴机器人"],
    "海尔兄弟机器人": ["陪伴机器人"],
    "星动纪元": ["陪伴机器人"],
    "朗毅机器人": ["陪伴机器人"],
    "骅羲智能": ["陪伴机器人"],
    "Andromeda Robotics": ["陪伴机器人"],
    "银河通用机器人": ["陪伴机器人"],
    "自变量机器人": ["陪伴机器人"],
    "浙江人形机器人创新中心": ["陪伴机器人"],
    "星尘智能": ["陪伴机器人"],
    "泉智博": ["康复机器人"],
    "Cartken": ["陪伴机器人"],
    "钛米机器人": ["康复机器人"],
    "LOVOT": ["陪伴机器人"],
    "PARO": ["陪伴机器人"],
    "Temi": ["陪伴机器人"],
    "达闼科技": ["陪伴机器人"],
    # 医疗器械 members
    "依瑞德": ["康复医疗"],
    "和佳医疗": ["康复医疗"],
    "品驰": ["康复医疗"],
    "景昱": ["康复医疗"],
    "瑞尔齿科": ["诊所"],
    "美呀植牙": ["诊所"],
    "谊安医疗": ["康复器械"],
    "通策医疗": ["诊所"],
    "鱼跃": ["康复器械"],
    "鼎植口腔": ["诊所"],
    "曼景科技": ["康复医疗"],
    "品驰医疗": ["康复医疗"],
    "爱康医疗": ["假肢矫形"],
    "Cala Health": ["康复器械"],
    "Ellipsis Health": ["康复器械"],
    "NeuroClues": ["体检筛查"],
    "Starling Medical": ["康复器械"],
    "Tennr": ["行业媒体"],
    "LambdaVision": ["眼镜"],
    "SetPoint Medical": ["康复医疗"],
    "Intus Care": ["远程护理"],
    "AdaptHealth": ["康复器械"],
    "Optain Health": ["眼镜"],
    "IrisVision": ["眼镜"],
    "eSight": ["眼镜"],
    "NuEyes": ["眼镜"],
    "九安医疗": ["康复器械"],
    "乐心医疗": ["康复器械"],
    "三诺生物": ["康复器械"],
    "康泰医学": ["康复器械"],
    "翔宇医疗": ["康复器械"],
}

# ---- NEW_TAGS for uncovered coherent sub-types (no specific available tag) ----
NEW_TAGS = {
    "医学营养品": {"l1":"食品营养","members":["冬泽","玛土撒拉","麦孚营养","冬泽特医","Kate Farms","脂代科技"]},
    "老年膳食配送": {"l1":"食品营养","members":["Mom's Meals","Silver Cuisine","Magic Kitchen","DiningRD"]},
    "健康营养补充剂": {"l1":"食品营养","members":["WonderLab","养乃世家","澳维诺","好健康 goodhealth","因你 inne","Seraphina Therapeutics (fatty15)","Air Protein","Huel","ByHeart","Bobbie","YgEia3","PurFoods","优生活羊奶"]},
    "数字营养平台": {"l1":"食品营养","members":["Bioniq","Day Two","Modify Health","Mend","RxDiet","Foodsmart","Nourish","NourishedRx","Miils","Healthnix","yooLab","维小饭"]},
    "养老社区运营商": {"l1":"养老服务","members":["Brookdale Senior Living","Clariane","Emeis (Orpea)","复星保德信颐养","松龄护老","Athulya Senior Care","Hebrew Senior Life","Riverspring Living","Artis Senior Living","Brightview Senior Living","东方华康","南京新百","The Ensign Group"]},
    "银发内容社区": {"l1":"文娱社交","members":["小年糕","彩视","票圈视频","半月浮生","摩登银龄","时尚奶奶团","最美芳华","锣钹科技","鹏翼时代","就爱广场舞","糖豆","舞动时代","老柚","遇见美好","爱风尚","晶彩人生","心乐空间","乐龄圈","退休俱乐部"]},
}

# ---- build key -> (rec, big_set) ----
key_info = {}
for bt in INSCOPE:
    for rec in data.get(bt, []):
        name = rec.get("name")
        name_cn = rec.get("name_cn")
        key = name_cn if name_cn else name
        if key not in key_info:
            key_info[key] = {"rec": rec, "big": set()}
        key_info[key]["big"].add(bt)

def classify(key, info):
    rec = info["rec"]
    big = info["big"]
    if key in OVERRIDES:
        tags = [t for t in OVERRIDES[key] if t in TARGET and t not in big]
        if tags:
            return sorted(set(tags))
    # harvest specific tokens from tag_l2
    tags = set()
    for t in rec.get("tag_l2", []):
        if t in TARGET and t not in big:
            tags.add(t)
        elif t in TOKEN_MAP and TOKEN_MAP[t] and TOKEN_MAP[t] in TARGET and TOKEN_MAP[t] not in big:
            tags.add(TOKEN_MAP[t])
    # keyword rules
    text = " ".join([
        str(rec.get("name",""),), str(rec.get("name_cn","") or ""),
        str(rec.get("description","") or ""), str(rec.get("desc_cn","") or ""),
        str(rec.get("business_model_cn","") or ""), str(rec.get("category_l1","") or ""),
        str(rec.get("category_l2","") or ""), " ".join(rec.get("tag_l2",[])),
        " ".join(rec.get("tag_l1",[]))
    ])
    for pat, tag in RULES:
        if re.search(pat, text, re.IGNORECASE) and tag in TARGET and tag not in big:
            tags.add(tag)
    if tags:
        return sorted(tags)
    # fallback by primary big tag
    fb = {
        "健康监测":"远程护理","AI":"AI医疗","智能硬件":"老年产品","养老机构":"专业护理",
        "营养食品":"消费品","适老化改造":"适老化","文娱":"会员俱乐部","专业护理":"上门",
        "机器人":"陪伴机器人","医疗器械":"康复器械",
    }
    for b in big:
        if fb.get(b) in TARGET:
            return [fb[b]]
    return ["消费品"]

REASSIGN = {}
problems = []
for key, info in key_info.items():
    tags = classify(key, info)
    # final guard: never include any umbrella/big tag
    tags = [t for t in tags if t in TARGET and t not in info["big"]]
    if not tags:
        tags = ["消费品"]
        problems.append(key + " (forced 消费品 fallback)")
    REASSIGN[key] = tags

# validate every key covered
assert len(REASSIGN) == len(key_info), "key count mismatch"

out = {"REASSIGN": REASSIGN, "NEW_TAGS": NEW_TAGS}
with open(OUTFILE, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# stats
from collections import Counter
cnt = Counter()
for v in REASSIGN.values():
    for t in v:
        cnt[t]+=1
print("Total enterprises reassigned:", len(REASSIGN))
print("Distinct target tags used:", len(cnt))
print("Tag member counts:")
for t,c in cnt.most_common():
    print(f"  {t}: {c}")
print("\nNew tags proposed:")
for n,m in NEW_TAGS.items():
    print(f"  {n} (l1={m['l1']}): {len(m['members'])} members")
print("\nProblems/forced fallback:", len(problems))
for p in problems:
    print("  ", p)
