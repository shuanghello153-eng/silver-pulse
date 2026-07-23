# -*- coding: utf-8 -*-
"""2026-07-16 W1 入库（第二批）：北美头部企业5家 + 最近一周资讯5条。
Pearl Health 已于 07-15 入库，本轮只补其余 5 家。标签后续由标签AI统一打。
"""
import json, copy

# ========== 企业入库 ==========
EP = "data/enterprise/all_enterprises.json"
ents = json.load(open(EP, encoding="utf-8"))
template = ents[0]
existing = {e.get("name", "").strip().lower() for e in ents}
maxserial = max(int(str(e.get("serial", "#0")).replace("#", "")) for e in ents if str(e.get("serial", "")).startswith("#"))

NEW_ENTS = [
    {"name":"The Ensign Group","region":"海外","category_l1":"养老服务","category_l2":"养老运营",
     "description":"美国上市养老服务运营商（NYSE: ENSG），专注 skilled nursing / SNF 与 senior living，通过持续并购扩张；2026-07 经 REIT 收购得州 2 家养老院（250 床）。",
     "funding_latest":{"date":"上市","amount":"NYSE 上市","round":"上市","display":"NYSE 上市 (ENSG)"},
     "funding_total":{"amount":"上市公司","display":"上市公司"},"investors":"—","founded":"1999",
     "website_url":"https://www.ensigngroup.net","stage":"上市",
     "source":"信源治理入库(Skilled Nursing News Finance) 2026-07-16","business_model":"上市运营商",
     "business_model_cn":"上市养老服务运营商","tags":["上市","近期并购"]},
    {"name":"Saber Healthcare","region":"海外","category_l1":"养老服务","category_l2":"养老运营",
     "description":"美国 SNF 养老护理运营商，2026-07 从 Ciena 收购横跨 3 州 27 家养老院，为其史上最大交易之一，持续并购扩张。",
     "funding_latest":{"date":"未披露","amount":"私有未披露","round":"私有","display":"私有未披露"},
     "funding_total":{"amount":"未披露","display":"未披露"},"investors":"—","founded":"未披露",
     "website_url":"https://www.saberhealth.com","stage":"成熟期",
     "source":"信源治理入库(Skilled Nursing News Finance) 2026-07-16","business_model":"私有运营商",
     "business_model_cn":"私有养老护理运营商","tags":["近期并购"]},
    {"name":"MatrixCare","region":"海外","category_l1":"智能科技","category_l2":"SaaS",
     "description":"面向老年护理/养老社区的 EHR 与运营软件平台；2026-07 Resmed 以 4.9 亿美元出售给 PE，是养老软件赛道头部标的。",
     "funding_latest":{"date":"2026-07","amount":"4.9亿美元","round":"被收购","display":"2026-07 被PE以$490M收购(原Resmed)"},
     "funding_total":{"amount":"被收购","display":"被收购"},"investors":"PE(买方未披露)","founded":"未披露",
     "website_url":"https://www.matrixcare.com","stage":"被收购",
     "source":"信源治理入库(MassDevice M&A) 2026-07-16","business_model":"B2B SaaS",
     "business_model_cn":"B2B 养老软件","tags":["被收购","近期并购"]},
    {"name":"Abridge","region":"海外","category_l1":"智能科技","category_l2":"AI",
     "description":"临床文档 AI 平台，用生成式 AI 自动生成病历草稿，显著提升医生/护理记录效率，广泛应用于养老与护理场景。",
     "funding_latest":{"date":"2026","amount":"3亿美元","round":"Series E","display":"Series E $300M (连续 mega round)"},
     "funding_total":{"amount":"累计约$5亿+","display":"累计约$5亿+"},"investors":"未披露","founded":"2018",
     "website_url":"https://www.abridge.com","stage":"成长期",
     "source":"信源治理入库(MedCity News Health Tech) 2026-07-16","business_model":"B2B SaaS",
     "business_model_cn":"B2B 临床AI","tags":["有融资","高融资","近期融资","AI"]},
    {"name":"PointClickCare","region":"海外","category_l1":"智能科技","category_l2":"SaaS",
     "description":"养老社区/长期照护 EHR 与数据分析平台（加拿大起家、北美领先）；2026-05 扩展 AI 产品 Chart Advisor 至 senior living。",
     "funding_latest":{"date":"2026-05","amount":"私有未披露","round":"私有","display":"私有未披露(2026-05 扩展AI产品线)"},
     "funding_total":{"amount":"未披露","display":"未披露"},"investors":"—","founded":"2000",
     "website_url":"https://www.pointclickcare.com","stage":"成熟期",
     "source":"信源治理入库(PointClickCare 官方稿) 2026-07-16","business_model":"B2B SaaS",
     "business_model_cn":"B2B 养老软件","tags":["AI","近期动态"]},
]

added = 0; skipped = 0
for e in NEW_ENTS:
    nm = e["name"].strip().lower()
    if nm in existing:
        skipped += 1; continue
    maxserial += 1
    ne = copy.deepcopy(template)
    ne["serial"] = f"#{maxserial:04d}"
    for k, v in e.items():
        ne[k] = v
    ne["tag_l1"] = []
    ne["tag_l2"] = []
    ne["news_coverage"] = {"news_count": 0, "news_quality": "unscored", "latest_news": None}
    ne["value_score"] = 0
    ne["recommend"] = ""
    ne["name_cn"] = ""
    ne["highlights"] = (f"成立于{e['founded']}年" if e.get("founded") and e["founded"] != "未披露" else "")
    ne["payor_model"] = "未披露"
    ne["desc_cn"] = e["description"]
    ents.append(ne)
    existing.add(nm)
    added += 1

json.dump(ents, open(EP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"企业入库：新增 {added} 家，跳过已存在 {skipped} 家；现有总数 {len(ents)}")

# ========== 资讯入库（manual_news.json）==========
MP = "data/manual_news.json"
news = json.load(open(MP, encoding="utf-8"))
existing_titles = {n.get("title", "").strip().lower() for n in news}

NEWS = [
    {"title":"The Ensign Group 经 REIT 收购得州 2 家养老院（250 床）",
     "summary":"美国上市养老运营商 The Ensign Group（NYSE: ENSG）2026-07 通过 REIT 结构收购得州 2 家养老院（共 250 床），延续其以并购扩张 SNF/senior living 版图的策略，Q1 业绩强劲。",
     "source_id":"skilled_nursing_news","source":"Skilled Nursing News",
     "url":"https://skillednursingnews.com/category/finance/","date":"2026-07-15",
     "tags":["收购","养老运营","SNF","近期并购"]},
    {"title":"Saber Healthcare 从 Ciena 收购横跨 3 州 27 家养老院",
     "summary":"美国 SNF 运营商 Saber Healthcare 2026-07 完成其史上最大交易之一，从 Ciena 收购横跨 3 个州的 27 家养老院，进一步扩张养老护理网络。",
     "source_id":"skilled_nursing_news","source":"Skilled Nursing News",
     "url":"https://skillednursingnews.com/category/finance/","date":"2026-07-15",
     "tags":["收购","养老运营","近期并购"]},
    {"title":"Resmed 以 4.9 亿美元向 PE 出售养老软件 MatrixCare",
     "summary":"呼吸/康复设备巨头 Resmed 2026-07 以 4.9 亿美元将其老年护理 EHR/软件业务 MatrixCare 出售给私募股权，反映养老软件赛道整合加速。",
     "source_id":"massdevice","source":"MassDevice",
     "url":"https://www.massdevice.com/category/business_financial_news/mergers_acquisitions/","date":"2026-07-15",
     "tags":["出售","养老软件","M&A"]},
    {"title":"Abridge 完成 3 亿美元 E 轮融资，临床文档 AI 持续 mega round",
     "summary":"临床文档 AI 平台 Abridge 完成 Series E 3 亿美元融资（连续大额轮），用生成式 AI 自动生成病历草稿，已深入养老/护理场景，估值与资本热度居数字健康前列。",
     "source_id":"medcity_news","source":"MedCity News",
     "url":"https://medcitynews.com/category/health-tech/","date":"2026-07-15",
     "tags":["融资","AI","高融资","近期融资"]},
    {"title":"PointClickCare 扩展 AI 产品 Chart Advisor 至 senior living",
     "summary":"北美养老社区 EHR 龙头 PointClickCare 2026-05 将其 AI 产品 Chart Advisor 扩展至 senior living 场景，用 AI 辅助护理记录与质量改进。",
     "source_id":"pointclickcare_official","source":"PointClickCare 官方",
     "url":"https://www.pointclickcare.com/","date":"2026-07-16",
     "tags":["AI","养老软件","产品"]},
]

n_added = 0; n_skip = 0
for n in NEWS:
    if n["title"].strip().lower() in existing_titles:
        n_skip += 1; continue
    n2 = dict(n); n2["ingest_time"] = "2026-07-16"
    news.append(n2)
    existing_titles.add(n["title"].strip().lower())
    n_added += 1

json.dump(news, open(MP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"资讯入库：新增 {n_added} 条，跳过已存在 {n_skip} 条；现有总数 {len(news)}")
