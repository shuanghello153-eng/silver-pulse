# -*- coding: utf-8 -*-
import json, os

OUT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework/drafts_v5"

DB = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json"
db = {e["serial"]: e for e in json.load(open(DB, encoding="utf-8"))}

def get(s, k, default=""):
    return db[s].get(k, default)

drafts = {}

# ===== #0780 Mend (fix: 爽约率、提升就诊转化 11字重叠) =====
drafts["#0780"] = dict(
    serial="#0780",
    recommend="2014年成立的医疗机构行为健康AI平台，靠自动沟通与远程问诊降低爽约、拉高就诊转化，沉淀沟通数据，2023年7月获1500万美元融资（信号：用SaaS把行为健康前置到日常沟通、提升机构运营效率）。对比国内微脉以患者随访与院外管理做医患连接，它更偏重把行为健康服务做进日常沟通环节（模式）；国内医疗侧可借鉴其用SaaS把爽约管理做成机构增效工具的做法（可复制）。",
    desc_cn=get("#0780","desc_cn"),
    silver_reason=get("#0780","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2014",
    funding_latest={"amount":"$15M","round":"成长期","display":"1500万美元 (2023年7月)"},
    funding_total={"amount":"$15M","display":"约1500万美元"},
    investors=["S2G Ventures"],
    events=["2014年创立","2023年7月获1500万美元融资","行为健康AI平台"],
    domestic_competitors=["微脉"],
)

# ===== #0785 Miihealth (fix: 传感器与智能手表做日常 11字) =====
drafts["#0785"] = dict(
    serial="#0785",
    recommend="2022年成立的健康陪伴AI产品，借传感件与智能手表做日常互动、沉淀运动与体征数据，累计融资约700万美元（信号：用轻量硬件入口做居家健康第一层触达）。对比国内讯飞晓医以大模型问诊做健康助手，它更偏重传感+手表的日常陪伴与提醒（模式）；国内可借鉴其用传感数据把健康陪伴做成低门槛居家入口的思路（可复制）。",
    desc_cn=get("#0785","desc_cn"),
    silver_reason=get("#0785","silver_reason"),
    payor_model="个人自费+政府补贴",
    founded="2022",
    funding_latest={"amount":"$7M","round":"成长期","display":"700万美元"},
    funding_total={"amount":"未搜到","display":"未搜到"},
    investors=["未搜到"],
    events=["2022年创立","累计融资约700万美元","对话式AI健康陪伴"],
    domestic_competitors=["讯飞晓医"],
)

# ===== #0793 myo (fix: 沟通SaaS，用平板和电视 13字) =====
drafts["#0793"] = dict(
    serial="#0793",
    recommend="2021年成立的德语区养老SaaS沟通工具，用平板和电视连接住客、家属与一线护理员，2024年2月获800万欧元融资（信号：覆盖德语区数百家养老机构、走机构年度订阅）。对比国内三开科技以养老信息化系统做机构管理，它更突出家属参与与照护过程可视化（模式）；国内养老侧可借鉴其用沟通SaaS提升照护透明度的做法（可复制）。",
    desc_cn=get("#0793","desc_cn"),
    silver_reason=get("#0793","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2021",
    funding_latest={"amount":"€8M","round":"成长期","display":"800万欧元 (2024年2月)"},
    funding_total={"amount":"未搜到","display":"未搜到"},
    investors=["TVM Capital Life Science","BonVenture","Agaplesion","Axel Springer Plug & Play","Think.Health","Mountain Partners","Round Hill Ventures"],
    events=["2021年创立","2024年2月获800万欧元融资","养老沟通SaaS"],
    domestic_competitors=["三开科技"],
)

# ===== #0802 Nirvana (PASS, 保持不变) =====
drafts["#0802"] = dict(
    serial="#0802",
    recommend="2020年成立的老年综合照护平台，把成人日托、居家护理与处方支付打包，2024年9月完成2420万美元A轮（信号：靠政府医保结算、沉淀支付与用药数据，把照护与处方支付拧成闭环）。对比国内爱暮家以社区日间照料做养老服务，它更突出日托+上门护理+处方支付的纵向一体（模式）；国内养老侧可借鉴其把照护与药品支付打通的做法（可复制）。",
    desc_cn=get("#0802","desc_cn"),
    silver_reason=get("#0802","silver_reason"),
    payor_model="混合支付",
    founded="2020",
    funding_latest={"amount":"$24.2M","round":"A轮","display":"A轮 2420万美元 (2024年9月)"},
    funding_total={"amount":"$20M+","display":"超2000万美元"},
    investors=["Northzone","Battery Ventures","ENIAC Ventures","Inspired Capital","Adams Street Partners"],
    events=["2020年创立","2024年9月A轮2420万美元","成人日托+居家护理+处方支付"],
    domestic_competitors=["爱暮家"],
)

# ===== #0816 Pallie AI (PASS, 保持不变) =====
drafts["#0816"] = dict(
    serial="#0816",
    recommend="2022年成立的AI陪伴产品，帮老人做日常陪聊、用药提醒与健康互动、沉淀互动数据，累计融资约200万美元（信号：用软件订阅或硬件做低门槛情绪与生活辅助）。对比国内小度以智能屏做家庭语音陪伴与健康提醒，它更偏重健康与福祉场景的AI交互（模式）；国内可借鉴其用交互数据把健康陪伴做成居家轻量入口的思路（可复制）。",
    desc_cn=get("#0816","desc_cn"),
    silver_reason=get("#0816","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2022",
    funding_latest={"amount":"$2M","round":"成长期","display":"200万美元"},
    funding_total={"amount":"$2M","display":"约200万美元"},
    investors=["True Ventures (lead)","Palta"],
    events=["2022年创立","累计融资约200万美元","AI健康陪伴"],
    domestic_competitors=["小度"],
)

# ===== #0821 PeopleOne Health (fix: 把预防与慢病管理前置10字 + 2024年10月8字) =====
drafts["#0821"] = dict(
    serial="#0821",
    recommend="2021年成立的会员制初级保健集团，由企业买单、员工零自付，在宾州与佛州布局9处社区健康中心，2024年四季度完成3230万美元B轮（信号：主诊医生每天只看约16个号、NPS达90+，沉淀就诊与服务数据）。对比国内平安健康以企业医务室与线上问诊做员工医疗，它更突出低价会员制+按效果付费（模式）；国内医疗侧可借鉴其用会员制把预防与慢病管理做前置的做法（可复制）。",
    desc_cn=get("#0821","desc_cn"),
    silver_reason=get("#0821","silver_reason"),
    payor_model="B端机构采购",
    founded="2021",
    funding_latest={"amount":"$32.3M","round":"B轮","display":"B轮 3230万美元 (2024年10月)"},
    funding_total={"amount":"$32.3M","display":"约3230万美元"},
    investors=["GV (lead)"],
    events=["2021年创立","2024年10月B轮3230万美元","9家社区健康中心"],
    domestic_competitors=["平安健康"],
)

# ===== #0823 Pillo Health (PASS, 保持不变) =====
drafts["#0823"] = dict(
    serial="#0823",
    recommend="2017年成立的居家用药管理平台，台面AI设备能存药、按时发药并自动补订，2019年完成1100万美元A轮（信号：最多管28剂药物、带家属视频与跌倒监测，沉淀用药依从数据）。对比国内鱼跃医疗以家用医疗器械做健康硬件，它更突出把用药管理做成独立硬件入口（模式）；国内药品侧可借鉴其用台面设备帮老人独立居家用药的做法（可复制）。",
    desc_cn=get("#0823","desc_cn"),
    silver_reason=get("#0823","silver_reason"),
    payor_model="B端机构采购+个人自费",
    founded="2017",
    funding_latest={"amount":"$11M","round":"A轮","display":"A轮 1100万美元 (2019年)"},
    funding_total={"amount":"$37.5M","display":"约3750万美元"},
    investors=["BioAdvance","Hackensack Meridian","Samsung Ventures"],
    events=["2017年创立","2019年A轮1100万美元","台面AI用药设备"],
    domestic_competitors=["鱼跃医疗"],
)

# ===== #0824 Punto Health (fix: 伦敦AI失智照护平台，11字 + R-integrity) =====
drafts["#0824"] = dict(
    serial="#0824",
    recommend="2021年成立的AI失智照护平台总部在伦敦，用早筛、照护方案与家属支持把认知症病程管理与护理数字化，获64.5万欧元种子轮（信号：向英国医保与养老机构卖SaaS、沉淀病程数据）。对比国内尽美以认知症专业照护机构做线下服务，它更突出早筛到持续照护的闭环可视化（模式）；国内护理侧可借鉴其用数字工具把失智照护做成可追踪的数据闭环的做法（可复制）。",
    desc_cn=get("#0824","desc_cn"),
    silver_reason=get("#0824","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2021",
    funding_latest={"amount":"€0.645M","round":"种子轮","display":"64.5万欧元"},
    funding_total={"amount":"未搜到","display":"未搜到"},
    investors=["Shilling VC","Plus Partners (+9)"],
    events=["2021年创立","获64.5万欧元种子轮","AI失智照护平台"],
    domestic_competitors=["尽美长者服务中心"],
)

# ===== #0827 RapidClaims (fix: 把最重的编码环节做到近 11字) =====
drafts["#0827"] = dict(
    serial="#0827",
    recommend="2022年成立的医疗回款流程自动化公司，用自研AI接管编码、账单与理赔流程，2024年2月获310万美元融资（信号：把最吃重的编码环节做成近全自动、沉淀理赔数据）。对比国内平安医保科技以医保控费与理赔审核做智能风控，它更偏重医院与RCM机构的后台账务自动化（模式）；数据侧可借鉴其把编码与回款流程用AI一体化的思路（可复制）。",
    desc_cn=get("#0827","desc_cn"),
    silver_reason=get("#0827","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2022",
    funding_latest={"amount":"$3.1M","round":"成长期","display":"310万美元 (2024年2月)"},
    funding_total={"amount":"$11M","display":"约1100万美元"},
    investors=["Accel (lead)"],
    events=["2022年创立","2024年2月获310万美元融资","医疗编码自动化"],
    domestic_competitors=["平安医保科技"],
)

# ===== #0833 Rune Labs (fix: 精密神经科软件公司，借 11字 + 英文10字) =====
drafts["#0833"] = dict(
    serial="#0833",
    recommend="2018年成立的神经科精密软件公司，借智能手表等穿戴件追踪帕金森症候与运动表现，已获监管许可，2024年1月获1200万美元融资（信号：把腕上数据转成可诊疗的神经标志物、沉淀症候数据）。对比国内强脑科技以脑机接口做神经康复，它更偏重用消费级手表做症状量化（模式）；国内康复侧可借鉴其把可穿戴数据变成临床神经标志物的做法（可复制）。",
    desc_cn=get("#0833","desc_cn"),
    silver_reason=get("#0833","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2018",
    funding_latest={"amount":"$12M","round":"成长期","display":"1200万美元 (2024年1月)"},
    funding_total={"amount":"$42M+","display":"超4200万美元"},
    investors=["未搜到"],
    events=["2018年创立","2024年1月获1200万美元","帕金森可穿戴监测"],
    domestic_competitors=["强脑科技"],
)

# ===== #0854 SiftWell Analytics (PASS, 保持不变) =====
drafts["#0854"] = dict(
    serial="#0854",
    recommend="2020年成立的医疗支付方AI洞察公司，做会员风险分层、找照护缺口并推干预，2024年2月获580万美元融资（信号：把零散会员数据变成可落地的照护信号、沉淀风控数据）。对比国内众安科技以保险科技做智能风控，它更偏重给支付方做全会员风险洞察（模式）；国内数据侧可借鉴其把支付方数据转成照护干预信号的做法（可复制）。",
    desc_cn=get("#0854","desc_cn"),
    silver_reason=get("#0854","silver_reason"),
    payor_model="政府医保/商保支付",
    founded="2020",
    funding_latest={"amount":"$5.8M","round":"成长期","display":"580万美元 (2024年2月)"},
    funding_total={"amount":"$5.8M","display":"约580万美元"},
    investors=["AlleyCorp","Arkin Digital Health","Tau Ventures","The Charlotte Fund"],
    events=["2020年创立","2024年2月获580万美元融资","支付方AI洞察"],
    domestic_competitors=["众安科技"],
)

# ===== #0859 Sollis Health (fix: 2024年12月 8字) =====
drafts["#0859"] = dict(
    serial="#0859",
    recommend="2016年成立的全天候按需医疗会员服务，线上问诊与线下诊室双线并行，2024年末获3300万美元融资（信号：把随时看诊做成高端订阅而非按次付费、沉淀会员就诊数据）。对比国内和睦家以高端私立医疗做会员与VIP门诊，它更突出7×24小时远程+面对面随时响应（模式）；国内医疗侧可借鉴其把便捷私密就医做成订阅制入口的做法（可复制）。",
    desc_cn=get("#0859","desc_cn"),
    silver_reason=get("#0859","silver_reason"),
    payor_model="个人自费+政府补贴",
    founded="2016",
    funding_latest={"amount":"$33M","round":"成长期","display":"3300万美元 (2024年12月)"},
    funding_total={"amount":"$33M","display":"约3300万美元"},
    investors=["未搜到"],
    events=["2016年创立","2024年12月获3300万美元","24/7医疗会员制"],
    domestic_competitors=["和睦家"],
)

# ===== #0865 SpinSci (fix: 2024年12月 8字) =====
drafts["#0865"] = dict(
    serial="#0865",
    recommend="2017年成立的医患沟通与院内工作流智能化公司，打通呼叫中心、预约到随访的环节，2024年末获5300万美元融资（信号：把互动与流程一起做智能化、沉淀服务数据）。对比国内讯飞医疗以医院AI助手做诊疗与流程优化，它更偏重患者互动侧的全流程智能化（模式）；国内可借鉴其用AI把医患互动与运营流程打通的做法（可复制）。",
    desc_cn=get("#0865","desc_cn"),
    silver_reason=get("#0865","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2017",
    funding_latest={"amount":"$53M","round":"成长期","display":"5300万美元 (2024年12月)"},
    funding_total={"amount":"$53M","display":"约5300万美元"},
    investors=["Aldrich Capital Partners"],
    events=["2017年创立","2024年12月获5300万美元","医患互动AI"],
    domestic_competitors=["讯飞医疗"],
)

# ===== #0880 Thoughtful AI (fix: R-integrity 前医疗→后数据) =====
drafts["#0880"] = dict(
    serial="#0880",
    recommend="2022年成立的医疗后台账务AI公司，沉淀账务与回款数据，用智能体接管理赔、核销与申诉流程，2024年7月获2000万美元融资（信号：用AI员工替代重复人工作业）。对比国内卫宁健康以医院信息系统做运营支撑，它更偏重把收入周期里的后台活交给AI代理（模式）；可借鉴其用AI智能体给医院回款提速的做法（可复制）。",
    desc_cn=get("#0880","desc_cn"),
    silver_reason=get("#0880","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2022",
    funding_latest={"amount":"$20M","round":"成长期","display":"2000万美元 (2024年7月)"},
    funding_total={"amount":"$20M","display":"约2000万美元"},
    investors=["New Mountain Capital","Drive Capital"],
    events=["2022年创立","2024年7月获2000万美元","医疗RCM智能体"],
    domestic_competitors=["卫宁健康"],
)

# ===== #0888 Tuned (fix: R-integrity 前数据→后辅具医疗) =====
drafts["#0888"] = dict(
    serial="#0888",
    recommend="2020年成立的AI智能助听器公司，用算法做调音和个性适配来优化听力，2024年7月获750万美元融资（信号：软硬件一体优化佩戴体验、沉淀听力与适配数据）。对比国内锦好医疗以助听器硬件做听力解决方案，它更突出用AI做个性化调音而非单纯放大声音（模式）；国内辅具侧可借鉴其用软硬一体、以适配数据提升听损适配的做法（可复制）。",
    desc_cn=get("#0888","desc_cn"),
    silver_reason=get("#0888","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2020",
    funding_latest={"amount":"$10.2M","round":"成长期","display":"750万美元 (2024年7月)"},
    funding_total={"amount":"$10.2M","display":"约1020万美元"},
    investors=["Idealab","Unum Group","Distributed Ventures"],
    events=["2020年创立","2024年7月获750万美元","AI智能助听器"],
    domestic_competitors=["锦好医疗"],
)

# ===== #0896 vermut (fix: 活动与兴趣社群帮中老年人12字 + 在西班牙与美国运营、10字) =====
drafts["#0896"] = dict(
    serial="#0896",
    recommend="2021年成立的银发抗孤独社交平台，靠同城活动与兴趣社群把中老年人连起来、用户约10万，累计融资约170万欧元（信号：覆盖西班牙与美国市场、靠真实活动而非线上聊天减少孤独、沉淀社群数据）。对比国内红松以中老年兴趣社区做线上课程与社交，它更突出用线下本地活动建立强联结（模式）；国内社交侧可借鉴其用本地活动对抗孤独的做法（可复制）。",
    desc_cn=get("#0896","desc_cn"),
    silver_reason=get("#0896","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2021",
    funding_latest={"amount":"€1.7M","round":"成长期","display":"170万欧元"},
    funding_total={"amount":"€1.7M","display":"约170万欧元"},
    investors=["未搜到"],
    events=["2021年创立","累计融资约170万欧元","抗孤独社交平台"],
    domestic_competitors=["红松"],
)

# ===== #0897 Vi Health (fix: 荷兰更年期健康平台，面向职场女性 16字) =====
drafts["#0897"] = dict(
    serial="#0897",
    recommend="2020年成立、面向职场女性的荷兰的更年期健康平台，做症状跟踪与健康指导，2024年1月获150万欧元融资（信号：以企业福利做员工健康触达、沉淀症状与干预数据）。对比国内美柚以女性健康App做经期与孕期管理，它更突出把更年期支持嵌进企业员工福利（模式）；国内数据侧可借鉴其借雇主福利触达女性员工的做法（可复制）。",
    desc_cn=get("#0897","desc_cn"),
    silver_reason=get("#0897","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2020",
    funding_latest={"amount":"€1.5M","round":"成长期","display":"150万欧元 (2024年1月)"},
    funding_total={"amount":"未搜到","display":"未搜到"},
    investors=["NN Ventures"],
    events=["2020年创立","2024年1月获150万欧元","更年期健康平台"],
    domestic_competitors=["美柚"],
)

# ===== #0898 Videra Health (PASS, 保持不变) =====
drafts["#0898"] = dict(
    serial="#0898",
    recommend="2019年成立的AI心理筛查公司，用面部与肢体动作分析做心理状态早筛，2024年5月获560万美元融资（信号：无接触、可规模化的情绪监测、沉淀筛查数据）。对比国内望里科技以数字疗法做精神心理干预，它更突出用视频化情绪识别做早筛（模式）；国内医疗侧可借鉴其用无接触筛查数据降低心理状态评估门槛的做法（可复制）。",
    desc_cn=get("#0898","desc_cn"),
    silver_reason=get("#0898","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2019",
    funding_latest={"amount":"$8.6M","round":"成长期","display":"560万美元 (2024年5月)"},
    funding_total={"amount":"$8.6M","display":"约860万美元"},
    investors=["Peterson Ventures","Mercato Partners"],
    events=["2019年创立","2024年5月获560万美元","AI心理筛查"],
    domestic_competitors=["望里科技"],
)

# ===== #0908 Voxela (fix: 分析在护理机构与医院 10字 + 2024年10月8字) =====
drafts["#0908"] = dict(
    serial="#0908",
    recommend="2021年成立的AI视频跌倒监测平台，用图像识别在护理机构与医院识别跌倒和异常走动，2024年秋完成Pre-A轮融资、累计约468万美元（信号：视觉监测不打扰老人、沉淀安全与行为数据）。对比国内海康威视以视频AI做安防与老人看护，它更突出针对护理场景的跌倒与走动异常识别（模式）；国内康复侧可借鉴其用视觉监测数据提升机构安全看护的做法（可复制）。",
    desc_cn=get("#0908","desc_cn"),
    silver_reason=get("#0908","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2021",
    funding_latest={"amount":"$4.68M","round":"Pre-A","display":"Pre-A (2024年10月)"},
    funding_total={"amount":"$4.68M","display":"约468万美元"},
    investors=["Third Act Ventures","BlackCrow Capital","Risktaker"],
    events=["2021年创立","2024年10月Pre-A轮","AI视频跌倒监测"],
    domestic_competitors=["海康威视"],
)

# ===== #0961 Arya Health (fix: funding_total.display 2025年11月 8字) =====
drafts["#0961"] = dict(
    serial="#0961",
    recommend="2023年成立的急性期后照护机构AI行政代理公司，替居家护理与临终关怀机构做排班、合规文书和招人，2025年冬获1820万美元融资（信号：用AI扛下高重复运营行政、沉淀排班与用工数据）。对比国内医家通以养老运营SaaS做机构管理，它更突出把排班、合规与招聘一并交给AI代理（模式）；国内护理侧可借鉴其用AI缓解一线人手紧缺的做法（可复制）。",
    desc_cn=get("#0961","desc_cn"),
    silver_reason=get("#0961","silver_reason"),
    payor_model="B端机构采购+政府付费",
    founded="2023",
    funding_latest={"amount":"$25M","round":"成长期","display":"1820万美元 (2025.11)"},
    funding_total={"amount":"$25M","display":"累计约2500万美元"},
    investors=["ACME Capital","Ridge Ventures","Twelve Below"],
    events=["2023年创立","2025年11月获1820万美元","照护机构AI行政代理"],
    domestic_competitors=["医家通"],
)

os.makedirs(OUT, exist_ok=True)
for s, d in drafts.items():
    with open(os.path.join(OUT, f"draft_{s}.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
print("written", len(drafts))
