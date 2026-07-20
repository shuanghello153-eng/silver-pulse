import json

def E(serial, signal_strength, info_score, diff_score, copy_score, research_value,
      recommend, desc_cn, payor_model, business_tags_role, founded, stage,
      highlights, events, silver_verdict, silver_reason):
    return dict(serial=serial, signal_strength=signal_strength,
        info_score=info_score, diff_score=diff_score, copy_score=copy_score,
        research_value=research_value, recommend=recommend, desc_cn=desc_cn,
        payor_model=payor_model, business_tags_role=business_tags_role,
        founded=founded, stage=stage, highlights=highlights, events=events,
        update_time="2026-07-17", silver_verdict=silver_verdict, silver_reason=silver_reason)

rec = {
"#0696": "信号充足、信息透明，其主动式AI陪伴机器人差异化突出（日均互动超30次、已规模化部署）；可复制性受国内商保与支付体系薄弱拖累——最该学的是适老化主动交互与孤独干预的软硬一体路径，先从机构与社区场景切入。",
"#0895": "信号充足、信息透明，4D成像雷达以无摄像头隐私保护做跌倒监测差异化清晰；壁垒在全自研射频芯片，国内有毫米波雷达同类但集成度偏低——最该学用雷达替代摄像头的非接触监测思路，可直接平移至养老机构与智能家居厂商。",
"#0977": "信号充足、信息透明，行为经济学加每日小额激励提升慢病依从的打法差异化明确，临床与财务成效指标清晰；可复制性受国内按效果付费与政府支付结构差异拖累——最该学用微小激励撬动依从率的行为设计，适配医保控费与慢病管理语境。",
"#1331": "信号中等、信息偏早期，其靶向tPA-NMDAr轴的首创神经血管抗体差异化突出，一药多适应症管线设计清晰；可复制性受临床与支付体系高门槛约束——国内宜学其血管-神经机制视角与生物标志物驱动的临床策略，而非直接复制形态。",
"#1334": "信号中等、信息偏新，其不卖家庭信息、零佣金、listing验真的养老小机构匹配模式差异化清晰；轻模式易复制——国内养老院信息分散、中介乱象普遍，最该学透明匹配加小机构曝光路径，优先切社区嵌入式小微机构。",
"#0387": "信号中等、信息量一般，其将健康与保健功能API化、嵌入寿险与健康险公司的操作系统差异化明确；轻模式易复制——作为本土团队，最该学以API把健康服务植入保单的路径，向养老险与长护险场景平移。",
"#0479": "信号充足、信息透明，仿真机器小狗以情感交互陪伴认知症老人的差异化突出，2.3万预购验证需求；可复制性受硬件成本与供应链约束——国内宜学仿生宠物加情感计算路径，先由认知症照护机构与养老社区批量采购切入。",
"#0500": "信号中等、信息量一般，其面向家庭照护者的一站式用品电商加照护知识平台差异化有限但模式轻；易复制——国内照护者散、专业供给缺，最该学用品加教育一站式路径，借社区与私域流量低成本落地。",
"#0501": "信号充足、信息透明，其居家生命体征监测平台被零售巨头整合的差异化路径清晰；可复制性受数据合规与渠道门槛约束——国内宜学监测硬件加平台被零售与家电渠道整合的打法，切适老化居家慢病与出院后管理。",
"#0511": "信号偏弱、信息量一般，其整合遗嘱、信托与数字账号管理的一站式遗产规划平台差异化有限但切老龄化财富传承；轻模式易复制——国内数字遗产与家族信托刚起步，最该学遗嘱加信托加账号一体化路径。",
"#0598": "信号中等、信息量一般，其全资自有、嵌入HR与薪资平台的退休金SaaS差异化在端到端自研；受国内外养老金融牌照与税制差异约束——国内宜学嵌入式退休金基础设施路径，切企业年金与个人养老金数字化。",
"#0604": "信号偏弱、信息量一般，其多药管理的智能药盒硬件差异化有限但模式轻；易复制——国内智能药盒同质化严重，最该学多药分仓加依从提醒的硬件路径，结合慢病管理与机构及医保渠道落地。",
}

desc = {
"#0696":"主动式AI陪伴机器人，缓解独居老人孤独与用药",
"#0895":"4D成像雷达，无摄像头跌倒监测赋能养老",
"#0977":"行为经济学加财务激励提升老年慢病依从",
"#1331":"神经退行性疾病Biotech，首创神经血管单抗",
"#1334":"家庭-小型养老院透明匹配平台，零佣金",
"#0387":"保险科技OS，把健康功能API化嵌入保单",
"#0479":"仿生机器小狗，陪伴认知症与认知障碍老人",
"#0500":"家庭照护用品电商加照护知识平台",
"#0501":"居家生命体征监测平台，被零售巨头整合",
"#0511":"数字遗产与遗嘱信托平台，整合遗嘱加信托",
"#0598":"中小企业自动化401(k)退休金管理平台",
"#0604":"智能药盒，管理多药老人的分仓与提醒",
}

payor = {
"#0696":"混合（政府老龄署或医疗组织B2G采购加个人订阅；MCO或Medicare支付）",
"#0895":"B端机构付费（向OEM、养老机构与智能家居厂商售雷达芯片或模组）",
"#0977":"混合（客户为健康计划，终极支付方为政府Medicare或Medicaid）",
"#1331":"研发期未商业化（未来上市后政府医保加商业保险支付）",
"#1334":"混合（C端家庭免费，B端机构订阅listing与运营工具）",
"#0387":"B端保险机构付费（健康险公司采购CareVoiceOS）",
"#0479":"B端机构加个人自费（机器宠物硬件销售）",
"#0500":"C端个人自费（家庭照护者购买用品）",
"#0501":"B端医疗机构或支付方加个人（居家监测方案）",
"#0511":"个人自费（遗嘱或信托服务）加B端顾问合作",
"#0598":"B端中小企业付费（401k管理SaaS）加员工缴费",
"#0604":"B端机构采购加个人自费（智能药盒硬件）",
}

role = {
"#0696":"服务商","#0895":"产品商","#0977":"服务商","#1331":"产品商","#1334":"平台",
"#0387":"服务商","#0479":"产品商","#0500":"平台","#0501":"平台","#0511":"平台",
"#0598":"服务商","#0604":"产品商",
}

stage = {
"#0696":"B轮","#0895":"成长期","#0977":"C轮","#1331":"A轮","#1334":"未搜到",
"#0387":"B轮","#0479":"A轮","#0500":"B轮","#0501":"被收购","#0511":"种子期",
"#0598":"B轮","#0604":"A轮",
}

founded = {
"#0696":2016,"#0895":2011,"#0977":2014,"#1331":2021,"#1334":"未搜到",
"#0387":2014,"#0479":2017,"#0500":2015,"#0501":2015,"#0511":2020,
"#0598":2020,"#0604":2017,
}

scores = {
"#0696":(8.0,8.0,6.0,61.2),"#0895":(8.0,5.0,7.0,57.1),"#0977":(8.0,6.0,5.0,55.2),
"#1331":(6.0,7.0,3.0,46.4),"#1334":(6.0,6.0,6.0,50.4),"#0387":(6.0,5.0,6.0,47.6),
"#0479":(7.0,7.0,6.0,54.7),"#0500":(6.0,4.0,7.0,47.6),"#0501":(7.0,6.0,6.0,52.7),
"#0511":(5.0,5.0,5.0,42.6),"#0598":(6.0,5.0,3.0,41.6),"#0604":(5.0,4.0,7.0,44.6),
}

sig = {"#0696":3.05,"#0895":3.05,"#0977":3.05,"#1331":2.8,"#1334":2.8,
"#0387":2.55,"#0479":2.55,"#0500":2.55,"#0501":2.55,"#0511":2.55,"#0598":2.55,"#0604":2.55}

highlights = {
"#0696":["主动式AI陪伴，日均互动超30次","已在美国数千家庭规模化部署","B2B机构或医保加B2C订阅双轮","针对独居老人孤独与用药提醒"],
"#0895":["4D成像雷达无摄像头、隐私保护","Vayyar Care养老跌倒与活动监测","2020年在华设全资子公司与研发中心","全自研RFIC加多天线阵列壁垒"],
"#0977":["行为经济学加每日小额财务激励提依从","服务Medicare Advantage或Medicaid或D-SNP","累计5000万加次打卡、住院降51%","2025年完成3600万美元C轮"],
"#1331":["首创靶向tPA-NMDAr轴的全人源单抗LYS241","覆盖帕金森或多系统萎缩或缺血卒中（一药多适应症）","获Michael J. Fox基金会超500万美元资助","累计融资超2500万欧元、推进至临床1a或1b"],
"#1334":["全美上线的家庭-小型养老院匹配平台","零佣金、不售家庭信息、listing验真","面向机构提供BedHub Operations运营工具","创始人具15年住宅辅助生活运营经验"],
"#0387":["上海或香港保险科技，CareVoiceOS健康操作系统","以API将分诊或保单或理赔嵌入保司","服务全球30余家保险公司","2024年完成千万美元级B轮"],
"#0479":["仿生机器小狗Jennie陪伴认知症老人","2026年A3轮700万美元、2.3万预购","Jim Henson团队参与拟真动画","计划2026年秋首批发货"],
"#0500":["家庭照护者一站式用品电商加知识平台","2023年B轮2470万美元、累计5470万","soonicorn级别、增长快","聚焦居家养老照护场景"],
"#0501":["居家生命体征监测远程平台","2021年被Best Buy以约4亿美元收购","2021年B轮4300万美元","服务老年慢病与居家照护"],
"#0511":["数字遗产与遗嘱信托一体化平台","整合遗嘱加信托加账号管理","2021年种子轮500万美元","面向老龄化财富传承"],
"#0598":["全资自有401(k)退休金管理平台","2025年B轮3300万美元、服务5000加企业","管理资产超10亿美元","嵌入式接入HCM或金融机构分销"],
"#0604":["智能药盒Karie管理多种药物","A轮融资、累计390万美元","面向多药老人用药依从","加拿大老年用药管理硬件商"],
}

events = {
"#0696":[{"date":"2024-08","text":"完成2500万美元新一轮融资，推进ElliQ规模化部署"},{"date":"2026-03","text":"十年复盘：累计部署数千家庭、日均互动超30次"}],
"#0895":[{"date":"2022-06","text":"完成1.08亿美元E轮，估值超10亿美元"},{"date":"2024-10","text":"完成2500万美元E轮扩展轮"},{"date":"2020","text":"在中国设立全资子公司与研发中心"}],
"#0977":[{"date":"2025-03","text":"完成3600万美元超额认购C轮"}],
"#1331":[{"date":"2026-06","text":"宣布累计融资超2500万欧元，推进LYS241临床1a或1b"}],
"#1334":[{"date":"2026-07","text":"全美上线家庭-小型养老院透明匹配平台"}],
"#0387":[{"date":"2024-03","text":"完成1000万美元B轮融资"}],
"#0479":[{"date":"2025-06","text":"完成610万美元A轮"},{"date":"2026-06","text":"完成700万美元A3轮，2.3万预购，计划秋季首发"}],
"#0500":[{"date":"2023-06","text":"完成2470万美元B轮"}],
"#0501":[{"date":"2021-04","text":"完成4300万美元B轮"},{"date":"2021","text":"被Best Buy以约4亿美元收购"}],
"#0511":[{"date":"2021","text":"完成500万美元种子轮"}],
"#0598":[{"date":"2025-12","text":"完成3300万美元B轮，Centana领投"}],
"#0604":[{"date":"2020","text":"完成A轮融资（约500万元）"}],
}

verdict = {
"#0696":("核心银发","专为老年人设计的主动式AI陪伴，直击孤独与健康管理"),
"#0895":("泛医疗擦边","底层是通用4D成像雷达半导体，养老跌倒监测仅为其多行业应用之一"),
"#0977":("核心银发","以行为经济学加财务激励服务Medicare或Medicaid高风险老年慢病人群"),
"#1331":("核心银发","主攻神经退行性与抗衰老脑科学，人群高度老龄化相关"),
"#1334":("核心银发","帮家庭搜寻优质小型养老照护机构的匹配平台，直接服务银发"),
"#0387":("核心银发","保险科技赋能健康险，间接服务银发客群"),
"#0479":("核心银发","仿生机器小狗专门陪伴痴呆症或认知障碍老人"),
"#0500":("核心银发","家庭照护者电商加教育平台，服务居家养老场景"),
"#0501":("核心银发","居家生命体征监测直接服务老年慢病与居家照护"),
"#0511":("核心银发","遗产规划或数字资产继承属银发金融范畴"),
"#0598":("核心银发","美国401k退休金自动化管理，属养老金融"),
"#0604":("核心银发","智能药盒管理多药老人用药，属用药照护"),
}

WHITE={"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
NAMES={"ElliQ","Vayyar","Wellth","Lys Therapeutics","BedHub","CareVoice","Tombot","Carewell","Current Health","GoodTrust","401GO","AceAge"}

enterprises=[]
order=["#0696","#0895","#0977","#1331","#1334","#0387","#0479","#0500","#0501","#0511","#0598","#0604"]
for s in order:
    i,d,c,rv=scores[s]
    v,reason=verdict[s]
    e=E(s,sig[s],i,d,c,rv,rec[s],desc[s],payor[s],role[s],founded[s],stage[s],
        highlights[s],events[s],v,reason)
    enterprises.append(e)

problems=[]
for e in enterprises:
    s=e["serial"]
    for k in ["info_score","diff_score","copy_score","research_value"]:
        if not (0<=e[k]<=10): problems.append(f"{s}: {k} out of range {e[k]}")
    r=e["recommend"]
    n=len(r)
    if not (60<=n<=120): problems.append(f"{s}: recommend len {n}")
    for nm in NAMES:
        if nm in r: problems.append(f"{s}: recommend contains name {nm}")
    for tk in ["成立","成立于"]:
        if tk in r: problems.append(f"{s}: recommend contains {tk}")
    if e["stage"] not in WHITE: problems.append(f"{s}: stage not whitelist {e['stage']}")
    if not e["payor_model"]: problems.append(f"{s}: payor empty")
    for kk in ["recommend","desc_cn","payor_model","business_tags_role","stage","silver_verdict","silver_reason","founded","update_time"]:
        if e[kk] in (None,"","[]"): problems.append(f"{s}: field {kk} empty")
    if len(e["desc_cn"])>30: problems.append(f"{s}: desc_cn too long {len(e['desc_cn'])}")

print("SELF-CHECK problems:", len(problems))
for p in problems: print("  -",p)
print("recommend lengths:")
for e in enterprises: print("  ",e["serial"], len(e["recommend"]))

# tag_review
tag_review=[
 {"serial":"#0696","name":"ElliQ","intro":"以色列Intuition Robotics出品的主动式AI老年陪伴机器人，能主动发起对话、提醒用药并推荐活动，已在美国数千家庭部署。","old_tags":{"tag_l1":["文娱社交"],"tag_l2":["陪伴机器人","陪伴服务"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},"suggested":[]},
 {"serial":"#0895","name":"Vayyar","intro":"以色列4D成像雷达（radar-on-chip）公司，以无摄像头、隐私保护的非接触式环境感知服务养老跌倒监测、智能家居、汽车与医疗等多场景，2020年在华设全资子公司。","old_tags":{"tag_l1":["消费品"],"tag_l2":["智能家居"],"business_tags":{"customer":"B2B","role":"产品商","channel":[]}},"suggested":[{"action":"change","tag":"tag_l1:消费品→智能硬件","reason":"底层是4D成像雷达半导体或传感器公司，消费品不准确"},{"action":"add","tag":"跌倒监测","reason":"养老场景核心应用是隐私保护的非接触式跌倒与活动监测，应补标签"},{"action":"change","tag":"tag_l2:智能家居→智能家居或传感器","reason":"技术跨养老、汽车、医疗多场景，单标智能家居偏窄"}]},
 {"serial":"#0977","name":"Wellth","intro":"美国数字健康公司，用行为经济学加每日小额财务激励提升慢性病人群（Medicare或Medicaid或D-SNP）的用药依从与预防就诊，临床显示住院降51%。","old_tags":{"tag_l1":["康复辅具"],"tag_l2":["用药提醒"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},"suggested":[{"action":"change","tag":"tag_l1:康复辅具→健康服务","reason":"本质是慢病管理与健康行为激励，非康复辅具"},{"action":"change","tag":"tag_l2:用药提醒→慢病管理或健康激励","reason":"业务是以行为经济学加财务激励提升整体依从，远宽于用药提醒"}]},
 {"serial":"#1331","name":"Lys Therapeutics","intro":"法国神经科学Biotech，自研全人源单抗LYS241靶向tPA-NMDAr轴，覆盖帕金森、多系统萎缩与缺血卒中，累计融资超2500万欧元、推进至临床1a或1b。","old_tags":{"tag_l1":["食品营养"],"tag_l2":["保健品"],"business_tags":{"customer":"B2B","role":"产品商","channel":[]}},"suggested":[{"action":"change","tag":"tag_l1:食品营养→生物医药","reason":"是开发单抗药物的Biotech，绝非食品或营养"},{"action":"change","tag":"tag_l2:保健品→神经退行或抗衰老药物","reason":"管线为靶向tPA-NMDAr轴的神经血管单抗，非保健品"}]},
 {"serial":"#1334","name":"BedHub","intro":"美国家庭-小型养老院透明匹配平台，零佣金、不售家庭信息、listing验真，并向机构提供BedHub Operations运营工具，2026年7月全美上线。","old_tags":{"tag_l1":["消费品"],"tag_l2":["智能家居"],"business_tags":{"customer":"B2B","role":"平台","channel":[]}},"suggested":[{"action":"change","tag":"tag_l1:消费品→养老服务","reason":"是养老照护机构匹配平台，非消费品"},{"action":"change","tag":"tag_l2:智能家居→养老运营或机构匹配","reason":"业务是家庭-小型养老院透明匹配与机构运营工具，与智能家居无关"}]},
 {"serial":"#0387","name":"CareVoice","intro":"总部上海或香港的保险科技公司，提供CareVoiceOS——基于API的数字化健康操作系统，覆盖症状分诊、医生查询、保单管理与理赔自动化，服务全球30余家保险公司。","old_tags":{"tag_l1":["金融保险"],"tag_l2":["保险科技"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},"suggested":[]},
 {"serial":"#0479","name":"Tombot","intro":"加州机器人公司，生产仿生机器小狗Jennie陪伴痴呆症与认知障碍老人，2026年A3轮700万美元、2.3万预购，计划秋季首发。","old_tags":{"tag_l1":["康复辅具"],"tag_l2":["机器人"],"business_tags":{"customer":"B2B+B2C","role":"产品商","channel":[]}},"suggested":[]},
 {"serial":"#0500","name":"Carewell","intro":"美国家庭照护者一站式电商加照护知识平台，销售照护用品并提供教育内容，B轮2470万美元、累计5470万。","old_tags":{"tag_l1":["行业服务","消费品"],"tag_l2":["养老信息平台","电商"],"business_tags":{"customer":"B2C","role":"平台","channel":[]}},"suggested":[]},
 {"serial":"#0501","name":"Current Health","intro":"居家生命体征监测远程患者监测平台，2021年被Best Buy以约4亿美元收购，服务老年慢病与居家照护。","old_tags":{"tag_l1":["养老服务"],"tag_l2":["远程护理"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},"suggested":[]},
 {"serial":"#0511","name":"GoodTrust","intro":"数字遗产与遗嘱信托一体化平台，整合遗嘱、信托与数字账号管理，服务老龄化财富传承，种子轮500万美元。","old_tags":{"tag_l1":["金融保险"],"tag_l2":["遗产规划"],"business_tags":{"customer":"B2B","role":"平台","channel":[]}},"suggested":[]},
 {"serial":"#0598","name":"401GO","intro":"美国全资自有401(k)退休金管理平台，以嵌入式接入HR或薪资服务商分销，B轮3300万美元、管理资产超10亿美元。","old_tags":{"tag_l1":["金融保险"],"tag_l2":["金融理财"],"business_tags":{"customer":"B2B","role":"服务商","channel":[]}},"suggested":[]},
 {"serial":"#0604","name":"AceAge","intro":"加拿大智能药盒Karie开发商，管理多药老人的分仓与用药提醒，A轮融资、累计390万美元。","old_tags":{"tag_l1":["康复辅具"],"tag_l2":["智能药盒","用药提醒","用药管理"],"business_tags":{"customer":"B2B","role":"产品商","channel":[]}},"suggested":[]},
]

nonsilver=[{"serial":"#0895","name":"Vayyar","verdict":"泛医疗擦边","reason":"底层是通用4D成像雷达半导体公司，养老跌倒监测仅为其多行业应用之一，医疗或养老属性偏弱"}]

out={"batch":13,"enterprises":enterprises,"tag_review":tag_review,"nonsilver":nonsilver}

with open("scores_draft/run_v2/out/batch_013_out.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("WROTE batch_013_out.json with", len(enterprises), "enterprises")
