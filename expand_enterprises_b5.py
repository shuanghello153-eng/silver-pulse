# -*- coding: utf-8 -*-
"""Batch 5: final top-up past 1300. Auto-dedup. Only APPENDS."""
import json
DATA_FILE = "data/enterprise/all_enterprises.json"
SRC = "WebSearch(企业库扩充B5: 公司官网/Crunchbase/Tracxn等)"
def mk(name, name_cn, region, l1, l2, tags, desc, highlights,
       flatest, ftotal, investors, founded, website, bm):
    return {"name": name, "name_cn": name_cn, "region": region,
        "category_l1": l1, "category_l2": l2, "tags": tags,
        "description": desc, "desc_cn": desc, "highlights": highlights,
        "funding_latest": flatest, "funding_total": ftotal,
        "investors": investors, "founded": founded, "value_score": 0,
        "source": SRC,
        "crunchbase_url": "https://www.crunchbase.com/textsearch?q=" + name.replace(" ", "+"),
        "website_url": website, "business_model": bm, "business_model_cn": bm,
        "news_coverage": {"latest_news": [], "news_count": 0, "news_quality": "low", "snippets": [desc]}}
def fd(a, r, d, disp): return {"amount": a, "round": r, "date": d, "display": disp}
def ft(t): return {"amount": t, "display": t}
NA = fd("未披露", "", "", "未披露"); NAT = ft("累计未披露")
C = []
C.append(mk("翔宇医疗", "翔宇医疗", "国内", "康复设备", "康复器械",
    ["上市公司", "康复器械", "对标标的"],
    "国内康复医疗器械上市公司（上交所），产品涵盖康复评定、训练与治疗设备，广泛服务于老年康复与养老机构。",
    "康复医疗器械上市（S1）",
    NA, ft("上市公司(翔宇医疗)"), "", "2002",
    "https://www.xiangyu.cn", "B2B 康复医疗器械（上市）"))
C.append(mk("伟思医疗", "伟思医疗", "国内", "康复设备", "康复器械",
    ["上市公司", "康复", "盆底/神经"],
    "国内康复医疗器械上市公司（上交所），聚焦电刺激、磁刺激与康复机器人，服务于神经与盆底康复等老年相关场景。",
    "康复医疗器械上市，神经/盆底康复",
    NA, ft("上市公司(伟思医疗)"), "", "2001",
    "https://www.vishee.com", "B2B 康复医疗器械（上市）"))
C.append(mk("Nymbl Science", "", "海外", "康复设备", "防跌倒训练",
    ["防跌倒", "APP", "平衡训练"],
    "面向老人的防跌倒平衡训练APP，通过每日简短双重任务训练改善平衡、降低跌倒风险。",
    "防跌倒平衡训练APP",
    NA, NAT, "", "2016",
    "https://www.nymblscience.com", "B2B2C 防跌倒训练APP"))
C.append(mk("Saga", "", "海外", "养老金融", "银发服务",
    ["银发服务", "上市公司", "英国", "对标标的"],
    "英国面向50+人群的服务集团（伦敦上市），业务涵盖银发旅游、保险与金融，是“以老为镜”的成熟银发消费标杆。",
    "英国50+银发服务上市集团（S1）",
    NA, ft("伦敦上市公司"), "", "1951",
    "https://www.saga.co.uk", "B2B2C 银发旅游/保险/金融（上市）"))
C.append(mk("Wheel", "", "海外", "健康服务", "虚拟护理运力",
    ["虚拟护理", "人力平台", "有融资"],
    "为医疗与养老客户提供虚拟护理与临床人力（telehealth staffing）的平台，缓解照护人力短缺。",
    "虚拟护理人力平台",
    NA, NAT, "", "2016",
    "https://www.wheel.com", "B2B 虚拟护理人力平台"))
C.append(mk("InHome Therapy", "", "海外", "健康服务", "到家康复",
    ["到家康复", "PT/OT", "平台"],
    "提供到家物理治疗、作业治疗与言语治疗的平台，服务居家老人的康复与功能维持。",
    "到家PT/OT/Speech康复平台",
    NA, NAT, "", "2012",
    "https://www.inhometherapy.com", "B2B2C 到家康复治疗"))
C.append(mk("EmpowerMe Wellness", "", "海外", "养老服务", "综合养老",
    ["综合养老", "预防", "有融资"],
    "为自理/辅助生活老人提供整合的预防式健康、健身与营养服务的养老运营公司。",
    "预防式综合养老服务",
    NA, NAT, "", "2016",
    "https://www.empowermewellness.com", "B2B/B2C 综合养老服务"))

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
