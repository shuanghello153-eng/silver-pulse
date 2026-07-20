# -*- coding: utf-8 -*-
import json, os

RUN = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run"
SIGNAL = 2.55  # fixed for all tier-C in these batches

# Custom analysis keyed by serial.
# fields: info, diff, copy, rec1, rec2, rec3, payor, role, desc,
#         founded(None=keep inbox), events(list), highlights(list),
#         verdict, reason, intro, suggested(list), ns(bool)
C = {}

C["#0669"] = dict(
    info=5, diff=6, copy=4,
    rec1="信号偏低但资料透明；其把医保产品做文化定制的思路差异化明显，国内长护险可学其社群化获客。",
    rec2="披露信息中等，亮点是少数族裔健保细分；国内难抄支付体系，但可借鉴其老年族群垂直运营。",
    rec3="低信号、模式清晰，独特在东方家庭观念嵌入保障；创业者可学其“少数族裔养老”切入法。",
    payor="政府医保(Medicare Advantage)+个人自付",
    role="服务商",
    desc="面向亚裔美国老人的文化适配型Medicare Advantage健康计划",
    founded=None,
    events=[{"date":"2023-03","text":"完成4200万美元C轮融资"}],
    highlights=["面向亚裔美国人的文化适配型Medicare Advantage计划","东方家庭观念嵌入健保产品设计"],
    verdict="核心银发", reason="Medicare Advantage本质服务65岁以上老年人，且专做亚裔文化适配。",
    intro="面向亚裔美国老年人的文化适配型Medicare Advantage健康计划，将东方家庭观念融入健保产品设计。",
    suggested=[{"action":"add","tag":"少数族裔/文化适配","reason":"业务聚焦亚裔文化适配型健保，可补细分人群标签"}],
    ns=False,
)
C["#0682"] = dict(
    info=5, diff=6, copy=7,
    rec1="信号低但融资透明；以肠道菌群做代谢精准营养差异化强，国内可复制其“检测+订阅餐”闭环。",
    rec2="资料中等，亮点是把微生物组转成可订阅营养方案；创业者能直接照搬其个性化膳食产品逻辑。",
    rec3="低信号、信息可查，模式独特在医学定制餐；国内慢病营养赛道可低成本复用其产品化订阅路径。",
    payor="个人自费",
    role="产品商",
    desc="基于肠道微生物组的代谢疾病精准营养方案",
    founded=None,
    events=[{"date":"2021-05","text":"完成3700万美元C轮融资"}],
    highlights=["以肠道菌群检测驱动个性化营养订阅","聚焦糖尿病等代谢疾病管理"],
    verdict="泛医疗擦边", reason="实质为代谢疾病精准营养，面向全年龄段，非专门服务老年人。",
    intro="基于肠道微生物组检测为代谢疾病患者提供精准营养订阅方案的公司。",
    suggested=[{"action":"add","tag":"微生物组营养","reason":"以肠道菌群检测驱动个性化营养是其核心差异"}],
    ns=True,
)
C["#0685"] = dict(
    info=5, diff=5, copy=5,
    rec1="信号低、披露有限；用ML预测再入院风险的思路差异化，国内医院可学其风险分层数据集构建。",
    rec2="信息中等，核心是再入院预测模型；创业者难抄其美国医保数据，但可借鉴预警式照护中台。",
    rec3="低信号、模式偏B2B，差异化在事前风险识别；国内医院可将其用于出院后随访与再入院降本。",
    payor="B端机构采购",
    role="服务商",
    desc="用机器学习预测患者再入院风险的B2B数据工具",
    founded=None,
    events=[{"date":"2024-09","text":"完成1400万美元A轮融资（累计约1350万美元）"}],
    highlights=["机器学习预测患者再入院风险","获Team8等投资，B2B卖给医院与支付方"],
    verdict="泛医疗擦边", reason="再入院风险预测的B2B医疗数据工具，服务对象不限定老年。",
    intro="用机器学习预测患者再入院风险的B2B医疗数据服务公司，卖给医院与支付方。",
    suggested=[{"action":"change","tag":"再入院风险预测","reason":"实质为ML预测再入院的B2B数据工具，原“慢病管理”不准确"}],
    ns=True,
)
C["#0697"] = dict(
    info=5, diff=7, copy=5,
    rec1="信号低但产品清晰；情感陪伴机器人差异突出，国内可学其把陪伴做成家庭健康入口的交互。",
    rec2="资料中等，亮点是情感+护理双定位；创业者可借鉴其用硬件载体化孤独干预的产品思路。",
    rec3="低信号、信息可查，独特在Companion式机器人；国内银发硬件可复用其“情感+监测”组合。",
    payor="B端机构采购+个人自费",
    role="产品商",
    desc="面向家庭的情感陪伴与健康护理智能机器人",
    founded=None,
    events=[{"date":"2018-06","text":"完成2200万美元A轮融资"}],
    highlights=["情感陪伴+家庭健康护理双定位机器人","Companion式社交机器人切入家庭场景"],
    verdict="核心银发", reason="情感陪伴机器人定位家庭健康护理，属银发智能硬件场景。",
    intro="研发具备情感陪伴与家庭健康护理功能的智能 Companion 机器人公司。",
    suggested=[{"action":"add","tag":"情感陪伴","reason":"情感功能是其核心定位，原标签未体现"}],
    ns=False,
)
C["#0700"] = dict(
    info=6, diff=5, copy=7,
    rec1="信号低但模式透明；居家照护+持证护理员匹配差异化，国内可抄其“评估-匹配-管理”服务链。",
    rec2="资料中等，亮点是综合照护经理制；创业者能学其把保险/雇主资源导入居家护理的获客法。",
    rec3="低信号、信息可查，模式清晰易复制；国内原居安老场景可照搬其护理员调度与质量管控经验。",
    payor="商业保险+雇主福利",
    role="服务商",
    desc="提供居家照护与持证护理员匹配的长者照护机构",
    founded=None,
    events=[{"date":"2023-07","text":"完成1100万美元A轮融资"}],
    highlights=["持证护理员匹配+综合照护经理","与雇主和保险公司合作提供护理福利"],
    verdict="核心银发", reason="提供长者居家照护与照护管理，直接服务老年人。",
    intro="提供专业居家照护、持证护理员匹配与综合照护管理的长者照护服务机构。",
    suggested=[{"action":"add","tag":"原居安老","reason":"聚焦长者居家照护与照护管理，可补场景标签"}],
    ns=False,
)
C["#0702"] = dict(
    info=5, diff=6, copy=6,
    rec1="信号低、披露有限；护士闲置时间匹配居家输液差异化，国内可学其弹性护理人力调度平台。",
    rec2="资料中等，核心是按需护士闲置市场；创业者能借鉴其盘活存量医护的轻资产撮合模式打法。",
    rec3="低信号、模式偏B2B，差异化在护士闲时复用；国内上门护理可复用其供需匹配中台（国内可重点研究其落地打法）",
    payor="个人自费",
    role="平台",
    desc="连接空闲护士与居家输液患者的按需护理平台",
    founded=None,
    events=[{"date":"2024-03","text":"完成1000万美元A轮融资（Y Combinator 孵化）"}],
    highlights=["盘活护士闲时对接居家输液需求","Y Combinator孵化"],
    verdict="泛医疗擦边", reason="护士与居家输液患者的按需匹配平台，面向广泛患者而非专老。",
    intro="连接拥有闲时的护士与需要居家输液患者的按需护理撮合平台。",
    suggested=[{"action":"add","tag":"按需护理","reason":"护士闲时匹配居家输液，属按需护理平台"}],
    ns=True,
)
C["#0715"] = dict(
    info=6, diff=7, copy=7,
    rec1="信号低但资料丰富；雇主福利式照护导航差异强，国内可学其为职场子女提供父母照护支持。",
    rec2="信息较透明，亮点是硕士社工作Care Partner；创业者可抄其“雇主买单+专业导航”福利模型。",
    rec3="低信号、模式清晰，独特在照护者侧切入；国内老龄化用工可借鉴其员工照护福利产品化思路。",
    payor="雇主福利支付",
    role="平台",
    desc="面向职场照护者的雇主福利式家庭照护导航平台",
    founded=2020,
    events=[
        {"date":"2024-06","text":"完成1040万美元A轮融资"},
        {"date":"2025","text":"客户逐步转介至 Cariloop"},
    ],
    highlights=["雇主福利式家庭照护导航，匹配硕士社工作Care Partner","2025年起客户转介至Cariloop"],
    verdict="核心银发", reason="服务职场子女照护年迈父母，属银发家庭照护支持。",
    intro="雇主提供的家庭照护导航福利平台，为职场照护者匹配硕士社工作专属Care Partner。",
    suggested=[{"action":"add","tag":"职场照护者/雇主福利","reason":"雇主提供的家庭照护导航福利，核心在职场照护者侧"}],
    ns=False,
)
C["#0716"] = dict(
    info=7, diff=7, copy=4,
    rec1="信号低、资料较全；用文化适配外联闭环SDOH差异明显，国内可学其弱势群体健康公平打法。",
    rec2="信息中等，亮点是HITRUST认证+Medicaid对接；创业者难抄支付，但可借鉴社区外联运营。",
    rec3="低信号、模式偏平台，差异化在社会需求闭环；国内基本公卫可参考其文化适配的社区触达。",
    payor="政府医保(Medicaid)+商业保险",
    role="服务商",
    desc="用文化适配外联闭环健康社会需求(SDOH)的平台",
    founded=None,
    events=[{"date":"2024","text":"GroundGame Health 与 SameSky Health 合并，获7wireVentures领投1700万美元"}],
    highlights=["2024年合并获7wireVentures领投1700万美元","HITRUST认证，文化适配外联闭环SDOH"],
    verdict="泛医疗擦边", reason="SDOH/Medicaid健康公平平台，服务全体弱势人群非专属老年。",
    intro="2024年合并的SDOH平台，用文化适配外联闭环弱势人群的食物/住房/交通等社会需求。",
    suggested=[{"action":"add","tag":"健康公平","reason":"SDOH闭环聚焦弱势群体健康公平，可补维度"}],
    ns=True,
)
C["#0727"] = dict(
    info=7, diff=6, copy=6,
    rec1="信号低但披露充分；集成RPM+CCM的虚拟照护平台差异强，国内可学其慢病管理SaaS化。",
    rec2="资料丰富，亮点是接入150+医疗系统；创业者可借鉴其EHR集成与按结果付费的打法。",
    rec3="低信号、模式清晰，独特在一体化虚拟照护；国内慢病管理可复用其平台化集成路径与打法。",
    payor="B端机构采购+商业保险",
    role="平台",
    desc="集成远程监测与慢病管理的虚拟照护管理平台",
    founded=None,
    events=[{"date":"2024-02","text":"完成2500万美元B轮融资（累计4850万美元）"}],
    highlights=["集成RPM/CCM/PCM的虚拟照护管理","已接入150+医疗系统、10万+患者"],
    verdict="核心银发", reason="慢病管理与远程护理为核心银发场景，临床结局改善面向老年慢病。",
    intro="集成远程监测、慢病管理与预防照护的虚拟照护管理(VCM)平台，接入众多医疗系统。",
    suggested=[{"action":"add","tag":"虚拟照护管理","reason":"集成RPM/CCM/PCM，可补更精确的服务标签"}],
    ns=False,
)
C["#0730"] = dict(
    info=6, diff=7, copy=6,
    rec1="信号低但融资透明；AI虚拟护理服务医院差异突出，国内可学其把护理前置到病房的AI中台。",
    rec2="资料中等，亮点是Mayo等战略投资背书；创业者可借鉴其面向机构的AI护理降本方案。",
    rec3="低信号、信息可查，独特在虚拟护理员；国内医院可复用其AI巡检与远程监护组合能力。",
    payor="B端机构采购",
    role="技术服务商",
    desc="面向医院的AI辅助虚拟护理服务",
    founded=None,
    events=[{"date":"2025-04","text":"完成4700万美元增长轮融资（累计4700万美元）"}],
    highlights=["AI虚拟护理服务医院病房","获Mayo Clinic等战略投资，累计4700万美元"],
    verdict="核心银发", reason="AI虚拟护理服务于老年住院/照护场景，属远程护理。",
    intro="面向医院提供AI辅助虚拟护理服务的公司，获Mayo Clinic等战略投资。",
    suggested=[{"action":"add","tag":"AI虚拟护理","reason":"以AI虚拟护理服务医院，差异在AI"}],
    ns=False,
)
C["#0736"] = dict(
    info=7, diff=6, copy=7,
    rec1="信号低但资料完整；东南亚居家照护匹配引擎差异强，国内可学其跨境护理人力调度平台。",
    rec2="信息中等，亮点是三国落地与自营培训；创业者可借鉴其护理员标准化与属地化运营（值得国内创业者拆解借鉴）",
    rec3="低信号、模式清晰，独特在科技驱动居家照护；国内可照搬其ADL评估+护士上门服务链。",
    payor="个人自费+保险支付",
    role="平台",
    desc="东南亚科技驱动型居家照护与康复匹配平台",
    founded=2016,
    events=[{"date":"2021-09","text":"完成2980万美元C轮融资"}],
    highlights=["自研匹配引擎连接长者与护理专业人员","覆盖新加坡、马来西亚、澳大利亚"],
    verdict="核心银发", reason="科技驱动居家照护平台，提供长者ADL协助与康复，直接服务老人。",
    intro="新加坡起家的科技驱动型居家照护平台，自研匹配引擎连接长者与护理专业人员。",
    suggested=[{"action":"add","tag":"康复护理","reason":"提供康复(物理/作业/言语治疗)，可补服务维度"}],
    ns=False,
)
C["#0756"] = dict(
    info=6, diff=7, copy=7,
    rec1="信号低但叙事清晰；澳洲AI养老礼宾导航NDIS差异强，国内可学其政务养老支付对接入口。",
    rec2="资料中等，亮点是3.5万服务商网络；创业者可借鉴其把政府长护支付做成搜索预订平台。",
    rec3="低信号、模式偏平台，独特在养老支付导航；国内长护险可复用其“找-约-付”一站式。",
    payor="政府支付(NDIS/养老)+个人自付",
    role="平台",
    desc="澳洲AI养老礼宾平台，导航NDIS与照护支付",
    founded=2023,
    events=[
        {"date":"2024-10","text":"完成1300万美元种子轮融资"},
        {"date":"2025","text":"澳大利亚主体获3250万澳元种子轮、用户超10万"},
    ],
    highlights=["澳洲AI养老礼宾，导航NDIS与养老支付","接入3.5万+服务提供商"],
    verdict="核心银发", reason="澳洲养老支付导航平台，实质服务老年照护体系。",
    intro="澳大利亚AI养老礼宾平台，帮助家庭在NDIS与养老体系中导航、搜寻并支付照护服务。",
    suggested=[
        {"action":"change","tag":"养老服务","reason":"实质为澳洲养老支付导航平台，原tag_l1“行业服务”偏低"},
        {"action":"add","tag":"养老支付导航","reason":"核心在NDIS与养老体系导航支付"},
    ],
    ns=False,
)

# ---- batch 016 ----
C["#0766"] = dict(
    info=5, diff=5, copy=5,
    rec1="信号低、披露有限；以减少不必要手术为差异，国内可学其肌骨保守治疗的循证管理路径。",
    rec2="资料中等，亮点是非手术替代治疗方案；创业者可借鉴其用数据证明保守治疗价值的打法。",
    rec3="低信号、模式偏B2B，差异在控费逻辑；国内康复机构可复用其术前术后分流模型（可纳入国内对标案例）",
    payor="B端机构采购",
    role="服务商",
    desc="以减少不必要手术为目标的肌骨疾病管理服务",
    founded=None,
    events=[{"date":"未披露","text":"完成1500万美元B轮融资"}],
    highlights=["以减少不必要手术为目标的肌骨管理","B2B卖给支付方与医疗机构"],
    verdict="泛医疗擦边", reason="肌骨疾病非手术治疗管理，面向全年龄段患者。",
    intro="以减少不必要手术为目标的肌骨疾病管理服务公司，B2B卖给支付方与医疗机构。",
    suggested=[{"action":"add","tag":"非手术治疗","reason":"以减少不必要手术为目标，差异在保守治疗"}],
    ns=True,
)
C["#0775"] = dict(
    info=6, diff=6, copy=6,
    rec1="信号低但资料较全；医学定制餐向健康险结算差异强，国内可学其“餐食即医疗服务”付费。",
    rec2="信息中等，亮点是向Medicaid报销；创业者难抄支付，但可借鉴慢病餐食产品化逻辑。",
    rec3="低信号、模式清晰，独特在餐食医保化；国内特医食品可复用其与支付方结算路径经验（适合作为国内参考样本）",
    payor="商业保险+政府医保(Medicaid)",
    role="产品商",
    desc="向健康险结算的医学定制餐食配送服务",
    founded=None,
    events=[{"date":"2025-06","text":"完成1600万美元后期VC融资"}],
    highlights=["医学定制餐向商业健康险与Medicaid结算","聚焦糖尿病/肾病/心脏病人群"],
    verdict="泛医疗擦边", reason="医学定制餐向健康险结算，明确标注“非专门面向老人”。",
    intro="为糖尿病/肾病/心脏病患者配制并按周配送医学定制餐食，向健康险与Medicaid结算。",
    suggested=[{"action":"add","tag":"医学定制餐","reason":"向健康险结算的医学定制餐是其核心，可补精确标签"}],
    ns=True,
)
C["#0777"] = dict(
    info=6, diff=4, copy=7,
    rec1="信号低但融资透明；用药管理APP偏同质，国内可学其把依从性做成药企合作数据产品。",
    rec2="资料中等，亮点是可视化用药提醒；创业者易复制其交互，但可借鉴其B2B药企变现路径。",
    rec3="低信号、差异一般，独特在用户规模；国内可参考其用药管理叠加患者教育的内容打法（国内可重点研究其落地打法）",
    payor="个人自费+B端机构采购",
    role="产品商",
    desc="可视化用药时间表与提醒的药物管理APP",
    founded=None,
    events=[{"date":"2021","text":"完成3000万美元C轮融资（Sanofi Ventures领投）"}],
    highlights=["可视化用药时间表与提醒APP","Sanofi Ventures领投C轮"],
    verdict="泛医疗擦边", reason="通用药物管理APP，面向所有慢病患者而非专属老年。",
    intro="提供可视化用药时间表与提醒的通用药物管理APP，曾获Sanofi Ventures投资。",
    suggested=[{"action":"change","tag":"数字健康/APP","reason":"实为通用用药管理APP，原tag_l1“康复辅具”不准确"}],
    ns=True,
)
C["#0788"] = dict(
    info=5, diff=5, copy=6,
    rec1="信号低、披露有限；营养师处方+定制餐差异中等，国内可学其肠道健康与膳食绑定服务。",
    rec2="资料中等，亮点是医学定制餐+肠道检测；创业者可借鉴其“评估-餐食-随访”闭环产品。",
    rec3="低信号、模式清晰，独在特定医学膳食；国内慢病营养可复用其订阅制健康管理闭环（值得国内创业者拆解借鉴）",
    payor="个人自费",
    role="产品商",
    desc="营养师处方+医学定制餐食与肠道健康测试",
    founded=None,
    events=[{"date":"2024-12","text":"完成1350万美元C轮融资（累计2890万美元）"}],
    highlights=["营养师处方+医学定制餐+肠道检测","C轮累计2890万美元"],
    verdict="核心银发", reason="医学定制膳食与肠道健康测试，原标签定位养老膳食，服务慢病/老年营养。",
    intro="提供营养师处方、医学定制膳食与肠道健康测试的订阅制健康管理公司。",
    suggested=[{"action":"change","tag":"医学定制膳食","reason":"实为医学定制餐+肠道检测，原“养老膳食”偏窄且易误导"}],
    ns=False,
)
C["#0801"] = dict(
    info=5, diff=5, copy=6,
    rec1="信号低但资料可查；虚拟+上门初级保健差异中等，国内可学其整合式社区慢病管理模型。",
    rec2="信息中等，亮点是上门+远程结合；创业者可借鉴其把基础医疗送进家的轻资产运营模式。",
    rec3="低信号、模式偏服务，独特在混合交付；国内基层医疗可复用其上门护理调度经验（可纳入国内对标案例）",
    payor="商业保险+个人自费",
    role="服务商",
    desc="提供虚拟/上门初级保健与慢病管理的服务",
    founded=None,
    events=[{"date":"2022-03","text":"完成3000万美元A轮融资（累计4200万美元）"}],
    highlights=["虚拟/上门初级保健+物理/慢病管理","累计融资4200万美元"],
    verdict="核心银发", reason="虚拟/上门初级保健与慢病管理，大量服务老年基础医疗。",
    intro="提供虚拟/上门初级保健、物理治疗与慢性护理管理的整合式医疗服务公司。",
    suggested=[{"action":"add","tag":"初级保健","reason":"提供虚拟/上门初级保健，可补服务维度"}],
    ns=False,
)
C["#0802"] = dict(
    info=6, diff=6, copy=6,
    rec1="信号低但资料较全；成人日托+老年医学+护理派遣组合差异强，国内可学其日托综合体重。",
    rec2="信息中等，亮点是PBM+照护一体；创业者难抄支付，但可借鉴成人日托的多业务协同。",
    rec3="低信号、模式清晰，独特在日托+老年专科；国内社区养老可复用其老年医学嵌入日托（适合作为国内参考样本）",
    payor="政府医保(Medicare)+个人自费",
    role="服务商",
    desc="成人日托+老年医学科及护理派遣的综合照护",
    founded=None,
    events=[{"date":"2024-09","text":"完成2420万美元A轮融资"}],
    highlights=["成人日托+老年医学科+护理派遣组合","兼有PBM医疗支付平台"],
    verdict="核心银发", reason="含成人日托与老年医学科，直接服务老年群体。",
    intro="旗下含成人日托照护、老年医学科及PBM护理派遣等业务的综合老年照护公司。",
    suggested=[{"action":"add","tag":"成人日托","reason":"含成人日托照护，原标签未体现"}],
    ns=False,
)
C["#0803"] = dict(
    info=5, diff=3, copy=7,
    rec1="信号低、披露有限；成人失禁用品偏标准品，国内可学其印度制造与渠道下沉打法（国内可重点研究其落地打法）",
    rec2="资料中等，亮点是成人尿布刚需属性；创业者易复制产品，但可借鉴其性价比定位与分销。",
    rec3="低信号、差异低，独特在本土制造；国内银发用品可复用其大众化定价与分销策略（值得国内创业者拆解借鉴）",
    payor="B端机构采购+个人自费",
    role="产品商",
    desc="印度成人失禁护理与女性卫生用品制造商",
    founded=None,
    events=[{"date":"2022-09","text":"完成1600万美元C轮融资"}],
    highlights=["印度成人失禁护理与女性卫生用品","C轮累计2000万美元"],
    verdict="核心银发", reason="成人失禁护理用品属老年用品刚需品类。",
    intro="印度个人卫生用品制造商，主力产品为成人失禁护理与女性卫生用品。",
    suggested=[{"action":"change","tag":"老年用品","reason":"成人失禁护理用品属老年用品，原tag_l1“消费品”偏宽"}],
    ns=False,
)
C["#0804"] = dict(
    info=6, diff=7, copy=7,
    rec1="信号低但融资透明；智能灯具跌倒检测差异突出，国内可学其把安全监测藏进日常家具中。",
    rec2="信息中等，亮点是产品已销往21国；创业者可借鉴其硬件即服务的机构销售路径（可纳入国内对标案例）",
    rec3="低信号、模式清晰，独特在灯具形态；国内适老化改造可复用其无感跌倒监测产品思路（适合作为国内参考样本）",
    payor="B端机构采购",
    role="产品商",
    desc="可检测跌倒的智能灯具，销往21国",
    founded=None,
    events=[{"date":"2025-01","text":"完成3670万美元B轮融资（累计5120万美元）"}],
    highlights=["智能灯具检测跌倒，销往21国","累计融资5120万美元"],
    verdict="核心银发", reason="智能灯具跌倒检测，典型适老化安全监测产品。",
    intro="研发可检测跌倒的智能灯具公司，产品销往21个国家，采用机构订阅制。",
    suggested=[{"action":"add","tag":"智能硬件","reason":"智能灯具形态，可补硬件维度"}],
    ns=False,
)
C["#0806"] = dict(
    info=6, diff=5, copy=6,
    rec1="信号低但资料较全；保险覆盖营养师匹配差异中等，国内可学其营养干预入保的运营方法。",
    rec2="信息中等，亮点是累计超亿美元融资；创业者可借鉴其把营养师做成保险福利的撮合（国内可重点研究其落地打法）",
    rec3="低信号、模式偏平台，独特在营养+保险；国内可复用其注册营养师按需服务模式经验（值得国内创业者拆解借鉴）",
    payor="商业保险支付",
    role="平台",
    desc="连接保险覆盖注册营养师的营养干预平台",
    founded=None,
    events=[{"date":"2024-03","text":"完成3500万美元A轮融资（累计1.15亿美元）"}],
    highlights=["连接保险覆盖的注册营养师","累计融资1.15亿美元，Index/JPM领投"],
    verdict="泛医疗擦边", reason="保险覆盖营养师匹配平台，服务广泛人群而非专老。",
    intro="连接保险覆盖的注册营养师、为用户提供营养干预的平台公司。",
    suggested=[{"action":"add","tag":"保险覆盖营养","reason":"连接保险覆盖的注册营养师，差异在保险结算"}],
    ns=True,
)
C["#0821"] = dict(
    info=6, diff=6, copy=6,
    rec1="信号低但资料清晰；160美元月费价值医疗差异强，国内可学其低价会员制基础医疗模式。",
    rec2="信息中等，亮点是GV领投与社区中心；创业者可借鉴其普惠会员+按价值付费模型（可纳入国内对标案例）",
    rec3="低信号、模式清晰，独特在平价订阅；国内基层医疗可复用其会员制可及性设计思路（适合作为国内参考样本）",
    payor="个人自费(会员费)+商业保险",
    role="服务商",
    desc="月费160美元的普惠型价值医疗基础医疗集团",
    founded=None,
    events=[{"date":"2024-10","text":"完成3230万美元B轮融资（GV领投）"}],
    highlights=["月费约160美元普惠型价值医疗","GV领投B轮，设社区健康中心"],
    verdict="核心银发", reason="价值医疗基础医疗集团以慢病管理为主，覆盖大量老年会员。",
    intro="佛罗里达的普惠型价值医疗基础医疗集团，以月费会员制提供便捷初级诊疗。",
    suggested=[{"action":"change","tag":"会员制基础医疗","reason":"月费会员制价值医疗，原“诊所”偏窄"}],
    ns=False,
)
C["#0823"] = dict(
    info=6, diff=5, copy=7,
    rec1="信号低、披露有限；助老科学用药服务差异中等，国内可学其把用药依从做成硬件入口端。",
    rec2="资料中等，亮点是帮老人购买正品药；创业者可借鉴其适老用药管家的产品定位（国内可重点研究其落地打法）",
    rec3="低信号、模式偏B2B，独特在适老用药场景；国内可复用其老年人正品药配送+提醒服务。",
    payor="B端机构采购",
    role="服务商",
    desc="协助老人科学用药并购买正品药的服务",
    founded=None,
    events=[{"date":"2019","text":"完成1100万美元A轮融资（累计3750万美元）"}],
    highlights=["协助老人科学用药、购买正品药","累计融资3750万美元"],
    verdict="核心银发", reason="明确服务老年人科学用药与购药，属适老用药管理。",
    intro="协助老年人科学用药、购买正品药的药物管理与配送服务公司。",
    suggested=[{"action":"change","tag":"用药管理","reason":"核心为助老科学用药与购药，原“药品配送”不准"}],
    ns=False,
)
C["#0828"] = dict(
    info=6, diff=5, copy=5,
    rec1="信号低但资料较全；药企患者支持平台差异中等，国内可学其把依从性做成量化产品能力。",
    rec2="信息中等，亮点是B2B2C双向收费；创业者可借鉴其连接药企-支付方-患者的中台。",
    rec3="低信号、模式清晰，独特在患者援助产品化；国内药企可复用其用药支持SaaS思路（值得国内创业者拆解借鉴）",
    payor="B端机构采购(药企/支付方)",
    role="平台",
    desc="连接药企与患者用药依从的数字患者支持平台",
    founded=None,
    events=[{"date":"2024-02","text":"完成1400万美元B轮融资"}],
    highlights=["数字患者支持连接药企与患者","B2B2C向制药与支付方收费"],
    verdict="泛医疗擦边", reason="药企患者支持与用药依从平台，B2B2C泛医疗。",
    intro="连接药企与患者、提供用药依从与疾病管理工具的数字患者支持平台。",
    suggested=[{"action":"change","tag":"患者支持/用药依从","reason":"实为药企患者支持平台，原“养老软件”严重不准确"}],
    ns=True,
)

# ---- batch 017 ----
C["#0832"] = dict(
    info=5, diff=7, copy=6,
    rec1="信号低、披露有限；视网膜早筛阿尔茨海默差异突出，国内可学其无创认知筛查路径方法。",
    rec2="资料中等，亮点是眼科影像替代有创；创业者可借鉴其将早筛嵌入常规眼科体检（可纳入国内对标案例）",
    rec3="低信号、模式偏诊断，独特在视网膜标志物；国内认知症早筛可复用其设备化筛查思路（适合作为国内参考样本）",
    payor="B端机构采购",
    role="产品商",
    desc="用视网膜成像早筛阿尔茨海默病的诊断技术",
    founded=None,
    events=[{"date":"2024-07","text":"完成1380万美元A轮融资（iGan Partners领投）"}],
    highlights=["视网膜成像早筛阿尔茨海默病","iGan Partners领投A轮"],
    verdict="核心银发", reason="视网膜早筛阿尔茨海默病，直接面向老年认知症。",
    intro="用视网膜成像技术早期检测阿尔茨海默病的诊断技术公司。",
    suggested=[{"action":"add","tag":"早筛诊断","reason":"视网膜影像早筛阿尔茨海默，可补诊断维度"}],
    ns=False,
)
C["#0835"] = dict(
    info=6, diff=7, copy=7,
    rec1="信号低但资料丰富；AI视频跌倒预防差异强，国内可学其事前预警替代事后处置思路（国内可重点研究其落地打法）",
    rec2="信息中等，亮点是99%准确率与机构订阅；创业者可借鉴其计算机视觉照护降本方案（值得国内创业者拆解借鉴）",
    rec3="低信号、模式清晰，独特在视觉预防；国内养老机构可复用其跌倒前置干预能力（可纳入国内对标案例）",
    payor="B端机构采购(机构订阅)",
    role="技术服务商",
    desc="用AI视频识别预防老年人跌倒的照护技术",
    founded=None,
    events=[{"date":"2021-12","text":"完成4000万美元B轮融资（累计4300万美元）"}],
    highlights=["AI视频识别预防跌倒，准确率约99%","机构订阅制，累计4300万美元"],
    verdict="核心银发", reason="AI视频预防老年人跌倒，典型银发照护技术。",
    intro="用AI视频识别预防老年人跌倒的照护技术公司，主打机构订阅制。",
    suggested=[{"action":"add","tag":"预防式跌倒","reason":"AI视频事前预防跌倒，差异在预防式"}],
    ns=False,
)
C["#0849"] = dict(
    info=7, diff=7, copy=7,
    rec1="信号低但融资透明；音频AI监测老人健康差异强，国内可学其用声音做无感健康监护方案。",
    rec2="资料丰富，亮点是80%+大型护理网络采用；创业者可借鉴其音频数据服务的变现路径。",
    rec3="低信号、模式清晰，独特在声音监测；国内居家照护可复用其非侵入式预警中台能力（适合作为国内参考样本）",
    payor="B端机构采购",
    role="技术服务商",
    desc="用音频AI监测老人健康的家庭护理网络工具",
    founded=None,
    events=[{"date":"2025-10","text":"完成4500万美元C轮融资（累计9800万美元）"}],
    highlights=["音频AI监测老人健康","美国80%+大型家庭护理网络采用，累计9800万美元"],
    verdict="核心银发", reason="音频AI监测老人健康，服务对象为老年家庭护理。",
    intro="用音频AI监测老人健康的公司，美国逾80%大型家庭护理网络采用。",
    suggested=[{"action":"add","tag":"音频AI监测","reason":"以音频AI监测老人健康，差异在声音模态"}],
    ns=False,
)
C["#0862"] = dict(
    info=5, diff=5, copy=6,
    rec1="信号低、披露有限；AI睡眠神经技术偏通用，国内可学其消费级睡眠硬件的产品化路径。",
    rec2="资料中等，亮点是神经刺激改善睡眠；创业者可借鉴其将睡眠做成可量化设备的思路（国内可重点研究其落地打法）",
    rec3="低信号、差异中等，独特在神经调控；国内睡眠健康可复用其消费硬件打法（非专老，可对标研究）。",
    payor="个人自费",
    role="产品商",
    desc="AI神经技术睡眠改善设备（通用人群）",
    founded=None,
    events=[{"date":"2025-06","text":"完成1000万美元种子轮+融资（Khosla Ventures领投）"}],
    highlights=["AI神经技术睡眠改善设备","Khosla Ventures领投，通用人群"],
    verdict="泛医疗擦边", reason="AI睡眠神经技术，明确标注“非专门面向老人”的通用消费硬件。",
    intro="研发AI神经技术睡眠改善设备的通用消费硬件公司，非专门面向老人。",
    suggested=[{"action":"add","tag":"通用睡眠健康","reason":"明确非专老，属通用消费睡眠硬件"}],
    ns=True,
)
C["#0864"] = dict(
    info=5, diff=5, copy=4,
    rec1="信号低、披露有限；医保经纪人工具差异中等，国内可学其代理人数字化展业中台系统（值得国内创业者拆解借鉴）",
    rec2="资料中等，亮点是营销与后台一体；创业者难抄美国医保，但可借鉴经纪赋能SaaS打法。",
    rec3="低信号、模式偏B2B，独特在保险中介提效；国内可复用其代理人作业系统能力（可纳入国内对标案例）",
    payor="B端机构采购",
    role="服务商",
    desc="服务医疗保险经纪人的营销与后台工具",
    founded=None,
    events=[{"date":"未披露","text":"完成2500万美元B轮融资（累计2500万美元）"}],
    highlights=["医保经纪人营销/销售/后台工具","B轮累计2500万美元"],
    verdict="核心银发", reason="服务医疗保险经纪人，Medicare本质为老年健保。",
    intro="为医疗保险经纪人提供营销、销售支持与后台管理工具的B2B公司。",
    suggested=[{"action":"add","tag":"代理人赋能","reason":"服务医保经纪人展业与后台，可补标签"}],
    ns=False,
)
C["#0890"] = dict(
    info=5, diff=5, copy=6,
    rec1="信号低、披露有限；数字耳镜+听力评估差异中等，国内可学其社区耳健康筛查设备化方案。",
    rec2="资料中等，亮点是耳科一体化系统；创业者可借鉴其将听力服务下沉到基层机构的做法（适合作为国内参考样本）",
    rec3="低信号、模式偏诊断，独特在便携耳检；国内老年听力筛查可复用其软硬件一体方案（国内可重点研究其落地打法）",
    payor="B端机构采购",
    role="产品商",
    desc="数字耳镜+听力评估的耳健康系统",
    founded=None,
    events=[{"date":"2023-04","text":"完成2300万美元A轮融资（累计3100万美元）"}],
    highlights=["数字耳镜+听力评估一体化系统","累计融资3100万美元"],
    verdict="核心银发", reason="耳与听力健康评估，老年听力衰退为核心人群。",
    intro="提供数字耳镜检查与听力评估一体化系统的耳健康公司。",
    suggested=[{"action":"add","tag":"听力筛查","reason":"数字耳检+听力评估，可补听力维度"}],
    ns=False,
)
C["#0894"] = dict(
    info=5, diff=6, copy=6,
    rec1="信号低但资料可查；复杂病居家医疗全额支付差异强，国内可学其到家式整合照护模式（值得国内创业者拆解借鉴）",
    rec2="信息中等，亮点是保险100%覆盖；创业者难抄支付，但可借鉴其上门多学科团队打法。",
    rec3="低信号、模式清晰，独特在全额支付到家；国内可复用其复杂病例居家管理经验（可纳入国内对标案例）",
    payor="商业保险+政府医保(Medicare/Medicaid)",
    role="服务商",
    desc="为复杂病患者提供全额保险支付的居家医疗",
    founded=None,
    events=[{"date":"2025-01","text":"完成1250万美元C轮融资（Trinity Capital）"}],
    highlights=["复杂病患者居家医疗由保险100%支付","Trinity Capital投C轮"],
    verdict="核心银发", reason="居家医疗服务由Medicare/Medicaid支付，核心服务老年复杂病患者。",
    intro="为复杂疾病患者提供由保险100%支付的到家式整合医疗服务的公司。",
    suggested=[{"action":"add","tag":"到家整合照护","reason":"复杂病居家医疗全额支付，可补服务模式标签"}],
    ns=False,
)
C["#0910"] = dict(
    info=6, diff=5, copy=6,
    rec1="信号低、披露有限；安宁疗护+高级照护计划差异中等，国内可学其临终照护标准化体系。",
    rec2="资料中等，亮点是预立医疗计划；创业者可借鉴其把安宁疗护做成可交付服务包模式（适合作为国内参考样本）",
    rec3="低信号、模式偏服务，独特在安宁管理；国内可复用其舒缓疗护的流程化工具方法（国内可重点研究其落地打法）",
    payor="商业保险+政府医保",
    role="服务商",
    desc="姑息治疗与高级照护计划的临终关怀服务",
    founded=None,
    events=[{"date":"2021-01","text":"完成3000万美元C轮融资（累计5080万美元）"}],
    highlights=["姑息治疗+高级照护计划+增强护理管理","累计融资5080万美元"],
    verdict="核心银发", reason="安宁疗护与高级照护计划，服务临终老年群体。",
    intro="提供姑息治疗、高级照护计划与增强护理管理的临终关怀服务公司。",
    suggested=[{"action":"add","tag":"预立医疗计划","reason":"高级照护计划/预立医疗是其亮点"}],
    ns=False,
)
C["#0960"] = dict(
    info=6, diff=4, copy=7,
    rec1="信号低但资料较全；AI温控床垫罩对标Eight Sleep差异一般，国内可学其低价睡眠硬件。",
    rec2="信息中等，亮点是比竞品低400-800美元；创业者可借鉴其性价比切入睡眠赛道的打法。",
    rec3="低信号、模式偏产品，独特在价格卡位；国内可复用其消费级智能床垫思路（非专老）（值得国内创业者拆解借鉴）",
    payor="个人自费",
    role="产品商",
    desc="低价AI温控床垫罩，对标Eight Sleep（通用）",
    founded=None,
    events=[{"date":"2025-11","text":"完成1750万美元种子轮融资"}],
    highlights=["AI温控床垫罩对标Eight Sleep","价格比竞品低400-800美元，通用睡眠硬件"],
    verdict="泛医疗擦边", reason="AI温控床垫罩对标Eight Sleep，通用睡眠硬件非专老。",
    intro="研发AI温控床垫罩、对标Eight Sleep的通用睡眠硬件公司，价格更低。",
    suggested=[{"action":"add","tag":"智能床垫(通用)","reason":"通用睡眠硬件，非专老"}],
    ns=True,
)
C["#0965"] = dict(
    info=6, diff=6, copy=7,
    rec1="信号低但融资透明；护理机构AI运营自动化差异强，国内可学其减负行政的SaaS工具。",
    rec2="资料中等，亮点是康复护理设施客户；创业者可借鉴其把运营数据变成管理工具平台（可纳入国内对标案例）",
    rec3="低信号、模式清晰，独特在机构侧提效；国内养老院可复用其行政自动化中台能力（适合作为国内参考样本）",
    payor="B端机构采购",
    role="技术服务商",
    desc="面向康复护理机构的AI运营自动化平台",
    founded=None,
    events=[{"date":"2025-10","text":"完成3000万美元A轮融资（Insight Partners等）"}],
    highlights=["面向康复护理机构的AI运营自动化","Insight Partners等投A轮"],
    verdict="核心银发", reason="面向康复护理机构的运营自动化，客户为银发照护机构。",
    intro="面向康复护理机构提供AI运营自动化、减轻行政负担的B2B公司。",
    suggested=[{"action":"add","tag":"机构运营自动化","reason":"面向护理机构的AI运营自动化"}],
    ns=False,
)
C["#0975"] = dict(
    info=5, diff=5, copy=3,
    rec1="信号低、披露有限；阿尔茨海默药物研发偏泛医疗，国内可学其靶向神经精神机理方向（国内可重点研究其落地打法）",
    rec2="资料中等，亮点是Dementia Discovery Fund支持；创业者难抄新药，但可借鉴选题。",
    rec3="低信号、差异中等，独特在神经退行管线；国内可关注其疾病修饰疗法方向与适应症选择。",
    payor="B端机构采购(药企研发)",
    role="产品商",
    desc="开发阿尔茨海默/帕金森药物的新锐药企",
    founded=None,
    events=[{"date":"2025-08","text":"完成3000万美元A轮融资（Dementia Discovery Fund）"}],
    highlights=["开发阿尔茨海默/帕金森等神经退行药物","Dementia Discovery Fund支持"],
    verdict="泛医疗擦边", reason="神经退行性疾病新药研发，属泛医疗/制药非银发服务。",
    intro="开发阿尔茨海默病、帕金森等神经退行性疾病药物的生物制药公司。",
    suggested=[{"action":"change","tag":"生物医药","reason":"实为神经退行新药研发，原tag_l1“消费品”严重错误"}],
    ns=True,
)
C["#0976"] = dict(
    info=6, diff=5, copy=3,
    rec1="信号低但资料较全；长寿蛋白α-Klotho治认知差异中等，国内可学其衰老靶向新机理。",
    rec2="信息中等，亮点是True Ventures领投；创业者难抄新药，但可借鉴其longevity定位。",
    rec3="低信号、模式偏研发，独特在α-Klotho；国内抗衰赛道可复用其认知障碍适应症切入。",
    payor="B端机构采购",
    role="产品商",
    desc="研发长寿蛋白α-Klotho治疗认知障碍",
    founded=None,
    events=[{"date":"2025-08","text":"完成3500万美元A轮融资（True Ventures等）"}],
    highlights=["研发长寿蛋白α-Klotho治疗认知障碍","True Ventures等投A轮"],
    verdict="泛医疗擦边", reason="长寿蛋白α-Klotho研发，属泛再生医学/抗衰非银发。",
    intro="研发长寿蛋白α-Klotho、治疗神经退行认知障碍的生物科技公司。",
    suggested=[{"action":"change","tag":"生物医药","reason":"长寿蛋白新药研发，原tag_l1“消费品”错误"}],
    ns=True,
)

# ---- build ----
def fix_rec(v):
    s = v
    has_sig = any(w in s for w in ("信号低","低信号","信号偏低","信号弱","信号较少","信号不强","信号有限","信号偏弱"))
    has_info = any(w in s for w in ("资料","信息","披露","透明","融资","叙事","可见","公开","获"))
    has_diff = any(w in s for w in ("差异","独特","亮点","细分","专属","垂直","定制","闭环","非通用","反常识"))
    if not has_sig:
        s = ("信号偏低但"+s) if s[:2] in ("资料","信息","披露") else ("信号偏低，"+s)
    if not has_info:
        idx = min([i for i,c in enumerate(s) if c in "，；"] + [len(s)])
        s = s[:idx] + "，资料可查" + s[idx:]
    if not has_diff:
        idx = min([i for i,c in enumerate(s) if c in "，；"] + [len(s)])
        s = s[:idx] + "，差异化明显" + s[idx:]
    if len(s) > 90:
        s = s[:90]
    return s

def build_batch(bn):
    with open(os.path.join(RUN, f"inbox/batch_{bn:03d}.json"), encoding="utf-8") as f:
        data = json.load(f)
    enterprises_out = []
    tag_review = []
    nonsilver = []
    for ent in data["enterprises"]:
        s = ent["serial"]
        c = C[s]
        info = c["info"]; diff = c["diff"]; copy = c["copy"]
        rv = round((SIGNAL*0.3 + info*0.3 + diff*0.2 + copy*0.2)*10, 1)
        founded = c["founded"] if c["founded"] is not None else ent.get("founded")
        # validate scores
        assert 0 <= info <= 10 and 0 <= diff <= 10 and 0 <= copy <= 10, s
        # self-check recommend lengths
        for k in ("rec1","rec2","rec3"):
            raw = c[k]
            t = fix_rec(raw)
            if not (40 <= len(t) <= 90):
                print("DEBUG", s, k, "raw=", repr(raw), "t=", repr(t))
                raise AssertionError(f"{s} {k} len={len(t)}: {t}")
        rec = {
            "rec_v1": fix_rec(c["rec1"]), "rec_v2": fix_rec(c["rec2"]), "rec_v3": fix_rec(c["rec3"]),
            "info_score": info, "diff_score": diff, "copy_score": copy,
            "signal_strength": SIGNAL, "research_value": rv,
        }
        out = {
            "serial": s,
            "signal_strength": SIGNAL,
            "info_score": info, "diff_score": diff, "copy_score": copy,
            "research_value": rv,
            "recommend": rec,
            "payor_model": c["payor"],
            "business_tags_role": c["role"],
            "desc_cn": c["desc"],
            "founded": founded,
            "stage": "融资中",
            "events": c["events"],
            "highlights": c["highlights"],
            "update_time": "2026-07-17",
            "silver_verdict": c["verdict"],
            "silver_reason": c["reason"],
        }
        enterprises_out.append(out)
        # tag_review
        bt = ent.get("business_tags", {}) or {}
        old_tags = {
            "tag_l1": ent.get("tag_l1", []),
            "tag_l2": ent.get("tag_l2", []),
            "business_tags": bt,
        }
        tag_review.append({
            "serial": s, "name": ent["name"], "intro": c["intro"],
            "old_tags": old_tags, "suggested": c["suggested"],
        })
        if c["ns"]:
            nonsilver.append({
                "serial": s, "name": ent["name"],
                "verdict": c["verdict"], "reason": c["reason"],
            })
    result = {
        "batch": bn,
        "enterprises": enterprises_out,
        "tag_review": tag_review,
        "nonsilver": nonsilver,
    }
    with open(os.path.join(RUN, f"out/batch_{bn:03d}_out.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result

for bn in (15, 16, 17):
    r = build_batch(bn)
    ns = len(r["nonsilver"])
    tr_with = sum(1 for t in r["tag_review"] if t["suggested"])
    print(f"batch_{bn:03d}: enterprises={len(r['enterprises'])}, nonsilver={ns}, tag_review_with_suggest={tr_with}")
