import json

def e(serial, signal, info, diff, copy, rv, recommend, desc_cn, payor,
       role, founded, stage, highlights, events, silver_verdict, silver_reason,
       funding_latest, funding_total, investors):
    return dict(serial=serial, signal_strength=signal, info_score=info,
                diff_score=diff, copy_score=copy, research_value=rv,
                recommend=recommend, desc_cn=desc_cn, payor_model=payor,
                business_tags_role=role, founded=founded, stage=stage,
                highlights=highlights, events=events,
                update_time="2026-07-17", silver_verdict=silver_verdict,
                silver_reason=silver_reason, funding_latest=funding_latest,
                funding_total=funding_total, investors=investors)

E = []

E.append(e("#0744", 3.55, 7.0, 6.0, 5.0, 53.7,
"信号中等偏强，已是医疗语音AI头部、覆盖财富50强，信息量足；差异化在把医保核验、事前授权等高摩擦行政呼叫做成可规模化的语音代理，可复制性强。国内启发：养老险/长护险理赔与事前授权的自动化呼叫，是银发服务最易落地的降本切口。",
"医疗语音AI代理，自动完成医保核验与处方协调等行政呼叫",
"B端机构采购（健康险公司/药企/医疗系统按用量付费）", "服务商", 2019, "C轮",
["语音AI代理自动完成医保核验、事前授权、处方续方等高频行政呼叫",
 "已自动化超1亿分钟对话、服务12.5万+医生，覆盖44%财富50强医疗企业",
 "面向药企、健康险、医疗系统与专科药房的通用代理平台，含无代码Studio与对话分析Lens"],
[{"date": "2024-10", "text": "完成5150万美元C轮，累计融资约1.03亿美元"}],
"泛医疗擦边", "医疗行政自动化基础设施，主要服务药企与健康险，仅间接惠及老年医保人群",
{"date": "2024年10月", "amount": "5150万美元", "round": "C轮", "display": "C轮 5150万美元 (2024年10月)"},
"$103M", "a16z, Kleiner Perkins, Coatue, GV, Memorial Hermann"))

E.append(e("#0768", 3.55, 7.0, 6.0, 7.0, 57.7,
"信号稳健、已是英国养老选院流量入口且月活超50万，信息量足；差异化在用房源实时空床+价格透明+免费顾问解决选错养老院痛点，可复制性靠B2B软件订阅。国内启发：养老社区/机构的透明化比价与空床信息平台，是缓解供需错配的高频刚需。",
"英国养老院比对平台，实时空床与价格透明，配免费顾问",
"B端机构采购（养老机构按询客/订阅付费，C端家庭免费）", "服务商", 2021, "A轮",
["英国养老院/居家照护/退休社区比对平台，展示实时空床与价格，配免费专家顾问",
 "已收购养老软件Found，打通入住CRM与支付，月活用户超50万",
 "商业模式类似Tripadvisor/Skyscanner，向机构收广告/订阅，家庭端免费"],
[{"date": "2023-10", "text": "完成1635万欧元A轮（Accel领投），累计融资约3100万美元"}],
"核心银发", "面向老年照护机构的信息匹配平台，直击养老选院信息不对称",
{"date": "2023年10月", "amount": "1635万欧元", "round": "A轮", "display": "A轮 1635万欧元 (2023年10月)"},
"$31M", "Accel, General Catalyst"))

E.append(e("#0783", 3.55, 9.0, 8.0, 7.0, 67.7,
"信号极强、已成独角兽且保险覆盖全美50州，信息量足；差异化在把更年期这一被忽视人群做成全国性虚拟专科平台，可复制性受国内商保薄弱拖累。最该学的是聚焦被低估人群+保险支付的专科路径，国内可从女性中年健康管理切入。",
"更年期/中年女性虚拟专科诊所，保险覆盖全美50州",
"商业保险支付（保险覆盖全美50州，正在拓展Medicare/Medicaid）", "服务商", 2021, "成长期",
["虚拟更年期/中年女性专科诊所，保险覆盖全美50州，周活患者超2.5万",
 "已成独角兽、累计融资约2.5亿美元，AI驱动分诊/排程/病历分析",
 "乳腺癌筛查依从性提升28个百分点、结直肠癌提升11个百分点"],
[{"date": "2026-02", "text": "完成1亿美元D轮（Goodwater领投），估值超10亿美元成独角兽"},
 {"date": "2025-10", "text": "完成5000万美元C轮，拓展至代谢/体重/肌肉骨骼等路径"}],
"核心银发", "专注更年期/中年女性这一被低估的银发相邻人群，切入长寿健康赛道",
{"date": "2026-02", "amount": "1亿美元", "round": "D轮", "display": "D轮 1亿美元 (2026-02)"},
"$250M", "Goodwater Capital, Foresite Capital, Serena Ventures, GV, Emerson Collective, McKesson Ventures"))

E.append(e("#0817", 3.55, 5.0, 4.0, 5.0, 43.7,
"信号偏弱、业务偏通用营养消费品，信息量一般；差异化在掌握牛初乳原料与临床级益生菌组合，可复制性强但银发属性弱。国内启发：初乳/益生菌+肠道-免疫的适老营养品若结合慢病管理更易切入，但需警惕被归为普通保健品。",
"牛初乳营养与益生菌消费品公司，布局消化与免疫健康",
"个人自费（C端保健品消费，经Tmall等电商渠道）", "产品商", 2007, "成长期",
["全球牛初乳原料龙头，产品含TruBiotics益生菌、DiaResQ、Life's First Naturals",
 "通过阿里Tmall Global进入中国保健市场，并开发CBP初乳碱性蛋白",
 "2024年引入更年期OB-GYN专家进入科学顾问委员会"],
[{"date": "2023-10", "text": "完成约5229万美元私募股权融资"}],
"泛医疗擦边", "通用营养保健品公司，银发关联弱（仅顾问含更年期专家）",
{"date": "2023-10月", "amount": "5229万美元", "round": "私募股权", "display": "私募股权 5229万美元 (2023年10月)"},
"约5229万美元（2023年私募股权轮）", ["未搜到"]))

E.append(e("#0885", 3.55, 7.0, 6.0, 6.0, 55.7,
"信号稳健、已深度绑定医保与商保支付方，信息量足；差异化在把碎片化的居家照护（DME/护理）做成带反欺诈的福利管理闭环，可复制性强。国内启发：长护险与医保居家医疗的供应商匹配+控费平台，是支付方最缺的基础设施。",
"家庭医疗用品与居家照护的保险福利管理/匹配平台",
"政府医保(Medicare Advantage/Medicaid/双重资格)+商业健康险（按PMPM节省分账）", "服务商", 2018, "B轮",
["技术驱动的居家医疗福利管理商，连接健康险与4万+居家照护供应商",
 "聚焦Medicare Advantage/Medicaid，声称首年12个月内实现约3倍ROI、节省3-5%",
 "AI反欺诈系统实时标记过度使用，订单100%路由至优质在网供应商"],
[{"date": "2022-06", "text": "完成6000万美元B轮（BOND领投），累计融资约9250万美元"}],
"核心银发", "聚焦居家照护与医保（Medicare Advantage/Medicaid）支付，直击老年居家医疗",
{"date": "2022年6月", "amount": "6000万美元", "round": "B轮", "display": "B轮 6000万美元 (2022年6月)"},
"$92.5M", "Andreessen Horowitz, Bond, Obvious Ventures, BoxGroup, Montauk Ventures"))

E.append(e("#0889", 3.55, 7.0, 6.0, 5.0, 53.7,
"信号稳健、已是混合行为健康头部且疗效数据突出，信息量足；差异化在治疗师匹配算法+测量式照护提升留存，可复制性强。国内启发：老龄化下老年抑郁/认知伴发情绪问题增多，精准匹配+疗效量化的线下+远程心理服务值得借鉴，但需先解决支付与病耻感。",
"心理治疗匹配平台，300维算法+测量式照护",
"商业保险支付（Aetna/Kaiser在网）+部分Medicare/Medicaid+个人自费(约226美元/次)", "服务商", 2017, "C轮",
["专有300变量算法+临床匹配访谈，97%患者与治疗师联盟度高",
 "测量式照护（每次就诊前收集量表），90%患者坚持到第四次session（行业均值36%）",
 "在网Aetna/Kaiser，覆盖加州/华盛顿/佛州并虚拟扩展至19州"],
[{"date": "2024-04", "text": "完成7200万美元C轮（股权+债权，Amplo领投），累计约1.03亿美元"}],
"泛医疗擦边", "泛心理健康服务，非老年专属，但覆盖复杂高年资患者与Medicare部分人群",
{"date": "", "amount": "7200万美元", "round": "C轮", "display": "C轮 7200万美元"},
"$100M", ["Amplo", "Maveron", "Fifth Down Capital", "What If Ventures"]))

E.append(e("#0907", 3.55, 7.0, 7.0, 6.0, 57.7,
"信号稳健、价值型肌骨护理临床与成本证据强，信息量足；差异化在医生+康复师+营养师一体化虚拟首诊，可复制性高。国内启发：老龄化下腰颈关节痛与跌倒是高频刚需，肌骨整合+控费的保险/企业福利路径，比单点康复更易规模化。",
"医生主导的肌肉骨骼虚拟/线下整合照护",
"商业保险支付(含Medicare)+雇主福利+个人自费", "服务商", 2020, "B轮",
["全美首个医生主导的肌骨整合照护，MD+PT同次问诊消除等待",
 "78-90%减少择期骨科手术、阿片使用降42%、抑郁焦虑降达68%",
 "验证4:1 ROI，服务Fortune 200企业与全国健康险，2025年B轮5300万美元"],
[{"date": "2025-03", "text": "完成5300万美元B轮（NEA领投），加速价值型肌骨护理"}],
"核心银发", "肌骨疼痛/跌倒/行动力是老龄化核心议题，价值型MS护理高度适老",
{"date": "2025年3月", "amount": "5300万美元", "round": "B轮", "display": "B轮 5300万美元 (2025年3月)"},
"$53M", ["NEA", "AlleyCorp", "Intermountain Ventures", "Echo Health Ventures", "Max Ventures"]))

E.append(e("#1280", 3.55, 5.0, 8.0, 6.0, 53.7,
"信号中等、临床验证扎实且差异化极高，信息量足；差异化在把AR眼镜做成居家神经康复数字疗法、依从率超100%，可复制性受硬件与监管标签制约。国内启发：卒中/帕金森居家康复的游戏化AR+远程督导路径，可借康复医保与智慧养老设备政策落地。",
"AR眼镜居家神经康复数字疗法（帕金森/卒中）",
"B端机构采购（NHS/诊所/康复机构）+个人自费（硬件+订阅）", "产品商", 2019, "A轮",
["AR眼镜Reality DTx把物理治疗游戏化，居家神经康复，临床依从率104%",
 "获NIHR 240万英镑资助开展帕金森病RCT，并与Cleveland Clinic美国合作",
 "单治疗师可多提供7倍治疗、省67%工时，面向NHS与居家场景"],
[{"date": "2025-03", "text": "完成1035万英镑A轮（IW Capital领投），加速神经康复数字疗法销售"}],
"核心银发", "AR居家神经康复直击帕金森/卒中老年人群，临床依从性超100%",
{"date": "2025-03", "amount": "1035万英镑(约1220万欧元)", "round": "A轮", "display": "A轮 1035万英镑 (2025-03)"},
{"amount": "累计约1035万英镑", "display": "累计约1035万英镑(A轮)"}, ["IW Capital"]))

E.append(e("#1320", 3.55, 5.0, 6.0, 7.0, 51.6,
"信号中等、比利时职场养老金数字化切口清晰，信息量足；差异化在持牌养老基金+零资产费率+AI财务教练重构补充养老，可复制性强。国内启发：企业年金/个人养老金的透明低费+财务教练模式，是提升养老金融参与率的可借鉴路径。",
"比利时职场养老金+全程财务教练平台",
"企业(B端)订阅（雇主固定费，员工养老金资本自留）+个人", "服务商", 2021, "种子期",
["自营IBP持牌养老基金，ETF低费组合、无资产费率，雇主固定订阅",
 "AI+真人财务教练覆盖养老/健康险/房贷/投资，已接入Mypension.be与PSD2",
 "一年内约百家比利时企业采用，目标2028年10万员工上平台"],
[{"date": "2026-06", "text": "完成1000万欧元种子轮（Motive Partners风投部领投），筹备欧洲扩张"}],
"核心银发", "职场养老金+财务教练，直击补充养老短板，属养老金融",
{"date": "2026-06", "amount": "1000万欧元", "round": "种子轮", "display": "种子轮 1000万欧元 (2026-06)"},
{"amount": "累计1000万欧元", "display": "累计1000万欧元(种子轮)"},
["Motive Partners(风投部)", "F Capital", "Entourage", "Syndicate One", "100IN"]))

E.append(e("#1330", 3.55, 6.0, 6.0, 6.0, 52.6,
"信号中等、退休账户+另类资产集成有差异化，信息量一般；差异化在把自助IRA做成低门槛另类投资入口，可复制性强。国内启发：个人养老金账户若开放更多元资产（如养老理财/REITs/私募）并简化开户，可显著提升参与率与长期收益。",
"自助IRA退休账户平台，可投另类资产",
"个人自费（账户月费/年费由个人承担，资金来自rollover或定供）", "服务商", 2018, "B轮",
["自助IRA托管平台，允许在退休账户内投创投/房产/加密/艺术品等另类资产",
 "与Coinbase及75+另类投资伙伴集成，Pro版年费250美元、无资产费率",
 "提供传统/Roth/SEP IRA，资金可rollover自401(k)，降低另类投资税负担"],
[{"date": "2026", "text": "完成7310万美元B轮（据Tracxn），累计融资约1亿美元"}],
"核心银发", "自建IRA退休账户、支持另类资产，属个人养老储蓄基础设施",
{"date": "2026", "amount": "7310万美元", "round": "B轮", "display": "B轮 7310万美元"},
{"amount": "约1亿美元", "display": "累计约1亿美元"}, ["未搜到"]))

E.append(e("#1351", 3.55, 9.0, 7.0, 7.0, 65.7,
"信号强、是养老软件赛道头部且交易透明，信息量足；差异化在把养老/长护机构的文档、报销与合规做成基础系统，可复制性受PE整合节奏影响。国内启发：养老机构EHR与长护险报销/评估的打通，是银发数字基建最该补的水电煤。",
"老年护理/养老社区EHR与运营SaaS平台",
"B端机构采购（养老/护理机构SaaS订阅）", "服务商", "未搜到", "被收购",
["面向养老/护理/临终关怀机构的EHR与运营平台，服务超1.5万家供应商",
 "2026年7月ResMed以4.9亿美元出售给Frazier，原ResMed 2019年7.5亿美元收购",
 "FY2026收入约2.2亿美元、经营利润约5500万美元，Best in KLAS多年获奖"],
[{"date": "2026-07", "text": "ResMed宣布以4.9亿美元将MatrixCare出售给Frazier Healthcare Partners（预计Q3交割）"}],
"核心银发", "面向养老/术后急性照护机构的EHR与运营系统，是银发数字基建",
{"date": "2026-07", "amount": "4.9亿美元", "round": "被收购", "display": "2026-07 被PE以$490M收购(原ResMed)"},
"被收购", "Frazier Healthcare Partners（买方）"))

E.append(e("#0561", 3.05, 8.0, 8.0, 7.0, 63.2,
"信号强、患者创立且保险覆盖全美，信息量足；差异化在把神经退行疾病做成专科医生+照护者支持+GUIDE模型的虚拟整合照护，可复制性受国内专科稀缺制约。国内启发：认知症居家照护的专科远程+照护者减负组合，最契合长护险与认知障碍照护政策。",
"神经退行性疾病（阿尔茨海默/帕金森/ALS）虚拟专科",
"政府医保(Medicare/Medicaid)+商业保险（在网，并参与CMS GUIDE痴呆照护）", "服务商", 2019, "A轮",
["患者与照护者创立的虚拟神经科，覆盖阿尔茨海默/帕金森/ALS，全美50州保险覆盖",
 "参与CMS GUIDE痴呆照护模型，提供专科医生+行为健康+照护者支持的整合包",
 "A轮2500万美元由B Capital领投，合作方含CVS Health Ventures、CommonSpirit"],
[{"date": "2024-11", "text": "完成2500万美元A轮（B Capital领投），累计融资约4610万美元"}],
"核心银发", "专注阿尔茨海默/帕金森/ALS等老年神经退行疾病的虚拟专科与照护者支持",
{"date": "2024-11", "amount": "2500万美元", "round": "A轮", "display": "A轮 2500万美元 (2024-11)"},
"$46.1M (截至2024年)", ["B Capital", "CommonSpirit Health", "CVS Health Ventures", "RA Capital Management", "Nexus NeuroTech Ventures", "Google Ventures", "Lifeforce Capital"]))

tag_review = [
 {"serial": "#0744", "name": "Infinitus Systems",
  "intro": "医疗语音AI代理公司，用自动化呼叫处理医保核验、事前授权、处方续方等行政流程，客户为药企、健康险与医疗系统。",
  "old_tags": {"tag_l1": ["行业服务"], "tag_l2": ["AI医疗"], "business_tags": {"customer": "B2B", "role": "技术服务商", "channel": []}},
  "suggested": [{"action": "add", "tag": "医保科技(行政自动化)", "reason": "业务本质是医疗行政呼叫自动化，现有AI医疗标签过宽"}]},
 {"serial": "#0768", "name": "Lottie",
  "intro": "英国养老选院信息平台，比对养老院/居家照护/退休社区的实时空床与价格，配免费顾问，向机构收订阅/广告。",
  "old_tags": {"tag_l1": ["行业服务"], "tag_l2": ["养老信息平台"], "business_tags": {"customer": "B2B", "role": "服务商(媒体/数据)", "channel": []}},
  "suggested": [{"action": "add", "tag": "养老比价/选院", "reason": "强调实时空床+价格透明的核心差异，便于检索"}]},
 {"serial": "#0783", "name": "Midi Health",
  "intro": "专注更年期/中年女性的虚拟专科诊所，保险覆盖全美50州，已成独角兽，AI驱动分诊与病历分析。",
  "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["诊所"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
  "suggested": [{"action": "add", "tag": "女性健康/更年期", "reason": "现有诊所过泛，应补齐更年期/女性中年健康这一核心标签"}]},
 {"serial": "#0817", "name": "PanTheryx",
  "intro": "牛初乳原料与益生菌/消化免疫营养消费品公司，通过Tmall进入中国，属通用保健品。",
  "old_tags": {"tag_l1": ["食品营养"], "tag_l2": ["保健品"], "business_tags": {"customer": "B2B", "role": "服务商(媒体/数据)", "channel": []}},
  "suggested": []},
 {"serial": "#0885", "name": "Tomorrow Health",
  "intro": "居家医疗福利管理商，连接健康险与4万+供应商，聚焦Medicare Advantage/Medicaid，带AI反欺诈。",
  "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["护工平台", "居家护理"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
  "suggested": [{"action": "change", "tag": "居家医疗/福利管理", "reason": "本质是保险福利管理与供应商匹配，护工平台窄化且偏差"}]},
 {"serial": "#0889", "name": "Two Chairs",
  "intro": "混合行为健康服务商，300变量算法匹配治疗师，测量式照护，在网Aetna/Kaiser。",
  "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["心理健康"], "business_tags": {"customer": "B2B", "role": "服务商(媒体/数据)", "channel": []}},
  "suggested": []},
 {"serial": "#0907", "name": "Vori Health",
  "intro": "医生主导的肌骨整合虚拟/线下照护，验证降低手术与阿片使用，服务健康险与企业。",
  "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["远程医疗"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
  "suggested": [{"action": "add", "tag": "肌骨健康", "reason": "现有远程医疗过泛，应补齐肌骨/运动系统健康核心标签"}]},
 {"serial": "#1280", "name": "Strolll",
  "intro": "AR眼镜神经康复数字疗法公司，面向帕金森/卒中居家康复，临床依从率超100%。",
  "old_tags": {"tag_l1": ["康复辅具", "消费品"], "tag_l2": ["视觉辅助", "眼镜"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
  "suggested": [{"action": "change", "tag": "神经康复(AR)", "reason": "视觉辅助误导，实为AR神经康复数字疗法"}]},
 {"serial": "#1320", "name": "Warren",
  "intro": "比利时职场养老金+AI财务教练平台，自营持牌养老基金、零资产费率，雇主固定订阅。",
  "old_tags": {"tag_l1": ["金融保险"], "tag_l2": ["金融理财"], "business_tags": {"customer": "未标注", "role": "服务商", "channel": []}},
  "suggested": []},
 {"serial": "#1330", "name": "AltoIRA",
  "intro": "自助IRA退休账户平台，允许在退休账户内投另类资产，与Coinbase及75+伙伴集成。",
  "old_tags": {"tag_l1": ["金融保险"], "tag_l2": ["金融理财"], "business_tags": {"customer": "B2B", "role": "服务商(媒体/数据)", "channel": []}},
  "suggested": []},
 {"serial": "#1351", "name": "MatrixCare",
  "intro": "面向养老/长护/临终关怀机构的EHR与运营SaaS平台，服务超1.5万家供应商，刚被PE收购。",
  "old_tags": {"tag_l1": ["行业服务"], "tag_l2": ["养老软件"], "business_tags": {"customer": "B2B", "role": "服务商(媒体/数据)", "channel": []}},
  "suggested": []},
 {"serial": "#0561", "name": "Synapticure",
  "intro": "患者创立的虚拟神经科，覆盖阿尔茨海默/帕金森/ALS，全美50州保险覆盖，参与CMS GUIDE模型。",
  "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["远程医疗"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
  "suggested": [{"action": "add", "tag": "神经退行/认知症", "reason": "现有远程医疗过泛，应补齐神经退行/认知症核心标签"}]},
]

nonsilver = [
 {"serial": "#0744", "name": "Infinitus Systems", "verdict": "泛医疗擦边", "reason": "医疗行政自动化基础设施，主要服务药企与健康险，仅间接惠及老年医保人群"},
 {"serial": "#0817", "name": "PanTheryx", "verdict": "泛医疗擦边", "reason": "通用营养保健品公司，银发关联弱（仅顾问含更年期专家）"},
 {"serial": "#0889", "name": "Two Chairs", "verdict": "泛医疗擦边", "reason": "泛心理健康服务，非老年专属，仅部分覆盖Medicare人群"},
]

out = {"batch": 12, "enterprises": E, "tag_review": tag_review, "nonsilver": nonsilver}

problems = []
for x in E:
    for k in ["recommend", "desc_cn", "payor_model", "business_tags_role", "stage", "silver_verdict", "silver_reason"]:
        if x[k] in (None, "", []):
            problems.append(f"{x['serial']} empty {k}")
    if not (60 <= len(x["recommend"]) <= 120):
        problems.append(f"{x['serial']} recommend len {len(x['recommend'])}")
    if len(x["desc_cn"]) > 30:
        problems.append(f"{x['serial']} desc_cn len {len(x['desc_cn'])}")
    if x["stage"] not in {"种子期", "天使", "Pre-A", "A轮", "B轮", "C轮", "成长期", "已上市", "被收购", "未搜到"}:
        problems.append(f"{x['serial']} stage not whitelist {x['stage']}")
    if not x["payor_model"]:
        problems.append(f"{x['serial']} payor empty")
    if x["founded"] in (None, ""):
        problems.append(f"{x['serial']} founded empty")
    for sc in ["info_score", "diff_score", "copy_score"]:
        if not (0 <= x[sc] <= 10):
            problems.append(f"{x['serial']} {sc} out of range")

print("PROBLEMS:", problems if problems else "NONE")
json.dump(out, open("scores_draft/run_v2/out/batch_012_out.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("WROTE batch_012_out.json with", len(E), "enterprises; tag_review", len(tag_review), "nonsilver", len(nonsilver))
