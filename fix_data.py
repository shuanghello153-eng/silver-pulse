# -*- coding: utf-8 -*-
"""一次性数据修复脚本：翻译英文标题 + 补空标签 + P1企业标注"""
import json, os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# === 1. 英文标题翻译 ===
TRANSLATIONS = {
    "Senior Living M&A Still Surging in 2026 — But Deals Are Getting Smaller": "2026年养老地产并购持续升温——但单笔规模缩小",
    "CMS Proposes Community-Based Palliative Care Benefit": "CMS提议新增社区姑息关怀福利",
    "In the Pipeline: LCS Plans $82M Expansion in North Carolina": "LCS计划8200万美元北卡扩建",
    "Atria Puts Turnaround Skills to the Test with Latest Acquisition": "Atria用最新收购验证扭亏能力",
    "Why Senior Living Operators Are Betting Big on Technology": "养老运营商为何大举押注技术",
    "Home Health Care News: Top Stories of the Week": "居家护理新闻：本周头条",
    "McKnight's Senior Living: Industry Updates": "McKnight's养老社区：行业动态",
    "Senior Housing News: Market Trends": "养老住房新闻：市场趋势",
    "Hospice News: Policy and Practice": "临终关怀新闻：政策与实践",
    "FierceHealthcare: Healthcare Industry News": "FierceHealthcare：医疗行业新闻",
    "MobiHealthNews: Digital Health Updates": "MobiHealthNews：数字健康动态",
    "Crunchbase News: Funding and M&A": "Crunchbase新闻：融资与并购",
    "TheGerontechnologist: Aging Tech Insights": "老年科技专家：养老科技洞察",
    "Bloomberg Law News: Healthcare Regulations": "彭博法律新闻：医疗法规",
    "Aging in Place Technology News": "居家养老技术新闻",
    "Forbes: Healthcare and Aging": "福布斯：医疗与养老",
    "TechCrunch: Health Tech Startup News": "TechCrunch：健康科技创业新闻",
    "Aging 2.0: Innovation in Senior Care": "Aging 2.0：养老护理创新",
    "NIA Director Discusses Aging Research Priorities": "NIA所长讨论衰老研究优先事项",
}

# === 2. 空标签补全 ===
TAG_FIXES = {
    "单笔融资重回亿元级": ["融资"],
    "2026年中国银发经济产业研究报告": ["智慧养老", "老年消费"],
    "AI时代中国银发科技发展研究报告": ["智慧养老"],
    "2026银发消费与流量前瞻": ["老年消费"],
    "2026银发经济爆款清单": ["老年消费"],
    "Atria Puts Turnaround Skills": ["养老地产", "战略合作"],
    "Why Senior Living Operators Are Betting Big on Technology": ["智慧养老", "老年消费"],
}

# === 3. 执行修复 ===

# 修复 scored_latest.json
scored_path = os.path.join(DATA_DIR, "scored_latest.json")
data = json.load(open(scored_path, encoding="utf-8"))

trans_count = 0
tag_count = 0
for art in data:
    title = art.get("title", "")
    # 翻译
    if title in TRANSLATIONS:
        art["title_cn"] = TRANSLATIONS[title]
        trans_count += 1
    # 补标签
    for key, tags in TAG_FIXES.items():
        if key in title and not art.get("tags"):
            art["tags"] = tags
            tag_count += 1
            break

json.dump(data, open(scored_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"翻译: {trans_count}条, 补标签: {tag_count}条")

# 修复 all_enterprises.json
ent_path = os.path.join(DATA_DIR, "enterprise", "all_enterprises.json")
ents = json.load(open(ent_path, encoding="utf-8"))

p1_count = 0
for ent in ents:
    if ent.get("priority") == "P1":
        funding = ent.get("funding", {})
        if isinstance(funding, dict):
            amount = funding.get("latest_amount_display", "")
            if not amount or "未披露" in str(amount) or "未公开" in str(amount):
                funding["latest_amount_display"] = "暂未搜到公开信息"
                p1_count += 1

json.dump(ents, open(ent_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"P1企业标注: {p1_count}家")
print("数据修复完成")
