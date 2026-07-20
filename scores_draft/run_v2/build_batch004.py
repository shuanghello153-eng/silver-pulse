# -*- coding: utf-8 -*-
import json

# ---- shared four-dimension scores (from main library all_enterprises.json) ----
# serial -> (info, diff, copy, research_value, stage, payor, business_tags_role, founded)
LIB = {
"#0950": (7.0,5.0,5.0,60.6,"已上市","政府医保(Medicare/Medicaid)+个人自费","服务商",2017),
"#0951": (8.0,6.0,4.0,63.7,"已上市","政府医保(Medicare+Medicaid按人头打包支付)","服务商",2007),
"#0952": (8.0,5.0,5.0,63.7,"已上市","政府医保(Medicaid/州政府)+商业保险(管理式医疗)+个人自费","服务商",1979),
"#0953": (7.0,5.0,5.0,60.6,"已上市","政府医保(Medicare/Medicaid)+个人自费","运营商",2019),
"#1135": (7.0,6.0,4.0,60.6,"已上市","个人自费(住户社区租金)为主","投资机构",2025),
"#1136": (8.0,5.0,4.0,61.6,"已上市","B端机构付费(triple-net净租赁，运营商付租金；终端政府医保+个人自付)","投资机构","未搜到"),
"#1144": (7.0,5.0,4.0,58.6,"已上市","个人自费(住户服务费)为主","运营商","未搜到"),
"#1147": (6.0,7.0,3.0,57.7,"已上市","商业保险+个人自费(研发阶段，尚未商业化)","产品商","未搜到"),
"#1153": (9.0,3.0,7.0,66.6,"已上市","B端机构付费（Triple-net净租赁，运营商付租金；终端来自政府医保Medicare/Medicaid+个人自付）","投资机构",1983),
"#1155": (8.0,4.0,5.0,61.6,"已上市","B端机构付费（Triple-net净租赁，运营商付租金；终端护理报销来自政府Medicare/Medicaid为主+个人自付）","投资机构",1992),
"#1156": (8.0,4.0,6.0,63.7,"已上市","B端机构付费（Triple-net净租赁，运营商付租金；终端来自政府Medicare/Medicaid+个人自付）","投资机构",2014),
"#1158": (8.0,3.0,5.0,59.6,"已上市","混合（医保/商业保险报销为主，个人自付为辅；B端机构合作）","服务商",1984),
}

SIGNAL = 6.55

# ---- recommends (rewritten for the 8 poor ones; 4 good ones preserved verbatim) ----
REC = {
"#0950": "信号稳、38州财报极透明（2025营收+20%/EBITDA+75%），信息量足；差异化在居家+安宁+私人护理多线整合与优选支付方策略，可复制性受美国医保波动牵制——国内居家护理最该学其护理员小时计费+优选商保的规模化中台，而非重资产扩张。",
"#0951": "信号中、PACE模式信息透明（20中心/年报完整），信息量足；差异化在政府按人头打包支付、全包照护绑定失能老人，可复制性受中国长护险支付限制拖累——最该学把医保+民政+商保做成封顶预算、由一家统筹居家到机构的整合照护。",
"#0952": "信号稳、并购与州费率信息透明，信息量足；差异化在以个人护理为核、密度并购换议价权的轻资产扩张，可复制性受国内居家护理低客单与医保结算慢制约——最该学其在单州做密度、用规模换政府/商保定价权的区域垄断打法。",
"#0953": "信号稳、分拆式并购与财报透明（收购同行剥离资产54处、去中心化运营），信息量足；差异化在放权地方院长+集群式整合的轻总部模式，可复制性受国内居家护理连锁化程度低制约——最该学其小股权独立运营+强中台赋能既扩张又保质量的收购操作系统。",
"#1135": "信号新、招股与运营数据透明，信息量足；差异化在把养老地产从综合REIT分拆为纯Play上市标的、用住户费而非医保现金流，可复制性受中国尚无公募养老REIT制约——最该学其资产分拆+外部管理人+单元化持有的轻资产路径。",
"#1136": "信号强、分拆与资本循环动作密集（剥离养老组合、与黑石合作、回购），信息量足；差异化在把养老地产作独立上市平台、母体转向门诊医疗/实验室的资产腾挪术，可复制性受国内REITs底层资产限制——最该学其用分拆给被低估板块单独定价的资本配置纪律。",
"#1144": "信号稳、运营与并购数据透明（同店入住率87.7%），信息量足；差异化在全资自持+运营一体化+区域做密度的业主运营商路径，可复制性受国内重资产回报周期长制约——最该学其resident-first品牌+收购式做大规模的纯养老社区打法。",
"#1147": "信号弱、仅更名与管线概念披露、无临床与营收，信息量低；差异化在基因改造细胞+封装技术做免免疫抑制的糖尿病/长寿蛋白疗法，可复制性极高风险尚在早期——最该学其用合资撬动成熟平台的轻资产研发与品牌定位，而非烧钱自建实验室。",
"#1153": "信息极丰富（官网IR+2025财报），REIT模式稳健、受老龄化与新建供给低位双重顺风。中国无直接上市养老REIT，但险资/地产基金可对标其资产组合与出租率逻辑——与Welltower并读，能看清“银发地产”的资本纪律与周期。",
"#1155": "信息丰富（2025年报），Triple-net REIT稳健但高度依赖运营商偿付（2025年租户破产凸显集中度风险）。国内护理院重资产可参考triple-net，但中国REITs/医保差异大、难平移——其“租户风险管控”是核心看点。",
"#1156": "信息丰富（年报+出海收购报道），从单租户分拆到多元化+出海的成长型REIT，模式清晰非反共识。国内“运营+地产”分拆REIT可参考其架构；但A股无纯养老REIT、出海难复制——其“轻杠杆+高出租率+多元租户”的资本纪律值得借鉴。",
"#1158": "信息丰富（财报+行业媒体），居家输液模式稳健、顺常识，反共识性低。中国居家护理/输液（京东健康上门、民营护理站）有同类但支付以医保/个人为主、上门标准化弱——其“药师驱动+冷链药品+居家场景”体系可对标，尤适老龄化下居家医疗。",
}

# ---- desc_cn (<=30) ----
DESC = {
"#0950":"居家健康/安宁/私人护理整合服务商",
"#0951":"PACE全包式失能老人整合照护平台",
"#0952":"以个人护理为核心的居家照护连锁",
"#0953":"居家健康/安宁/养老社区分拆运营",
"#1135":"纯Play养老社区RIDEA结构REIT",
"#1136":"综合医疗地产REIT(分拆养老)",
"#1144":"养老社区业主-运营商(自持一体)",
"#1147":"长寿细胞疗法生物科技(早期)",
"#1153":"美国第二大养老/医疗地产REIT",
"#1155":"专注护理院的三重净租赁REIT",
"#1156":"自管理养老社区净租赁REIT",
"#1158":"全美最大独立居家输液专科药房",
}

# ---- highlights (2-4) ----
HL = {
"#0950":["38州居家健康/安宁/私人护理/医疗解决方案多线运营","2025营收24.33亿美元(+20.2%)，调整后EBITDA 3.21亿(+74.8%)","优选支付方策略覆盖约57%管理式医疗量，并收购Thrive儿科居家护理","对2026年医保居家护理拟削减6.4%保持纪律性并购"],
"#0951":["PACE全包照护龙头，服务以失能双重资格老人为主","2025营收8.537亿美元(+11.8%)，参与者约8010人、20个中心6州","按人头打包支付(Medicare+Medicaid)，公司承担全部风险","FY2026指引参与者7900-8100、营收9-9.5亿美元"],
"#0952":["以个人护理为核心，260个网点覆盖23州，德州最大供应商","2024年3.506亿美元收购Gentiva个人护理资产","德州基础时薪+9.9%预计年增收1770万美元，目标年增10%","支付以Medicaid/州政府+管理式医疗为主，正向商保转移"],
"#0953":["去中心化控股：141家居家健康/安宁机构+61个养老社区独立运营","2025年1.465亿美元收购UnitedHealth/Amedisys剥离的54处资产(最大交易)","Medicare居家护理FFS收入占比<20%，多元抗支付波动","放权地方院长+集群式整合的轻总部收购操作系统"],
"#1135":["由Healthpeak分拆的纯Play养老社区REIT，34社区/10422单元/10州","2026-03纽交所上市(JAN)，发行4830万股@$20募资约8.78亿美元","RIDEA结构：收入主要来自住户费而非政府报销","Healthpeak任外部管理人并持有约81.6%股权"],
"#1136":["S&P500医疗地产REIT，2026-01将34个养老社区注入Janus Living","分拆后聚焦门诊医疗与生命科学实验室资产","2026 Q1完成7.14亿美元养老收购，并与黑石组门诊医疗JV(作价2.12亿)","回购590万股(约1亿美元)，资本循环积极"],
"#1144":["独立/辅助生活与记忆照护业主-运营商，纽交所SNDA","2025 Q3同店入住率87.7%(疫后新高)，组合NOI+21%","住户费收入占比约87%，支付以个人自费为主","2026-03完成收购CNL(69社区)，组合达153处、全美第8大"],
"#1147":["前身Avant Technologies，2026-02更名聚焦长寿细胞疗法","两大合资：Insulinova(糖尿病细胞疗法)+Klothonova(α-Klotho长寿蛋白)","借Austrianova的Cell-in-a-Box封装做免免疫抑制递送","均处临床前，OTCQB挂牌、无营收，高投机性"],
"#1153":["美国第二大养老/医疗REIT，纽交所VTR，1400+处物业","2025通过远期股权协议结算约1640万股、募资约11亿美元加仓养老社区","SHOP同店现金NOI同比+13%(2025 Q2)","资产覆盖养老社区/门诊医疗/生命科学实验室，多元化分散风险"],
"#1155":["专注Skilled Nursing护理院与长期急症医院的医疗REIT，纽交所OHI","2025投资资产115亿美元、1111处物业、9.3万+张床位","2025租户Genesis破产凸显租户集中度风险","2025 Q4发行Omega OP Units约2.22亿美元，新设20亿美元ATM计划"],
"#1156":["自管理养老REIT，纳斯达克CTRE，2014自Ensign分拆","2025以约8.17亿美元收购英国Care REIT(135处)开启出海","连续10年提高股息，低杠杆+Triple-net+高出租率","2025 Q3公开募资7.36亿美元"],
"#1158":["全美最大独立居家输液与专科药房，纳斯达克OPCH","服务免疫/肿瘤/罕见病等复杂慢病患者的居家/门诊输液","通过并购成长为赛道龙头","支付以医保/商业保险报销为主、个人自付为辅"],
}

# ---- events ----
EV = {
"#0950":[{"date":"2025全年","text":"完成三年战略转型，营收24.33亿美元(+20.2%)，调整后EBITDA 3.21亿(+74.8%)"},
        {"date":"2025","text":"收购Thrive Skilled Pediatric Care，并宣布1.755亿美元收购Family First Homecare(预计2026 Q2完成)"},
        {"date":"2025-11","text":"对2026年医保居家护理拟削减6.4%表达关切，对安宁并购保持纪律性(回避两位数倍数)"}],
"#0951":[{"date":"2025-09","text":"发布FY2025年报：营收8.537亿美元(+11.8%)，参与者约7740人、20个中心"},
        {"date":"2026指引","text":"预计参与者7900-8100、营收9-9.5亿美元、调整后EBITDA 5600-6500万美元"}],
"#0952":[{"date":"2024-12-02","text":"以3.506亿美元收购Gentiva个人护理资产，进入德州并成为最大供应商"},
        {"date":"2025","text":"德州基础时薪+9.9%预计年增收1770万美元；目标每年增长10%(半数为并购)"},
        {"date":"2025-08","text":"收购Helping Hands Home Care继续扩张"}],
"#0953":[{"date":"2025-10-01","text":"以1.465亿美元收购UnitedHealth/Amedisys剥离的54处居家健康/安宁资产(田纳西/乔治亚/阿拉巴马)"},
        {"date":"2025","text":"Q3营收2.29亿美元(+26.8%)，Medicare居家护理FFS收入占比<20%"}],
"#1135":[{"date":"2026-01-07","text":"Healthpeak宣布分拆组建纯Play养老REIT Janus Living"},
        {"date":"2026-03-20","text":"纽交所上市(JAN)，发行4830万股@$20，募资约8.78亿美元"},
        {"date":"2026 Q1","text":"完成7.14亿美元养老社区收购并注入Janus"}],
"#1136":[{"date":"2026-01-07","text":"宣布将34个养老社区(1.04万单元)注入Janus Living并任外部管理人"},
        {"date":"2026 Q1","text":"完成7.14亿美元养老收购；与黑石组建门诊医疗JV(作价2.12亿美元)"},
        {"date":"2026-03","text":"回购590万股(约1亿美元)"}],
"#1144":[{"date":"2025 Q3","text":"同店入住率87.7%(疫后新高)，组合NOI+21%"},
        {"date":"2026-03-11","text":"完成收购CNL Healthcare Properties(69社区)，组合达153处、全美第8大"}],
"#1147":[{"date":"2026-02-11","text":"由Avant Technologies更名Avaí Bio，聚焦长寿细胞疗法"},
        {"date":"2025-10/11","text":"与Austrianova设合资Insulinova、Klothonova(糖尿病/长寿蛋白细胞疗法，均临床前)"}],
"#1153":[{"date":"2025 Q2","text":"SHOP同店现金NOI同比+13%"},
        {"date":"2025","text":"通过远期股权协议结算约1640万股、募资约11亿美元加仓养老社区"}],
"#1155":[{"date":"2025","text":"投资资产115亿美元、1111处物业；租户Genesis破产凸显集中度风险"},
        {"date":"2025 Q4","text":"发行Omega OP Units约2.22亿美元，新设20亿美元ATM计划"}],
"#1156":[{"date":"2025 Q3","text":"公开募资7.36亿美元"},
        {"date":"2025","text":"以约8.17亿美元收购英国Care REIT(135处)出海；连续10年提高股息"}],
"#1158":[{"date":"1984至今","text":"通过持续并购成长为全美最大独立居家输液与专科药房服务商"}],
}

# ---- silver verdict / reason ----
SILVER = {
"#0950":("核心银发","居家健康、安宁疗护、私人护理直接服务老龄与失能人群，且含儿科属多元。"),
"#0951":("核心银发","PACE全包式整合照护专为失能双重资格老人设计，是银发支付创新范本。"),
"#0952":("核心银发","个人护理/居家照护是银发最基础的到家服务，直接服务老人与长护人群。"),
"#0953":("核心银发","居家健康/安宁/养老社区覆盖老龄全场景，去中心化运营提升照护质量。"),
"#1135":("核心银发","纯Play养老社区REIT，资产直接服务活跃/照护型长者居住需求。"),
"#1136":("核心银发","分拆出的养老社区组合是核心银发地产，母公司仍持多数股权与管理。"),
"#1144":("核心银发","独立/辅助生活与记忆照护社区业主-运营商，直接服务银发居住。"),
"#1147":("核心银发","长寿细胞疗法直击健康寿命延长与年龄相关衰退，属银发科技前沿。"),
"#1153":("核心银发","养老/医疗地产REIT，底层资产以养老社区为核心银发不动产。"),
"#1155":("核心银发","专注护理院(SNF)地产，终端支付来自政府医保与长者护理报销。"),
"#1156":("核心银发","自管理养老社区REIT，资产100%围绕银发居住与照护。"),
"#1158":("核心银发","居家输液/专科药房服务复杂慢病长者，是居家医疗银发场景。"),
}

# ---- tag_review ----
TAG_REVIEW = [
 {"serial":"#0950","name":"Aveanna Healthcare","intro":"全美居家健康、安宁疗护、私人护理与医疗解决方案整合服务商，覆盖38州，2025年完成战略转型营收高增。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["安宁疗护"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[{"action":"add","tag":"居家护理","reason":"业务含私人护理/居家健康，仅标安宁疗护偏窄"},{"action":"change","tag":"business_tags.role:服务商","reason":"实际提供到家照护服务，'上市公司'非业务角色"}]},
 {"serial":"#0951","name":"InnovAge","intro":"PACE(全包式养老照护)龙头，按人头打包支付服务失能双重资格老人，20个中心覆盖6州。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["专业护理","居家护理"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[{"action":"add","tag":"PACE整合照护","reason":"其差异化核心是PACE全包模式，应单列标签"},{"action":"change","tag":"business_tags.role:服务商","reason":"系照护运营方，'上市公司'非业务角色"}]},
 {"serial":"#0952","name":"Addus HomeCare","intro":"以个人护理为核心的居家照护连锁，260个网点覆盖23州，靠密度并购换议价权。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["居家护理"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[{"action":"add","tag":"个人护理","reason":"个人护理是其最大且最核心的 service line"},{"action":"change","tag":"business_tags.role:服务商","reason":"提供到家照护，'上市公司'非业务角色"}]},
 {"serial":"#0953","name":"The Pennant Group","intro":"去中心化控股公司，独立运营141家居家健康/安宁机构与61个养老社区，靠放权地方院长整合。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["安宁疗护","居家护理"],"business_tags":{"customer":"未标注","role":"上市公司","channel":[]}},
  "suggested":[{"action":"add","tag":"养老社区","reason":"组合含61个养老社区，标签未体现"},{"action":"change","tag":"business_tags.role:运营商","reason":"既持有又运营机构与社区，'上市公司'非业务角色"}]},
 {"serial":"#1135","name":"Janus Living","intro":"由Healthpeak分拆的纯Play养老社区REIT，34个社区/1万+单元，RIDEA结构、收入来自住户费。",
  "old_tags":{"tag_l1":["投资机构"],"tag_l2":["养老REIT"],"business_tags":{"customer":"未标注","role":"服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role:投资机构","reason":"实为持有养老地产的REIT，与tag_l1投资机构一致；'服务商'不符"}]},
 {"serial":"#1136","name":"Healthpeak Properties","intro":"S&P500医疗地产REIT，2026年把养老社区组合分拆为Janus Living后聚焦门诊医疗与实验室。",
  "old_tags":{"tag_l1":["投资机构"],"tag_l2":["养老REIT"],"business_tags":{"customer":"未标注","role":"服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role:投资机构","reason":"系持有并管理医疗/养老地产的REIT，'服务商'不符"}]},
 {"serial":"#1144","name":"Sonida Senior Living","intro":"独立/辅助生活与记忆照护业主-运营商，收购CNL后达153个社区，全美第8大。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["CCRC"],"business_tags":{"customer":"未标注","role":"平台","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role:运营商","reason":"自持并运营社区，'平台'表述不准确"},{"action":"add","tag":"记忆照护","reason":"业务含Memory Care，CCRC标签未覆盖"}]},
 {"serial":"#1147","name":"Avaí Bio","intro":"前身Avant Technologies，2026年更名聚焦长寿细胞疗法，两大合资推进糖尿病与α-Klotho长寿蛋白(均临床前)。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["长寿抗衰"],"business_tags":{"customer":"未标注","role":"制造商(药)","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l1:医疗健康","reason":"系生物科技公司，'消费品'分类错误"},{"action":"change","tag":"business_tags.role:产品商","reason":"研发细胞疗法产品，'制造商(药)'口径偏实"}]},
 {"serial":"#1153","name":"Ventas","intro":"美国第二大养老/医疗REIT，1400+处物业，近年加仓养老社区、SHOP同店NOI高增。",
  "old_tags":{"tag_l1":["投资机构"],"tag_l2":["养老REIT"],"business_tags":{"customer":"未标注","role":"平台","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role:投资机构","reason":"系持有并管理不动产的REIT，'平台'不准确"}]},
 {"serial":"#1155","name":"Omega Healthcare Investors","intro":"专注Skilled Nursing护理院的医疗REIT，1111处物业，高度依赖运营商偿付能力。",
  "old_tags":{"tag_l1":["投资机构"],"tag_l2":["养老REIT"],"business_tags":{"customer":"未标注","role":"服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role:投资机构","reason":"系持有护理院地产的REIT，'服务商'不符"}]},
 {"serial":"#1156","name":"CareTrust REIT","intro":"自管理养老社区REIT，低杠杆+高出租率+连续10年提息，2025年出海收购英国Care REIT。",
  "old_tags":{"tag_l1":["投资机构"],"tag_l2":["养老REIT"],"business_tags":{"customer":"未标注","role":"平台","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role:投资机构","reason":"系持有并自管理养老地产的REIT，'平台'不准确"}]},
 {"serial":"#1158","name":"Option Care Health","intro":"全美最大独立居家输液与专科药房，服务免疫/肿瘤/罕见病等复杂慢病患者的到家治疗。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["药品配送"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l1:健康服务","reason":"属居家医疗/药房服务，'消费品'分类错误"}]},
]

# ---- assemble ----
enterprises = []
order = ["#0950","#0951","#0952","#0953","#1135","#1136","#1144","#1147","#1153","#1155","#1156","#1158"]
for s in order:
    info,diff,copy,rv,stage,payor,role,founded = LIB[s]
    v,reason = SILVER[s]
    enterprises.append({
        "serial": s,
        "signal_strength": SIGNAL,
        "info_score": info,
        "diff_score": diff,
        "copy_score": copy,
        "research_value": rv,
        "recommend": REC[s],
        "desc_cn": DESC[s],
        "payor_model": payor,
        "business_tags_role": role,
        "founded": founded,
        "stage": stage,
        "highlights": HL[s],
        "events": EV[s],
        "update_time": "2026-07-17",
        "silver_verdict": v,
        "silver_reason": reason,
    })

out = {
    "batch": 4,
    "enterprises": enterprises,
    "tag_review": TAG_REVIEW,
    "nonsilver": [],
}

# ---- self-check ----
STAGE_OK = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
errors = []
for e in enterprises:
    nm = e["serial"]
    # 0-10 applies to the three sub-scores; research_value is on a 0-100 scale
    for k in ["info_score","diff_score","copy_score"]:
        if not (0 <= e[k] <= 10): errors.append(f"{nm}: {k} out of 0-10 ({e[k]})")
    r = e["recommend"]
    if not (60 <= len(r) <= 120): errors.append(f"{nm}: recommend length {len(r)} (need 60-120)")
    for bad in ["成立于","融资","轮","上市融资","IPO","纽交所","纳斯达克","OTC"]:
        if bad in r: errors.append(f"{nm}: recommend contains forbidden word '{bad}'")
    if e["stage"] not in STAGE_OK: errors.append(f"{nm}: stage not in whitelist ({e['stage']})")
    if not e["payor_model"]: errors.append(f"{nm}: payor empty")
    for fld in ["recommend","desc_cn","payor_model","business_tags_role","stage","silver_verdict","silver_reason","update_time"]:
        if e[fld] in (None,"","未标注"): errors.append(f"{nm}: field '{fld}' empty/placeholder")
    for fld in ["highlights","events"]:
        if not e[fld]: errors.append(f"{nm}: {fld} empty")
    if len(e["desc_cn"]) > 30: errors.append(f"{nm}: desc_cn {len(e['desc_cn'])} >30")
    for h in e["highlights"]:
        if len(h) > 60: errors.append(f"{nm}: highlight too long: {h[:20]}...")

print("SELF-CHECK ERRORS:", len(errors))
for er in errors: print("  -", er)
for e in enterprises:
    print(e["serial"], "rec_len=", len(e["recommend"]), "desc_len=", len(e["desc_cn"]), "stage=", e["stage"], "role=", e["business_tags_role"], "founded=", e["founded"])

with open("G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run_v2/out/batch_004_out.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("WROTE out/batch_004_out.json")
