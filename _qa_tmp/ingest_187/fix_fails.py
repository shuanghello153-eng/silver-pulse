# -*- coding: utf-8 -*-
"""修复 validate_all 报出的13家失败：
   A. tag_l1与tag_l2不一致 → 对全137家按 _l2_l1.json 统一重算 tag_l1（根治）
   B/C. 7家 recommend 改写（避开状态词/黑话/融资数字，保留原意）
   D. 4家库内重复 → 从分片剔除并登记 _dropped_indb.json
   原地改写 draft_out/*.json。"""
import json, os, glob

ROOT = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
HERE = os.path.join(ROOT, "_qa_tmp", "ingest_187")
L2L1 = json.load(open(os.path.join(ROOT, "data/enterprise/_l2_l1.json"), encoding="utf-8"))
STRAGGLER_L1 = {"养老社区": "养老服务", "社区居家": "养老服务",
                "保险经纪": "金融保险", "健康管理": "医疗健康"}

def derive_l1(t2):
    out = []
    for b in t2:
        l1 = L2L1.get(b)
        if isinstance(l1, list):
            l1 = l1[0] if l1 else None
        if not l1:
            l1 = STRAGGLER_L1.get(b)
        if l1 and l1 not in out:
            out.append(l1)
    return out

# B/C：7家 recommend 改写
REWRITE = {
"NaviHealth": "衔接医院出院与社区康复的『院后一段』，由支付方买单去做急性后期照护导航，是控制再入院率的关键环节。国内在病人出院后转接社区、制定出院计划上仍在摸索，这类以支付方为锚点的协调机制值得对照其运行逻辑。",
"HealthBeacon": "注射类慢病用药依从性管理在国内糖尿病与自免患者群中同样突出，硬件结合数据的方案比单纯提醒更能形成管理回路，其把设备嵌入医保报销与药企渠道的打法值得对照。",
"ベネッセホールディングス（Benesse HD）": "教育巨头引入海外长期资本联手创始家族做深度重整，转身押注教育与长照两大主业，这类『成熟龙头借外部资本重塑业务』的案例，是理解养老资产为何吸引长期资金的好切口；它把教育领域积累的会员与品牌迁移到养老的路径，也给国内跨界做养老的企业提供现实参照。",
"セントケア・ホールディングス（Saint-Care）": "上门介护龙头近期完成一轮资本运作，是观察日本居家照护赛道资本动向的新鲜案例；上门介护人力重、单值低，它能长期跑通并获得资本青睐，其排班效率与访问看护的搭配，对正在发力居家上门护理的国内企业是很有时效性的参照。",
"Estia Health": "住宅式养老机构运营商的公开财报与监管披露，便于追踪单床模型与人力成本结构；认知症与安宁服务线对国内机构的细分定位有参照，其监管框架也适合对照了解。",
"Regis Healthcare": "全国化运营多年的护理集团，机构养老与居家照护双线协同可作为连锁化样本；公开披露使单店经济与区域密度数据透明，利于分析规模化养老服务的成本曲线。",
"CarePort Health": "聚焦『出院到居家』这一最易断档的衔接环节，用数据打通机构间转诊，后被更大的医疗IT公司整合。国内在病人出院后转接社区、制定出院计划上同样薄弱，其衔接逻辑有参照意义。",
}

# D：库内重复，剔除
DROP = {"RetiSpec", "Sensi.ai", "DUOS", "HomeThrive"}

dropped = []
n_rec, n_l1, n_drop = 0, 0, 0
for fp in glob.glob(os.path.join(HERE, "draft_out", "*.json")):
    d = json.load(open(fp, encoding="utf-8"))
    keep = []
    for r in d:
        nm = r.get("name")
        if nm in DROP:
            r["_srcfile"] = os.path.basename(fp)
            dropped.append(r); n_drop += 1
            continue
        # A: 重算 tag_l1
        t2 = r.get("tag_l2") or []
        if isinstance(t2, str): t2 = [t2]
        new_l1 = derive_l1(t2)
        if new_l1 and new_l1 != (r.get("tag_l1") or []):
            r["tag_l1"] = new_l1; n_l1 += 1
        # B/C: 改写 recommend
        if nm in REWRITE:
            r["recommend"] = REWRITE[nm]; n_rec += 1
        keep.append(r)
    json.dump(keep, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

json.dump(dropped, open(os.path.join(HERE, "_dropped_indb.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"tag_l1重算 {n_l1} 家 | recommend改写 {n_rec} 家 | 剔除库内重复 {n_drop} 家")
print("剔除清单:", [x.get("name") for x in dropped])
