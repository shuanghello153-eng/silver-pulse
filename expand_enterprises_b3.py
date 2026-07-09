# -*- coding: utf-8 -*-
"""Batch 3: more real AgeTech / silver-economy companies (medical alert,
hospital-at-home, China listed medtech/robots, companion robots, estate
planning). Auto-dedup. Only APPENDS."""
import json

DATA_FILE = "data/enterprise/all_enterprises.json"
SRC = "WebSearch(企业库扩充B3: 公司官网/Crunchbase/Tracxn/PRNewswire等)"

def mk(name, name_cn, region, l1, l2, tags, desc, highlights,
       flatest, ftotal, investors, founded, website, bm):
    return {
        "name": name, "name_cn": name_cn, "region": region,
        "category_l1": l1, "category_l2": l2, "tags": tags,
        "description": desc, "desc_cn": desc, "highlights": highlights,
        "funding_latest": flatest, "funding_total": ftotal,
        "investors": investors, "founded": founded, "value_score": 0,
        "source": SRC,
        "crunchbase_url": "https://www.crunchbase.com/textsearch?q=" + name.replace(" ", "+"),
        "website_url": website, "business_model": bm, "business_model_cn": bm,
        "news_coverage": {"latest_news": [], "news_count": 0,
                          "news_quality": "low", "snippets": [desc]},
    }
def fd(a, r, d, disp): return {"amount": a, "round": r, "date": d, "display": disp}
def ft(t): return {"amount": t, "display": t}
NA = fd("未披露", "", "", "未披露"); NAT = ft("累计未披露")

C = []
# 医疗警报 / 紧急呼叫
C.append(mk("Lively", "", "海外", "养老用品", "医疗警报",
    ["医疗警报", "可穿戴", "上市公司关联"],
    "面向活跃老人的医疗警报与跌倒检测品牌（原GreatCall，已被Best Buy收购），提供紧急呼叫手环与手机。",
    "老年医疗警报品牌（Best Buy体系）",
    NA, ft("被Best Buy收购"), "", "2006",
    "https://www.lively.com", "B2C 医疗警报硬件+订阅"))
C.append(mk("Medical Guardian", "", "海外", "养老用品", "医疗警报",
    ["医疗警报", "跌倒", "订阅"],
    "美国较大的家用医疗警报与跌倒监测服务商，提供多种紧急呼叫与活动监测方案。",
    "美国家用医疗警报头部服务商",
    NA, NAT, "", "2005",
    "https://www.medicalguardian.com", "B2C 医疗警报订阅"))
C.append(mk("MobileHelp", "", "海外", "养老用品", "医疗警报",
    ["医疗警报", "GPS", "订阅"],
    "提供带GPS的家用与移动医疗警报系统，服务居家与户外老人的紧急呼叫需求。",
    "GPS移动医疗警报系统",
    NA, NAT, "", "2006",
    "https://www.mobilehelp.com", "B2C 医疗警报订阅"))
# 到家医疗 / 价值医疗
C.append(mk("Cityblock Health", "", "海外", "健康服务", "复杂护理",
    ["复杂护理", "价值医疗", "有融资"],
    "面向Medicare/Medicaid复杂需求人群（多为老年共病）的价值医疗公司，整合并管理医疗与社会照护。",
    "复杂人群价值医疗，整合医疗+社会照护",
    NA, NAT, "", "2015",
    "https://www.cityblock.com", "B2B2C 价值医疗管理"))
C.append(mk("DispatchHealth", "", "海外", "健康服务", "到家医疗",
    ["到家医疗", "急症", "有融资"],
    "提供上门急症医疗服务的公司，让老人在家获得急诊级护理，避免不必要的住院。",
    "上门急症医疗，减少老人非必要住院",
    NA, NAT, "", "2013",
    "https://www.dispatchhealth.com", "B2B2C 到家急症医疗"))
C.append(mk("MedArrive", "", "海外", "健康服务", "到家护理",
    ["到家护理", "技术+人力", "有融资"],
    "将技术平台与专业护理员结合，提供到家健康管理与慢病护理协调服务。",
    "技术+人力到家护理协调",
    NA, NAT, "", "2018",
    "https://www.medarrive.com", "B2B2C 到家护理平台"))
C.append(mk("Medically Home", "", "海外", "健康服务", "医院到家",
    ["医院到家", "急性护理", "有融资"],
    "“医院到家”（Hospital-at-Home）运营商，让符合条件的急性患者在家接受医院级治疗。",
    "医院到家急性护理模式",
    NA, NAT, "", "2016",
    "https://www.medicallyhome.com", "B2B 医院到家运营"))
C.append(mk("TytoCare", "", "海外", "健康服务", "远程检查",
    ["远程检查", "硬件", "有融资"],
    "提供家用远程体检设备与平台，老人可在家完成听诊、体温、耳镜等检查并连线医生。",
    "家用远程体检设备+平台",
    NA, NAT, "", "2012",
    "https://www.tytocare.com", "B2B2C 远程体检硬件+平台"))
# 中国上市医械 / 家用医疗
C.append(mk("鱼跃医疗", "鱼跃医疗", "国内", "康复设备", "家用医疗",
    ["上市公司", "家用医疗", "对标标的"],
    "国内家用医疗器械龙头（深交所上市），产品涵盖制氧机、血压计、呼吸机、血糖仪等，深度布局老年慢病与居家监护。",
    "家用医疗器械龙头，上市（S1）",
    NA, ft("上市公司(鱼跃医疗)"), "", "1998",
    "https://www.yuyue.com.cn", "B2B2C 家用医疗器械（上市）"))
C.append(mk("九安医疗", "九安医疗", "国内", "康复设备", "家用医疗",
    ["上市公司", "血压血糖", "对标标的"],
    "国内家用医疗与健康设备企业（深交所上市），以iHealth品牌布局血压、血糖等老年健康监测与海外数字健康。",
    "iHealth品牌家用监测，上市（S1）",
    NA, ft("上市公司(九安医疗)"), "", "1995",
    "https://www.andon.com.cn", "B2B2C 家用健康监测（上市）"))
C.append(mk("可孚医疗", "可孚医疗", "国内", "康复设备", "家用医疗",
    ["上市公司", "家用医疗", "康复辅具"],
    "国内家用医疗器械企业（深交所上市），覆盖血压计、轮椅、护理床、康复辅具等适老家用产品。",
    "家用医疗器械上市，适老品类齐全",
    NA, ft("上市公司(可孚医疗)"), "", "2009",
    "https://www.cofoe.com", "B2B2C 家用医疗器械（上市）"))
C.append(mk("钛米机器人", "钛米机器人", "国内", "养老机器人", "医疗服务机器人",
    ["医疗服务机器人", "有融资"],
    "医疗服务机器人公司（TMiRob），产品涵盖消毒、配送、巡检等机器人，可向养老机构与医养场景延伸。",
    "医疗服务机器人，医养场景延展",
    NA, NAT, "", "2015",
    "https://www.tmirobot.com", "B2B 医疗服务机器人"))
# 陪伴 / 社交机器人
C.append(mk("LOVOT", "", "海外", "陪伴机器人", "陪伴机器人",
    ["陪伴机器人", "日本", "情感"],
    "日本Groove X出品的情感陪伴机器人，以可爱外形与交互为独居老人与家庭提供情感陪伴。",
    "日本情感陪伴机器人（Groove X）",
    NA, NAT, "", "2015",
    "https://www.lovot.com", "B2C 情感陪伴机器人"))
C.append(mk("PARO", "", "海外", "陪伴机器人", "治疗机器人",
    ["陪伴机器人", "治疗", "日本"],
    "日本产海豹型治疗机器人（AIST体系），广泛用于痴呆照护机构缓解焦虑、提升情绪。",
    "海豹治疗机器人，痴呆照护应用",
    NA, NAT, "", "2001",
    "https://www.parorobots.com", "B2B 治疗机器人（养老机构）"))
C.append(mk("Temi", "", "海外", "陪伴机器人", "服务机器人",
    ["服务机器人", "语音助手"],
    "通用室内服务机器人（以色列Roboteam），兼具移动视频陪伴与智能助手功能，可用于老人居家。",
    "室内服务/陪伴机器人（以色列）",
    NA, NAT, "", "2016",
    "https://www.robotemi.com", "B2B2C 室内服务机器人"))
# 身后 / 遗产规划
C.append(mk("Trust & Will", "", "海外", "养老金融", "遗产规划",
    ["遗产规划", "遗嘱", "有融资"],
    "在线遗嘱与信托设立平台，帮助家庭便捷完成遗产与临终法律安排。",
    "在线遗嘱与信托设立平台",
    NA, NAT, "", "2017",
    "https://www.trustandwill.com", "B2C 遗产规划SaaS"))
# 药房 / 医药
C.append(mk("Alto Pharmacy", "", "海外", "健康服务", "数字药房",
    ["数字药房", "配送", "有融资"],
    "技术驱动的数字药房，提供送药上门与用药管理，便利慢病与老年用药。",
    "数字药房送药上门",
    NA, NAT, "", "2015",
    "https://www.alto.com", "B2B2C 数字药房"))
# 视力自测
C.append(mk("Visibly", "", "海外", "健康服务", "视力检测",
    ["视力", "在线检测", "APP"],
    "提供在线视力检测与处方更新的平台，让老人远程完成基础视力评估。",
    "在线视力检测平台",
    NA, NAT, "", "2015",
    "https://www.visibly.io", "B2C 在线视力检测"))
C.append(mk("EyeQue", "", "海外", "健康服务", "视力检测",
    ["视力", "家用设备"],
    "提供家用视力与眼健康自测设备，帮助老人追踪视力变化。",
    "家用视力自测设备",
    NA, NAT, "", "2015",
    "https://www.eyeque.com", "B2C 家用视力检测硬件"))
# 认知评估
C.append(mk("Neurotrack", "", "海外", "认知健康", "认知评估",
    ["认知评估", "AI", "早筛"],
    "通过眼动（eye-tracking）进行阿尔茨海默风险早期筛查的认知健康公司。",
    "眼动认知早筛，阿尔茨海默风险",
    NA, NAT, "", "2012",
    "https://www.neurotrack.com", "B2B2C 认知早筛平台"))
# 长寿生物
C.append(mk("BioAge Labs", "", "海外", "长寿科技/生物医药", "衰老靶点",
    ["长寿科技", "上市公司", "对标标的"],
    "以AI发现衰老相关药物靶点的长寿生物科技公司，2025年完成IPO，聚焦肌肉衰减与长寿干预。",
    "2025年IPO，AI衰老靶点药物（S1）",
    NA, ft("NASDAQ上市公司(2025 IPO)"), "", "2014",
    "https://www.bioagelabs.com", "B2B 长寿药物研发（上市）"))
# 老人出行
C.append(mk("GoGoGrandparent", "", "海外", "养老服务", "老人出行",
    ["老人出行", "打车", "有融资"],
    "为不擅长智能手机的老人提供电话即可叫车（Uber/Lyft）与配送的转接服务。",
    "电话叫车/配送，服务非智能机老人",
    NA, NAT, "", "2016",
    "https://www.gogograndparent.com", "B2B2C 老人出行转接服务"))
# 远程患者监测
C.append(mk("Current Health", "", "海外", "健康服务", "远程监测",
    ["远程监测", "可穿戴", "上市公司关联"],
    "远程患者监测平台（可穿戴+AI），已被Best Buy收购，用于慢病与术后老人在家监测。",
    "远程患者监测，Best Buy体系",
    NA, ft("被Best Buy收购"), "", "2015",
    "https://www.currenthealth.com", "B2B 远程患者监测平台"))

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = set()
    for x in data:
        n = (x.get("name") or "").strip().lower()
        if n: existing.add(n)
        nc = (x.get("name_cn") or "").strip().lower()
        if nc: existing.add(nc)
    max_serial = max([int(x.get("serial","#0000").lstrip("#"))
                      for x in data if str(x.get("serial","")).startswith("#")], default=0)
    added, skipped = [], []
    for c in C:
        key = (c["name"] or "").strip().lower()
        key2 = (c.get("name_cn") or "").strip().lower()
        if key in existing or (key2 and key2 in existing):
            skipped.append(c["name"]); continue
        max_serial += 1
        c["serial"] = "#%04d" % max_serial
        data.append(c); added.append(c["name"]); existing.add(key)
        if key2: existing.add(key2)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("TOTAL after:", len(data))
    print("ADDED:", len(added))
    for a in added: print("  +", a)
    print("SKIPPED (dup):", len(skipped))
    for s in skipped: print("  =", s)

if __name__ == "__main__":
    main()
