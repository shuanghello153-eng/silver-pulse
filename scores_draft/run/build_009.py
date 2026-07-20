# -*- coding: utf-8 -*-
import json

out = {
  "batch": 9,
  "enterprises": [
    {
      "serial": "#0741",
      "signal_strength": 4.55,
      "info_score": 7, "diff_score": 5, "copy_score": 4,
      "research_value": 52.6,
      "recommend": {
        "rec_v1": "卒中取栓龙头信息透明、技术壁垒高，血管介入机器人拓展构筑术式闭环；信号明确但强监管与资本门槛高，国内高端器械出海路径值得跟踪。",
        "rec_v2": "老年卒中刚需催生取栓器械，产品矩阵覆盖多血管场景，差异化在专病平台化；国内同类多但高端仍依赖进口，可借鉴其临床定位打法。",
        "rec_v3": "医院直销模式信号扎实，差异化靠手术机器人新赛道；创业者可学'专病器械平台'思路，但FDA审批与重资产使可复制性偏低。",
        "info_score": 7, "diff_score": 5, "copy_score": 4, "signal_strength": 4.55, "research_value": 52.6
      },
      "payor_model": "B端机构采购（医院设备采购）",
      "business_tags_role": "产品商",
      "desc_cn": "神经与血管介入医疗器械商，主攻卒中取栓及血栓切除系统",
      "founded": 2015,
      "stage": "融资中",
      "events": [
        {"date": "2024-07", "text": "完成E轮1.5亿美元融资"},
        {"date": "2026-03", "text": "完成1亿美元可转债融资"}
      ],
      "highlights": [
        "累计融资约5.96亿美元，E轮后再获可转债",
        "在研Telos血管介入机器人拓展手术机器人赛道",
        "核心Zoom取栓系统覆盖急性缺血性卒中",
        "产品矩阵覆盖静脉血栓与急性肢体缺血"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "泛医疗擦边",
      "silver_reason": "血管介入器械面向医院销售，老年卒中高发但非银发专属照护，属泛医疗范畴"
    },
    {
      "serial": "#0772",
      "signal_strength": 4.55,
      "info_score": 6, "diff_score": 6, "copy_score": 5,
      "research_value": 53.7,
      "recommend": {
        "rec_v1": "澳洲居家照护P2P信号清晰、模式轻盈，老人直雇护工压缩中介成本；差异化在双边信任机制，国内可抄但需适配用工与监管环境。",
        "rec_v2": "信息较全的照护交易市场样本，轻资产连接供需；其打法对国内社区养老有借鉴，但中外照护体系差异使模式复制受限。",
        "rec_v3": "模式与需求双明确，差异化在把护工转为独立接单者；平台逻辑可学，然国内护工社保与信任短板是本地化落地的主要门槛。",
        "info_score": 6, "diff_score": 6, "copy_score": 5, "signal_strength": 4.55, "research_value": 53.7
      },
      "payor_model": "个人自费（用户直付护工）+平台佣金",
      "business_tags_role": "平台",
      "desc_cn": "澳大利亚居家照护P2P平台，老人直雇独立护工并按交易抽佣",
      "founded": 2017,
      "stage": "融资中",
      "events": [
        {"date": "2021-09", "text": "完成1亿美元私募股权融资"}
      ],
      "highlights": [
        "澳洲居家照护P2P平台，连接老人与独立护工",
        "按交易额抽佣，用户直付护工",
        "覆盖上门照料/接送/社交陪伴多场景"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "直接服务澳大利亚老人与残障群体居家照护，属核心银发"
    },
    {
      "serial": "#0789",
      "signal_strength": 4.55,
      "info_score": 6, "diff_score": 5, "copy_score": 4,
      "research_value": 49.6,
      "recommend": {
        "rec_v1": "美国非紧急转运龙头信息量与支付方信号强，整合护理与上门监测帮健康计划降住院成本；差异化在payer捆绑，国内医保语境难直接平移。",
        "rec_v2": "垂直打通转运/护理/监测三块，数据透明度高；'为支付方省成本'的商业模式反共识，值得研究但强依赖美国医保，复制性低。",
        "rec_v3": "信号来自上市背书与大额贷款，差异化在一体化非急诊服务网；国内可借鉴转运与上门看护协同，但支付结构迥异难照搬。",
        "info_score": 6, "diff_score": 5, "copy_score": 4, "signal_strength": 4.55, "research_value": 49.6
      },
      "payor_model": "政府医保支付（Medicaid/Medicare）",
      "business_tags_role": "服务商",
      "desc_cn": "美国非紧急医疗转运+居家个人护理+远程监测整合服务商",
      "founded": 2021,
      "stage": "融资中",
      "events": [
        {"date": "2024-07", "text": "获5.25亿美元定期贷款"}
      ],
      "highlights": [
        "美国Medicaid/Medicare会员非紧急医疗转运龙头",
        "整合个人护理+远程患者监测的一站式服务",
        "为健康计划降低急诊与住院成本"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "非紧急转运+个人护理+远程监测主要服务老年/失能 Medicaid人群"
    },
    {
      "serial": "#0869",
      "signal_strength": 4.55,
      "info_score": 6, "diff_score": 6, "copy_score": 7,
      "research_value": 57.7,
      "recommend": {
        "rec_v1": "护理人力培训信号新、信息充足，短训+临床实习快速供给养老人力；差异化在按就业结果分成的收费，国内职教缺口大、可复制性高。",
        "rec_v2": "AI驱动医疗培训叙事清晰，把'招生—实训—就业'拧成闭环；对国内护理员短缺是直接参考，模式轻、政策友好，易本地化落地。",
        "rec_v3": "融资与需求双强，差异化在收入分成绑定就业；国内可抄'培训即输送'路径，但需补上资质认证与机构合作两道门槛。",
        "info_score": 6, "diff_score": 6, "copy_score": 7, "signal_strength": 4.55, "research_value": 57.7
      },
      "payor_model": "个人自费（学费）+收入分成（ISA）",
      "business_tags_role": "服务商",
      "desc_cn": "短期在线培训医疗助理与护理员，按学费或收入分成并输送至机构",
      "founded": 2020,
      "stage": "融资中",
      "events": [
        {"date": "2020", "text": "公司成立"},
        {"date": "2026-06", "text": "完成C轮5700万美元融资"}
      ],
      "highlights": [
        "短期在线课程+临床实习快速培训护理人力",
        "学费或收入分成(ISA)双收费模式",
        "毕业生定向输送至养老机构与医院"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "培训护理人力输送至养老机构，支撑银发照护供给"
    },
    {
      "serial": "#0966",
      "signal_strength": 4.55,
      "info_score": 7, "diff_score": 7, "copy_score": 4,
      "research_value": 56.6,
      "recommend": {
        "rec_v1": "老年健康福利激活平台信息厚实，聚焦把复杂保险福利讲明白并驱动使用；差异化在'福利执行'而非卖保险，国内可学导航思路但支付方难复制。",
        "rec_v2": "面向长者的健康导航AI，信号与差异化兼具；降低福利浪费的思路对国内商保/惠民保有启发，然深度嵌入美国医保限制其平移。",
        "rec_v3": "高信息量样本，帮老人真正用上已购健康权益；可复制性低因绑定特定医保计划，但'福利可视化'方法论值得借鉴。",
        "info_score": 7, "diff_score": 7, "copy_score": 4, "signal_strength": 4.55, "research_value": 56.6
      },
      "payor_model": "Medicare Advantage等商业保险支付",
      "business_tags_role": "服务商",
      "desc_cn": "AI驱动老年健康导航平台，帮Medicare Advantage会员激活并使用福利",
      "founded": 2020,
      "stage": "融资中",
      "events": [
        {"date": "2025-10", "text": "完成B轮1.3亿美元融资"}
      ],
      "highlights": [
        "聚焦Medicare Advantage会员福利激活与执行",
        "AI健康导航降低保险福利浪费",
        "B轮1.3亿美元，累计融资1.67亿美元"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "聚焦Medicare Advantage老年会员福利激活，直接服务长者"
    },
    {
      "serial": "#0974",
      "signal_strength": 4.55,
      "info_score": 8, "diff_score": 4, "copy_score": 5,
      "research_value": 55.6,
      "recommend": {
        "rec_v1": "消费睡眠硬件信息极丰富、信号稳，温控+生物监测形成'硬件即服务'；差异化在睡眠代理订阅，国内智能床红海下其DTC打法可观察。",
        "rec_v2": "全球睡眠科技明星，把床垫变数据入口的思路反共识；但高价订阅在国内水土不服，入华弃订阅改电商的本土化转折值得跟踪。",
        "rec_v3": "信号来自多轮融资与入华动作，差异化在实时调温的睡眠代理；可复制性中等——硬件易学、AI订阅留存难，本土化是核心课题。",
        "info_score": 8, "diff_score": 4, "copy_score": 5, "signal_strength": 4.55, "research_value": 55.6
      },
      "payor_model": "个人自付（C端硬件+会员订阅）",
      "business_tags_role": "产品商",
      "desc_cn": "消费级AI智能睡眠硬件，温控床垫罩+生物监测含订阅",
      "founded": 2014,
      "stage": "融资中",
      "events": [
        {"date": "2025-08", "text": "完成D轮1亿美元融资"},
        {"date": "2026-03", "text": "获Tether 5000万美元战略轮，估值15亿美元"},
        {"date": "2026-04", "text": "正式进入中国市场"}
      ],
      "highlights": [
        "Pod智能床垫罩温控+HRV/心率/呼吸监测",
        "硬件+会员订阅的AI睡眠代理模式",
        "2026年4月入华，取消订阅改DTC电商"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "泛医疗擦边",
      "silver_reason": "消费级睡眠科技面向大众，更年期/睡眠呼吸仅为适老切面，非银发专属"
    },
    {
      "serial": "#1145",
      "signal_strength": 4.55,
      "info_score": 6, "diff_score": 7, "copy_score": 4,
      "research_value": 53.7,
      "recommend": {
        "rec_v1": "老年慢病AI护理获大医疗系统采用、信号明确，差异化在按效付费绑定疗效；国内可学其慢病管理范式，但依赖美国支付体系难复制。",
        "rec_v2": "信息较新的临床AI样本，用护理模型管慢病降住院；'疗效挂钩收费'反共识，对国内慢病管理有参考价值，复制受医保结构约束。",
        "rec_v3": "融资与采用双强，差异化在把AI嵌进医疗系统工作流；可复制性中低，然'AI+按效'组合是国内创业者值得拆解的范式。",
        "info_score": 6, "diff_score": 7, "copy_score": 4, "signal_strength": 4.55, "research_value": 53.7
      },
      "payor_model": "B端机构采购（医疗系统）+按效付费",
      "business_tags_role": "技术服务商",
      "desc_cn": "临床AI用护理模型管理老年慢病，按效付费被大型医疗系统采用",
      "founded": None,
      "stage": "融资中",
      "events": [
        {"date": "2026-06", "text": "完成C轮1亿美元融资，Spark Capital领投"}
      ],
      "highlights": [
        "AI护理模型管理老年慢病，对标value-based care",
        "被全美领先医疗系统采用",
        "Spark Capital领投C轮"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "AI管理老年慢病、被医疗系统采用，直接服务长者照护"
    },
    {
      "serial": "#1168",
      "signal_strength": 4.55,
      "info_score": 8, "diff_score": 8, "copy_score": 8,
      "research_value": 69.7,
      "recommend": {
        "rec_v1": "英国居家医疗AI标杆信息量与信号双高，AI调度使住院率显著下降；差异化在闭环运营，国内'居家养老+AI'可直接对标。",
        "rec_v2": "数据透明的居家照护范本，模式清晰；用AI压缩护理成本的反共识打法，对国内医养结合是可复制度高的参考。",
        "rec_v3": "高信号高信息样本，把护工调度/远程医疗/监测拧成平台；可复制性强——模式清晰、国内空白、政策利好，属重点研究对象。",
        "info_score": 8, "diff_score": 8, "copy_score": 8, "signal_strength": 4.55, "research_value": 69.7
      },
      "payor_model": "混合支付（政府医保NHS+个人自付+保险）",
      "business_tags_role": "运营商",
      "desc_cn": "英国最大数字化居家医疗商，AI调度护工+远程监测+远程医疗",
      "founded": 2016,
      "stage": "融资中",
      "events": [
        {"date": "2016", "text": "公司成立于伦敦"},
        {"date": "2025-01", "text": "完成1.5亿美元Series C"},
        {"date": "2026-05", "text": "再完成1.5亿美元Series C，累计约4.21亿美元"}
      ],
      "highlights": [
        "英国最大数字化居家医疗提供商",
        "AI调度护工使住院率降约70%",
        "累计融资约4.21亿美元，36氪已专题报道"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "英国最大数字化居家医疗，直接服务老年居家照护"
    },
    {
      "serial": "#1245",
      "signal_strength": 4.55,
      "info_score": 6, "diff_score": 9, "copy_score": 3,
      "research_value": 55.6,
      "recommend": {
        "rec_v1": "细胞重编程延寿赛道信息中等、信号靠早期大额融资；差异化在最前沿长寿科技，但重资产强监管周期长，短期难复制。",
        "rec_v2": "长寿生物科技叙事强、技术反共识，资金厚度足；healthspan研究对国内抗衰产业有风向意义，然临床与监管门槛使可抄性极低。",
        "rec_v3": "信号来自早期重金投入，差异化在重编程延寿路径；可复制性低（深科技+FDA），但'抗衰即银发'定位值得国内Biotech借鉴。",
        "info_score": 6, "diff_score": 9, "copy_score": 3, "signal_strength": 4.55, "research_value": 55.6
      },
      "payor_model": "研发阶段未商业化，远期处方/合作支付",
      "business_tags_role": "制造商(药)",
      "desc_cn": "长寿生物科技公司，以细胞重编程技术延长健康寿命",
      "founded": 2021,
      "stage": "融资中",
      "events": [
        {"date": "2023", "text": "完成1.8亿美元早期融资"}
      ],
      "highlights": [
        "细胞重编程延寿的前沿长寿生物科技",
        "2023年完成1.8亿美元早期融资",
        "聚焦健康寿命(healthspan)延长研究"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "细胞重编程延寿直指健康寿命，属长寿科技核心银发"
    },
    {
      "serial": "#1311",
      "signal_strength": 4.55,
      "info_score": 4, "diff_score": 5, "copy_score": 6,
      "research_value": 47.7,
      "recommend": {
        "rec_v1": "西班牙医养结合样本信息偏少、信号一般，但整合养老+医疗的运营可借鉴；差异化在一体化服务，国内对照价值中等。",
        "rec_v2": "欧洲整合照护范本，模式清晰；把养老医疗打通的思路对国内有对照意义，可复制性中——模式可学、支付需本地化。",
        "rec_v3": "信号来自海外B轮投入，差异化在养老医疗双线运营；信息量有限但作为医养结合案例，对国内创业者有制度层面参考。",
        "info_score": 4, "diff_score": 5, "copy_score": 6, "signal_strength": 4.55, "research_value": 47.7
      },
      "payor_model": "混合支付（政府医保+个人自付）",
      "business_tags_role": "服务商",
      "desc_cn": "西班牙'养老+医疗'整合服务商，提供医养结合照护",
      "founded": 2017,
      "stage": "融资中",
      "events": [
        {"date": "2017", "text": "公司成立于西班牙"}
      ],
      "highlights": [
        "西班牙医养结合整合服务范本",
        "累计融资约6000万欧元(B轮)",
        "对国内'医养结合'运营有对照价值"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "西班牙养老+医疗整合服务，直接服务老年群体"
    },
    {
      "serial": "#1352",
      "signal_strength": 4.55,
      "info_score": 8, "diff_score": 7, "copy_score": 5,
      "research_value": 61.6,
      "recommend": {
        "rec_v1": "生成式AI病历平台信息极丰、信号强，提升医护文书效率；差异化在嵌入临床工作流，国内医疗AI可学，受EHR与监管约束。",
        "rec_v2": "临床文书自动化明星，应用广含护理场景；用AI替医护写字的思路反共识，对国内智慧养老文书有启发，复制中度。",
        "rec_v3": "高信息高信号样本，把生成式AI落地到病历草稿；可复制性中——技术可追，但中美EHR生态与合规差异是主要门槛。",
        "info_score": 8, "diff_score": 7, "copy_score": 5, "signal_strength": 4.55, "research_value": 61.6
      },
      "payor_model": "B端机构采购（医疗系统SaaS订阅）",
      "business_tags_role": "技术服务商",
      "desc_cn": "生成式AI临床文书平台，自动生成病历草稿提升医护记录效率",
      "founded": 2018,
      "stage": "融资中",
      "events": [
        {"date": "2018", "text": "公司成立"},
        {"date": "2026", "text": "完成Series E 3亿美元融资，累计约5亿美元"}
      ],
      "highlights": [
        "生成式AI自动生成病历草稿，提升医护记录效率",
        "累计融资约5亿美元，2026年Series E 3亿美元",
        "广泛应用于养老与护理场景的文书自动化"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "临床文书AI广泛应用于养老与护理场景，服务银发照料方"
    },
    {
      "serial": "#0034",
      "signal_strength": 4.05,
      "info_score": 7, "diff_score": 6, "copy_score": 6,
      "research_value": 57.2,
      "recommend": {
        "rec_v1": "中老年图文社区信息足、信号稳，微信生态内差异化在内容创作黏性；国内银发文娱可直接对标，可复制性中等。",
        "rec_v2": "银发内容社区范本，从工具到电商路径清晰；抓住中老年表达需求的反共识打法，对国内文娱创业者是高可复制参考。",
        "rec_v3": "信号来自庞大用户基础，差异化在兴趣社交+创作工具；可复制性中高——模式本土已验证，后来者易学难超。",
        "info_score": 7, "diff_score": 6, "copy_score": 6, "signal_strength": 4.05, "research_value": 57.2
      },
      "payor_model": "个人自费（会员/电商）+B端广告",
      "business_tags_role": "平台",
      "desc_cn": "中老年图文创作与兴趣社交社区，微信生态内的'老红书'",
      "founded": 2015,
      "stage": "融资中",
      "events": [
        {"date": "2015", "text": "公司成立"},
        {"date": "2017-12", "text": "完成A+轮4300万美元融资"}
      ],
      "highlights": [
        "中老年图文创作与兴趣社交社区，用户超1亿",
        "微信生态内热门，被称为'老红书'",
        "从工具到电商的内容变现路径"
      ],
      "update_time": "2026-07-17",
      "silver_verdict": "核心银发",
      "silver_reason": "中老年图文创作社区，核心用户为银发群体"
    }
  ],
  "tag_review": [
    {
      "serial": "#0741", "name": "Imperative Care",
      "intro": "神经与血管介入医疗器械公司，主攻缺血性卒中取栓及静脉/肢体缺血血栓切除系统，并研发血管介入机器人。",
      "old_tags": {"tag_l1": ["康复辅具"], "tag_l2": ["医疗器械"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
      "suggested": [
        {"action": "del", "tag": "康复辅具", "reason": "血管介入/取栓器械不属于康复辅具，标签错配，建议归健康服务一级"}
      ]
    },
    {
      "serial": "#0772", "name": "Mable",
      "intro": "澳大利亚居家照护P2P在线市场，老人与残障人士直接雇佣独立护工上门照料、接送与陪伴，平台按交易抽佣。",
      "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["护工平台"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
      "suggested": [
        {"action": "add", "tag": "居家护理", "reason": "P2P居家照护平台，可补居家护理二级标签"}
      ]
    },
    {
      "serial": "#0789", "name": "Modivcare",
      "intro": "美国非紧急医疗转运、个人护理与远程患者监测整合服务商，主要服务Medicaid/Medicare会员以降低急诊与住院成本。",
      "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["适老化"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
      "suggested": [
        {"action": "del", "tag": "适老化", "reason": "主营非紧急转运+个人护理+远程监测，非适老化改造"},
        {"action": "add", "tag": "居家护理", "reason": "个人护理与上门服务可补居家护理标签"}
      ]
    },
    {
      "serial": "#0869", "name": "Stepful",
      "intro": "通过短期在线课程加临床实习培训医疗助理与患者护理员，向学员收学费或按收入分成，并输送至养老机构与医院就业。",
      "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["护工培训"], "business_tags": {"customer": "B2C", "role": "服务商", "channel": []}},
      "suggested": []
    },
    {
      "serial": "#0966", "name": "Duos",
      "intro": "AI驱动的数字健康平台，聚焦Medicare Advantage等支付方，帮助老年会员理解、激活并使用复杂的健康福利。",
      "old_tags": {"tag_l1": ["金融保险"], "tag_l2": ["保险"], "business_tags": {"customer": "B2B+B2C", "role": "服务商", "channel": []}},
      "suggested": [
        {"action": "add", "tag": "健康管理", "reason": "AI健康导航激活保险福利，可补健康管理二级标签（若受控词表含）"}
      ]
    },
    {
      "serial": "#0974", "name": "Eight Sleep",
      "intro": "消费级AI智能睡眠硬件公司，核心产品Pod智能床垫罩（水循环温控+生物传感），用睡眠代理实时调节睡眠环境。",
      "old_tags": {"tag_l1": ["消费品", "康复辅具"], "tag_l2": ["更年期", "睡眠监测"], "business_tags": {"customer": "B2B", "role": "技术服务商", "channel": []}},
      "suggested": [
        {"action": "del", "tag": "康复辅具", "reason": "消费级智能睡眠硬件非康复辅具，标签错配"}
      ]
    },
    {
      "serial": "#1145", "name": "Cadence",
      "intro": "临床AI公司，用AI护理模型管理老年慢病，被全美领先医疗系统采用，对标按效付费(value-based)慢病管理。",
      "old_tags": {"tag_l1": ["行业服务"], "tag_l2": ["AI医疗"], "business_tags": {"customer": "B2B", "role": "技术服务商", "channel": []}},
      "suggested": [
        {"action": "add", "tag": "慢病管理", "reason": "AI管理老年慢病，可补慢病管理二级标签"},
        {"action": "change", "tag": "行业服务→健康服务", "reason": "临床AI慢病管理应归健康服务一级更贴切"}
      ]
    },
    {
      "serial": "#1168", "name": "Cera",
      "intro": "英国最大数字化居家医疗提供商，以AI平台调度护工、远程监测与远程医疗，累计融资约4.21亿美元。",
      "old_tags": {"tag_l1": ["养老服务", "金融保险"], "tag_l2": ["远程医疗", "保险"], "business_tags": {"customer": "B2B+B2C", "role": "技术服务商", "channel": []}},
      "suggested": [
        {"action": "add", "tag": "居家护理", "reason": "AI居家医疗调度，可补居家护理标签"}
      ]
    },
    {
      "serial": "#1245", "name": "Retro Biosciences",
      "intro": "长寿生物科技公司，聚焦细胞重编程技术延长健康寿命(healthspan)，2023年完成1.8亿美元早期融资。",
      "old_tags": {"tag_l1": ["消费品"], "tag_l2": ["长寿抗衰"], "business_tags": {"customer": "B2B", "role": "制造商(药)", "channel": []}},
      "suggested": [
        {"action": "del", "tag": "消费品", "reason": "长寿生物医药公司非消费品"},
        {"action": "change", "tag": "消费品→长寿科技/生物医药", "reason": "细胞重编程长寿药企应归长寿科技/生物医药一级"}
      ]
    },
    {
      "serial": "#1311", "name": "Qida",
      "intro": "西班牙养老与医疗健康整合服务商，成立于2017年，累计融资约6000万欧元(B轮)，提供医养结合照护。",
      "old_tags": {"tag_l1": ["养老服务"], "tag_l2": ["远程医疗"], "business_tags": {"customer": "未标注", "role": "服务商", "channel": []}},
      "suggested": [
        {"action": "add", "tag": "医养结合", "reason": "西班牙养老+医疗整合服务，可补医养结合二级标签（若受控词表含）"}
      ]
    },
    {
      "serial": "#1352", "name": "Abridge",
      "intro": "生成式AI临床文档平台，自动生成病历草稿提升医生/护理记录效率，广泛应用于养老与护理场景。",
      "old_tags": {"tag_l1": ["行业服务"], "tag_l2": ["AI医疗"], "business_tags": {"customer": "B2B", "role": "服务商(媒体/数据)", "channel": []}},
      "suggested": [
        {"action": "change", "tag": "行业服务→智能科技", "reason": "生成式AI临床文书平台，行业服务一级过宽，归智能科技更贴切"}
      ]
    },
    {
      "serial": "#0034", "name": "美篇",
      "intro": "中老年图文创作与兴趣社交社区，微信生态内热门应用，提供图文排版、影集制作，被称为银发群体的'老红书'。",
      "old_tags": {"tag_l1": ["文娱社交"], "tag_l2": ["文娱"], "business_tags": {"customer": "B2B+B2C", "role": "平台", "channel": []}},
      "suggested": []
    }
  ],
  "nonsilver": [
    {
      "serial": "#0741", "name": "Imperative Care", "verdict": "泛医疗擦边",
      "reason": "血管介入器械面向医院销售，老年卒中高发但非银发专属照护，属泛医疗范畴"
    },
    {
      "serial": "#0974", "name": "Eight Sleep", "verdict": "泛医疗擦边",
      "reason": "消费级睡眠科技面向大众，更年期/睡眠呼吸仅为适老切面，非银发专属"
    }
  ]
}

with open(r"G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run/out/batch_009_out.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("written, enterprises:", len(out["enterprises"]), "tag_review:", len(out["tag_review"]), "nonsilver:", len(out["nonsilver"]))
