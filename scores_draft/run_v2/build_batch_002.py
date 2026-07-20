# -*- coding: utf-8 -*-
import json, re, os

BASE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
by = {e["serial"]: e for e in json.load(open(DB, encoding="utf-8"))}

def ga(s, k, default=None):
    return by[s].get(k, default)

# ---- recommend (60~120中文字, 含四维视角, 无企业名/融资轮/成立年) ----
REC = {
"#0394": "信号中等偏稳；信息量足（年报公开、市占率多年居首）；差异化在成人失禁细分龙头与自主品牌出海；可复制性看长护险全国铺开，国内创业者最该学'细分刚需+标准话语权'打法。",
"#0397": "信号强（退休俱乐部刷屏）；信息透明（掌门人亲自披露康养布局）；差异化在复用教育基因做银发文旅+本地社交；可复制性看轻资产与内容流量，国内创业者可学'品牌+内容获客'切入退休人群。",
"#0401": "信号中等；信息较透明（老博会首秀银发专区）；差异化在婚恋平台基因切入中老年'重交友轻相亲'；可复制性看社区本地活动+红娘服务，国内创业者可学'高频社交引流、低频红娘变现'。",
"#0436": "信号稳（财报全披露）；信息密度高（营收规模大、海外增逾三成）；差异化在家用医疗器械全品类+进口替代；可复制性看CGM与可穿戴新品出海，国内创业者最该学'渠道下沉+研发压强'的制造壁垒。",
"#0447": "信号稳（港交所年报透明）；信息量足（收入增一成、海外占两成）；差异化在数字骨科技术闭环（3D打印+手术机器人）；可复制性受集采进口替代驱动，国内创业者可学'硬科技+临床绑定'的器械出海路径。",
"#0475": "信号新但强（AI模型数据亮眼）；信息逐步披露（PACE中心运营结果）；差异化在文化适配型PACE+AI中台降本；可复制性有限（依赖美国医保），但国内创业者可学'整合照护+运营系统化'切长护险。",
"#0493": "信号极强（上市公司财报详尽）；信息量高（多次收购与剥离全披露）；差异化在零售跨界老年科技的'试错-剥离'反例；可复制性看其止损逻辑，国内零售巨头可学'小步试错、果断砍掉错配业务'。",
"#1152": "信号极强（REIT财报与投资者关系全透明）；信息密度最高；差异化偏弱（收租模式成熟不反共识）；可复制性看'Right Market/Asset/Operator'逻辑，国内险资与养老地产基金可学其资产组合与出租率管理。",
"#0470": "信号强（IPO后财报密集）；信息量足（营收与减亏数据公开）；差异化偏弱（数字MSK顺常识）；可复制性在支付方——靠雇主采购福利、会员零自付跑通，国内创业者最该学'雇主福利+降手术率'付费闭环。",
"#0392": "信号强（资本与出海报道密集）；信息透明（独角兽估值、落地马来西亚国家级项目）；差异化在康复跨界人形机器人双线；可复制性看其分层出海，国内创业者可学'临床落地反哺具身智能'。",
"#0495": "信号中等；信息透明（年报与季报全披露）；差异化在重资产养老运营的规模壁垒；可复制性弱（盈利难题凸显），但国内创业者最该学其'退出低效社区、聚焦密度与运营效率'的瘦身打法。",
"#0497": "信号中等；信息偏少（被收购后披露有限）；差异化在照护匹配平台基因+老年照护规划顾问；可复制性看其'家庭订阅+企业福利'双付费，国内创业者可学'平台撮合+重度服务变现'。",
}

# ---- desc_cn (<=30字, 无企业名/成立于/融资/轮) ----
DESC = {
"#0394": "成人失禁护理龙头，银发刚需消费品",
"#0397": "银发文旅与退休社交，康养旅居品牌",
"#0401": "婚恋交友平台，中老年相亲与银发社交",
"#0436": "家用与机构医疗器械，失能护理刚需",
"#0447": "骨科植入物龙头，老年关节置换与康复",
"#0475": "美国PACE整合照护运营商，老年慢病",
"#0493": "老年科技与居家照护，PERS紧急响应",
"#1152": "医疗地产REIT，持有运营养老社区",
"#0470": "数字肌肉骨骼疼痛护理，慢病康复",
"#0392": "康复机器人跨界通用人形机器人",
"#0495": "全谱系养老社区运营商，独立辅助生活",
"#0497": "全球家庭照护匹配平台，含老年规划",
}

ROLE = {
"#0394":"产品商","#0397":"服务商","#0401":"平台","#0436":"产品商","#0447":"产品商",
"#0475":"运营商","#0493":"服务商","#1152":"投资机构","#0470":"服务商","#0392":"产品商",
"#0495":"运营商","#0497":"平台",
}

STAGE = {
"#0394":"已上市","#0397":"成长期","#0401":"已上市","#0436":"已上市","#0447":"已上市",
"#0475":"成长期","#0493":"已上市","#1152":"已上市","#0470":"已上市","#0392":"成长期",
"#0495":"已上市","#0497":"被收购",
}

FOUNDED = {
"#0394":2001,"#0397":2023,"#0401":2005,"#0436":1998,"#0447":2003,"#0475":2021,
"#0493":1966,"#1152":1970,"#0470":2014,"#0392":2015,"#0495":1978,"#0497":2006,
}

PAYOR = {
"#0394":"个人自费为主+B端机构采购",
"#0397":"个人自费(C端文旅/课程消费)",
"#0401":"个人自费(会员/红娘服务)",
"#0436":"B端机构采购+个人自费+医保",
"#0447":"B端医院采购+医保支付",
"#0475":"政府医保(Medicare/Medicaid)支付+PACE",
"#0493":"混合（Lively/PERS+个人自付；亦B端与医疗系统合作居家照护）",
"#1152":"B端机构付费为主（向养老运营商收租/分成）",
"#0470":"B端机构付费（雇主与健康计划采购，会员零自付）+拓展Medicare Advantage",
"#0392":"混合（康复机器人B端机构采购为主，C端辅助器具个人自付）",
"#0495":"个人自费(社区月费)+长期护理保险/医保部分覆盖",
"#0497":"个人自费(家庭订阅)+B端企业福利采购(Care@Work)",
}

SILVER_V = {s:"核心银发" for s in REC}
SILVER_R = {
"#0394":"成人失禁护理是老年刚需消费品，直接服务失能/半失能老人群体。",
"#0397":"聚焦中老年文旅、康养旅居与退休群体兴趣社交，银发属性明确。",
"#0401":"专门布局中老年相亲交友，属银发社交/文娱服务范畴。",
"#0436":"轮椅/护理器械是老年康复与居家照护的刚需硬件。",
"#0447":"关节置换等骨科植入需求随老龄化显著增长，直接服务老年患者。",
"#0475":"专注老年慢病整合照护，典型银发健康服务，服务双重资格老人群体。",
"#0493":"Best Buy Health以Lively/PERS+紧急响应切入老年安全照护，银发属性明确。",
"#1152":"持有并运营养老社区/医疗地产，是美国银发地产资本闭环的核心标的。",
"#0470":"MSK疼痛与术后康复在老年群体高发，并主动覆盖Medicare Advantage老年付费方。",
"#0392":"康复机器人直接服务于老年偏瘫/术后康复，是银发智能硬件核心赛道。",
"#0495":"全美最大养老社区运营商，独立/辅助生活与记忆照护直接服务老年人。",
"#0497":"含老年照护匹配与规划顾问服务，切入银发家庭照护刚需。",
}

# ---- tag_review ----
TAG_REVIEW = [
 {"serial":"#0394","name":"可靠护理","intro":"国内成人失禁护理用品龙头（创业板301009），连续多年市占率第一，近年升级为'银发生态构建者'，自主品牌出海占比近四成。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["尿失禁","纸尿裤"],"business_tags":{"customer":"B2B","role":"产品商","channel":[]}},
  "suggested":[{"action":"add","tag":"成人失禁护理","reason":"公司核心品类为成人失禁护理，现行'尿失禁/纸尿裤'偏产品词，补一个品类级l2更利于检索。"},
               {"action":"change","tag":"尿失禁→失禁护理","reason":"'失禁护理'比'尿失禁'更贴合其全人群(含轻度失禁)产品矩阵定位。"}]},
 {"serial":"#0397","name":"新东方文旅","intro":"新东方旗下银发文旅品牌，2023年成立，以退休俱乐部、康养旅居、老年大学切入中老年文旅与社交。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["CCRC"],"business_tags":{"customer":"B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"del","tag":"CCRC","reason":"实际业务为文旅+退休俱乐部社交与康养旅居，并非CCRC持续照料退休社区，标签错位。"},
               {"action":"add","tag":"银发文旅","reason":"核心定位即银发文旅。"},
               {"action":"add","tag":"退休社交","reason":"退休俱乐部以兴趣课程+本地社交为主，是重要银发切点。"}]},
 {"serial":"#0401","name":"百合佳缘","intro":"百合网与世纪佳缘合并的婚恋交友平台，复星控股，注册用户超4亿，专设中老年相亲与银发社交场景。",
  "old_tags":{"tag_l1":["文娱社交"],"tag_l2":["相亲"],"business_tags":{"customer":"B2B","role":"平台","channel":[]}},
  "suggested":[{"action":"add","tag":"中老年相亲","reason":"专门布局中老年相亲垂直场景，应单列l2以凸显银发属性。"}]},
 {"serial":"#0436","name":"鱼跃医疗","intro":"A股家用医疗器械龙头（002223），产品涵盖呼吸、血糖、血压、轮椅等，2025年营收近80亿、海外增三成。",
  "old_tags":{"tag_l1":["康复辅具"],"tag_l2":["轮椅"],"business_tags":{"customer":"B2B","role":"制造商","channel":[]}},
  "suggested":[{"action":"add","tag":"家用医疗器械","reason":"产品远不止轮椅，呼吸/血糖/血压监测全品类均属家用医疗器械，l2应补品类级标签。"},
               {"action":"add","tag":"慢病监测","reason":"血糖/血压等慢病居家监测是其核心银发场景。"}]},
 {"serial":"#0447","name":"爱康医疗","intro":"港股骨科植入物龙头（1789.HK），关节置换市占领先，数字骨科(3D打印+iCOS+手术机器人)形成技术闭环。",
  "old_tags":{"tag_l1":["康复辅具"],"tag_l2":["康复器械"],"business_tags":{"customer":"B2B","role":"制造商","channel":[]}},
  "suggested":[{"action":"change","tag":"康复器械→骨科植入","reason":"核心是关节置换植入物与数字骨科，非一般康复器械，原标签易误导。"},
               {"action":"add","tag":"手术机器人","reason":"K3/K3+骨科手术机器人已商业化，是重要差异化标签。"}]},
 {"serial":"#0475","name":"Seen Health","intro":"美国PACE整合照护运营商，2021年创立、2025年首个中心落地，以文化适配+AI中台服务亚裔等少数族裔老年慢病群体。",
  "old_tags":{"tag_l1":["养老服务","金融保险"],"tag_l2":["慢病管理","保险"],"business_tags":{"customer":"B2B+B2C","role":"运营商","channel":[]}},
  "suggested":[{"action":"add","tag":"PACE整合照护","reason":"核心模式为PACE全人整合照护，应作为l2主标签。"}]},
 {"serial":"#0493","name":"百思买","intro":"全球消费电子零售巨头，通过Best Buy Health以Lively/PERS+紧急响应切入老年安全照护，并曾收购GreatCall、Current Health。",
  "old_tags":{"tag_l1":["消费品"],"tag_l2":["电商","零售"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"add","tag":"老年科技","reason":"银发切入点为Best Buy Health与Lively/PERS，补l2凸显银发属性。"},
               {"action":"add","tag":"PERS紧急响应","reason":"PERS+紧急响应是其老年照护核心产品，值得单列。"}]},
 {"serial":"#1152","name":"Welltower","intro":"全球最大医疗地产REIT（纽交所WELL），持有运营养老社区、医疗办公楼与长期护理地产，是美国银发地产定价锚。",
  "old_tags":{"tag_l1":["投资机构"],"tag_l2":["养老REIT"],"business_tags":{"customer":"未标注","role":"投资机构","channel":[]}},
  "suggested":[]},
 {"serial":"#0470","name":"Hinge Health","intro":"美国数字肌肉骨骼(MSK)疼痛护理龙头，纽交所上市(HNGE)，以AI动作追踪+可穿戴为自保雇主与健康计划降手术率。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["远程医疗","慢病管理"],"business_tags":{"customer":"B2B+B2C","role":"服务商","channel":[]}},
  "suggested":[{"action":"add","tag":"数字疗法","reason":"以数字化MSK护理+可穿戴实现临床结果，属数字疗法范式，应补l2。"}]},
 {"serial":"#0392","name":"傅里叶智能","intro":"上海康复机器人公司，双线布局康复机器人与人形机器人(GR系列)，估值冲80亿的具身智能独角兽，出海落地马来西亚国家级项目。",
  "old_tags":{"tag_l1":["康复辅具"],"tag_l2":["康复器械","机器人"],"business_tags":{"customer":"B2B+B2C","role":"产品商","channel":[]}},
  "suggested":[{"action":"add","tag":"人形机器人","reason":"已跨界通用人形机器人并量产交付，是核心差异化，应单列l2。"}]},
 {"serial":"#0495","name":"Brookdale Senior Living","intro":"全美最大养老社区运营商（NYSE:BKD），提供独立/辅助生活、记忆照护与CCRC，近年战略收缩聚焦运营效率。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["康养地产"],"business_tags":{"customer":"B2B+B2C","role":"运营商","channel":[]}},
  "suggested":[{"action":"add","tag":"记忆照护","reason":"提供阿尔茨海默记忆照护与CCRC，补l2更完整。"}]},
 {"serial":"#0497","name":"Care.com","intro":"全球家庭照护在线匹配平台，2020年被IAC收购，含育儿/养老/成人照护，并推Senior Care Advisor老年照护规划。",
  "old_tags":{"tag_l1":["养老服务"],"tag_l2":["家政"],"business_tags":{"customer":"B2B+B2C","role":"平台","channel":[]}},
  "suggested":[{"action":"add","tag":"老年照护规划","reason":"Senior Care Advisor为老年家庭提供照护规划，是明确银发切点，应补l2。"}]},
]

NONSILVER = []

# ---- assemble enterprises ----
enterprises = []
for s in REC:
    e = by[s]
    enterprises.append({
        "serial": s,
        "signal_strength": e["signal_strength"],
        "info_score": e["info_score"],
        "diff_score": e["diff_score"],
        "copy_score": e["copy_score"],
        "research_value": e["research_value"],
        "recommend": REC[s],
        "desc_cn": DESC[s],
        "payor_model": PAYOR[s],
        "business_tags_role": ROLE[s],
        "founded": FOUNDED[s],
        "stage": STAGE[s],
        "highlights": e["highlights"],
        "events": e["events"],
        "update_time": "2026-07-17",
        "silver_verdict": SILVER_V[s],
        "silver_reason": SILVER_R[s],
    })

out = {"batch": 2, "enterprises": enterprises, "tag_review": TAG_REVIEW, "nonsilver": NONSILVER}

# ================= SELF-CHECK =================
WHITELIST = {"种子期","天使","Pre-A","A轮","B轮","C轮","成长期","已上市","被收购","未搜到"}
SIG_KW=["信号"]; INFO_KW=["信息","资料","披露","数据","透明度","公开"]
DIFF_KW=["差异","独特","打法","模式","定位","反常识","壁垒","亮点"]
COPY_KW=["复制","借鉴","可学","照搬","落地","国内","抄"]
forbidden = [r"成立于", r"创立于", r"轮次", r"[A-Za-z]?轮(?!椅)",
             r"(融资|募|IPO|ipo|上市)[额次]", r"融[资了]?[约]?\d", r"\d+万?美元",
             r"\d+亿", r"\d+万元", r"\$\d", r"本轮", r"上轮"]
problems=[]
for e in enterprises:
    s=e["serial"]
    for k in ["info_score","diff_score","copy_score"]:
        if not (0<=float(e[k])<=10): problems.append((s,"四维越界",k))
    rec=e["recommend"]; L=len(rec)
    if L<60 or L>120: problems.append((s,"recommend长度",L))
    if any(w in rec for w in SIG_KW)==False: problems.append((s,"rec缺信号",""))
    if any(w in rec for w in INFO_KW)==False: problems.append((s,"rec缺信息",""))
    if any(w in rec for w in DIFF_KW)==False: problems.append((s,"rec缺差异",""))
    if any(w in rec for w in COPY_KW)==False: problems.append((s,"rec缺复制",""))
    for p in forbidden:
        if re.search(p, rec): problems.append((s,"rec禁用词",p)); break
    if e["stage"] not in WHITELIST: problems.append((s,"stage白名单",e["stage"]))
    if not e["payor_model"].strip(): problems.append((s,"payor空",""))
    dc=e["desc_cn"]
    if len(dc)>30: problems.append((s,"desc超30",len(dc)))
    nm=str(e.get("serial")); 
    # name check: compare with original name/name_cn from lib
    oname=str(by[s].get("name") or ""); oncn=str(by[s].get("name_cn") or "")
    if (oname and oname in dc) or (oncn and oncn in dc): problems.append((s,"desc含企业名",""))
    if re.search(r"(融资|轮|\$|\d+万)", dc): problems.append((s,"desc禁忌",dc))
    # all non-empty
    for kk in ["recommend","desc_cn","payor_model","business_tags_role","founded","stage","highlights","events","silver_verdict","silver_reason","update_time"]:
        v=e[kk]
        if v is None or (isinstance(v,str) and v.strip()=="") or (isinstance(v,list) and len(v)==0):
            problems.append((s,"空字段",kk))

print("SELF-CHECK problems:", len(problems))
for p in problems: print("  ", p)

if not problems:
    path=os.path.join(BASE,"scores_draft/run_v2/out/batch_002_out.json")
    json.dump(out, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("WROTE", path)
else:
    print("NOT WRITTEN due to problems")
