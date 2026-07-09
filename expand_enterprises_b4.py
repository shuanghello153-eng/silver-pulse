# -*- coding: utf-8 -*-
"""Batch 4: final push past 1300. Real companies across China medtech/robots,
hearing, home care, care coordination, MA plans. Auto-dedup. Only APPENDS."""
import json

DATA_FILE = "data/enterprise/all_enterprises.json"
SRC = "WebSearch(企业库扩充B4: 公司官网/Crunchbase/Tracxn等)"

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
C.append(mk("乐心医疗", "乐心医疗", "国内", "康复设备", "家用医疗",
    ["上市公司", "健康穿戴", "对标标的"],
    "国内家用医疗与健康穿戴上市公司（深交所），产品含血压计、智能手环、体脂秤等，布局慢病健康监测。",
    "健康穿戴与家用监测上市（S1）",
    NA, ft("上市公司(乐心医疗)"), "", "2002",
    "https://www.lifesense.com", "B2B2C 健康穿戴/家用监测（上市）"))
C.append(mk("三诺生物", "三诺生物", "国内", "康复设备", "家用医疗",
    ["上市公司", "血糖监测", "对标标的"],
    "国内血糖监测龙头上市公司（深交所），家用血糖仪与慢病管理，深度服务老年糖尿病群体。",
    "血糖监测龙头，上市（S1）",
    NA, ft("上市公司(三诺生物)"), "", "2002",
    "https://www.sinocare.com", "B2B2C 血糖监测（上市）"))
C.append(mk("康泰医学", "康泰医学", "国内", "康复设备", "家用医疗",
    ["上市公司", "监护监测", "对标标的"],
    "国内医疗器械上市公司（深交所），产品含脉搏血氧、血压、心电、监护等家用与临床监测设备。",
    "监护/血氧监测上市医械（S1）",
    NA, ft("上市公司(康泰医学)"), "", "1996",
    "https://www.contec.com.cn", "B2B2C 监护监测设备（上市）"))
C.append(mk("达闼科技", "达闼科技", "国内", "养老机器人", "云端机器人",
    ["服务机器人", "云端智能", "有融资"],
    "云端智能机器人公司（CloudMinds），提供云端大脑+机器人本体，服务机器人可用于养老陪护与导诊场景。",
    "云端智能服务机器人，养老陪护延展",
    NA, NAT, "", "2015",
    "https://www.cloudminds.com", "B2B 云端服务机器人"))
C.append(mk("hear.com", "", "海外", "智能硬件", "听觉辅具",
    ["助听器", "DTC", "高端"],
    "高端助听器的DTC平台与听力中心网络，连接用户与本地听力专家完成验配。",
    "高端助听器DTC+听力中心网络",
    NA, NAT, "", "2012",
    "https://www.hear.com", "B2C 高端助听器平台"))
C.append(mk("Hinge Health", "", "海外", "康复设备", "数字康复",
    ["数字康复", "MSK", "有融资"],
    "数字肌肉骨骼（MSK）与慢性疼痛康复平台，结合可穿戴传感器与远程物理治疗师，服务老年背痛/关节疼痛人群。",
    "数字MSK/疼痛康复平台，远程物理治疗",
    NA, NAT, "", "2014",
    "https://www.hingehealth.com", "B2B2C 数字康复平台"))
C.append(mk("Wellthy", "", "海外", "养老服务", "照护协调",
    ["照护协调", "家庭", "有融资"],
    "照护协调平台，帮家庭管理复杂照护事务（预约、保险、日常安排），类似Cariloop的雇主福利。",
    "家庭照护协调平台",
    NA, NAT, "", "2015",
    "https://www.wellthy.com", "B2B2C 照护协调平台"))
C.append(mk("Right at Home", "", "海外", "养老服务", "居家照护",
    ["居家照护", "特许经营", "对标标的"],
    "全球居家护理与老年照护特许经营龙头，提供居家陪伴、个人护理与康复支持服务。",
    "全球居家护理特许经营龙头（S1）",
    NA, NAT, "", "1995",
    "https://www.rightathome.net", "B2B2C 居家护理特许经营"))
C.append(mk("Visiting Angels", "", "海外", "养老服务", "居家照护",
    ["居家照护", "特许经营"],
    "全美大型居家护理与陪护特许经营网络，为老人提供非医疗与生活协助服务。",
    "全美居家陪护特许经营网络",
    NA, NAT, "", "1992",
    "https://www.visitingangels.com", "B2B2C 居家陪护特许经营"))
C.append(mk("Amada Senior Care", "", "海外", "养老服务", "居家照护",
    ["居家照护", "特许经营"],
    "居家养老护理公司，以特许经营+自营结合提供个人护理、陪伴与养老咨询。",
    "居家养老护理（特许经营+自营）",
    NA, NAT, "", "2007",
    "https://www.amadaseniorcare.com", "B2B2C 居家养老护理"))
C.append(mk("Care.com", "", "海外", "养老服务", "照护匹配",
    ["照护匹配", "平台", "上市公司关联"],
    "大型照护人员匹配平台（已被Providence Equity收购），连接家庭与保姆/护理员，涵盖老年护理。",
    "大型照护匹配平台（含老年护理）",
    NA, NAT, "", "2006",
    "https://www.care.com", "B2B2C 照护人员匹配平台"))
C.append(mk("SCAN Health Plan", "", "海外", "养老金融", "医疗保险计划",
    ["Medicare Advantage", "非营利", "对标标的"],
    "美国大型非营利Medicare Advantage健康计划，专注老年人群，提供MA与健康计划服务。",
    "大型非营利MA计划，专注老年（S1）",
    NA, NAT, "", "1977",
    "https://www.scanhealthplan.com", "B2B2C Medicare Advantage保险"))

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
