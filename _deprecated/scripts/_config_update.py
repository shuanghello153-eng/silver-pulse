# -*- coding: utf-8 -*-
"""2026-07-15 信源治理入库：加8个新源 + 修正 agetech_com 死栏目 + (死标恢复在 health 脚本里做)"""
import io, sys

PATH = "config.py"
src = open(PATH, encoding="utf-8").read()

# ---- 1) 修正 agetech_com：/venture/ 与 /companies/ 已 404，内容并入 /news/ ----
old_ag = '''    "agetech_com": {
        "name": "AgeTech.com",
        "l1_domain": "agetech.com",
        "l2_channels": [
            ("news", "https://www.agetech.com/news/", "google_news"),
            ("venture", "https://www.agetech.com/venture/", "google_news"),
            ("companies", "https://www.agetech.com/companies/", "google_news"),
        ],'''
new_ag = '''    "agetech_com": {
        "name": "AgeTech.com",
        "l1_domain": "agetech.com",
        "l2_channels": [
            ("news", "https://www.agetech.com/news/", "google_news"),
        ],'''
assert old_ag in src, "agetech_com 旧块未匹配"
src = src.replace(old_ag, new_ag)

# ---- 2) 在 age_uk (SOURCES 最后一个条目) 之后插入 8 个新源 ----
NEW = '''    # === 新增：2026-07-15 信源治理批次（研究员实查+入库）===
    "silvereco": {
        "name": "Silvereco",
        "l1_domain": "silvereco.fr",
        "l2_channels": [
            ("actualites", "https://www.silvereco.fr/actualites/", "google_news"),
            ("acteurs", "https://www.silvereco.fr/acteurs-silver-economie/", "google_news"),
            ("feed", "https://www.silvereco.fr/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "法国银发经济垂直门户；有直采RSS(actualites新闻/acteurs企业名录)；反查AGECLUB得来",
        "lang": "fr",
        "kind": "primary",
    },
    "tracxn_age_tech": {
        "name": "Tracxn Age Tech",
        "l1_domain": "tracxn.com",
        "l2_channels": [
            ("us", "https://tracxn.com/d/explore/age-tech-startups-in-united-states/__F1W7P9wFbrSgBBr3Gz5jcFFD5jxsRPSVQv_u10Oa4I0", "google_news"),
            ("germany", "https://tracxn.com/d/explore/age-tech-startups-in-germany/__hdRFJQR2d3H7Z_B_ZXB9MWAQ3q_JvQ91qSIGRIeB5yY/companies", "google_news"),
        ],
        "tier": 2,  # 企业数据库非媒体+付费墙遮金额，按T2入库；作头部公司发现器
        "region": "overseas",
        "notes": "全球银发科技企业数据库(按地区分榜,美国1165家);金额被付费墙遮$*****;点开深链可能弹双标签页(站点重定向),关掉一个即可",
        "kind": "database",
    },
    "seedtable_elder": {
        "name": "Seedtable Elder Tech",
        "l1_domain": "seedtable.com",
        "l2_channels": [
            ("elder_technology", "https://seedtable.com/startups-elder-technology", "google_news"),
            ("elder_care", "https://www.seedtable.com/best-elder-care-startups", "google_news"),
        ],
        "tier": 3,  # 噪音偏大(混长寿biotech)，仅宽覆盖
        "region": "overseas",
        "notes": "老年科技排名榜;ageing子榜混长寿biotech噪音,只用前两个干净子榜",
        "kind": "ranking",
    },
    "being_patient": {
        "name": "Being Patient",
        "l1_domain": "beingpatient.com",
        "l2_channels": [
            ("alzheimers", "https://beingpatient.com/alzheimers-disease/", "google_news"),
        ],
        "tier": 2,  # 认知症垂直高质量媒体
        "region": "overseas",
        "notes": "认知症/脑健康垂直媒体(前WSJ编辑创办);认知症赛道高质量入口",
        "kind": "primary",
    },
    "addf_portfolio": {
        "name": "ADDF Diagnostics Accelerator",
        "l1_domain": "alzdiscovery.org",
        "l2_channels": [
            ("portfolio", "https://www.alzdiscovery.org/research-and-grants/diagnostics-accelerator/portfolio", "google_news"),
        ],
        "tier": 2,  # 认知症投融资反查利器
        "region": "overseas",
        "notes": "阿尔茨海默药物发现基金会诊断加速器被投组合;认知症投融资反查利器/企业发现器",
        "kind": "database",
    },
    "dementia_care_central": {
        "name": "Dementia Care Central",
        "l1_domain": "dementiacarecentral.com",
        "l2_channels": [
            ("aboutdementia", "https://www.dementiacarecentral.com/aboutdementia", "google_news"),
        ],
        "tier": 3,  # 偏工具/资源，非新闻流
        "region": "overseas",
        "notes": "照护者向认知症知识库/资源指南",
        "kind": "guide",
    },
    "alzheimers_net": {
        "name": "Alzheimers.net",
        "l1_domain": "alzheimers.net",
        "l2_channels": [
            ("home", "https://www.alzheimers.net/", "google_news"),
        ],
        "tier": 3,  # 含机构导流，噪音中
        "region": "overseas",
        "notes": "阿尔茨海默资讯+记忆照护机构目录(含商业导流,噪音中)",
        "kind": "primary",
    },
    "hearingtracker": {
        "name": "HearingTracker",
        "l1_domain": "hearingtracker.com",
        "l2_channels": [
            ("rechargeable", "https://hearingtracker.com/rechargeable-hearing-aids", "google_news"),
        ],
        "tier": 3,  # 助听细分产品发现器
        "region": "overseas",
        "notes": "助听器实验室声学测评+年度榜单;助听细分产品发现器",
        "kind": "ranking",
    },
'''

anchor = '        "kind": "primary",\n    },\n'
idx = src.rfind(anchor)
assert idx != -1, "未找到 age_uk 末尾锚点"
src = src[:idx] + NEW + src[idx:]

open(PATH, "w", encoding="utf-8").write(src)
print("config.py 写入成功；新增 8 源，agetech_com 栏目已修正")
