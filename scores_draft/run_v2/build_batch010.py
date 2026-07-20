# -*- coding: utf-8 -*-
import json

OUT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run_v2/out/batch_010_out.json"

WHITELIST_STAGE = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}

# ---- per-company drafted data ----
# recommend / desc_cn / payor_model / business_tags_role / stage / founded / silver_verdict / silver_reason
rec = {
"#0037": dict(
  stage="成长期", founded=2019, payor="个人自费+B端机构采购", role="产品商",
  desc="柔性肌肉外甲助行外骨骼，增强老人行走与康复。",
  recommend="信号中、信息透明（量产进院与营收可查），差异化在柔性肌肉外甲以AI预测动作意图实时补力，已从康复切到消费级助行；可复制性强，最该学“医疗器械打底+消费级外骨骼放量”双轮，国内已有同类淘宝秒罄验证。",
  silver="核心银发", silver_reason="柔性助行外骨骼直接服务老年人与行动不便人群日常康复助行。"),
"#0032": dict(
  stage="天使", founded=2020, payor="B端机构采购+个人自费", role="服务商",
  desc="手机AI眼动认知早筛，6分钟评估老人痴呆风险。",
  recommend="信号偏弱、信息量一般，差异化在以手机摄像头做AI眼动认知早筛，6分钟出报告且获三类械证，并联合险企打通“检测-干预-保障”闭环；可复制性高，最该学把早筛做成可规模化数字生物标志物，国内落地阻力在支付与渠道。",
  silver="核心银发", silver_reason="以AI眼动筛查服务老年认知障碍早筛与干预，直击失智赛道。"),
"#0471": dict(
  stage="B轮", founded=2016, payor="混合支付", role="服务商",
  desc="家庭照护支持平台，把养老照护做成员工福利。",
  recommend="信号中、信息透明（雇主与健康计划双渠道、成效数据公开），差异化在用AI加真人Care Guide把家庭照护做成可白标员工福利；可复制性受国内企业福利体系薄弱拖累，最该学“照护支持嵌入企业EAP与商业保险”的B2B2C路径。",
  silver="核心银发", silver_reason="面向家庭照护者提供支持，间接服务老年人群的专业护理需求。"),
"#0564": dict(
  stage="成长期", founded=2017, payor="保险支付+个人自费", role="平台",
  desc="非医疗陪伴网络，以共享儿女对接独居老人。",
  recommend="信号中、信息透明，差异化在非医疗“共享儿女”陪伴网络，并借CMS痴呆照护项目与保险方做预防性触达；可复制性受国内陪护合规与支付差异制约，最该学把轻陪伴做成健康计划的获客黏性入口而非单纯家政。",
  silver="核心银发", silver_reason="以大学生陪伴对接独居老人情感与家务需求，直击银发孤独经济。"),
"#0861": dict(
  stage="成长期", founded=2016, payor="混合支付(健康计划+政府Medicare价值医疗合同，B端机构付费为主)", role="服务商",
  desc="价值导向肾病与心血管护理，延缓老人病程。",
  recommend="信号中、信息透明，差异化在把肾病与心血管护理做成按价值付费的综合体，靠预测分析与到家多学科团队延缓病程；可复制性受国内按价值付费环境缺失制约，最该学“数据预测+到家服务+支付方风险共担”的慢病架构。",
  silver="核心银发", silver_reason="面向中老年慢性病(肾/心)人群的价值导向综合护理，直接服务银发健康。"),
"#0959": dict(
  stage="B轮", founded=2020, payor="B端机构采购", role="服务商",
  desc="AI语音护理记录助手，自动生成合规养老病历。",
  recommend="信号中、信息透明（落地机构与护士数公开），差异化在把护理员口述实时转成合规结构化病历且离线可用；可复制性强，最该学用语音AI切入养老护理记录自动化，国内痛点是EHR割裂与方言准确度需本地化训练。",
  silver="核心银发", silver_reason="为养老机构提供护理记录自动化，直接提升银发照护效率。"),
"#0457": dict(
  stage="成长期", founded=2014, payor="混合支付", role="平台",
  desc="居家护理网络平台，连接护工与家庭并输出技术。",
  recommend="信号偏弱、信息一般，差异化在以技术底座连接护理员与家庭并用并购整合护工网络；可复制性中等，最该学“平台+标准化服务+并购扩张”的护工网络打法，国内落地难点在护工供给质量与本地化运营。",
  silver="核心银发", silver_reason="居家护理技术与网络平台，直接服务老年护理供需匹配。"),
"#0458": dict(
  stage="成长期", founded=2016, payor="B端机构采购", role="服务商",
  desc="AI环境感知监护设备，无感守护老年社区安全。",
  recommend="信号偏弱、信息一般，差异化在以环境感知设备把老年社区变成无感安全监护网络；可复制性中等，最该学“智能基础设施”定位而非单点硬件，国内落地受隐私顾虑与养老院付费能力双重制约。",
  silver="核心银发", silver_reason="AI环境感知直接服务老年社区安全监护与生活质量。"),
"#0463": dict(
  stage="A轮", founded=2020, payor="混合支付", role="平台",
  desc="连接医疗与社会服务的银发社区支持平台。",
  recommend="信号偏弱、信息一般，差异化在把医疗与社会服务组织连成银发社区支持网，覆盖交通送餐与社交；可复制性中等，最该学“资源连接器”定位，国内落地需借力社区与政府购买服务，纯商业获客难。",
  silver="核心银发", silver_reason="为社会隔离老人提供交通/送餐/社交等基础银发支持服务。"),
"#0464": dict(
  stage="A轮", founded=2013, payor="B端机构采购", role="服务商",
  desc="AI行为感知可穿戴，早期预警老人健康恶化。",
  recommend="信号偏弱、信息一般，差异化在被动式可穿戴持续感知行为、提前预警健康恶化（住院降39%、跌倒降69%）；可复制性强，最该学“无感监测+预测干预”的养老运营数据闭环，国内落地卡在支付与隐私合规。",
  silver="核心银发", silver_reason="AI行为监测直接服务老年健康预警与跌倒预防。"),
"#0465": dict(
  stage="C轮", founded=2012, payor="B端企业采购+个人自费", role="服务商",
  desc="企业员工家庭照护支持平台，留人亦护老。",
  recommend="信号偏弱、信息一般，差异化在把员工的家庭照护负担做成企业留人福利，客户含宝洁、毕马威；可复制性中等，最该学“企业买单+专业照护导航”的B2B2C路径，国内可嫁接EAP与商业健康险。",
  silver="核心银发", silver_reason="通过企业福利支持在职子女照护老年亲属，切入银发照护链。"),
"#0472": dict(
  stage="A轮", founded=2019, payor="个人自费", role="产品商",
  desc="自动对焦老花眼镜，按视力实时调节镜片度数。",
  recommend="信号偏弱、信息一般，差异化在全球首款自动对焦老花镜，用液晶镜片加眼动追踪实时变焦；可复制性中等，最该学“眼镜即科技消费品”定位，国内落地难点在量产良率、医疗械证与千元级定价市场教育。",
  silver="核心银发", silver_reason="自动对焦老花镜直接服务老年视力退化人群。"),
}

# scores + funding + highlights + events pulled from main library (verbatim, non-empty)
lib = {
"#0037": dict(ss=4.05,info=6.0,diff=7.0,copy=5.0,rv=54.1,
  fl={"date":"2021-04","amount":"10000000","round":"A","display":"A $1000万 (2021-04)"},
  ft={"amount":"超千万美元","display":"累计超千万美元"},
  inv="碧桂园创投、乔贝资本领投，高瓴资本、BV百度风投、线性资本跟投",
  hl=["全球首款轻量级柔性肌肉外甲，AI预测动作意图实时补力","产品进入全国40余家三甲医院，已实现量产销售","2025入选MIT TR50聪明公司，获央视新质生产力奖项"],
  ev=[{"date":"2022-07","text":"肌肉外甲获二类医疗器械注册证并发布"},{"date":"2024","text":"完成6400万元B轮融资（无锡梁溪科创基金领投）"},{"date":"2025","text":"入选《麻省理工科技评论》50家聪明公司"}]),
"#0032": dict(ss=3.55,info=5.0,diff=7.0,copy=6.0,rv=51.6,
  fl={"date":"2022-02","amount":"10000000","round":"天使轮","display":"天使轮 $1000万 (2022-02)"},
  ft={"amount":"约1000万元","display":"累计约1000万元"}, inv="诺庾资本",
  hl=["AI眼动追踪6分钟评估认知功能，鉴别准确度约93%","延伸至干预治疗与保险支付综合服务","产品用于医疗机构、企业与政府脑健康管理"],
  ev=[{"date":"2022-02","text":"完成1000万元天使轮，诺庾资本投资"}]),
"#0471": dict(ss=4.05,info=7.0,diff=7.0,copy=5.0,rv=57.1,
  fl={"date":"2022-05","amount":"20000000","round":"Series B","display":"Series B $2000万 (2022-05)"},
  ft={"amount":"38000000","display":"累计$3800万"}, inv=["未搜到"],
  hl=["技术驱动family caregiving，服务雇主与健康计划","2024年11月融资2000万美元，自2022年规模增4倍","客户含数百家企业，切入员工照护福利"],
  ev=[{"date":"2022-05","text":"完成2000万美元B轮"},{"date":"2024-11","text":"再融资2000万美元，规模自2022年增4倍"},{"date":"2025-04","text":"36氪报道其融资1.5亿、数百家企业买单"}]),
"#0564": dict(ss=4.05,info=7.0,diff=8.0,copy=4.0,rv=57.1,
  fl={"date":"2024-07","amount":"$60M","round":"Series D延展","display":"Series D延展 $60M (2024-07)"},
  ft={"amount":"$257M","display":"累计$257M"},
  inv="SoftBank Vision Fund 2, Tiger Global, Canaan, Initialized Capital, Y Combinator, Comcast Ventures, TCG, Seven Seven Six",
  hl=["非医疗陪伴‘共享儿女’模式，估值14亿美元独角兽","服务覆盖全美50州、超100家健康计划，累计服务超260万次","保险支付+长者自费，会员医疗开支降9%、住院减18%"],
  ev=[{"date":"2021-11","text":"完成1.5亿美元D轮，估值14亿美元成独角兽"},{"date":"2024-07","text":"完成6000万美元D轮延展"},{"date":"2026-06","text":"获联邦痴呆照护项目支持，扩展人性化照护"}]),
"#0861": dict(ss=4.05,info=7.0,diff=4.0,copy=4.0,rv=49.1,
  fl={"round":"G轮","amount":"约7500万美元","currency":"USD","date":"2025-06","display":"G轮 约7500万美元 (2025-06)","investors":["未披露(Forge标注Undisclosed)"]},
  ft={"amount":"约14亿美元(含可转债)","display":"累计约14亿美元(含可转债结构)"}, inv=["未披露"],
  hl=["价值导向肾+心血管综合护理龙头","G轮约7500万美元(2025-06)，估值约49.8亿","服务突破50万生命，降低肾病死亡率13%"],
  ev=[{"date":"2022-02","text":"完成3.25亿美元E轮，估值超25亿美元"},{"date":"2025-06","text":"完成约7500万美元G轮，估值约49.8亿美元"}]),
"#0959": dict(ss=4.05,info=7.0,diff=6.0,copy=5.0,rv=55.2,
  fl={"date":"2025.11","amount":"5000万美元","round":"A/B轮","display":"A/B轮 5000万美元 (2025.11)"},
  ft={"amount":"$59M","display":"累计$59M (截至2025年11月)"},
  inv="Balderton Capital, HV Capital, Y Combinator, MK Venture Capital",
  hl=["AI语音将护理口述转结构化合规文档","已在德国1000+家养老机构落地","2025年连获种子+A轮，累计约5900万欧元"],
  ev=[{"date":"2025-03","text":"获900万美元种子轮"},{"date":"2025-11","text":"获4300万欧元A轮，由Balderton领投"}]),
"#0457": dict(ss=3.55,info=6.0,diff=7.0,copy=5.0,rv=52.6,
  fl={"date":"2024-03","amount":"$70M","round":"Series E","display":"Series E $70M (2024-03)"},
  ft={"amount":"$325M+","display":"累计$325M+"},
  inv="Baillie Gifford, 8VC, Prosus, Andreessen Horowitz (a16z), Thrive Capital, T. Rowe Price",
  hl=["‘滴滴护工’模式连接护理员与家庭，估值超30亿美元","2021收购Home Instead，网络覆盖14国","2025年3月再获1.4亿美元融资"],
  ev=[{"date":"2021","text":"收购全美最大居家护理公司Home Instead(估值约21亿美元)"},{"date":"2024-03","text":"完成7000万美元E轮"},{"date":"2025-03","text":"与Home Instead再获1.4亿美元融资"}]),
"#0458": dict(ss=3.55,info=6.0,diff=7.0,copy=5.0,rv=52.6,
  fl={"date":"2025-03","amount":"35000000","round":"Series A","display":"Series A $3500万 (2025-03)"},
  ft={"amount":"$155M (截至2025年)","display":"累计$155M (截至2025年)"},
  inv=["Insight Partners","Avenir Growth Capital","Primary Venture Partners","Scale Venture Partners","Story Ventures","Third Prime"],
  hl=["AUGi设备实时感知老年社区环境，定位护理智能基础设施","2025年连获A、B轮共1.35亿美元","18个月拿下150+老年社区"],
  ev=[{"date":"2025-03","text":"完成3500万美元A轮"},{"date":"2025-09","text":"完成1亿美元B轮，Insight Partners领投"}]),
"#0463": dict(ss=3.55,info=6.0,diff=6.0,copy=5.0,rv=50.6,
  fl={"date":"2025-04","amount":"26000000","round":"Series A","display":"Series A $2600万 (2025-04)"},
  ft={"amount":"32500000","display":"累计$3250万"}, inv="Insight Partners (领投)",
  hl=["连接医疗保健提供者与社会服务组织，覆盖21州700+社区","为老人提供交通、送餐、社交等社会照护支持","2025年完成2600万美元A轮"],
  ev=[{"date":"2025-04","text":"完成2600万美元A轮，Insight Partners领投"}]),
"#0464": dict(ss=3.55,info=6.0,diff=7.0,copy=5.0,rv=52.6,
  fl={"date":"2023-07","amount":"29000000","round":"Series A","display":"Series A $2900万 (2023-07)"},
  ft={"amount":"48600000","display":"累计$4860万"},
  inv="Medtech Convergence Fund, Secocha Ventures 等 (8位投资人)",
  hl=["AI识别日常活动与行为变化，提前发现健康异常","落地数据：住院率降39%、跌倒率降69%","2023年完成2900万美元A轮，累计约4860万美元"],
  ev=[{"date":"2023-07","text":"完成2900万美元A轮"}]),
"#0465": dict(ss=3.55,info=6.0,diff=7.0,copy=5.0,rv=52.6,
  fl={"date":"2024-04","amount":"20000000","round":"Series C","display":"Series C $2000万 (2024-04)"},
  ft={"amount":"$42M (截至2024年)","display":"累计$42M (截至2024年)"},
  inv=["Noro-Moseley Partners","ABS Capital Partners","Green Park & Golf Ventures"],
  hl=["为宝洁、毕马威等企业提供员工家庭照护支持","3年收入增长近300%，NPS超80","2024年完成2000万美元C轮"],
  ev=[{"date":"2024-04","text":"完成2000万美元C轮"}]),
"#0472": dict(ss=3.55,info=6.0,diff=7.0,copy=5.0,rv=52.6,
  fl={"date":"2025-04","amount":"36500000","round":"Unknown","display":"Unknown $3650万 (2025-04)"},
  ft={"amount":"$36.5M (截至2025年)","display":"累计$36.5M (截至2025年)"},
  inv=["Plural","Tesi","byFounders","Heartcore","Eurazeo","FOV Ventures","Tiny Supercomputer","Amazon Alexa Fund","Maki.vc","First Fellow"],
  hl=["全球首款自动对焦老花眼镜，按佩戴者视力实时调焦","获亚马逊Alexa基金等投资","2025年完成3650万美元融资"],
  ev=[{"date":"2025-04","text":"完成3650万美元融资，亚马逊Alexa基金参投"}]),
}

names = {
"#0037":"远也","#0032":"织生科技","#0471":"Homethrive","#0564":"Papa","#0861":"Somatus",
"#0959":"Voize","#0457":"Honor","#0458":"Inspiren","#0463":"Blooming Health",
"#0464":"CarePredict","#0465":"Cariloop","#0472":"IXI"}

order = ["#0037","#0032","#0471","#0564","#0861","#0959","#0457","#0458","#0463","#0464","#0465","#0472"]

enterprises=[]
for s in order:
    r=rec[s]; l=lib[s]; n=names[s]
    enterprises.append({
        "serial":s,
        "signal_strength":l["ss"],
        "info_score":l["info"],
        "diff_score":l["diff"],
        "copy_score":l["copy"],
        "research_value":l["rv"],
        "recommend":r["recommend"],
        "desc_cn":r["desc"],
        "payor_model":r["payor"],
        "business_tags_role":r["role"],
        "founded":r["founded"],
        "stage":r["stage"],
        "funding_latest":l["fl"],
        "funding_total":l["ft"],
        "investors":l["inv"],
        "highlights":l["hl"],
        "events":l["ev"],
        "update_time":"2026-07-17",
        "silver_verdict":r["silver"],
        "silver_reason":r["silver_reason"],
    })

# tag_review
tag_review=[
 {"serial":"#0037","name":"远也","intro":"哈佛、MIT团队创立的柔性外骨骼（肌肉外甲）研发商，以AI预测动作意图为老人与康复人群提供助行增能，已从医疗康复拓展至消费级助行产品。",
  "old_tags":{"tag_l1":["康复辅具"],"tag_l2":["外骨骼","助行器","可穿戴监测"],"business_tags":{"customer":"B2C","role":"产品商","channel":[]}},
  "suggested":[{"action":"add","tag":"康复机器人","reason":"肌肉外甲属康复机器人范畴，现有标签未体现该品类属性"},{"action":"change","tag":"business_tags.customer→B2C+B2B","reason":"产品已进入40余家三甲医院，存在B端机构采购，当前仅标B2C"}]},
 {"serial":"#0032","name":"织生科技","intro":"以AI眼动追踪技术做脑健康认知筛查的国内企业，6分钟评估阿尔茨海默风险，已获三类医疗器械证并联合险企打通“检测-干预-保障”闭环。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["认知训练","认知筛查"],"business_tags":{"customer":"未标注","role":"服务商","channel":[]}},
  "suggested":[{"action":"add","tag":"数字生物标志物","reason":"企业自述核心为数字生物标志物产品，现标签未体现"},{"action":"change","tag":"business_tags.customer→B2B+B2C","reason":"已服务70+三甲医院与险企并面向个人早筛，当前标“未标注”"}]},
 {"serial":"#0471","name":"Homethrive","intro":"面向家庭照护者的支持平台，以AI加真人Care Guide为雇主与健康计划提供白标照护福利，覆盖从育儿到失能、临终的全周期照护。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["照护支持"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"add","tag":"员工福利","reason":"核心卖点是作为企业员工福利售卖，现标签未体现该场景"}]},
 {"serial":"#0564","name":"Papa","intro":"以“共享儿女”式非医疗陪伴连接陪伴者与老人的平台，通过健康计划与雇主福利免费提供，并借CMS痴呆项目做喘息照护。",
  "old_tags":{"tag_l1":["文娱社交"],"tag_l2":["陪伴服务"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l1 文娱社交→养老服务","reason":"本质是面向老人的陪伴照护平台，归文娱社交弱化了银发照护属性"}]},
 {"serial":"#0861","name":"Somatus","intro":"价值导向的肾病与心血管综合护理龙头，以RenalIQ预测分析与到家多学科团队延缓病程，按Medicare与健康计划的价值医疗合同收费。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["慢病管理"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"add","tag":"价值医疗(VBC)","reason":"按价值付费的慢病管理是其核心模式，现标签未体现"}]},
 {"serial":"#0959","name":"Voize","intro":"柏林AI语音护理记录助手，将护理员口述实时转为合规结构化病历，已落地德国1000余家养老机构，支持离线与企业EHR对接。",
  "old_tags":{"tag_l1":["行业服务"],"tag_l2":["养老软件"],"business_tags":{"customer":"B2B","role":"技术服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l2 养老软件→语音护理AI","reason":"产品核心是语音转结构化病历的AI，“养老软件”过泛"},{"action":"change","tag":"business_tags.role→服务商","reason":"原“技术服务商”不在白名单，应为服务商"}]},
 {"serial":"#0457","name":"Honor","intro":"技术驱动的居家护理网络平台（“滴滴护工”），连接护理员与家庭并输出技术底座，2021年收购Home Instead、网络覆盖14国。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["护工平台"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
  "suggested":[{"action":"add","tag":"居家护理","reason":"核心场景是居家护理供需匹配，现标签未体现"}]},
 {"serial":"#0458","name":"Inspiren","intro":"以AUGi环境感知设备为老年社区提供无感安全监护的AI公司，定位“护理智能基础设施”，18个月落地150余家社区。",
  "old_tags":{"tag_l1":["康复辅具"],"tag_l2":["跌倒监测"],"business_tags":{"customer":"B2B","role":"技术服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l1 康复辅具→养老服务","reason":"做老年社区无感监护而非康复辅具，分类错配"},{"action":"change","tag":"business_tags.role→服务商","reason":"原“技术服务商”不在白名单，应为服务商"}]},
 {"serial":"#0463","name":"Blooming Health","intro":"连接医疗保健提供者与社会服务组织的银发社区支持平台，为老人提供交通、送餐、社交等社会照护，覆盖21州700余家社区。",
  "old_tags":{"tag_l1":["文娱社交"],"tag_l2":["社区"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l1 文娱社交→养老服务","reason":"本质是面向老人的社会照护连接平台，归文娱社交偏弱"}]},
 {"serial":"#0464","name":"CarePredict","intro":"AI行为感知可穿戴（Tempo）公司，被动监测老人日常活动以提前预警健康恶化，住院率降39%、跌倒率降69%，正向Medicare Advantage拓展。",
  "old_tags":{"tag_l1":["康复辅具"],"tag_l2":["跌倒监测"],"business_tags":{"customer":"B2B","role":"技术服务商","channel":[]}},
  "suggested":[{"action":"change","tag":"tag_l1 康复辅具→养老服务","reason":"做老人健康行为监测而非康复辅具，分类错配"},{"action":"change","tag":"business_tags.role→服务商","reason":"原“技术服务商”不在白名单，应为服务商"}]},
 {"serial":"#0465","name":"Cariloop","intro":"为企业员工提供家庭照护支持的平台，帮助在职子女照护老年亲属以提升留任与福利，客户含宝洁、毕马威。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["照护支持"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"add","tag":"员工福利","reason":"以企业员工福利形式切入照护，现标签未体现该场景"}]},
 {"serial":"#0472","name":"IXI","intro":"研发全球首款自动对焦老花眼镜的芬兰硬件公司，以液晶镜片加眼动追踪实时变焦，2025年完成A轮、亚马逊参投，尚未商业化。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["眼镜"],"business_tags":{"customer":"B2B","role":"服务商(媒体/数据)","channel":[]}},
  "suggested":[{"action":"change","tag":"business_tags.role→产品商","reason":"本质是眼镜硬件产品商，原“服务商(媒体/数据)”明显错配"}]},
]

nonsilver=[]

out={"batch":10,"enterprises":enterprises,"tag_review":tag_review,"nonsilver":nonsilver}

# ---- self-check ----
errors=[]
for e in enterprises:
    s=e["serial"]; n=names[s]
    for k in ["info_score","diff_score","copy_score"]:
        v=e[k]
        if not (isinstance(v,(int,float)) and 0<=v<=10):
            errors.append(f"{s} {k}={v} 不在0~10")
    if not (isinstance(e["signal_strength"],(int,float)) and 0<=e["signal_strength"]<=10):
        errors.append(f"{s} signal_strength={e['signal_strength']} 不在0~10")
    if not (isinstance(e["research_value"],(int,float)) and 0<=e["research_value"]<=100):
        errors.append(f"{s} research_value={e['research_value']} 不在0~100")
    recs=e["recommend"]
    if not isinstance(recs,str): errors.append(f"{s} recommend非字符串")
    else:
        L=len(recs)
        if not (60<=L<=120): errors.append(f"{s} recommend长度{L} 不在60~120")
        for bad in ["融资","成立于","轮次"]:
            if bad in recs: errors.append(f"{s} recommend含禁用词'{bad}'")
        if n in recs: errors.append(f"{s} recommend复述了企业名")
    if e["stage"] not in WHITELIST_STAGE: errors.append(f"{s} stage={e['stage']} 不在白名单")
    if not e["payor_model"]: errors.append(f"{s} payor_model为空")
    for k in ["recommend","desc_cn","payor_model","business_tags_role","stage","founded","silver_verdict","silver_reason","update_time"]:
        if e.get(k) in (None,"",[]): errors.append(f"{s} 字段{k}为空")
    if len(e["desc_cn"])>30: errors.append(f"{s} desc_cn超30字({len(e['desc_cn'])})")
    if n in e["desc_cn"]: errors.append(f"{s} desc_cn含企业名")

print("自检错误数:", len(errors))
for x in errors: print("  ✗", x)
if not errors:
    print("✓ 全部自检通过")
    json.dump(out, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("已写入", OUT)
else:
    print("未写入，需先修正")
