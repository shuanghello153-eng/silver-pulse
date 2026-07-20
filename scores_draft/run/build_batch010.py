# -*- coding: utf-8 -*-
import json

def rv(signal, info, diff, copy):
    s = signal*0.3 + info*0.3 + diff*0.2 + copy*0.2
    return round(s*10, 1)

# each: serial, signal, info, diff, copy, desc_cn, payor, role, founded, stage,
#       events, highlights, silver_verdict, silver_reason,
#       rec_v1, rec_v2, rec_v3
E = []

E.append(dict(
    serial="#0037", signal=4.05, info=6, diff=7, copy=6,
    desc_cn="柔性外骨骼助行设备商，主打轻量化肌肉外甲",
    payor="个人自费为主，部分康复场景纳入医保/商业保险",
    role="制造商(硬件/设备)", founded=2018, stage="融资中",
    events=[
        {"date":"2021-04","text":"完成A轮约$1000万融资（碧桂园创投、乔贝资本领投，高瓴、BV百度风投、线性资本跟投）"},
        {"date":"2024","text":"产品获国内医疗器械注册认证"},
        {"date":"2025-01","text":"获央视新质生产力年度殊荣并入选《麻省理工科技评论》50家聪明公司"}
    ],
    highlights=[
        "柔性可穿戴'肌肉外甲'用于偏瘫等康复场景",
        "2024年获国内医疗器械注册认证",
        "2025年入选《麻省理工科技评论》50家聪明公司",
        "获央视新质生产力年度殊荣（2025）"
    ],
    silver_verdict="核心银发",
    silver_reason="柔性外骨骼直接服务老年人及行动不便人群日常助行与康复",
    rec_v1="资本与媒体双重背书下，这家柔性外骨骼技术方公开资料扎实，其'肌肉外甲'把康复从机构搬到日常，轻量化思路值得国内硬件创业者参考。",
    rec_v2="信息层面央视与MIT榜单已有定调，差异化在于用柔性可穿戴重构助行体验，国内适老辅具同质化严重，它的产品定义值得拆解借鉴。",
    rec_v3="信号来自A轮与权威奖项，资料可读性强；把偏瘫康复做成消费级穿戴的路径反共识，国内创业者可学其供应链与场景切法。"
))

E.append(dict(
    serial="#0471", signal=4.05, info=7, diff=7, copy=5,
    desc_cn="为雇主与健康计划提供护理员支持服务的平台",
    payor="企业雇主+健康计划+个人自付（混合支付）",
    role="服务商", founded=2018, stage="融资中",
    events=[
        {"date":"2022-05","text":"Series B 约$2000万"},
        {"date":"2024-11","text":"Series B Extension 约$2000万，自2022年以来规模增长4倍"}
    ],
    highlights=[
        "技术驱动的家庭照护（family caregiving）解决方案，服务雇主与健康计划",
        "2024年11月再融资约$2000万，规模自2022年增长4倍",
        "累计融资约$5800万~$7850万（来源口径差异）"
    ],
    silver_verdict="核心银发",
    silver_reason="面向老年家庭照护者提供情感与专业支持，根植老龄化照护需求",
    rec_v1="雇主与健康计划买单的照护者支持模式信号清晰，公开案例丰富，它把'照护离职'变成员工福利，国内企业福利尚空白可借鉴。",
    rec_v2="信息与融资脉络清楚，差异化在绕开直接服务老人、专做护理员后援，这种B端切法对国内照护平台有启发。",
    rec_v3="资本持续加注印证需求真实，材料详实；用平台托管情感与专业支持的做法反常规，国内可抄其雇主合作框架。"
))

E.append(dict(
    serial="#0564", signal=4.05, info=8, diff=8, copy=5,
    desc_cn="连接学生与老人的陪伴式照护平台（共享儿女）",
    payor="健康计划/Medicare+个人自付+企业福利（混合支付）",
    role="服务商", founded=2016, stage="融资中",
    events=[
        {"date":"2024-07","text":"Series D延展$60M，累计约$257M"},
        {"date":"2026-06","text":"获联邦痴呆照护项目支持"}
    ],
    highlights=[
        "'共享儿女'陪伴模式连接学生与老人，提供交通/家务/陪伴",
        "估值约$1.4B，软银愿景基金2领投",
        "2026年获联邦痴呆照护项目背书"
    ],
    silver_verdict="核心银发",
    silver_reason="以陪伴服务切入老年群体文娱社交与照护，典型银发赛道",
    rec_v1="独角兽级信号与高曝光下资料充沛，其'共享儿女'把陪伴做成规模化服务，国内银发陪伴多小散，可学其平台化与支付设计。",
    rec_v2="信息广度够写深度稿，差异化在以学生劳动力重构照护关系，反共识强；国内缺健康计划付费方，但模式骨架可平移。",
    rec_v3="信号与媒体声量双高，案例可读性强；把人情陪伴标准化交付的思路独特，国内创业者应研究其获客与质量管控。"
))

E.append(dict(
    serial="#0861", signal=4.05, info=8, diff=5, copy=4,
    desc_cn="美国价值导向肾病与心血管综合护理龙头",
    payor="混合（健康计划+政府Medicare价值医疗合同，B端机构付费为主）",
    role="服务商", founded=2016, stage="融资中",
    events=[
        {"date":"2022-02","text":"Series E $325M（估值超$25亿）"},
        {"date":"2025-06","text":"Series G 约$75M，估值约$4.98B"}
    ],
    highlights=[
        "价值导向肾+心血管综合护理龙头",
        "G轮约$75M（2025-06），估值约$4.98B",
        "服务突破50万生命，降低肾病死亡率13%",
        "自研预测分析RenalIQ延缓疾病进展"
    ],
    silver_verdict="核心银发",
    silver_reason="聚焦老年高发的肾病/心血管慢病管理，价值医疗直接服务老龄群体",
    rec_v1="大额G轮与临床数据构成强信号，公开材料扎实，其肾心一体价值医疗路径清晰，国内按价值付费尚早但方向可对标。",
    rec_v2="信息维度第三方研究充分，差异化在把慢病管理绑定支付方降本，反共识弱但稳健，国内可借鉴其多学科团队打法。",
    rec_v3="资本与成效双重背书，资料详实；以预测分析延缓肾衰的VBC模型独特，国内医保支付改革下值得跟踪其对标样本。"
))

E.append(dict(
    serial="#0959", signal=4.05, info=7, diff=7, copy=7,
    desc_cn="AI语音转写护理记录的养老软件（德国1000+机构）",
    payor="B端机构采购（养老机构订阅）",
    role="技术服务商", founded=2020, stage="成长期",
    events=[
        {"date":"2025-03","text":"Seed $9M"},
        {"date":"2025-11","text":"A轮€4300万（Balderton Capital领投）"}
    ],
    highlights=[
        "AI语音将护理员口述转为合规结构化文档",
        "已在德国1000+家养老机构落地",
        "2025年A轮€4300万，Balderton领投"
    ],
    silver_verdict="核心银发",
    silver_reason="为养老机构提供AI护理记录工具，直接提升老龄照护效率",
    rec_v1="德国千机构落地给出强信号，公开技术细节充足，其语音转护理文档直击记录痛点，国内养老机构数字化正缺此类轻量工具。",
    rec_v2="信息与融资脉络清楚，差异化在把AI塞进护理员口述场景而非堆硬件，反共识；国内可快速复制这套SaaS化思路。",
    rec_v3="资本连续加注印证赛道，材料可读；用语音解放护理生产力的模式清晰，国内创业者应学其合规文档与部署轻量化。"
))

E.append(dict(
    serial="#0032", signal=3.55, info=4, diff=7, copy=6,
    desc_cn="AI眼动追踪认知障碍早筛与干预服务商",
    payor="医疗机构/企业/政府支付+个人自费（混合支付）",
    role="产品商(软件/AI)", founded=2020, stage="早期",
    events=[
        {"date":"2022-02","text":"天使轮约$1000万（诺庾资本）"}
    ],
    highlights=[
        "AI摄像头眼动追踪，6分钟评估认知功能",
        "阿尔茨海默风险鉴别准确度约93%",
        "延伸干预治疗与保险支付综合服务"
    ],
    silver_verdict="核心银发",
    silver_reason="专注认知障碍早筛与干预，直接对应失智老人赛道",
    rec_v1="早期信号偏弱但技术叙事清晰，公开资料有限，其眼动筛查把认知症评估压到6分钟，国内早筛蓝海值得跟踪其注册路径。",
    rec_v2="信息量中等，差异化在用眼动数字标记物替代问卷，反共识强；国内认知筛查刚起量，可借鉴其医疗+保险闭环设计。",
    rec_v3="资本关注尚浅但技术独特，材料偏少；把阿尔茨海默风险量化到93%准确度的思路稀缺，国内创业者可学其产品化切入。"
))

E.append(dict(
    serial="#0457", signal=3.55, info=7, diff=6, copy=5,
    desc_cn="居家护理技术与网络平台，号称滴滴护工",
    payor="个人自付+政府/长护险+机构采购（混合支付）",
    role="服务商", founded=2014, stage="融资中",
    events=[
        {"date":"2021","text":"收购全美最大居家护理公司Home Instead（约$2.1B，覆盖14国）"},
        {"date":"2024-03","text":"Series E $70M"},
        {"date":"2025-03","text":"再融资约$1.4亿"}
    ],
    highlights=[
        "全球最大居家养老网络与技术平台",
        "2021年收购Home Instead（覆盖14国）",
        "估值约$1.25B，2025年再融约$1.4亿"
    ],
    silver_verdict="核心银发",
    silver_reason="居家护理平台直接服务老年人群，典型银发照护基础设施",
    rec_v1="独角兽与收购Home Instead构成强信号，公开报道充足，其'滴滴护工'把分散劳动力组网，国内居家护理可学其平台调度。",
    rec_v2="信息与资本脉络清楚，差异化在自营+加盟混合网络，反共识；国内护工平台散乱，可借鉴其标准化与并购扩张法。",
    rec_v3="高信号伴随高曝光，案例详实；把护理员当核心资产运营的轻模式独特，国内应研究其质量管控与B端合作框架。"
))

E.append(dict(
    serial="#0458", signal=3.55, info=7, diff=7, copy=6,
    desc_cn="AI监护设备商，实时感知老年社区环境",
    payor="B端机构采购（养老社区订阅）+个人增值",
    role="技术服务商", founded=2016, stage="融资中",
    events=[
        {"date":"2025-03","text":"Series A $35M"},
        {"date":"2025-09","text":"Series B $100M（Insight Partners领投）"}
    ],
    highlights=[
        "AUGi设备实时感知老年社区环境",
        "定位'老年护理智能基础设施'",
        "2025年B轮$100M，18个月落地150+社区"
    ],
    silver_verdict="核心银发",
    silver_reason="AI监护直接服务老年社区安全与生活质量",
    rec_v1="亿级B轮与百家社区给出强信号，材料详实，其AUGi设备把监护变被动为主动，国内养老社区缺这类智能基建可借鉴。",
    rec_v2="信息维度融资与落地清晰，差异化在用环境感知替代可穿戴，反共识；国内可复制其'护理智能基础设施'定位。",
    rec_v3="资本与扩张双高，资料可读；把AI嵌入生活场景而非告警器的思路独特，国内创业者应学其B端部署与数据闭环。"
))

E.append(dict(
    serial="#0463", signal=3.55, info=6, diff=6, copy=5,
    desc_cn="连接医疗与社会服务的老年社区支持平台",
    payor="政府/医保+健康计划+个人自付（混合支付）",
    role="平台", founded=2020, stage="融资中",
    events=[
        {"date":"2025-04","text":"Series A $26M（Insight Partners领投）"}
    ],
    highlights=[
        "覆盖21个州700+社区项目",
        "连接医疗保健提供者与社会服务组织",
        "为老人提供交通/送餐/社交等支持"
    ],
    silver_verdict="核心银发",
    silver_reason="整合医疗与社会服务支撑老年社区生活，根植银发需求",
    rec_v1="千万级A轮与21州覆盖构成信号，公开信息中等，其连接医疗与社会服务的整合照护反共识，国内可学其社区协同框架。",
    rec_v2="资料维度融资与规模清楚，差异化在把送餐交通社交打包成服务，轻模式；国内社区养老可借鉴其跨系统对接。",
    rec_v3="资本加注印证需求，材料可读；用平台缝合碎片化老龄服务的思路独特，国内创业者应研究其B端政府/机构合作。"
))

E.append(dict(
    serial="#0464", signal=3.55, info=6, diff=6, copy=6,
    desc_cn="可穿戴AI健康监测，提前预警健康下滑",
    payor="B端机构采购（养老机构订阅）+个人增值",
    role="技术服务商", founded=2013, stage="融资中",
    events=[
        {"date":"2023-07","text":"Series A $29M"}
    ],
    highlights=[
        "AI自主识别日常活动与行为变化",
        "住院率降低39%，跌倒率降低69%",
        "累计融资约$4860万"
    ],
    silver_verdict="核心银发",
    silver_reason="可穿戴AI监测服务老年健康预警，典型银发科技",
    rec_v1="近五千万融资与明确成效数据构成信号，信息公开度中等，其可穿戴提前预警健康下滑，国内机构可学其行为分析模型。",
    rec_v2="资料维度融资与成效清楚，差异化在用日常行为而非体征做预测，反共识；国内可复制其跌倒/住院率下降打法。",
    rec_v3="资本与临床双背书，材料可读；把AI埋进生活轨迹预警的思路独特，国内创业者应研究其硬件+数据分析闭环。"
))

E.append(dict(
    serial="#0465", signal=3.55, info=6, diff=6, copy=5,
    desc_cn="企业雇主端的在职照护者支持平台",
    payor="企业雇主采购+个人自付（混合支付）",
    role="服务商", founded=2012, stage="融资中",
    events=[
        {"date":"2024-04","text":"Series C $20M"}
    ],
    highlights=[
        "为宝洁、毕马威等企业提供照护者支持",
        "收入3年增长近300%，NPS超80",
        "定位员工福利与留任率提升"
    ],
    silver_verdict="核心银发",
    silver_reason="支持在职子女照护老年父母，照护对象为老龄群体",
    rec_v1="数千万C轮与宝洁等客户给出信号，公开信息中等，其把照护变员工福利的反共识切法，国内企业福利空白可借鉴。",
    rec_v2="资料维度融资与客户清楚，差异化在绕开C端直做雇主端，轻模式；国内可学其HR福利嵌入与留存指标。",
    rec_v3="资本持续支持印证需求，材料可读；用平台托住在职照护者的思路独特，国内创业者应研究其B端获客与服务体系。"
))

E.append(dict(
    serial="#0472", signal=3.55, info=6, diff=7, copy=7,
    desc_cn="自动对焦老花镜，全球首款度数自调节眼镜",
    payor="个人自费（消费电子）+零售渠道",
    role="产品商(硬件/消费品)", founded=2019, stage="融资中",
    events=[
        {"date":"2025-04","text":"融资约$3650万（Amazon Alexa Fund等投资）"}
    ],
    highlights=[
        "全球首款自动对焦老花镜，按老花眼自动调度数",
        "亚马逊Alexa基金等投资",
        "2025年融资约$3650万"
    ],
    silver_verdict="核心银发",
    silver_reason="自动对焦眼镜直击老花眼这一老年专属视觉需求，属银发消费品",
    rec_v1="亚马逊加持与数千万融资构成信号，公开信息中等，其自动对焦老花镜把光学变智能，国内老花镜存量市场可借鉴产品定义。",
    rec_v2="资料维度融资与投资方清楚，差异化在首款度数自调节消费电子，反共识；国内可复制其硬件+品牌打法。",
    rec_v3="资本与巨头背书双高，材料可读；把老花眼做成科技单品的思路独特，国内创业者应学其消费级定价与渠道。"
))

# ---- build output ----
enterprises_out = []
tag_review = []
nonsilver = []

# map serial -> old tags from input (hardcoded per batch)
old_tags_map = {
    "#0037": {"tag_l1":["康复辅具"], "tag_l2":["外骨骼","助行器","可穿戴监测"], "business_tags":{"customer":"B2C","role":"制造商(硬件/设备)","channel":[]}},
    "#0471": {"tag_l1":["养老服务"], "tag_l2":["照护支持"], "business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
    "#0564": {"tag_l1":["文娱社交"], "tag_l2":["陪伴服务"], "business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
    "#0861": {"tag_l1":["养老服务"], "tag_l2":["慢病管理"], "business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
    "#0959": {"tag_l1":["行业服务"], "tag_l2":["养老软件"], "business_tags":{"customer":"B2B","role":"技术服务商","channel":[]}},
    "#0032": {"tag_l1":["养老服务"], "tag_l2":["认知训练","认知筛查"], "business_tags":{"customer":"未标注","role":"服务商","channel":[]}},
    "#0457": {"tag_l1":["养老服务"], "tag_l2":["护工平台"], "business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
    "#0458": {"tag_l1":["康复辅具"], "tag_l2":["跌倒监测"], "business_tags":{"customer":"B2B","role":"技术服务商","channel":[]}},
    "#0463": {"tag_l1":["文娱社交"], "tag_l2":["社区"], "business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
    "#0464": {"tag_l1":["康复辅具"], "tag_l2":["跌倒监测"], "business_tags":{"customer":"B2B","role":"技术服务商","channel":[]}},
    "#0465": {"tag_l1":["养老服务"], "tag_l2":["照护支持"], "business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
    "#0472": {"tag_l1":["消费品"], "tag_l2":["眼镜"], "business_tags":{"customer":"B2B","role":"服务商(媒体/数据)","channel":[]}},
}

name_map = {
    "#0037":"远也","#0471":"Homethrive","#0564":"Papa","#0861":"Somatus","#0959":"Voize",
    "#0032":"织生科技","#0457":"Honor","#0458":"Inspiren","#0463":"Blooming Health",
    "#0464":"CarePredict","#0465":"Cariloop","#0472":"IXI"
}

intro_map = {
    "#0037":"国内柔性外骨骼/肌肉外甲研发商，面向偏瘫及行动不便老人提供轻量化助行康复设备。",
    "#0471":"美国雇主与健康计划端的数智化家庭照护支持平台，服务在职照护者与老年家庭成员。",
    "#0564":"美国'共享儿女'式陪伴照护平台，连接学生劳动力与老人提供陪伴、交通与远程医疗。",
    "#0861":"美国价值导向的肾脏与心血管综合护理龙头，以预测分析绑定支付方降本。",
    "#0959":"德国AI语音护理记录软件商，将护理员口述转为合规结构化文档，已落地千家机构。",
    "#0032":"国内AI眼动追踪认知筛查与干预服务商，6分钟评估认知功能并延伸至保险支付。",
    "#0457":"美国居家养老网络与技术平台，收购Home Instead后覆盖14国，号称滴滴护工。",
    "#0458":"美国AI监护设备商，以AUGi实时感知老年社区环境，定位护理智能基础设施。",
    "#0463":"美国连接医疗与社会服务的老年社区支持平台，覆盖21州700+社区。",
    "#0464":"美国可穿戴AI健康监测平台，以行为分析提前预警健康下滑。",
    "#0465":"美国面向企业雇主的在职照护者支持平台，客户含宝洁、毕马威。",
    "#0472":"全球首款自动对焦老花镜研发商，按老花眼自动调度数，获亚马逊投资。"
}

# suggested tag changes (only confident ones)
suggested_map = {
    "#0458":[{"action":"change","tag":"智能硬件","reason":"Inspiren 是 AI 监护平台/智能设备商，归入'康复辅具'不够准确，建议归'智能硬件'一级"}],
    "#0464":[{"action":"change","tag":"智能硬件","reason":"CarePredict 是可穿戴AI健康平台而非康复辅具，建议归'智能硬件'一级"}],
    "#0472":[{"action":"change","tag":"产品商(硬件/消费品)","reason":"原business_tags.role误标为'服务商(媒体/数据)'，实为眼镜产品商，应在输出中更正role"}]
}

for e in E:
    ser = e["serial"]
    r = rv(e["signal"], e["info"], e["diff"], e["copy"])
    enterprises_out.append({
        "serial": ser,
        "signal_strength": e["signal"],
        "info_score": e["info"], "diff_score": e["diff"], "copy_score": e["copy"],
        "research_value": r,
        "recommend": {
            "rec_v1": e["rec_v1"], "rec_v2": e["rec_v2"], "rec_v3": e["rec_v3"],
            "info_score": e["info"], "diff_score": e["diff"], "copy_score": e["copy"],
            "signal_strength": e["signal"], "research_value": r
        },
        "payor_model": e["payor"],
        "business_tags_role": e["role"],
        "desc_cn": e["desc_cn"],
        "founded": e["founded"],
        "stage": e["stage"],
        "events": e["events"],
        "highlights": e["highlights"],
        "update_time": "2026-07-17",
        "silver_verdict": e["silver_verdict"],
        "silver_reason": e["silver_reason"]
    })
    tag_review.append({
        "serial": ser,
        "name": name_map[ser],
        "intro": intro_map[ser],
        "old_tags": old_tags_map[ser],
        "suggested": suggested_map.get(ser, [])
    })

out = {
    "batch": 10,
    "enterprises": enterprises_out,
    "tag_review": tag_review,
    "nonsilver": nonsilver
}

with open("G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run/out/batch_010_out.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("WROTE batch_010_out.json, enterprises:", len(enterprises_out))
for e in enterprises_out:
    print(e["serial"], "rv=", e["research_value"], "silver=", e["silver_verdict"])
