import json

def rv(s, i, d, c):
    return round((s*0.3 + i*0.3 + d*0.2 + c*0.2)*10, 1)

# (serial, name, signal, info, diff, copy, scores_block, completion, tag_review, nonsilver?)
# Build per enterprise.
E = []

def mk(serial, name, signal, info, diff, copy, recs, fill, tagl1, tagl2, bt):
    r = rv(signal, info, diff, copy)
    rec_obj = {
        "rec_v1": recs[0], "rec_v2": recs[1], "rec_v3": recs[2],
        "info_score": info, "diff_score": diff, "copy_score": copy,
        "signal_strength": signal, "research_value": r
    }
    ent = {
        "serial": serial,
        "signal_strength": signal,
        "info_score": info, "diff_score": diff, "copy_score": copy,
        "research_value": r,
        "recommend": rec_obj,
        "payor_model": fill["payor_model"],
        "business_tags_role": fill["role"],
        "desc_cn": fill["desc_cn"],
        "founded": fill["founded"],
        "stage": fill["stage"],
        "events": fill["events"],
        "highlights": fill["highlights"],
        "update_time": "2026-07-17",
        "silver_verdict": fill["verdict"],
        "silver_reason": fill["reason"]
    }
    E.append(ent)
    return {
        "serial": serial, "name": name,
        "intro": fill["intro"],
        "old_tags": {"tag_l1": tagl1, "tag_l2": tagl2, "business_tags": bt},
        "suggested": fill["suggested"]
    }

tag_reviews = []
nonsilver = []

# ---------- #0919 YgEia3 ----------
tr = mk("#0919", "YgEia3", 5.55, 6, 5, 4,
    [
     "信号中等但质地扎实：刚被PE全资收购印证模式价值。它把实验室健康检测打包成企业员工福利，差异化一般、国内体检红海难照搬，但机构级健康管理思路值得看。",
     "信息量尚可（有营收与收购记录）。亮点是企业健康检测的产品化，但同质化高、对国内创业者可抄性低；其价值在验证'检测即服务'的B端付费逻辑。",
     "虽非银发专属，信号稳健（5.55）且刚被收购。模式无强反共识、复制受本地体检格局制约；可学的是把科学检测嵌入企业福利的商业化路径。"
    ],
    {
     "intro": "企业科学健康检测公司，为雇主/机构员工提供实验室体检与个性化wellness项目，2025年被SHUAAA PE全资收购。",
     "payor_model": "B端机构采购（企业雇主员工健康福利）",
     "role": "服务商",
     "desc_cn": "企业科学健康检测商，为员工提供实验室体检与健康管理",
     "founded": 2012,
     "stage": "被收购",
     "events": [
        {"date":"2025-07", "text":"SHUAAA Private Equity 完成全资收购，交易额约£6.82亿"},
        {"date":"2023-05", "text":"据库内记录完成私募股权融资（约£4.83亿）"}
     ],
     "highlights": [
        "企业级科学健康检测（员工实验室体检与wellness项目）",
        "2025年7月被SHUAAA Private Equity全资收购（约£6.82亿）",
        "服务企业、职业球队与高校，YgEia3 Sports 独立运营"
     ],
     "verdict": "泛医疗擦边",
     "reason": "主营企业员工科学健康检测，非专门面向老年人群",
     "suggested": [
        {"action":"change","tag":"消费品","reason":"实为健康检测/企业wellness公司，非消费品，建议改健康服务"},
        {"action":"change","tag":"服务商(媒体/数据)","reason":"业务为健康检测服务而非媒体/数据，role建议改服务商"},
        {"action":"add","tag":"企业健康","reason":"补'企业健康/员工福利'维度以反映B端定位"}
     ]
    },
    ["消费品"], ["体检筛查"],
    {"customer":"B2B","role":"服务商(媒体/数据)","channel":[]}
)
tag_reviews.append(tr)
nonsilver.append({"serial":"#0919","name":"YgEia3","verdict":"泛医疗擦边","reason":"主营企业员工科学健康检测，非专门面向老年人群"})

# ---------- #1197 太医管家 ----------
tr = mk("#1197", "太医管家", 5.55, 7, 6, 7,
    [
     "信号与信息量都不错（9.2亿战略轮+家庭医生入口）。差异化在'管理式医疗'整合，对国内创业者可抄性高——其以家庭医生撬动长期健康管理的路径值得拆解。",
     "作为本土平台信号扎实、信息丰厚度高。模式把优质医疗资源做成一站式管理，不算颠覆但极适合国情，国内创业者可直接借鉴其B2B2C运营打法。",
     "9.2亿融资背书、信息透明。差异化中等（家庭医生+管理式医疗），可复制性强：国内医保控费与慢病管理趋势下，这套打法有高借鉴价值。"
    ],
    {
     "intro": "以家庭医生为入口的一站式管理式医疗服务平台，汇集优质医疗资源，获上海国际资管等9.2亿元战略轮融资。",
     "payor_model": "混合支付（个人自费+商业保险+机构采购）",
     "role": "平台",
     "desc_cn": "家庭医生入口的一站式管理式医疗平台",
     "founded": 2020,
     "stage": "融资中",
     "events": [
        {"date":"2024", "text":"获9.2亿元战略轮融资（上海国际资管等参与）"}
     ],
     "highlights": [
        "9.2亿元战略轮融资",
        "以家庭医生为入口的管理式医疗",
        "汇集优质医疗资源的一站式健康管理平台"
     ],
     "verdict": "核心银发",
     "reason": "家庭医生+管理式医疗直接服务老年人群健康管理",
     "suggested": [
        {"action":"change","tag":"金融保险","reason":"实为家庭医生+管理式医疗平台，非金融业务，建议改健康服务"},
        {"action":"change","tag":"金融理财","reason":"业务为医疗服务非理财，建议改家庭医生/慢病管理"}
     ]
    },
    ["金融保险"], ["金融理财"],
    {"customer":"B2B+B2C","role":"平台","channel":[]}
)
tag_reviews.append(tr)

# ---------- #1310 AIM ----------
tr = mk("#1310", "AIM", 5.55, 4, 7, 8,
    [
     "信号中等但信息偏少（仅榜单来源）。亮在用既有X光/CT做老年慢病早筛、部署极低成本，差异化清晰，对国内基层'设备闲置+老年筛查'可抄性极高。",
     "虽公开资料有限，模式却很巧：不买新设备、复用现有影像做骨质疏松/心血管早筛。差异化强、国内县乡医院可直接套用，创业者值得重点研究。",
     "信息量低但信号有效（5.55）。核心差异是'影像复用'降本，复制门槛低——国内基层老龄化早筛刚需强，这套轻量方案比重资产路线更可学。"
    ],
    {
     "intro": "台湾AI医疗影像公司，分析既有胸部X光与CT，早期筛查老年人骨质疏松、心血管等慢性病，获1.25亿新台币种子融资。",
     "payor_model": "B端机构采购（医院/影像中心）",
     "role": "技术服务商",
     "desc_cn": "台湾AI医学影像公司，用既有X光/CT早筛老年慢病",
     "founded": 2020,
     "stage": "融资中",
     "events": [
        {"date":"2020", "text":"成立於台北，获1.25亿新台币种子融资"}
     ],
     "highlights": [
        "用既有X光/CT做老年骨质疏松/心血管早筛，部署成本低",
        "获1.25亿新台币种子融资（WI Harper等）",
        "对国内基层老年疾病早筛具强借鉴价值"
     ],
     "verdict": "核心银发",
     "reason": "专注老年人骨质疏松、心血管等慢性病早期筛查",
     "suggested": [
        {"action":"change","tag":"消费品","reason":"AI医学影像公司，非消费品，建议改智能诊断/健康服务"},
        {"action":"add","tag":"老年健康","reason":"专注老年骨质疏松/心血管早筛，应补老年健康维度"},
        {"action":"change","tag":"未标注","reason":"客户应为B2B（医院/影像中心），补customer"}
     ]
    },
    ["消费品","行业服务"], ["心血管","AI医疗"],
    {"customer":"未标注","role":"技术服务商","channel":[]}
)
tag_reviews.append(tr)

# ---------- #1317 PointClickCare ----------
tr = mk("#1317", "PointClickCare", 5.55, 7, 6, 6,
    [
     "信号稳健、信息公开度中高（头部LTC SaaS）。差异化在打通临床/财务/运营的养老信息化闭环，国内养老机构数字化可直接对标其数据结构与付费逻辑。",
     "北美长期照护EHR龙头，信息量足。模式成熟不颠覆，但对国内'养老信息化'是现成范本；其把照护数据变成运营资产的做法值得抄。",
     "信号尚可（5.55）、资料较全。差异化中等但极具参照价值，国内养老机构SaaS仍碎片化，可学其一体化平台与机构订阅的商业化路径。"
    ],
    {
     "intro": "面向长期照护与急性期后护理机构的云端EHR/SaaS平台，打通临床、财务与运营数据，北美长期照护信息化头部企业。",
     "payor_model": "B端机构采购（养老机构/护理机构订阅）",
     "role": "服务商",
     "desc_cn": "北美长期照护云端EHR/SaaS平台",
     "founded": 1995,
     "stage": "融资中",
     "events": [
        {"date":"2026-05", "text":"扩展AI产品Chart Advisor至senior living场景"}
     ],
     "highlights": [
        "北美长期照护领域头部EHR/SaaS",
        "累计融资约2.97亿加元",
        "2026年扩展AI产品至养老社区场景"
     ],
     "verdict": "核心银发",
     "reason": "长期照护信息化平台，直接服务养老机构与老年护理",
     "suggested": [
        {"action":"add","tag":"养老服务","reason":"长期照护SaaS，应补养老服务一级标签"},
        {"action":"change","tag":"未标注","reason":"客户为B2B养老机构/护理机构，补customer"}
     ]
    },
    ["行业服务"], ["养老软件"],
    {"customer":"未标注","role":"服务商","channel":[]}
)
tag_reviews.append(tr)

# ---------- #0791 Monogram Health ----------
tr = mk("#0791", "Monogram Health", 5.05, 7, 5, 4,
    [
     "信号与信息都强（15条新闻、年收入22亿美元）。居家慢病护理模式清晰但深绑美国Medicare Advantage，差异化一般、国内支付环境不同难直接平移。",
     "公开资料丰富、信号扎实。亮点在把慢病护理送进家门并绑定保险方，但强依赖美国医保体系，对国内创业者可抄性低，重点学其风险分层思路。",
     "信息量高、信号5.05。模式服务老年MA人群、规模化明显，差异化不突出；复制受本地支付方缺位制约，可借鉴其'护理+支付'协同框架。"
    ],
    {
     "intro": "美国多种慢性疾病居家护理公司，主要服务Medicare Advantage人群，2023年收入近22亿美元，获TPG等3.75亿美元C轮。",
     "payor_model": "政府医保(Medicare Advantage)+商业保险支付",
     "role": "服务商",
     "desc_cn": "美国慢病居家护理公司，服务Medicare Advantage人群",
     "founded": 2017,
     "stage": "融资中",
     "events": [
        {"date":"2023", "text":"完成3.75亿美元C轮融资"},
        {"date":"2025-03", "text":"与Memorial Hermann启动合资企业"}
     ],
     "highlights": [
        "2023年收入近22亿美元",
        "服务全美超30% MA会员",
        "与CVS Health、Humana等保险方深度合作"
     ],
     "verdict": "核心银发",
     "reason": "面向老年Medicare Advantage人群的慢病居家护理",
     "suggested": [
        {"action":"add","tag":"慢病管理","reason":"核心为慢病/多发病居家护理，建议补二级标签"}
     ]
    },
    ["养老服务"], ["专业护理","居家护理"],
    {"customer":"B2B+B2C","role":"平台","channel":[]}
)
tag_reviews.append(tr)

# ---------- #0853 Sidecar Health ----------
tr = mk("#0853", "Sidecar Health", 5.05, 7, 8, 3,
    [
     "信号中等但信息扎实（D轮+独角兽）。'去网络、透明定价、会员分润'极具反共识，但深植美国雇主健康险，国内支付结构差异大、直接平移难度高。",
     "信息丰厚度高，差异化极强：用Visa卡直付打破HMO网络限制。可抄性低——我国缺乏雇主直付福利与透明定价土壤，但其分润机制设计值得研究。",
     "信号5.05、公开材料充分。最大亮点是最颠覆的传统保险逻辑，但受牌照与医保体系强约束，国内难复制；可学的是'透明+激励相容'的产品哲学。"
    ],
    {
     "intro": "透明定价健康险运营商，会员持Visa福利卡按协商价直付诊所、无网络限制，2021年成独角兽，2024年完成1.65亿美元D轮。",
     "payor_model": "商业保险/雇主福利(B端)：雇主赞助保险，会员用Visa福利卡直付并按节省分润",
     "role": "服务商",
     "desc_cn": "透明定价健康险，会员Visa卡直付无网络限制",
     "founded": 2018,
     "stage": "融资中",
     "events": [
        {"date":"2021", "text":"成为独角兽"},
        {"date":"2024-06", "text":"完成1.65亿美元D轮融资"}
     ],
     "highlights": [
        "透明定价+无网络限制健康险",
        "Visa福利卡直付、会员按节省分润",
        "2021成独角兽，覆盖44+州"
     ],
     "verdict": "泛医疗擦边",
     "reason": "为通用健康险（雇主/个人），非专门服务老年人群",
     "suggested": [
        {"action":"add","tag":"健康险","reason":"更精准描述其透明定价健康险业务"}
     ]
    },
    ["金融保险"], ["保险"],
    {"customer":"B2B+B2C","role":"服务商","channel":[]}
)
tag_reviews.append(tr)
nonsilver.append({"serial":"#0853","name":"Sidecar Health","verdict":"泛医疗擦边","reason":"为通用健康险（雇主/个人），非专门服务老年人群"})

# ---------- #0872 Strive Health ----------
tr = mk("#0872", "Strive Health", 5.05, 8, 4, 4,
    [
     "信息极丰富（临床降本20%、住院降41%）。价值医疗肾脏护理模式稳健但反共识性低，深绑美国VBC支付，国内缺风险承担机制、可抄性中等。",
     "信号靠谱、披露充分。差异化一般（肾脏慢病管理），但实证成效强；国内肾病管理多按项目付费，其'风险分层+现场护理'绑定支付方值得借鉴。",
     "信息量高、信号5.05。模式不颠覆却极扎实，难点在支付侧：我国价值医疗合同尚早，创业者可重点拆解其让患者与支付方双赢的分成设计。"
    ],
    {
     "intro": "美国价值导向(value-based)肾脏护理全国领导者，用AI+现场护理团队为CKD→ESKD患者提供早期干预，2025年完成5.5亿美元D轮。",
     "payor_model": "混合（商业保险+政府Medicare/MA，通过风险/价值医疗合同向健康计划与医疗系统收费）",
     "role": "服务商",
     "desc_cn": "美国价值导向肾脏护理龙头，AI+现场护理",
     "founded": 2018,
     "stage": "融资中",
     "events": [
        {"date":"2025-09", "text":"完成5.5亿美元D轮（估值18亿美元）"}
     ],
     "highlights": [
        "价值导向肾脏护理全国龙头",
        "管理近50亿美元年医疗支出、14.5万+患者",
        "临床实证：总医疗成本降20%、住院降41%"
     ],
     "verdict": "核心银发",
     "reason": "肾脏慢病管理主要服务老年人群，属核心银发康养",
     "suggested": [
        {"action":"add","tag":"肾病管理","reason":"专注价值导向肾脏护理，建议补肾病维度"}
     ]
    },
    ["养老服务"], ["慢病管理"],
    {"customer":"B2B+B2C","role":"服务商","channel":[]}
)
tag_reviews.append(tr)

# ---------- #0915 Wheel ----------
tr = mk("#0915", "Wheel", 5.05, 6, 6, 5,
    [
     "信号中等、信息尚可。差异化在把虚拟医疗能力做成可嵌入底层服务（白标+医生网络），对国内做医疗SaaS的创业者有借鉴，但通用数字医疗非银发专属。",
     "公开资料中等。亮点是'虚拟护理基础设施'定位，避免重资产；可抄性中等，国内远程医疗平台可学其模块化输出思路，但市场适配需调整。",
     "信息量一般、信号5.05。模式巧在把问诊能力产品化供他方调用，差异化清晰；国内复制可行但竞争激烈，重点参考其弹性医生网络运营。"
    ],
    {
     "intro": "虚拟医疗基础设施公司，运营可弹性调用的临床医生网络，并为企业提供白标远程问诊平台，按平台与接诊量收费，累计融资超2.16亿美元。",
     "payor_model": "B端机构采购（企业SaaS+接诊量计费）",
     "role": "服务商",
     "desc_cn": "虚拟医疗基础设施商，白标远程问诊+医生网络",
     "founded": 2018,
     "stage": "融资中",
     "events": [
        {"date":"2022-02", "text":"完成1.5亿美元C轮融资"}
     ],
     "highlights": [
        "把虚拟医疗能力做成可嵌入底层服务",
        "运营弹性临床医生网络",
        "累计融资超2.16亿美元"
     ],
     "verdict": "泛医疗擦边",
     "reason": "虚拟医疗基础设施为通用数字医疗，非老年专属",
     "suggested": [
        {"action":"change","tag":"养老服务","reason":"实为虚拟医疗基础设施（白标远程问诊平台），非直接养老，建议改数字医疗"},
        {"action":"change","tag":"远程医疗","reason":"更准确应为医疗基础设施/虚拟护理SaaS"}
     ]
    },
    ["养老服务"], ["远程医疗"],
    {"customer":"B2B+B2C","role":"服务商","channel":[]}
)
tag_reviews.append(tr)
nonsilver.append({"serial":"#0915","name":"Wheel","verdict":"泛医疗擦边","reason":"虚拟医疗基础设施为通用数字医疗，非老年专属"})

# ---------- #0964 Synchron ----------
tr = mk("#0964", "Synchron", 5.05, 9, 9, 4,
    [
     "信号与信息都顶级（Bloomberg等密集报道+临床数据）。免开颅血管内脑机接口是稀缺前沿路线，差异化极强，但监管支付未定、国内难直接平移。",
     "公开材料极丰、信号扎实。亮点是Stentrode微创路线与首例意念控iPad，反共识性强；可抄性低——研发与审批壁垒高，可作硬核案例研究。",
     "信息量极高、信号5.05。最大价值在开辟非手术BCI路径，差异化满分；受技术与支付双重制约难复制，但其临床转化节奏值得长期跟踪。"
    ],
    {
     "intro": "非手术（血管内）脑机接口公司，Stentrode经颈静脉微创植入运动皮层，帮助瘫痪患者用思维控制数字设备，2025年完成2亿美元D轮。",
     "payor_model": "B端机构付费（面向医院/医疗系统的植入式设备；远期或由商业/政府医疗保险覆盖，尚未商业上市）",
     "role": "制造商(硬件/设备)",
     "desc_cn": "血管内微创脑机接口，助瘫痪者意念控制设备",
     "founded": 2012,
     "stage": "融资中",
     "events": [
        {"date":"2025-08", "text":"全球首例ALS患者用Apple BCI协议意念控制iPad"},
        {"date":"2025-11", "text":"完成2亿美元D轮融资"}
     ],
     "highlights": [
        "血管内微创Stentrode免开颅",
        "2025首例意念控制iPad（ALS患者）",
        "D轮2亿美元（2025-11）"
     ],
     "verdict": "泛医疗擦边",
     "reason": "当前面向瘫痪/神经退行患者，老龄化应用尚在拓展中",
     "suggested": [
        {"action":"change","tag":"消费品","reason":"脑机接口植入式医疗器械，非消费品，建议改医疗器械/智能硬件"},
        {"action":"change","tag":"服务商(媒体/数据)","reason":"实为设备制造商，role建议改制造商(硬件/设备)"},
        {"action":"add","tag":"神经科技","reason":"补神经科技/脑机接口维度"}
     ]
    },
    ["消费品"], ["智能硬件"],
    {"customer":"B2B","role":"服务商(媒体/数据)","channel":[]}
)
tag_reviews.append(tr)
nonsilver.append({"serial":"#0964","name":"Synchron","verdict":"泛医疗擦边","reason":"当前面向瘫痪/神经退行患者，老龄化应用尚在拓展中"})

# ---------- #0969 Hippocratic AI ----------
tr = mk("#0969", "Hippocratic AI", 5.05, 9, 6, 6,
    [
     "信号与信息双高（Reuters等+50+合作方）。'安全优先不诊断'的AI代理定位清晰，差异化中等但商业化快，国内医疗大模型客服可借鉴其合规边界。",
     "公开材料丰富、信号扎实。亮点在低风险AI替代人力客服并规模化，可抄性中高；国内同类多激进，其'无诊断'安全框架与付费方结构值得拆解。",
     "信息量极高、信号5.05。模式不颠覆但增长猛，差异化在合规定位；对国内创业者可学性强——如何把生成式AI安全落地医疗客服的场景设计。"
    ],
    {
     "intro": "专注'安全第一'的医疗生成式AI代理公司，提供不诊断、不开方的低风险面向患者AI客服（随访、预约、用药提醒），与50+医疗系统/支付方合作。",
     "payor_model": "B端机构付费（向医疗系统、健康计划/支付方、药企收SaaS/使用费）",
     "role": "技术服务商",
     "desc_cn": "安全优先医疗生成式AI代理，低风险患者客服",
     "founded": 2023,
     "stage": "融资中",
     "events": [
        {"date":"2025-11", "text":"完成1.26亿美元C轮（估值35亿美元）"}
     ],
     "highlights": [
        "安全优先、不诊断的低风险AI代理",
        "合作50+医疗系统/支付方，1.15亿+次互动",
        "C轮估值35亿美元"
     ],
     "verdict": "泛医疗擦边",
     "reason": "通用医疗AI客服代理，非专门面向老年人群",
     "suggested": [
        {"action":"add","tag":"医疗AI代理","reason":"更精准描述其安全优先医疗AI代理定位"}
     ]
    },
    ["行业服务"], ["AI医疗"],
    {"customer":"B2B","role":"技术服务商","channel":[]}
)
tag_reviews.append(tr)
nonsilver.append({"serial":"#0969","name":"Hippocratic AI","verdict":"泛医疗擦边","reason":"通用医疗AI客服代理，非专门面向老年人群"})

# ---------- #0978 SetPoint Medical ----------
tr = mk("#0978", "SetPoint Medical", 5.05, 7, 8, 3,
    [
     "信号中等、信息较足（FDA批准+融资）。植入式迷走神经刺激治RA是神经免疫新路线，差异化强；但器械重监管、国内支付未明，复制门槛高。",
     "公开资料中等偏上。亮点在2025年获FDA批准的首款RA神经调控器械，反共识明显；可抄性低——植入设备审批与商业化周期长，宜作技术标杆。",
     "信息量尚可、信号5.05。最大价值是验证'神经调控治炎症'新范式，差异化高；受重资产强监管制约难平移，可学其从临床到获批的转化路径。"
    ],
    {
     "intro": "神经免疫调节疗法开发商，研发SetPoint System植入式设备，通过迷走神经刺激治疗类风湿性关节炎，2025年7月获FDA批准。",
     "payor_model": "B端机构采购+个人自费（植入器械，远期医保覆盖）",
     "role": "制造商(硬件/设备)",
     "desc_cn": "植入式迷走神经刺激器械，治疗类风湿等炎症病",
     "founded": 2007,
     "stage": "融资中",
     "events": [
        {"date":"2025-07", "text":"SetPoint System获FDA批准用于类风湿关节炎"},
        {"date":"2025-08", "text":"完成1.4亿美元D轮+C轮二期融资"}
     ],
     "highlights": [
        "FDA批准首款RA迷走神经刺激植入器械",
        "2025年8月完成1.4亿美元融资",
        "投资方含雅培、波士顿科学相关资本"
     ],
     "verdict": "泛医疗擦边",
     "reason": "为类风湿关节炎等炎症病的植入器械，非老年专属",
     "suggested": [
        {"action":"change","tag":"康复辅具","reason":"为植入式神经调控器械，非康复辅具，建议改医疗器械"},
        {"action":"change","tag":"康复器械","reason":"建议改为神经调控/植入式器械"}
     ]
    },
    ["康复辅具"], ["康复器械"],
    {"customer":"B2B+B2C","role":"制造商(硬件/设备)","channel":[]}
)
tag_reviews.append(tr)
nonsilver.append({"serial":"#0978","name":"SetPoint Medical","verdict":"泛医疗擦边","reason":"为类风湿关节炎等炎症病的植入器械，非老年专属"})

# ---------- #0456 Chapter ----------
tr = mk("#0456", "Chapter", 4.55, 6, 7, 5,
    [
     "信号中等（D轮+E轮、估值30亿）。专为老人做Medicare导航、unbiased顾问模式差异化清晰，但深绑美国医保，国内社保体系不同、直接复制难。",
     "信息公开度中高、信号4.55。亮点在'全市场 unbiased 医保导航+AI'，对国内养老金融科普有启发，但依赖美国保险佣金结构，可抄性中等。",
     "虽信号略低，模式却精准切中退休人群痛点。差异化在独立顾问+算法匹配，国内类似平台可借鉴其信任机制；支付与监管差异限制直接平移。"
    ],
    {
     "intro": "美国最大Medicare导航与退休指导平台，用AI+持牌顾问为老年人提供无利益冲突的医保方案选择与退休规划，2020年成立。",
     "payor_model": "混合支付（个人用户免费，靠保险方/机构合作分润）",
     "role": "服务商",
     "desc_cn": "美国Medicare导航与退休指导平台，助老人选医保",
     "founded": 2020,
     "stage": "融资中",
     "events": [
        {"date":"2025-04", "text":"完成7500万美元D轮融资（Stripes领投）"},
        {"date":"2026-04", "text":"完成1亿美元E轮融资（估值30亿美元）"}
     ],
     "highlights": [
        "美国领先Medicare导航/退休指导平台",
        "2025年D轮7500万美元；2026年E轮1亿美元（估值30亿）",
        "帮助老年人选择并管理医保优势计划"
     ],
     "verdict": "核心银发",
     "reason": "专为老年人 Medicare 选择与退休规划提供导航服务",
     "suggested": [
        {"action":"add","tag":"退休规划","reason":"定位Medicare导航+退休指导，建议补退休规划维度"}
     ]
    },
    ["金融保险"], ["保险科技"],
    {"customer":"B2B+B2C","role":"服务商","channel":[]}
)
tag_reviews.append(tr)

out = {
    "batch": 7,
    "enterprises": E,
    "tag_review": tag_reviews,
    "nonsilver": nonsilver
}

with open("G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run/out/batch_007_out.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("WROTE", len(E), "enterprises;", len(tag_reviews), "tag_reviews;", len(nonsilver), "nonsilver")
for e in E:
    print(e["serial"], e["research_value"], e["silver_verdict"])
