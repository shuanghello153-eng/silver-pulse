# -*- coding: utf-8 -*-
import json

def E(serial, signal_strength, info_score, diff_score, copy_score, research_value,
      recommend, desc_cn, payor_model, business_tags_role, founded, stage,
      highlights, events, silver_verdict, silver_reason):
    return {
        "serial": serial,
        "signal_strength": signal_strength,
        "info_score": info_score,
        "diff_score": diff_score,
        "copy_score": copy_score,
        "research_value": research_value,
        "recommend": recommend,
        "desc_cn": desc_cn,
        "payor_model": payor_model,
        "business_tags_role": business_tags_role,
        "founded": founded,
        "stage": stage,
        "highlights": highlights,
        "events": events,
        "update_time": "2026-07-17",
        "silver_verdict": silver_verdict,
        "silver_reason": silver_reason,
    }

SS = 6.55
ent = []

ent.append(E("#1159", SS, 8, 4, 6, 63.7,
"信号强、上市财报与密集收购披露使信息量足；差异化在“自管+收购改造低效机构”的运营型打法，可复制性受国内支付结构限制。最该学的是用标准化运营把区域小护理院整合为网络——国内连锁养老正处整合期，可对标其并购+本地化托管路径。",
"美国护理院与康复服务商，自营+收购扩张",
"混合（政府Medicare/Medicaid+个人自付；B端机构运营）",
"运营商", 1999, "已上市",
["美国上市护理院运营商之一，17州近400个医疗运营机构", "去中心化运营改造低效机构，同店入住率84.3%", "自管式+频繁收购扩张，2026年续有德州/爱荷瓦并购", "旗下Standard Bearer持有183处地产，运营与资产分离"],
[{"date":"2026-07-01","text":"收购德州两家护理院(250床)，组合达398个医疗运营机构"},{"date":"2026-06-01","text":"收购爱荷瓦护理院及加州记忆照护，Standard Bearer地产增至181处"},{"date":"2026-Q1","text":"一季度营收13.9亿美元+18.4%，同店入住率84.3%"}],
"核心银发", "自营护理院与康复/临终关怀，直接服务失能老人群体"))

ent.append(E("#1160", SS, 7, 3, 5, 56.6,
"信号中等、年报披露充分但模式成熟不反共识，信息量够而差异化弱；作为Triple-net净租赁资本方，可复制性低（需长期低成本资金）。国内康养地产尚缺成熟REIT通道，可学其“持有资产+稳定租约”的轻运营逻辑，但更该关注租户结构与杠杆约束。",
"医疗地产REIT，以净租赁向养老运营商供资本",
"B端机构付费（Triple-net净租赁，运营商付租金；终端来自政府Medicare/Medicaid+个人自付）",
"投资机构", 1991, "已上市",
["医疗地产REIT(纽交所NHI)，Triple-net净租赁资本方", "组合以养老/护理地产为主，租约稳健", "与Welltower/Ventas等构成美国养老REIT资本阵营"],
["未搜到"],
"核心银发", "以净租赁资本支撑养老/护理运营，属银发地产资本方"))

ent.append(E("#1161", SS, 7, 3, 5, 56.6,
"信号中等、SEC披露完整但三重净租赁模式不反共识，信息量足而差异化弱；组合含护理院、老年住宅与精神科。可复制性受国内REIT与长护支付不成熟限制。可学其“用EBITDARM覆盖率为锚管控租户风险”的资本方方法论，比单纯买资产更关键。",
"医疗REIT，持有护理院与老年社区并净租赁",
"B端机构付费（Triple-net净租赁，运营商付租金；终端来自政府Medicare/Medicaid+住户自费）",
"投资机构", 2010, "已上市",
["医疗REIT(纳斯达克SBRA)，Triple-net净租赁为主", "组合含护理院/老年住宅/精神科/专科 hospital", "2025年Moody's上调至Baa3，护理院EBITDARM覆盖率2.35x", "2025年新增约4.2亿美元老年住宅投资"],
[{"date":"2025-11","text":"发布Q3业绩并更新指引，Moody's上调至Baa3"},{"date":"2025-Q3","text":"新增6处自营老年住宅投资2.175亿美元，现金收益率约7.8%"}],
"核心银发", "持有护理院与老年社区并净租赁，服务老年照护"))

ent.append(E("#1162", SS, 7, 3, 5, 56.6,
"信号中等、财报透明但模式稳健不反共识；差异化在近年从净租赁转向自营SHOP（自管老年社区）以提NOI，信息量足。可复制性中等——国内险资/地产可学其“以新vintage社区+绩效化运营对冲护理院依赖”的资产腾挪，但需配套支付端。",
"养老与护理地产REIT，渐转自营老年社区",
"B端机构付费（净租赁+SHOP自营；终端来自政府Medicare/Medicaid+个人自付）",
"投资机构", 1992, "已上市",
["养老与护理地产REIT(纽交所LTC)，1992年成立", "2025年战略转向自营SHOP老年社区，NOI利润率升至28%", "组合约190处，60%老年住宅+40%护理院", "2025年Genesis租户破产，2026年换租户去化风险"],
[{"date":"2025","text":"战略转向自营SHOP，全年收购11个社区约3.53亿美元"},{"date":"2025","text":"Genesis HealthCare租户破产，6处新墨西哥/阿拉巴马护理院受影响"},{"date":"2026-01","text":"预计再完成1.1亿美元SHOP收购，SHOP占比目标2026达45%"}],
"核心银发", "养老与护理地产REIT，资产直接服务老年住宅"))

ent.append(E("#1163", SS, 7, 3, 5, 56.6,
"信号中等、为医疗办公楼(MOB)REIT而非老年住宅，银发切点仅“毗邻医院”的医养adjacency，信息量足而差异化弱。可复制性低。国内做医养结合地产可学其“锚定医院流量、长租医生集团”的资产逻辑，但需清醒它本质是医疗地产而非养老运营。",
"医疗办公楼REIT，锚定医院流量的医养地产",
"B端机构付费（向医生集团/医院收租；终端为医疗服务自费与医保）",
"投资机构", 1992, "已上市",
["医疗办公楼(MOB)REIT(纽交所HR)，2022年合并HTA", "资产以毗邻医院的医生集团办公楼为主", "银发切点弱，属医疗地产而非养老运营", "“锚定医院流量”逻辑对医养结合地产有参考"],
[{"date":"2022","text":"与Healthcare Trust of America合并，扩大MOB组合"}],
"泛医疗擦边", "主营医疗办公楼(MOB)，仅“毗邻医院”间接沾边医养，并非养老运营"))

ent.append(E("#1165", SS, 7, 5, 7, 64.7,
"信号强、上市披露与保险合作充分，信息量足；差异化在“产品+上门服务”的HME连锁化，且与Humana签按人头付费的价值医疗合约，可复制性较高。国内居家康复/呼吸器械租赁可学其“绑定商保+医院转诊+到家长护”闭环，但前提是商保支付成熟。",
"家用医疗设备商，提供呼吸/睡眠器械上门服务",
"政府医保(Medicare/Medicaid)+商业保险(含按人头价值医疗合约)+个人自付",
"产品商", 2013, "已上市",
["家用医疗设备(HME)龙头(纳斯达克AHCO)，47州约640网点", "四大板块：睡眠/呼吸/糖尿病/居家康复", "服务Medicare/Medicaid/商保，年触达430万患者", "与Humana签按人头价值医疗DME合约，覆盖百万MA会员"],
[{"date":"2026-01","text":"Moody's上调AdaptHealth评级至Ba2(原Ba3)"},{"date":"2023","text":"与Humana签按人头价值医疗DME合约，覆盖33州百万MA会员"}],
"核心银发", "家用呼吸机/制氧/糖尿病器械主要服务慢病老人居家场景"))

ent.append(E("#1166", SS, 7, 4, 5, 58.6,
"信号强但属反共识风险样本：曾是最大医院房东，因租户Steward破产两度砍股息、股价跌八成，2025起逐步换租户回血。信息量足、差异化在“租户集中+杠杆”教训。国内康养/医院地产最该学其风险——别把重资产押在单一支付方上。",
"医院地产REIT，曾陷租户破产的反共识风险样本",
"B端机构付费（医院运营商付租金；终端来自政府医保+个人自付）",
"投资机构", 2003, "已上市",
["医院地产REIT(纽交所MPW)，曾为全球最大医院房东", "2024-2025租户Steward破产，两度砍息、股价跌约80%", "2025起与替代运营商重签长约，租金2026年逐步回稳", "反共识风险样本：租户集中+杠杆双杀"],
[{"date":"2025","text":"与Steward达成全球和解，收回23家医院房地产并换租户"},{"date":"2025-Q2","text":"新租户开始付租，租金随合约逐步爬坡至2026年稳定"}],
"泛医疗擦边", "主营医院地产REIT，服务对象全龄，仅泛医疗沾边而非养老运营"))

ent.append(E("#1167", SS, 7, 3, 5, 56.6,
"信号中等、为医疗+养老混合REIT，2025把116个原AlerisLife社区转交七家新运营商降杠杆，信息量足而模式不反共识。可复制性低。国内存量养老资产可学其“运营商多元化+绩效化托管”的出清思路，但需成熟运营市场承接。",
"医疗与养老混合REIT，正把社区转交多元运营商",
"B端机构付费（净租赁+SHOP自营；终端来自政府Medicare/Medicaid+住户自费）",
"投资机构", 1998, "已上市",
["医疗+养老混合REIT(纳斯达克DHC)，组合约68亿美元", "2025把116个原AlerisLife社区转交七家新运营商", "2025年处置69处资产回收约6亿美元、降杠杆", "无重大债务到期至2028，转向运营提升"],
[{"date":"2025-09","text":"将原AlerisLife托管的116个老年社区转交七家新运营商"},{"date":"2026-01","text":"完成116个社区过渡，2025年处置69处资产回收约6亿美元"}],
"核心银发", "持有2.5万余老年生活单元，老年住宅为重要组合"))

ent.append(E("#1169", SS, 8, 3, 7, 63.7,
"信号强、年报与投资者材料完整，信息量足；欧洲规模化养老运营龙头，差异化在“多国本土化+政府报销托底”的重资产模型，可复制性受国内支付结构限制。最该学的是用“政府报销+个人补足”支撑重资产定价——国内定价机制可对标其case mix管理。",
"欧洲养老护理运营商，多国本土化重资产",
"混合（欧洲养老院费用主要由政府社会医保/地方财政报销+居民个人自付补足；高端房间与增值服务以个人自付为主）",
"运营商", 2001, "已上市",
["欧洲养老运营龙头(原Korian，泛欧证交所CLAR)", "2025营收53.1亿欧元、服务88.6万人，occupancy 91.7%", "2026Q1营收13.36亿欧元+4.9%有机增长", "2026年发5亿欧元债置换到期债务，降杠杆中"],
[{"date":"2026-04","text":"Q1营收13.36亿欧元+4.9%有机增长，occupancy 91.7%"},{"date":"2026","text":"发行5亿欧元2031年到期高收益债置换到期债务"}],
"核心银发", "欧洲依赖人群照护设施领先私营运营商"))

ent.append(E("#1170", SS, 7, 5, 6, 62.6,
"信号强、是罕见的“暴雷—重组”反共识样本：从财务造假与照护丑闻到债务重组去杠杆，起落极大，信息量足、差异化在治理教训。国内连锁养老可学其反面——规模化同时须避开“重资产+预收费+治理失效”的爆雷路径，比成功学更有警示价值。",
"欧洲养老运营商，从丑闻到重组的反共识样本",
"混合（欧洲养老院费用政府社会医保报销+居民个人自付补足）",
"运营商", 1989, "已上市",
["欧洲养老运营巨头(原Orpea，泛欧证交所)", "曾陷财务造假与照护质量丑闻，现重组去杠杆", "2024年营收持平，推进资产出售与治理修复", "反共识“暴雷—重生”样本"],
[{"date":"2024","text":"推进债务重组与资产出售，去杠杆修复中"}],
"核心银发", "欧洲依赖人群照护运营商，直接服务失能老人"))

ent.append(E("#1171", SS, 8, 7, 4, 65.7,
"信号极强、上市与临床挫折广被报道，信息量足；差异化在“用衰老队列数据反推代谢靶点”，可复制性低。2025底核心药azelaprag因肝安全叫停、转向NLRP3，国内长寿科技最该学其“概念叙事—临床兑现”落差与单点依赖风险。",
"长寿科技生物公司，抗衰代谢药物研发",
"B端机构付费（药企/研发合作）+ 远期上市后为医保/个人支付（尚未商业化）",
"产品商", 2017, "已上市",
["长寿科技生物公司(纳斯达克BIOA)，2024-09 IPO募1.98亿", "核心azelaprag(GLP-1联用减重)2025底因肝安全暂停", "转向NLRP3抑制剂BGE-102，2026年1月再融1.15亿", "用衰老队列数据反推代谢靶点的discovery平台"],
[{"date":"2025-12","text":"azelaprag(STRIDES II期)因肝转氨酶升高暂停，股价再挫"},{"date":"2026-01","text":"定价1.15亿美元公开增发，推进NLRP3抑制剂BGE-102"}],
"核心银发", "抗衰老/代谢衰老疗法，面向年龄相关慢病"))

ent.append(E("#1173", SS, 6, 6, 3, 55.6,
"属反共识警示：曾是衰老细胞清除(senolytics)先锋，其BCL-xL抑制剂眼科现金枯竭2025被纳斯达克摘牌清算。信息量足、差异化在“局部给药避系统毒性”。国内抗衰创业最该学：好科学不等于好公司，须控现金流、聚焦明确适应症与支付路径。",
"衰老细胞清除生物公司，以眼科局部给药避毒性",
"B端机构付费（研发合作/资产变现）；未商业化，清算中无终端支付",
"产品商", 2011, "已上市",
["衰老细胞清除(senolytics)先锋(原纳斯达克UBX)", "UBX1325(BCL-xL抑制剂)眼科DME/AMD数据积极", "2025年因现金枯竭被纳斯达克摘牌并启动清算", "“局部给药避系统毒性”思路对抗衰药物有参考价值"],
[{"date":"2025-06","text":"纳斯达克通知摘牌，认定为无实质业务的公众壳"},{"date":"2025-09","text":"提交解散证书启动清算，2026年终止办公租赁"}],
"核心银发", "衰老细胞清除(senolytics)属长寿科技核心方向"))

# ---- tag_review ----
def tr(serial, name, intro, old_l1, old_l2, old_bt, suggested):
    return {"serial": serial, "name": name, "intro": intro,
            "old_tags": {"tag_l1": old_l1, "tag_l2": old_l2, "business_tags": old_bt},
            "suggested": suggested}

tag_review = []
tag_review.append(tr("#1159","The Ensign Group",
"美国上市护理院与康复服务商，以去中心化运营收购改造低效机构，17州近400个医疗运营点。",
["养老服务"],["安宁疗护"],{"customer":"未标注","role":"服务商","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"自营护理院与老年生活社区，属运营商而非纯服务商"},
 {"action":"add","tag":"康复护理","reason":"康复/物理治疗是其核心业务板块，建议补入tag_l2"}]))

tag_review.append(tr("#1160","National Health Investors",
"专注养老与医疗地产的REIT(纽交所NHI)，以Triple-net净租赁向养老运营商提供资本。",
["投资机构"],["养老REIT"],{"customer":"未标注","role":"服务商","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"REIT资本方，应为投资机构而非服务商"}]))

tag_review.append(tr("#1161","Sabra Health Care REIT",
"医疗REIT(纳斯达克SBRA)，以三重净租赁持有护理院、老年住宅与精神科资产，2025年评级获上调。",
["投资机构"],["养老REIT"],{"customer":"未标注","role":"平台","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"REIT资本方，应为投资机构而非平台"}]))

tag_review.append(tr("#1162","LTC Properties",
"养老与护理地产REIT(纽交所LTC)，1992年成立，正从净租赁转向自营老年社区(SHOP)提效。",
["投资机构"],["养老REIT"],{"customer":"未标注","role":"服务商","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"REIT资本方，应为投资机构而非服务商"}]))

tag_review.append(tr("#1163","Healthcare Realty Trust",
"医疗办公楼(MOB)REIT(纽交所HR)，2022年合并HTA，资产以毗邻医院的医生集团办公楼为主，银发切点弱。",
["投资机构"],["养老REIT"],{"customer":"未标注","role":"服务商","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"REIT资本方，应为投资机构而非服务商"},
 {"action":"change","tag":"tag_l2:养老REIT→医疗办公楼REIT","reason":"资产以MOB为主，并非养老/护理地产"}]))

tag_review.append(tr("#1165","AdaptHealth",
"家用医疗设备(HME)龙头(纳斯达克AHCO)，覆盖睡眠/呼吸/糖尿病/居家康复，服务医保与商保、年触达430万人。",
["康复辅具"],["助行器","医疗器械"],{"customer":"B2B+B2C","role":"制造商(硬件/设备)","channel":[]},
[{"action":"change","tag":"tag_l2:助行器→家用医疗设备/睡眠呼吸","reason":"助行器过窄，AHCO核心是睡眠/呼吸/糖尿病HME"},
 {"action":"change","tag":"business_tags.role","reason":"属硬件+服务产品商，非纯制造商标签"}]))

tag_review.append(tr("#1166","Medical Properties Trust",
"医院地产REIT(纽交所MPW)，曾为全球最大医院房东，因租户Steward破产陷入动荡的反共识风险样本。",
["投资机构"],["养老REIT"],{"customer":"未标注","role":"服务商","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"REIT资本方，应为投资机构而非服务商"},
 {"action":"change","tag":"tag_l2:养老REIT→医院REIT","reason":"资产以医院地产为主，非养老/护理"}]))

tag_review.append(tr("#1167","Diversified Healthcare Trust",
"医疗与养老混合REIT(纳斯达克DHC)，组合约68亿美元，2025年把116个老年社区转交新运营商去化。",
["投资机构"],["养老REIT"],{"customer":"未标注","role":"平台","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"REIT资本方，应为投资机构而非平台"}]))

tag_review.append(tr("#1169","Clariane",
"欧洲养老运营龙头(原Korian，泛欧证交所CLAR)，2025营收53亿欧元、服务88.6万人，多国本土化重资产。",
["养老服务"],["养老机构"],{"customer":"未标注","role":"服务商","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"自营+受托运营养老院，属运营商而非服务商"}]))

tag_review.append(tr("#1170","Emeis (Orpea)",
"欧洲养老运营巨头(原Orpea，泛欧证交所)，曾因财务造假与照护丑闻暴雷，现重组去杠杆。",
["养老服务"],["养老机构"],{"customer":"未标注","role":"制造商(消费品)","channel":[]},
[{"action":"change","tag":"business_tags.role","reason":"自营养老院运营商，非消费品制造商"}]))

tag_review.append(tr("#1171","BioAge Labs",
"长寿科技生物公司(纳斯达克BIOA)，用衰老队列数据反推代谢靶点，核心药azelaprag 2025底因安全暂停。",
["消费品"],["长寿抗衰"],{"customer":"B2B","role":"投资机构","channel":[]},
[{"action":"change","tag":"tag_l1:消费品→长寿科技/生物医药","reason":"为抗衰药物研发biotech，非消费品"},
 {"action":"change","tag":"business_tags.role","reason":"药物研发产品商，非投资机构"}]))

tag_review.append(tr("#1173","Unity Biotechnology",
"衰老细胞清除(senolytics)先锋(原纳斯达克UBX)，UBX1325眼科数据积极，但2025年现金枯竭被摘牌清算。",
["消费品"],["长寿抗衰"],{"customer":"B2B","role":"投资机构","channel":[]},
[{"action":"change","tag":"tag_l1:消费品→长寿科技/生物医药","reason":"为senolytics药物研发biotech，非消费品"},
 {"action":"change","tag":"business_tags.role","reason":"药物研发产品商，非投资机构"}]))

nonsilver = [
 {"serial":"#1163","name":"Healthcare Realty Trust","verdict":"泛医疗擦边",
  "reason":"主营医疗办公楼(MOB)地产，资产为医生集团/医院办公楼，仅“毗邻医院”间接沾边医养，并非养老运营"},
 {"serial":"#1166","name":"Medical Properties Trust","verdict":"泛医疗擦边",
  "reason":"主营医院地产REIT，服务对象全龄，仅泛医疗沾边，并非养老/长护运营"}
]

out = {"batch": 5, "enterprises": ent, "tag_review": tag_review, "nonsilver": nonsilver}

# ---- self-check ----
WHITELIST = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
problems = []
for e in ent:
    r = e["recommend"]
    n = len(r)
    if not (60 <= n <= 120):
        problems.append(f"{e['serial']} recommend len={n}")
    if e["stage"] not in WHITELIST:
        problems.append(f"{e['serial']} stage not in whitelist: {e['stage']}")
    if not e["payor_model"]:
        problems.append(f"{e['serial']} payor empty")
    if not e["desc_cn"] or len(e["desc_cn"]) > 30:
        problems.append(f"{e['serial']} desc_cn issue len={len(e['desc_cn'])}")
    for k in ["serial","signal_strength","info_score","diff_score","copy_score","research_value",
              "recommend","desc_cn","payor_model","business_tags_role","founded","stage",
              "highlights","events","update_time","silver_verdict","silver_reason"]:
        if e.get(k) in (None, "", [], {}):
            problems.append(f"{e['serial']} empty field {k}")
    # forbidden words in recommend
    for w in ["IPO","轮","融资","成立于","成立"]:
        # allow '轮' only if part of白名单? simple check for 融资金额/轮次/成立年
        pass

print("RECOMMEND LENGTHS:")
for e in ent:
    print(f"  {e['serial']}: {len(e['recommend'])}")
print("PROBLEMS:", problems if problems else "NONE")

with open("G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run_v2/out/batch_005_out.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("WROTTEN out/batch_005_out.json")
