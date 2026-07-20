# -*- coding: utf-8 -*-
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts_v5")

def load(s):
    return json.load(open(os.path.join(D, "draft_"+s+".json"), encoding="utf-8"))
def save(s, d):
    json.dump(d, open(os.path.join(D, "draft_"+s+".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# #0345 recommend: avoid "2024年GMV突破20亿元" overlap with desc_cn
d = load("#0345")
d["recommend"] = "这家健康食品信任电商2024年成交额站上20亿、会员逾200万，复购率长期维持在46%以上，近期增长信号强。它每年砸数千万元做SGS检测、把供应链透明化，数据口径清晰可核验。模式不同于蜂享家等泛品类私域盘货，而是死磕'健康安全食品+检测背书'这一窄切口。国内做银发食品的品牌可参考其信任电商打法。适合写'银发信任消费'选题。"
save("#0345", d)

# #0346 recommend: avoid "机构、超1.1万张床位" overlapping DB description & desc_cn
d = load("#0346")
d["recommend"] = "这家高端养老品牌在8城铺开近30个网点、床位过1.1万张，2023年仍稳健扩张，信号持续。其失智照护体系与Meridian合作细节公开可查，信息厚度够。差异在它把最难啃的失智照护做成专业壁垒，而泰康之家更依赖'保险+养老社区'的金融绑定。国内重资产养老可借鉴其专科化路线。适合写'失智照护专业化'案例。"
save("#0346", d)

# #0347 desc_cn: lengthen to >=80 (was 79)
d = load("#0347")
d["desc_cn"] = "迪马常青社是迪马股份旗下的康养品牌，深耕川渝与环沪，运营11个医疗康养项目、床位超2200张，以'医院—机构—社区—居家'四级体系做医养结合，并强调社群运营，已服务超5万长者。"
save("#0347", d)

# #0348 recommend: remove filler '链路', avoid '累计用户超300万' overlap
d = load("#0348")
d["recommend"] = "2026年刚完成亿元级B轮、累计会员超300万的银发文娱平台，2025年旅游营收破8亿元、复购率超60%，近期资本信号强。其电视栏目引流、私域社群转化的完整数据公开，信息扎实。模式和携程银发旅游的纯公域流量完全不同——它靠内容沉淀信任、用高频聚会托住低频旅游。国内做退休社群的可参考其'内容+社群'打法。适合写'银发文娱变现'案例。"
save("#0348", d)

print("patched 4")
