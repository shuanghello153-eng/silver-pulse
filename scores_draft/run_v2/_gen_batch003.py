# -*- coding: utf-8 -*-
import json

SIG = 6.55
WHITELIST = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
FORBIDDEN_NAMES = ["The Villages","Riverspring","BrightSpring","Caredoc","CVS","GoodRx","One Medical","SCI","Nikko Travel","镰仓新书","Best Buy Health","Encompass Health","百思买","亚马逊"]

# serial: (info, diff, copy, rv)
SCORES = {
 "#0557":(8.0,8.0,7.0,73.7),
 "#0558":(5.0,6.0,6.0,58.7),
 "#0647":(8.0,7.0,5.0,67.7),
 "#0654":(7.0,8.0,8.0,72.6),
 "#0678":(10,7.0,5.0,73.7),
 "#0712":(7.0,4.0,5.0,58.6),
 "#0810":(9.0,6.0,6.0,70.6),
 "#0840":(9.0,7.0,5.0,70.6),
 "#0935":(6.0,6.0,7.0,63.7),
 "#0938":(7.0,7.0,6.0,66.7),
 "#0945":(7.0,8.0,8.0,72.6),
 "#0946":(9.0,7.0,5.0,70.6),
}

E = {}  # serial -> full record

E["#0557"] = {
 "serial":"#0557","signal_strength":SIG,
 "recommend":"信号强、覆盖全美且运营数据透明，信息量足；差异化在把退休社区做成生活方式会员而非卖房、社交密度极高，可复制性受国内土地与会员制成熟度拖累——最该学的是以社群活动为内核、用月度设施费持续变现的活跃养老路径。",
 "desc_cn":"全球最大55+活跃退休社区，社群会员制",
 "payor_model":"个人自费（购房+月度设施会员费）",
 "business_tags_role":"运营商",
 "founded":1980,"stage":"已上市",
 "highlights":["全球最大55+活跃退休社区，居民超16万",
   "月度设施会员费+社区发展区(CDD)自治治理模式",
   "高尔夫球车交通网+每周3000+活动构建强社交"],
 "events":[{"date":"2023","text":"2022-2023居民同比增长约4.7%，持续扩张"}],
 "silver_verdict":"核心银发","silver_reason":"聚焦55+活力老人的社交与生活方式的巨型退休社区",
}
E["#0558"] = {
 "serial":"#0558","signal_strength":SIG,
 "recommend":"信号中、非营利架构下运营透明但财务披露有限，信息量一般；差异化在把VR/机器人等适老科技真正转化为护理ROI并做全周期照护，可复制性受国内非营利土壤薄弱拖累——最该学的是以可量化成效倒逼科技采购的落地方法论。",
 "desc_cn":"纽约百年非营利连续照护机构，适老科技落地",
 "payor_model":"政府医保(Medicare/Medicaid 专业护理)+个人自付（月费/入住费）",
 "business_tags_role":"服务商",
 "founded":1989,"stage":"未搜到",
 "highlights":["非营利连续照护（独立/协助/记忆/专业护理）全周期",
   "VR疗法、机器人等适老科技以ROI为导向落地",
   "设Medicaid补助协助生活计划，覆盖中低收入长者"],
 "events":[{"date":"2026","text":"CEO分享 Hauser Care Connect 全国科技照护模型"}],
 "silver_verdict":"核心银发","silver_reason":"非营利连续照护+适老科技落地的老年护理机构",
}
E["#0647"] = {
 "serial":"#0647","signal_strength":SIG,
 "recommend":"信号强、全美50州覆盖且年报与论文透明，信息量足；差异化在把药房与上门医护垂直整合、用循证数据做居家全周期照护，可复制性受国内支付与居家护理供给薄弱拖累——最该学的是药+护+数据一体、对接按效付费的居家整合路径。",
 "desc_cn":"居家整合药+护+数据的复杂慢病照护平台",
 "payor_model":"政府医保(Medicare/Medicaid)+商业保险",
 "business_tags_role":"服务商",
 "founded":1996,"stage":"已上市",
 "highlights":["全美50州、日服务超46万复杂/老年慢病患者",
   "药房(PharMerica)与上门医护垂直整合",
   "发表十余篇同行评审研究，循证驱动质量改进"],
 "events":[{"date":"2024-01","text":"登陆纳斯达克(BTSG)，KVK+Walgreens体系分拆上市"}],
 "silver_verdict":"核心银发","silver_reason":"面向老年与复杂慢病人群的居家整合医疗平台",
}
E["#0654"] = {
 "serial":"#0654","signal_strength":SIG,
 "recommend":"信号强、月服务万级用户且GMV透明，信息量足；差异化在做成覆盖住宅/护理/上门的全生命周期平台并牵手资管做高端养老地产，可复制性高——最该学的是区域起家+长护险支付+轻重资产结合的养老平台路径。",
 "desc_cn":"韩国第一全生命周期养老护理平台",
 "payor_model":"政府长期护理保险+个人自付",
 "business_tags_role":"平台",
 "founded":2018,"stage":"B轮",
 "highlights":["韩国养老护理行业IPO第一股候选，区域(釜山)起步",
   "约3000名护理协调员、月均超1万用户、累计GMV超3000亿韩元",
   "联手景顺(Invesco)合资开发高端养老地产品牌"],
 "events":[{"date":"2025-10","text":"签署310亿韩元养老地产项目融资(PF)，韩国首例"},
   {"date":"2027","text":"目标IPO，已选定韩国投资证券为主承销商"}],
 "silver_verdict":"核心银发","silver_reason":"覆盖住宅/护理/上门的全生命周期韩国养老平台",
}
E["#0678"] = {
 "serial":"#0678","signal_strength":SIG,
 "recommend":"信号极强、并购与财报高度透明，信息量足；差异化在把药店、保险与老年初级保健垂直整合、用价值医疗绑定慢病老人，可复制性受国内医药险分业监管拖累——最该学的是药房即养老健康入口、保险支付闭环的整合路径。",
 "desc_cn":"医药险一体的老年价值医疗整合平台",
 "payor_model":"商业保险(Medicare Advantage/Aetna)+政府医保(Medicare)",
 "business_tags_role":"服务商",
 "founded":1963,"stage":"已上市",
 "highlights":["自有Aetna保险+Oak Street老年初级保健+Caremark PBM",
   "Oak Street以价值医疗做老人初级保健，2026年将超300中心",
   "药店与诊所同址，药师与医生每日协同管慢病"],
 "events":[{"date":"2023","text":"以106亿美元收购 Oak Street Health，补全老年初级保健"},
   {"date":"2024","text":"在CVS门店内铺开 Oak Street 老年健康中心新店型"}],
 "silver_verdict":"核心银发","silver_reason":"医药险垂直整合、聚焦老年价值医疗的养老健康巨头",
}
E["#0712"] = {
 "serial":"#0712","signal_strength":SIG,
 "recommend":"信号中、公开财报透明但业务偏向通用医疗，信息量一般；差异化在用药价透明与省钱券降低自付，可复制性受国内药价与处方流转管制拖累——最该学的是以比价+会员帮慢病老人控药费的轻量切入，但需本地化支付结构。",
 "desc_cn":"处方药比价省钱平台，惠及慢病老人",
 "payor_model":"个人自费（处方药自付+Gold会员订阅）",
 "business_tags_role":"平台",
 "founded":2011,"stage":"已上市",
 "highlights":["处方药比价+省钱券+Gold会员，降低自付药费",
   "NASDAQ上市，靠PBM返点/订阅/药企广告变现",
   "慢病多重用药老人群体为高频使用者"],
 "events":[{"date":"2024","text":"公布2024年报，处方药省钱平台持续运营"}],
 "silver_verdict":"泛医疗擦边","silver_reason":"处方药省钱为通用医疗工具，老年用户占比高但非银发专属业务",
}
E["#0810"] = {
 "serial":"#0810","signal_strength":SIG,
 "recommend":"信号中、被科技巨头收购后路径清晰，信息量足；差异化在会员制+数字化便捷初级保健，可复制性较高——最该学的是用订阅与线上体验重构门诊入口，但需叠加老年慢病管理才更贴银发。",
 "desc_cn":"会员制数字化初级保健（被亚马逊收购）",
 "payor_model":"个人会员费+商业保险(含Medicare Advantage)",
 "business_tags_role":"平台",
 "founded":2007,"stage":"被收购",
 "highlights":["会员制+年费+保险，数字化便捷门诊",
   "2023年被亚马逊收购，并入其健康生态",
   "虚拟+到店全科，覆盖含老人在内全龄人群"],
 "events":[{"date":"2023","text":"被亚马逊以约39亿美元收购"}],
 "silver_verdict":"泛医疗擦边","silver_reason":"会员制数字化全科初级保健，服务全龄含老人但业务非银发专属",
}
E["#0840"] = {
 "serial":"#0840","signal_strength":SIG,
 "recommend":"信号强、财报透明且网点规模清晰，信息量足；差异化在把殡葬做成全国连锁+预付费信托的规模化生意，可复制性受国内殡葬公益属性与管制拖累——最该学的是预付费锁定+标准化服务的终老消费路径。",
 "desc_cn":"北美最大殡葬连锁，预付费信托模式",
 "payor_model":"个人自付（殡葬/墓园+预付费）",
 "business_tags_role":"运营商",
 "founded":1962,"stage":"已上市",
 "highlights":["北美最大殡葬服务商，2000+设施、年服务30万家庭",
   "预付费(pre-need)保险/信托锁定终身需求",
   "NYSE上市，规模与品牌护城河显著"],
 "events":[{"date":"2025-02","text":"发布2024 Q4财报，营收同比+4%"}],
 "silver_verdict":"核心银发","silver_reason":"面向终老消费的北美最大殡葬连锁服务商",
}
E["#0935"] = {
 "serial":"#0935","signal_strength":SIG,
 "recommend":"信号中、被百货集团收购后定位清晰，信息量一般；差异化在聚焦富裕老人做高端主题旅行、复购率超七成，可复制性较高——最该学的是小而美+强复购+精神社交的高净值老年文旅路径。",
 "desc_cn":"高端富裕老人主题旅行，复购率超七成",
 "payor_model":"个人自费（高端旅行套餐）",
 "business_tags_role":"服务商",
 "founded":1976,"stage":"被收购",
 "highlights":["九成以上客群为60+富裕老人，年服务约5000人",
   "高端海外/国内/邮轮主题旅行，复购率70%+",
   "2017年被三越伊势丹收购，协同高端客群"],
 "events":[{"date":"2017","text":"被三越伊势丹集团收购控股"}],
 "silver_verdict":"核心银发","silver_reason":"聚焦富裕老人的高端主题旅行，客群九成以上为60+",
}
E["#0938"] = {
 "serial":"#0938","signal_strength":SIG,
 "recommend":"信号中、公开门户数据透明但偏媒体属性，信息量一般；差异化在把终活(葬仪/墓/佛坛/相续/介护)做成一站式信息撮合平台并向周边延展，可复制性高——最该学的是以可信信息入口撮合B端服务商、靠推荐佣金变现的终老平台路径。",
 "desc_cn":"终活一站式信息撮合平台（殡葬/墓/介护）",
 "payor_model":"B端机构付费（服务商推荐佣金/广告）+ 个人免费使用",
 "business_tags_role":"平台",
 "founded":1984,"stage":"已上市",
 "highlights":["运营'いい葬儀/いいお墓'等终活门户，推荐佣金+广告变现",
   "多域名相互送客，并拓展保险/不动产/介护周边",
   "2025年承继Ateam'Life.'事业，强化终活综合平台"],
 "events":[{"date":"2025-06","text":"承继Ateam旗下终活综合站'Life.'事业"}],
 "silver_verdict":"核心银发","silver_reason":"围绕终活的一站式信息撮合平台，深度绑定老龄化需求",
}
E["#0945"] = {
 "serial":"#0945","signal_strength":SIG,
 "recommend":"信号中、依托零售巨头渠道清晰，信息量一般；差异化在用PERS/远程监测+极客式上门支持帮老人居家安全，并嵌入Medicare Advantage福利，可复制性高——最该学的是硬件+响应服务+保险/自费支付的居家安全产品化路径。",
 "desc_cn":"居家紧急响应+远程监测的适老科技",
 "payor_model":"商业保险(Medicare Advantage/Medicaid 计划采购)+个人自费(自购PERS)",
 "business_tags_role":"产品商",
 "founded":2018,"stage":"已上市",
 "highlights":["Lively PERS 一键呼叫+跌倒检测，7×24响应",
   "Current Health 做远程患者监测(RPM)",
   "与Medicare Advantage/Medicaid 计划及自费双轨合作"],
 "events":[{"date":"2021","text":"与Regence等Medicare Advantage计划合作提供Lively设备"}],
 "silver_verdict":"核心银发","silver_reason":"以PERS与远程监测服务老人居家安全的适老科技公司",
}
E["#0946"] = {
 "serial":"#0946","signal_strength":SIG,
 "recommend":"信号强、公开披露详尽且患者量清晰，信息量足；差异化在把住院康复做成全国连锁并用远程康复+数据分析优化流程，可复制性受国内康复支付与床位供给拖累——最该学的是连锁康复+居家延伸+数据提质的老年康复路径。",
 "desc_cn":"全美最大住院康复连锁，延伸居家",
 "payor_model":"政府医保(Medicare)+商业保险+个人自付",
 "business_tags_role":"运营商",
 "founded":1984,"stage":"已上市",
 "highlights":["全美最大住院康复(IRF)提供商，2024年服务约25万患者",
   "远程康复+数据分析优化照护流程",
   "成熟连锁体系，并拓展居家健康与临终关怀"],
 "events":[{"date":"2025-04","text":"发布2024年报，住院康复出院量同比+8.3%"}],
 "silver_verdict":"核心银发","silver_reason":"面向老年康复需求的全美最大住院康复连锁",
}

# ---- tag_review ----
def tr(serial, name, intro, old, suggested):
    return {"serial":serial,"name":name,"intro":intro,"old_tags":old,"suggested":suggested}

TAGREVIEW = [
 tr("#0557","The Villages","全球最大55+活跃退休社区，以'生活方式会员'为核心而非单纯卖房，靠强社交与月度设施费变现。",
   {"tag_l1":["养老服务"],"tag_l2":["CCRC"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
   [{"action":"change","tag":"CCRC","reason":"The Villages 是55+活跃退休社区、以生活方式会员为核心，非典型CCRC持续照护，建议改为'活跃养老社区'"},
    {"action":"change","tag":"平台","reason":"实际为大型社区开发商/运营商，business_tags.role 建议改'运营商'"}]),
 tr("#0558","Riverspring Living","纽约百年非营利连续照护机构，以VR/机器人等适老科技落地护理ROI为差异化。",
   {"tag_l1":["养老服务"],"tag_l2":["养老机构","康复医疗"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
   [{"action":"add","tag":"适老科技","reason":"以VR疗法/机器人等AgeTech落地护理ROI为差异化，建议补充标签"}]),
 tr("#0647","BrightSpring Health","面向老年与复杂慢病的居家整合医疗平台，垂直整合药房与上门医护。",
   {"tag_l1":["养老服务"],"tag_l2":["居家护理"],"business_tags":{"customer":"B2B","role":"服务商","channel":[]}},
   [{"action":"add","tag":"居家医疗","reason":"业务核心是药房+上门医护整合的居家医疗，现仅'居家护理'未能涵盖"},
    {"action":"change","tag":"B2B","reason":"通过Medicare/Medicaid服务个人患者，business_tags.customer 建议改'B2B+B2C'"}]),
 tr("#0654","Caredoc","韩国第一全生命周期养老护理平台，覆盖住宅/护理匹配/上门护理并合资布局养老地产。",
   {"tag_l1":["养老服务"],"tag_l2":["居家护理"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
   [{"action":"add","tag":"养老平台","reason":"覆盖住宅/护理匹配/上门的全生命周期平台，'居家护理'过窄"}]),
 tr("#0678","CVS Health","医药险垂直整合的养老健康巨头，自有保险+Aetna与Oak Street老年初级保健。",
   {"tag_l1":["养老服务"],"tag_l2":["诊所"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
   [{"action":"add","tag":"老年初级保健","reason":"Oak Street 以价值医疗做老人初级保健为核心差异化，建议补充标签"}]),
 tr("#0712","GoodRx","处方药比价省钱平台，靠PBM返点/订阅/广告变现，慢病老人为高频用户。",
   {"tag_l1":["消费品"],"tag_l2":["药品"],"business_tags":{"customer":"未标注","role":"平台","channel":[]}},
   []),
 tr("#0810","One Medical","会员制数字化全科初级保健，2023年被亚马逊收购，服务全龄含老人。",
   {"tag_l1":["养老服务"],"tag_l2":["诊所"],"business_tags":{"customer":"B2C","role":"服务商","channel":[]}},
   [{"action":"change","tag":"养老服务","reason":"会员制全科初级保健服务全龄、非银发专属，归为养老服务易误导，建议改'健康服务'"}]),
 tr("#0840","SCI (Service Corporation International)","北美最大殡葬连锁服务商，以预付费信托锁定终身终老需求。",
   {"tag_l1":["养老服务"],"tag_l2":["殡葬"],"business_tags":{"customer":"未标注","role":"运营商","channel":[]}},
   []),
 tr("#0935","Nikko Travel","聚焦富裕老人的高端主题旅行服务商，客群九成以上为60+、复购率超七成。",
   {"tag_l1":["文娱社交"],"tag_l2":["旅游"],"business_tags":{"customer":"未标注","role":"服务商","channel":[]}},
   []),
 tr("#0938","镰仓新书","围绕终活的一站式信息撮合平台，运营'いい葬儀'等门户、靠推荐佣金与广告变现。",
   {"tag_l1":["养老服务"],"tag_l2":["殡葬"],"business_tags":{"customer":"未标注","role":"平台","channel":[]}},
   [{"action":"add","tag":"终活服务","reason":"业务覆盖葬仪/墓/佛坛/相续/介护一站式终活，'殡葬'过窄"}]),
 tr("#0945","Best Buy Health","以PERS与远程监测服务老人居家安全的适老科技公司，嵌入Medicare Advantage福利。",
   {"tag_l1":["养老服务"],"tag_l2":["远程护理"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
   []),
 tr("#0946","Encompass Health","面向老年康复需求的全美最大住院康复连锁，并拓展居家健康与临终关怀。",
   {"tag_l1":["养老服务"],"tag_l2":["康复医疗"],"business_tags":{"customer":"未标注","role":"运营商","channel":[]}},
   []),
]

NONSILVER = [
 {"serial":"#0712","name":"GoodRx","verdict":"泛医疗擦边","reason":"处方药比价省钱为通用医疗工具，老年用户占比高但非银发专属业务模式"},
 {"serial":"#0810","name":"One Medical","verdict":"泛医疗擦边","reason":"会员制数字化全科初级保健，服务全龄含老人但业务非银发专属"},
]

# ---- assemble ----
enterprises=[]
for s in ["#0557","#0558","#0647","#0654","#0678","#0712","#0810","#0840","#0935","#0938","#0945","#0946"]:
    r=E[s]
    info,diff,copy,rv=SCORES[s]
    rec=dict(r)
    rec["info_score"]=info; rec["diff_score"]=diff; rec["copy_score"]=copy; rec["research_value"]=rv
    rec["update_time"]="2026-07-17"
    enterprises.append(rec)

out={"batch":3,"enterprises":enterprises,"tag_review":TAGREVIEW,"nonsilver":NONSILVER}

# ---- self-check ----
errs=[]
for e in enterprises:
    for k in ["recommend","desc_cn","payor_model","business_tags_role","stage","silver_verdict","silver_reason"]:
        if not e.get(k): errs.append(f"{e['serial']} empty {k}")
    for k in ["info_score","diff_score","copy_score","research_value","signal_strength"]:
        v=e.get(k)
        if not isinstance(v,(int,float)) or not (0<=v<=10 if k!="research_value" else 0<=v<=100): errs.append(f"{e['serial']} bad {k}={v}")
    rec=e["recommend"]
    L=len(rec)
    if not (60<=L<=120): errs.append(f"{e['serial']} recommend len={L}")
    for nm in FORBIDDEN_NAMES:
        if nm in rec: errs.append(f"{e['serial']} recommend contains name '{nm}'")
    if any(w in rec for w in ["轮","融资","上市","亿","成立于","成立年份","万美元"]): errs.append(f"{e['serial']} recommend has forbidden word")
    if not all(d in rec for d in ["信号","信息量","差异化","可复制"]): errs.append(f"{e['serial']} recommend missing 4-dim keyword")
    if len(e["desc_cn"])>30: errs.append(f"{e['serial']} desc_cn len={len(e['desc_cn'])}")
    if e["stage"] not in WHITELIST: errs.append(f"{e['serial']} stage {e['stage']} not whitelist")
    if not (isinstance(e["founded"],int) or e["founded"]=="未搜到"): errs.append(f"{e['serial']} founded bad {e['founded']}")
    if not e["highlights"]: errs.append(f"{e['serial']} no highlights")
    if not e["events"]: errs.append(f"{e['serial']} no events")

print("=== SELF-CHECK (recommend lengths) ===")
for e in enterprises:
    print(e["serial"], len(e["recommend"]), "OK" if 60<=len(e["recommend"])<=120 else "BAD")
print("=== ERRORS ===")
if not errs:
    print("NONE - all checks passed")
else:
    for x in errs: print(" -", x)

if not errs:
    with open("G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/run_v2/out/batch_003_out.json","w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
    print("WROTE out/batch_003_out.json")
else:
    print("NOT WRITTEN due to errors")
