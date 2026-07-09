# -*- coding: utf-8 -*-
"""Batch 2: expand enterprise library with real AgeTech / silver-economy
companies (global, 2025-2026 verified). Auto-dedup against existing names.
Only APPENDS; never modifies existing entries.
"""
import json

DATA_FILE = "data/enterprise/all_enterprises.json"
SRC = "WebSearch(WebSearch企业库扩充: Crunchbase/Tracxn/TheGerontechnologist/PRNewswire/公司官网等)"

def mk(name, name_cn, region, l1, l2, tags, desc, highlights,
       flatest, ftotal, investors, founded, website, bm):
    return {
        "name": name, "name_cn": name_cn, "region": region,
        "category_l1": l1, "category_l2": l2, "tags": tags,
        "description": desc, "desc_cn": desc, "highlights": highlights,
        "funding_latest": flatest, "funding_total": ftotal,
        "investors": investors, "founded": founded, "value_score": 0,
        "source": SRC,
        "crunchbase_url": "https://www.crunchbase.com/textsearch?q=" + name.replace(" ", "+"),
        "website_url": website, "business_model": bm, "business_model_cn": bm,
        "news_coverage": {"latest_news": [], "news_count": 0,
                          "news_quality": "low", "snippets": [desc]},
    }

def fd(a, r, d, disp): return {"amount": a, "round": r, "date": d, "display": disp}
def ft(t): return {"amount": t, "display": t}
NA = fd("未披露", "", "", "未披露")
NAT = ft("累计未披露")

C = []
# ---------------- 听力 / 听觉辅具 ----------------
C.append(mk("Audicus", "", "海外", "智能硬件", "听觉辅具",
    ["助听器", "DTC"],
    "直接面向消费者的在线助听器公司，提供平价、可自调的助听器与听力测试，降低老年听力障碍干预门槛。",
    "DTC平价助听器，降低老年听障干预门槛",
    NA, NAT, "", "2012", "https://www.audicus.com", "B2C 在线助听器订阅+服务"))
C.append(mk("Lexie Hearing", "", "海外", "智能硬件", "听觉辅具",
    ["助听器", "DTC"],
    "由WS Audiology支持的DTC助听器品牌，提供APP自助验配与远程听力专家服务，面向轻中度听损老人。",
    "WS Audiology支持的DTC助听器，APP自助验配",
    NA, NAT, "", "2020", "https://www.lexiehearing.com", "B2C DTC助听器+远程验配"))
C.append(mk("Audien", "", "海外", "智能硬件", "听觉辅具",
    ["助听器", "平价"],
    "主打极致平价的自验配助听器品牌，面向预算敏感老年听损人群，通过电商直售。",
    "平价自验配助听器，电商直售",
    NA, NAT, "", "2018", "https://www.audienhearing.com", "B2C 平价助听器硬件"))
C.append(mk("Olive Union", "", "海外", "智能硬件", "听觉辅具",
    ["助听器", "消费级"],
    "消费级智能耳塞/助听器公司，将听力增强做成时尚可穿戴，降低老年用户佩戴 stigma。",
    "消费级时尚助听器，降低佩戴 stigma",
    NA, NAT, "", "2016", "https://www.olive.co", "B2C 消费级听力增强可穿戴"))
C.append(mk("Earlens", "", "海外", "智能硬件", "听觉辅具",
    ["助听器", "光传导", "技术差异化"],
    "采用光传导（light-based）技术的差异化助听器公司，解决传统气导助听器音质瓶颈，面向中重度听损。",
    "光传导助听器，差异化技术路线",
    NA, NAT, "", "2010", "https://www.earlens.com", "B2B2C 高端助听器（技术授权/直售）"))
# ---------------- 视觉 / 低视力 ----------------
C.append(mk("IrisVision", "", "海外", "智能硬件", "视觉障碍",
    ["低视力", "AR"],
    "通过AR头显为黄斑变性等低视力老人提供视觉增强，放大并提升剩余视力，改善独立生活能力。",
    "AR头显增强低视力老人剩余视力",
    NA, NAT, "", "2016", "https://www.irisvision.com", "B2C/B2B 低视力AR辅助硬件"))
C.append(mk("eSight", "", "海外", "智能硬件", "视觉障碍",
    ["低视力", "电子眼镜"],
    "低视力电子眼镜公司，用高清晰摄像头与显示屏为法定盲人/低视力者提供实时视觉增强。",
    "低视力电子眼镜，实时视觉增强",
    NA, NAT, "", "2006", "https://www.esighteyewear.com", "B2C 低视力电子眼镜硬件"))
C.append(mk("NuEyes", "", "海外", "智能硬件", "视觉障碍",
    ["低视力", "AI眼镜"],
    "推出轻量AI智能眼镜，为低视力与阅读困难的老人提供放大、对比增强与文字识别。",
    "轻量AI智能眼镜，低视力阅读增强",
    NA, NAT, "", "2013", "https://www.nueyes.com", "B2C 低视力AI眼镜硬件"))
# ---------------- 行动 / 轮椅 / 外骨骼 ----------------
C.append(mk("WHILL", "", "海外", "康复设备", "智能轮椅",
    ["智能轮椅", "出行", "有融资"],
    "日本个人出行（personal mobility）公司，推出造型时尚、操控灵活的个人电动移动设备，提升老人户外自主出行。",
    "日本个人智能出行设备，提升老人户外自主",
    NA, NAT, "", "2012", "https://www.whill.inc", "B2B2C 个人智能移动设备"))
C.append(mk("Permobil", "", "海外", "康复设备", "智能轮椅",
    ["智能轮椅", "上市公司", "对标标的"],
    "全球动力轮椅与坐姿支撑系统龙头（Investor AB体系），深度服务重度行动障碍与老年人群。",
    "全球动力轮椅龙头，银发行动障碍标杆（S1）",
    NA, ft("上市公司(Investor AB体系)"), "", "1967",
    "https://www.permobil.com", "B2B 动力轮椅与康复辅具（上市）"))
C.append(mk("Sunrise Medical", "", "海外", "康复设备", "智能轮椅",
    ["轮椅", "辅具"],
    "全球轮椅与移动辅具巨头，提供手动/动力轮椅、轻量化出行方案，覆盖老年与残障人群。",
    "全球轮椅与移动辅具巨头",
    NA, NAT, "", "1983",
    "https://www.sunrisemedical.com", "B2B 轮椅与移动辅具"))
C.append(mk("ReWalk Robotics", "", "海外", "康复设备", "外骨骼",
    ["外骨骼", "上市公司", "对标标的"],
    "上市外骨骼机器人公司（NASDAQ:RWLK），为脊髓损伤与卒中后行走障碍提供医用/家用外骨骼康复系统。",
    "上市外骨骼公司，医用/家用行走康复（S1）",
    NA, ft("NASDAQ上市公司"), "", "2001",
    "https://www.rewalk.com", "B2B 医用外骨骼康复系统（上市）"))
C.append(mk("Ekso Bionics", "", "海外", "康复设备", "外骨骼",
    ["外骨骼", "上市公司", "对标标的"],
    "上市外骨骼机器人公司（NASDAQ:EKSO），为卒中与神经损伤患者提供临床级步态康复外骨骼。",
    "上市外骨骼公司，临床步态康复（S1）",
    NA, ft("NASDAQ上市公司"), "", "2005",
    "https://www.eksobionics.com", "B2B 临床康复外骨骼（上市）"))
# ---------------- 脑健康 / 认知 ----------------
C.append(mk("MindMate", "", "海外", "认知健康", "认知训练",
    ["认知训练", "APP"],
    "面向认知障碍与早期痴呆的APP，提供脑力训练、记忆游戏与日常提醒，延缓认知衰退。",
    "认知障碍早期干预APP",
    NA, NAT, "", "2015", "https://www.mindmate-app.com", "B2C 认知训练APP"))
C.append(mk("Constant Therapy", "", "海外", "认知健康", "神经康复",
    ["神经康复", "APP", "语言治疗"],
    "提供基于证据的神经康复（言语、语言、认知）个性化训练平台，用于卒中与脑损伤后恢复。",
    "个性化神经康复训练平台",
    NA, NAT, "", "2011", "https://www.constanttherapyhealth.com", "B2B2C 神经康复APP"))
C.append(mk("HappyNeuron Pro", "", "海外", "认知健康", "认知训练",
    ["认知训练", "专业版"],
    "面向临床与治疗师的专业认知训练平台，提供标准化大脑训练项目用于老年认知康复。",
    "专业级认知训练平台（治疗师用）",
    NA, NAT, "", "2009", "https://www.happyneuronpro.com", "B2B 认知训练SaaS"))
C.append(mk("CogniFit", "", "海外", "认知健康", "认知评估",
    ["认知评估", "训练"],
    "认知评估与脑训练平台，提供标准化认知测评与个性化训练，用于老年认知健康监测。",
    "认知评估+训练平台",
    NA, NAT, "", "1999", "https://www.cognifit.com", "B2B2C 认知评估训练平台"))
C.append(mk("Dakim", "", "海外", "认知健康", "认知训练",
    ["认知训练", "触摸屏"],
    "早期老年认知训练公司，提供大屏触摸式脑健康活动，用于养老社区与家庭认知刺激。",
    "大屏触摸式老年认知刺激",
    NA, NAT, "", "2001", "https://www.dakim.com", "B2B2C 认知训练硬件/软件"))
C.append(mk("BrainHQ", "", "海外", "认知健康", "认知训练",
    ["认知训练", "循证"],
    "Posit Science出品的循证脑训练平台，多项研究支持其改善老年认知处理速度。",
    "循证脑训练平台（研究背书）",
    NA, NAT, "", "2003", "https://www.brainhq.com", "B2C/B2B 脑训练订阅"))
# ---------------- 社交 / 孤独 ----------------
C.append(mk("The Joy Club", "", "海外", "老年文娱", "会员俱乐部",
    ["会员", "社交", "英国"],
    "英国面向50+人群的会员制俱乐部，组织线下活动、课程与社群，对抗老年孤独。",
    "英国50+会员俱乐部，对抗孤独",
    NA, NAT, "", "2020", "https://www.thejoyclub.com", "B2C 老年会员社群"))
# ---------------- 照护运营 SaaS ----------------
C.append(mk("WellSky", "", "海外", "养老服务", "照护运营SaaS",
    ["照护SaaS", "上市后", "对标标的"],
    "post-acute与家庭护理领域头部SaaS与数据分析平台，连接机构、支付方与家庭，优化照护交付。",
    "post-acute照护SaaS头部（S1）",
    NA, NAT, "", "1998", "https://www.wellsky.com", "B2B 照护运营SaaS+数据"))
C.append(mk("AlayaCare", "", "海外", "养老服务", "居家照护SaaS",
    ["居家照护", "SaaS", "加拿大"],
    "加拿大居家与社区护理SaaS平台，整合临床、排班、远程监测与家庭端，提升居家养老运营效率。",
    "加拿大居家护理SaaS平台",
    NA, NAT, "", "2014", "https://www.alayacare.com", "B2B 居家护理SaaS"))
C.append(mk("CareMerge", "", "海外", "养老照护平台", "养老机构SaaS",
    ["养老机构", "SaaS", "对接"],
    "面向养老社区与Life Plan社区的运营平台，打通居民参与、家庭沟通与合规文档。",
    "养老社区运营对接平台",
    NA, NAT, "", "2013", "https://www.caremerge.com", "B2B 养老社区SaaS"))
C.append(mk("LifeLoop", "", "海外", "养老照护平台", "居民参与",
    ["养老社区", "居民参与", "家庭沟通"],
    "专注养老社区居民参与与家庭沟通的软件，提升入住体验与家属信任。",
    "养老社区居民参与+家庭沟通",
    NA, NAT, "", "2018", "https://www.lifeloopcare.com", "B2B 养老社区参与SaaS"))
C.append(mk("OnShift", "", "海外", "养老服务", "人力资源SaaS",
    ["人力", "排班", "养老"],
    "面向老年护理与长期照护机构的人力资源与排班SaaS，缓解照护人力短缺。",
    "照护机构人力排班SaaS",
    NA, NAT, "", "2008", "https://www.onshift.com", "B2B 护理人力SaaS"))
C.append(mk("ClearCare", "", "海外", "养老服务", "居家照护SaaS",
    ["居家照护", "SaaS"],
    "家庭护理机构运营SaaS（已被WellSky收购），提供排班、计费与家庭门户。",
    "家庭护理SaaS（已被WellSky收购）",
    NA, NAT, "", "2008", "https://www.clearcareonline.com", "B2B 家庭护理SaaS"))
C.append(mk("Medflyt", "", "海外", "养老服务", "居家照护匹配",
    ["居家照护", "排班匹配"],
    "面向家庭护理机构的排班与合规自动化平台，连接护理员与班次需求。",
    "家庭护理排班匹配自动化",
    NA, NAT, "", "2016", "https://www.medflyt.com", "B2B 家庭护理排班SaaS"))
C.append(mk("CareJoy", "", "海外", "养老服务", "居家照护运营",
    ["居家照护", "运营"],
    "家庭护理机构运营平台，提供排班、计费、合规与家庭沟通一体化方案。",
    "家庭护理机构运营一体化",
    NA, NAT, "", "", "https://www.carejoy.com", "B2B 家庭护理运营SaaS"))
C.append(mk("Hometeam", "", "海外", "养老服务", "居家照护",
    ["居家照护", "技术+服务"],
    "将技术平台与人力结合的家庭护理公司，用自研APP提升护理协调与家属可视性。",
    "技术+服务的家庭护理",
    NA, NAT, "", "2013", "https://www.hometeam.com", "B2B2C 家庭护理平台"))
# ---------------- 医保计划 (Medicare Advantage) ----------------
C.append(mk("Clover Health", "", "海外", "养老金融", "医疗保险计划",
    ["Medicare Advantage", "上市公司", "对标标的"],
    "以技术驱动的Medicare Advantage健康险公司（NASDAQ:CLOV），用Clover Assistant赋能医生决策。",
    "技术驱动MA计划，上市（S1）",
    NA, ft("NASDAQ上市公司"), "", "2014",
    "https://www.cloverhealth.com", "B2B2C Medicare Advantage保险"))
C.append(mk("Alignment Health", "", "海外", "养老金融", "医疗保险计划",
    ["Medicare Advantage", "上市公司", "对标标的"],
    "以人为中心的Medicare Advantage健康险公司（NASDAQ:ALHC），强调慢病管理与个性化照护。",
    "MA计划，上市（S1），慢病管理导向",
    NA, ft("NASDAQ上市公司"), "", "2013",
    "https://www.alignmenthealthplan.com", "B2B2C Medicare Advantage保险"))
C.append(mk("CareMax", "", "海外", "养老金融", "医疗保险+诊所",
    ["Medicare", "诊所", "上市公司"],
    "为Medicare受益人与复杂慢病人群提供综合医疗与养老关怀服务的上市公司（NASDAQ:CMAX）。",
    "Medicare综合医疗+养老关怀，上市",
    NA, ft("NASDAQ上市公司"), "", "2011",
    "https://www.caremax.com", "B2B2C Medicare医疗+养老"))
# ---------------- 长寿 / 生物医药 ----------------
C.append(mk("Retro Biosciences", "", "海外", "长寿科技/生物医药", "细胞重编程",
    ["长寿科技", "有融资", "对标标的"],
    "长寿生物科技公司，聚焦细胞重编程（ reprogramming）延长健康寿命，2023年完成1.8亿美元融资。",
    "1.8亿美元融资，细胞重编程延长健康寿命",
    fd("1.8亿美元", "早期", "2023", "早期 1.8亿美元 (2023)"),
    ft("累计约1.8亿美元"), "", "2021",
    "https://www.retrobiosciences.com", "B2B 长寿生物技术研发"))
C.append(mk("Life Biosciences", "", "海外", "长寿科技/生物医药", "衰老干预",
    ["长寿科技", "有融资"],
    "专注衰老干预（包括休眠神经元重激活等）的长寿生物科技公司，曾获多轮融资。",
    "衰老干预长寿生物科技",
    NA, NAT, "", "2017", "https://www.lifebiosciences.com", "B2B 长寿生物技术研发"))
C.append(mk("Idoven", "", "海外", "长寿科技/生物医药", "AI心电",
    ["AI诊断", "心电", "有融资"],
    "用AI解读心电图的可穿戴心电监测公司，提前发现房颤等老年高发心血管风险。",
    "AI心电监测，老年心血管风险早筛",
    NA, NAT, "", "2016", "https://www.idoven.ai", "B2B2C AI心电监测"))
C.append(mk("InsideTracker", "", "海外", "长寿科技/生物医药", "血液生物标志",
    ["长寿", "血液检测", "订阅"],
    "通过血液生物标志物+AI提供个性化健康与长寿建议的消费级平台。",
    "血液标志物+AI个性化长寿建议",
    NA, NAT, "", "2009", "https://www.insidetracker.com", "B2C 长寿血液检测订阅"))
C.append(mk("Function Health", "", "海外", "长寿科技/生物医药", "全面体检",
    ["长寿", "体检", "订阅"],
    "提供100+项指标年度体检与趋势追踪的会员制健康平台，面向 longevity 人群。",
    "会员制全面体检+趋势追踪",
    NA, NAT, "", "2020", "https://www.functionhealth.com", "B2C 长寿体检订阅"))
C.append(mk("Prenuvo", "", "海外", "长寿科技/生物医药", "全身MRI",
    ["长寿", "影像学", "全身MRI"],
    "提供30分钟无痛全身MRI早筛的连锁服务，面向高支付力健康与长寿人群。",
    "全身MRI早筛连锁",
    NA, NAT, "", "2018", "https://www.prenuvo.com", "B2C 全身MRI早筛"))
C.append(mk("Fountain Life", "", "海外", "长寿科技/生物医药", "长寿诊所",
    ["长寿诊所", "早筛"],
    "由Bryan Johnson等推动的长寿诊所与年度体检中心，整合AI、基因组与影像早筛。",
    "高端长寿诊所+年度早筛",
    NA, NAT, "", "2021", "https://www.fountainlife.com", "B2C 长寿诊所会员"))
C.append(mk("Elysium Health", "", "海外", "长寿科技/生物医药", "补剂",
    ["长寿", "补剂", "科研背书"],
    "将长寿科研转化为消费级补剂（如NAD+前体Basis）的公司，与MIT等研究机构合作。",
    "长寿消费补剂（科研转化）",
    NA, NAT, "", "2014", "https://www.elysiumhealth.com", "B2C 长寿补剂订阅"))
# ---------------- 女性健康 / 更年期 ----------------
C.append(mk("Peppy", "", "海外", "健康服务", "更年期健康",
    ["女性健康", "雇主福利", "英国"],
    "英国雇主更年期与女性健康福利平台，为职场女性提供专家支持，覆盖围绝经期。",
    "英国雇主更年期福利平台",
    NA, NAT, "", "2018", "https://www.peppy.health", "B2B 雇主女性健康福利"))
C.append(mk("Stella", "", "海外", "健康服务", "更年期健康",
    ["女性健康", "更年期", "APP"],
    "面向更年期女性的数字健康平台，提供症状评估、专家咨询与个性化管理方案。",
    "更年期女性数字健康平台",
    NA, NAT, "", "2021", "https://www.stella.io", "B2B2C 更年期数字健康"))
# ---------------- 安全 / 跌倒监测 ----------------
C.append(mk("Kinesense", "", "海外", "健康服务", "步态分析",
    ["步态", "跌倒预测", "AI"],
    "通过AI视频分析步态与活动模式，早期预测跌倒风险，用于养老机构与医院。",
    "AI步态分析预测跌倒风险",
    NA, NAT, "", "2017", "https://www.kinesense.com", "B2B 步态跌倒风险SaaS"))
C.append(mk("Cartken", "", "海外", "养老机器人", "配送机器人",
    ["配送机器人", "有融资"],
    "自主配送机器人公司，可将餐食、药品等送达养老机构与社区老人，缓解人力短缺。",
    "自主配送机器人，养老场景配送",
    NA, NAT, "", "2015", "https://www.cartken.com", "B2B 自主配送机器人"))
C.append(mk("WalkJoy", "", "海外", "康复设备", "步态训练",
    ["步态", "防跌倒", "可穿戴"],
    "通过可穿戴设备提供实时步态反馈与训练，改善老人平衡、降低跌倒风险。",
    "可穿戴步态反馈防跌倒",
    NA, NAT, "", "2014", "https://www.walkjoy.com", "B2C/B2B 步态训练可穿戴"))
C.append(mk("Kraydel", "", "海外", "健康服务", "远程监测",
    ["远程监测", "英国", "雷达"],
    "英国养老远程监测公司，用非侵入式传感器监测老人在家安全与日常活动异常。",
    "英国非侵入式居家安全监测",
    NA, NAT, "", "2019", "https://www.kraydel.com", "B2B 居家远程监测"))
C.append(mk("Tunstall", "", "海外", "健康服务", "远程照护",
    ["远程照护", "英国", "紧急呼叫"],
    "英国老牌远程照护（telecare）与紧急呼叫服务商，为大量老年与脆弱人群提供24/7监测。",
    "英国远程照护与紧急呼叫龙头",
    NA, NAT, "", "1957", "https://www.tunstall.co.uk", "B2B 远程照护+紧急呼叫"))
C.append(mk("Lifted", "", "海外", "健康服务", "远程监测",
    ["远程监测", "英国", "AI"],
    "英国AI养老监测公司，用非穿戴传感器识别跌倒、离床等异常并告警家属/护理方。",
    "英国AI非穿戴养老监测",
    NA, NAT, "", "2019", "https://www.lifted.ai", "B2B 养老AI监测"))
# ---------------- 用药管理 ----------------
C.append(mk("Capsule", "", "海外", "健康服务", "药品配送",
    ["药品配送", "药房", "有融资"],
    "以技术驱动的连锁药房，提供当日送药与用药管理，便利居家老人慢病用药。",
    "技术药房当日送药，便利老人",
    NA, NAT, "", "2016", "https://www.capsule.com", "B2B2C 药品配送+管理"))
C.append(mk("EllieGrid", "", "海外", "健康服务", "智能药盒",
    ["用药管理", "智能药盒"],
    "智能药盒公司，通过APP提醒与色彩编码帮助老人按时按量服药。",
    "智能药盒提醒按时服药",
    NA, NAT, "", "2015", "https://www.elliegrid.com", "B2C 智能药盒"))
C.append(mk("PharmAdva", "", "海外", "健康服务", "用药管理",
    ["用药管理", "预分包"],
    "为长期用药老人提供按次预分包（pill packaging）与配送的服务，降低错服漏服。",
    "用药预分包+配送服务",
    NA, NAT, "", "", "https://www.pharmadva.com", "B2B2C 用药预分包服务"))
# ---------------- 膳食 / 营养 ----------------
C.append(mk("Mom's Meals", "", "海外", "健康食品", "病炊配送",
    ["医疗膳食", "配送", "慢病"],
    "面向慢病与居家老人的医疗定制餐食配送公司，可对接医保/医疗计划。",
    "医疗定制餐食配送，对接医保",
    NA, NAT, "", "1994", "https://www.momsmeals.com", "B2B2C 医疗餐食配送"))
C.append(mk("Silver Cuisine", "", "海外", "健康食品", "老年膳食",
    ["老年膳食", "订阅"],
    "bistroMD旗下针对50+人群的定制膳食订阅服务，按营养需求配送。",
    "50+定制膳食订阅",
    NA, NAT, "", "2012", "https://www.silvercuisine.com", "B2C 老年膳食订阅"))
C.append(mk("Magic Kitchen", "", "海外", "健康食品", "老年膳食",
    ["老年膳食", "冷冻餐"],
    "提供适合老人（低脂/软食/疾病特定）的冷冻餐配送公司。",
    "老年特定冷冻餐配送",
    NA, NAT, "", "2005", "https://www.magickitchen.com", "B2C 老年膳食配送"))
C.append(mk("Kate Farms", "", "海外", "健康食品", "医学营养",
    ["医学营养", "有融资"],
    "植物基医学营养（医用营养品）公司，为吞咽/营养障碍人群提供管饲与口服营养。",
    "植物基医用营养品",
    NA, NAT, "", "2010", "https://www.katefarms.com", "B2B2C 医学营养品"))
# ---------------- 临终 / 身后规划 ----------------
C.append(mk("Solace", "", "海外", "健康服务", "福利导航",
    ["福利导航", "有融资"],
    "医疗福利导航平台，帮用户梳理保险、找到合适医疗资源，含复杂慢病与临终关怀协调。",
    "医疗福利导航，含临终协调",
    NA, NAT, "", "2020", "https://www.solace.health", "B2B2C 医疗福利导航"))
C.append(mk("Empathy", "", "海外", "健康服务", "身后事务",
    ["身后规划", "哀伤支持", "有融资"],
    "bereavement（丧亲）支持平台，帮助逝者家属处理法律、财务与情绪事务，获a16z等投资。",
    "丧亲事务+哀伤支持平台",
    NA, NAT, "", "2020", "https://www.empathy.com", "B2C 丧亲支持平台"))
# ---------------- 其他 / 跨界 ----------------
C.append(mk("Butlr", "", "海外", "适老科技", "非接触传感",
    ["非接触传感", "有融资", "隐私"],
    "用热传感（thermal）实现非接触式存在/跌倒/睡眠监测的AI平台，保护隐私，适用于养老场景。",
    "热传感非接触式养老监测（隐私优先）",
    NA, NAT, "", "2019", "https://www.butlr.io", "B2B 非接触式传感AI平台"))
C.append(mk("Lotus", "", "海外", "健康服务", "女性健康",
    ["女性健康", "更年期"],
    "面向女性全生命周期（含围绝经期）的数字健康公司，获1843 Capital等投资。",
    "女性全生命周期数字健康",
    NA, NAT, "", "", "https://www.lotushealth.com", "B2B2C 女性数字健康"))
C.append(mk("Guaranteed", "", "海外", "养老金融", "退休理财",
    ["退休理财", "有融资"],
    "面向老年人的退休理财与年金咨询平台，帮助规划退休收入，获Cake Ventures投资。",
    "老年退休理财规划平台",
    NA, NAT, "", "2020", "https://www.guaranteed.ai", "B2B2C 退休理财规划"))
C.append(mk("Bright", "", "海外", "养老金融", "退休理财",
    ["退休理财", "有融资"],
    "退休收入与理财规划平台，帮助临近退休人群优化储蓄与支出，获Cake Ventures投资。",
    "退休收入规划平台",
    NA, NAT, "", "2021", "https://www.bright.app", "B2B2C 退休理财规划"))
C.append(mk("Voxela", "", "海外", "健康服务", "慢病管理",
    ["慢病管理", "数据", "有融资"],
    "面向老年慢病（如COPD）的远程监测与数据平台，获Third Act Ventures等投资。",
    "老年慢病远程监测平台",
    NA, NAT, "", "", "https://www.voxela.com", "B2B 慢病远程监测"))
C.append(mk("Cariloop", "", "海外", "养老服务", "照护协调",
    ["照护协调", "雇主福利", "有融资"],
    "为雇主提供的照护协调福利平台，帮员工平衡工作与家庭照护责任，获1843 Capital投资。",
    "雇主照护协调福利平台",
    NA, NAT, "", "2012", "https://www.cariloop.com", "B2B 照护协调福利"))
C.append(mk("Bluecrest", "", "海外", "健康服务", "健康筛查",
    ["健康筛查", "英国", "体检"],
    "英国平价健康筛查与体检公司，为成人（含老人）提供常规指标检测与风险预警。",
    "英国平价健康筛查",
    NA, NAT, "", "2015", "https://www.bluecresthealth.co.uk", "B2C 健康筛查体检"))
# ---------------- 欧洲养老科技 ----------------
C.append(mk("Hometouch", "", "海外", "养老服务", "居家照护",
    ["居家照护", "英国", "平台"],
    "英国居家照护平台，直接雇佣并培训护理员，提供透明定价的居家养老护理。",
    "英国直雇式居家照护平台",
    NA, NAT, "", "2015", "https://www.hometouch.co.uk", "B2B2C 居家照护平台"))
C.append(mk("SuperCarers", "", "海外", "养老服务", "居家照护匹配",
    ["居家照护", "匹配", "英国"],
    "英国居家照护匹配平台，连接家庭与经过审核的护理员，并提供管理工具。",
    "英国居家照护匹配平台",
    NA, NAT, "", "2014", "https://www.supercarers.com", "B2B2C 居家照护匹配"))
C.append(mk("Portever", "", "海外", "养老地产", "养老社区",
    ["养老社区", "运营", "海外"],
    "海外养老社区与退休生活运营商，提供持续照料退休社区（CCRC）模式。",
    "海外CCRC养老社区运营商",
    NA, NAT, "", "", "https://www.portever.com", "B2B/B2C 养老社区运营"))
C.append(mk("Person Centred Software", "", "海外", "养老照护平台", "照护记录",
    ["照护记录", "英国", "SaaS"],
    "英国养老照护记录（mCare）SaaS，用移动端简化护理记录与合规，覆盖大量养老机构。",
    "英国移动护理记录SaaS",
    NA, NAT, "", "2013", "https://www.personcentredsoftware.com", "B2B 护理记录SaaS"))
C.append(mk("Mayden", "", "海外", "健康服务", "健康记录",
    ["健康记录", "英国", "SaaS"],
    "英国心理健康与护理SaaS公司，提供电子健康记录系统（如iaptus），覆盖老年心理照护。",
    "英国护理电子健康记录SaaS",
    NA, NAT, "", "2006", "https://www.mayden.co.uk", "B2B 护理EHR SaaS"))
C.append(mk("Oomph! Wellness", "", "海外", "老年文娱", "活力康养",
    ["活力康养", "活动", "英国"],
    "英国为养老机构提供活力康养（wellbeing）活动与训练的公司，提升入住老人身心活跃度。",
    "英国养老机构活力康养活动",
    NA, NAT, "", "2011", "https://www.oomph-wellness.org", "B2B 养老机构康养活动"))
C.append(mk("CareVision", "", "海外", "养老照护平台", "家庭沟通",
    ["家庭沟通", "英国", "SaaS"],
    "英国养老照护平台，提供家庭门户、护理记录与运营工具，连接机构与家属。",
    "英国养老家庭门户SaaS",
    NA, NAT, "", "2015", "https://www.carevision.co.uk", "B2B 养老家庭门户SaaS"))
# ---------------- 康复 / 神经 ----------------
C.append(mk("Strolll", "", "海外", "康复设备", "AR神经康复",
    ["神经康复", "AR眼镜", "有融资"],
    "用增强现实（AR）眼镜为神经疾病（帕金森、卒中）患者提供居家神经康复训练，2025年3月完成1220万欧元融资。",
    "1220万欧元融资，AR眼镜居家神经康复",
    fd("1220万欧元", "早期", "2025-03", "早期 1220万欧元 (2025-03)"),
    ft("累计约1220万欧元"), "", "2019",
    "https://www.strolll.com", "B2B2C AR神经康复硬件+软件"))
C.append(mk("Sword Health", "", "海外", "康复设备", "数字康复",
    ["数字康复", "有融资", "远程"],
    "远程数字肌肉骨骼（MSK）与疼痛康复平台，用智能设备+远程物理治疗师为慢病/老年疼痛提供康复。",
    "数字MSK/疼痛康复平台，远程物理治疗",
    NA, NAT, "", "2015", "https://www.swordhealth.com", "B2B2C 数字康复平台"))
C.append(mk("Kaia Health", "", "海外", "康复设备", "数字康复",
    ["数字康复", "MSK", "APP"],
    "数字肌肉骨骼与慢病康复APP，提供AI-guided 运动治疗，用于老年背痛与慢性疼痛管理。",
    "数字MSK康复APP，AI指导运动治疗",
    NA, NAT, "", "2016", "https://www.kaiahealth.com", "B2B2C 数字康复APP"))
# ---------------- 中国补充 ----------------
C.append(mk("星纵物联", "星纵物联", "国内", "智能硬件", "毫米波传感",
    ["毫米波", "跌倒监测", "物联网"],
    "物联网传感企业（Milesight），推出LoRaWAN雷达跌倒检测传感器，用于养老机构与居家非接触式跌倒/离床监测。",
    "毫米波雷达跌倒监测传感器（养老场景）",
    NA, NAT, "", "2011", "https://www.milesight.cn", "B2B 物联网传感（养老监测）"))
C.append(mk("清雷科技", "清雷科技", "国内", "智能硬件", "毫米波雷达",
    ["毫米波", "跌倒监测", "呼吸监测"],
    "专注毫米波雷达的生命体征与跌倒监测公司（86Elec），提供非接触式老人看护与睡眠呼吸监测方案。",
    "毫米波雷达非接触式老人看护",
    NA, NAT, "", "2019", "https://www.86elec.com", "B2B 毫米波雷达监测方案"))
C.append(mk("来邦科技", "来邦科技", "国内", "养老用品", "呼叫系统",
    ["呼叫系统", "养老机构", "上市公司"],
    "国产医护对讲与养老呼叫系统企业，为养老机构提供紧急呼叫、监护对讲等适老通信设备（新三板/上市体系）。",
    "国产养老呼叫对讲系统（上市体系）",
    NA, ft("上市公司(来邦科技)"), "", "2004",
    "https://www.laibang.com", "B2B 养老呼叫通信系统"))

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = set()
    for x in data:
        n = (x.get("name") or "").strip().lower()
        if n: existing.add(n)
        nc = (x.get("name_cn") or "").strip().lower()
        if nc: existing.add(nc)
    max_serial = max([int(x.get("serial","#0000").lstrip("#"))
                      for x in data if str(x.get("serial","")).startswith("#")], default=0)
    added, skipped = [], []
    for c in C:
        key = (c["name"] or "").strip().lower()
        key2 = (c.get("name_cn") or "").strip().lower()
        if key in existing or (key2 and key2 in existing):
            skipped.append(c["name"]); continue
        max_serial += 1
        c["serial"] = "#%04d" % max_serial
        data.append(c); added.append(c["name"])
        existing.add(key)
        if key2: existing.add(key2)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("TOTAL after:", len(data))
    print("ADDED:", len(added)); 
    for a in added: print("  +", a)
    print("SKIPPED (dup):", len(skipped))
    for s in skipped: print("  =", s)

if __name__ == "__main__":
    main()
