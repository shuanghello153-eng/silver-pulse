# -*- coding: utf-8 -*-
"""
Score and merge collected articles into scored_latest.json.
Low-cost approach: use signal_score (keyword-based) as final_score proxy,
generate template recommendations (no per-article AI call = save tokens).
Matches user's "脚本优先，低成本" preference (ref: AIHOT article).
"""
import json
import os
import re
from datetime import datetime

DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, f"raw_{datetime.now().strftime('%Y%m%d')}.json")
SCORED_FILE = os.path.join(DATA_DIR, "scored_latest.json")

MIN_SIGNAL = 4.0  # Exclude noise (signal_score < 4.0 = no meaningful positive signal)

# Tag detection keywords
TAG_MAP = [
    ("融资", ["raises", "raises series", "series a", "series b", "series c", "funding", "融资", "战略融资", "A轮", "B轮", "C轮", "天使轮", "seed round"]),
    ("收购", ["acquires", "acquisition", "acquired", "收购", "并购"]),
    ("IPO上市", ["ipo", "ipo filing", "goes public", "上市"]),
    ("战略合作", ["partners with", "partnership", "strategic partnership", "战略合作", "达成合作"]),
    ("产品发布", ["launches", "launching", "unveils", "introduces", "debuts", "发布", "上线", "推出"]),
    ("政策法规", ["medicaid", "medicare", "cms", "fda", "政策", "法规", "津贴", "长护险"]),
    ("居家养老", ["home care", "home health", "居家护理", "居家照护", "居家养老"]),
    ("养老地产", ["senior housing", "assisted living", "养老社区", "养老地产", "护理院"]),
    ("认知症", ["dementia", "alzheimer", "认知症", "失智", "阿尔茨海默"]),
    ("数字疗法", ["digital health", "telehealth", "remote", "数字疗法", "远程医疗"]),
    ("保险科技", ["insurance", "insurtech", "保险科技", "长护险"]),
    ("健康服务", ["caregiver", "caregiving", "护理", "康养", "医养"]),
    ("康复设备", ["rehab", "康复", "辅助器具", "辅具"]),
    ("养老用品", ["wearable", "智能床垫", "电子皮肤", "养老用品", "硬件"]),
    ("长寿科技", ["longevity", "长寿", "anti-aging"]),
    ("智慧养老", ["ai", "人工智能", "机器人", "智慧养老", "智能"]),
    ("行业趋势", ["market", "report", "趋势", "洞察", "研究报告"]),
]

CHINA_REF = {
    "融资": "中国银发企业可参照其融资节奏与估值逻辑，关注同赛道国内玩家。",
    "收购": "美国银发赛道并购活跃，中国创业者可关注被并购方的产品能力是否可引入国内。",
    "IPO上市": "海外银发企业上市路径值得研究，国内同类企业可参考其商业模式与合规框架。",
    "战略合作": "战略合作往往预示生态卡位，中国创业者可思考同类联盟机会。",
    "产品发布": "新产品发布揭示用户需求演进，国内团队可对照自身产品路线图。",
    "政策法规": "海外政策变动是中国政策的先行指标，长护险/支付端改革可提前研判。",
    "居家养老": "居家养老是中美共同主战场，服务模式差异值得深度对标。",
    "养老地产": "养老地产存量改造经验对中国大量老旧设施有参考价值。",
    "认知症": "认知症照护是刚需赛道，海外照护模式可为中国家庭提供范本。",
    "数字疗法": "数字疗法/远程医疗的支付与落地模式，中国可少走弯路。",
    "保险科技": "保险科技降低银发风险成本，国内长护险商业化可借鉴。",
    "健康服务": "护理人力是共性瓶颈，海外用工模式对中国有参照意义。",
    "康复设备": "康复辅具国产化空间大，海外产品定义值得研究。",
    "养老用品": "智能硬件+服务是趋势，国内供应链优势可放大。",
    "长寿科技": "长寿科技是长期赛道，早期布局者值得跟踪。",
    "智慧养老": "AI+养老的落地场景，国内可结合本地数据优势。",
    "行业趋势": "行业报告揭示结构性机会，可作为选题地图。",
}

EVENT_MAP = [
    ("融资", ["raises", "raises series", "series a", "series b", "series c", "funding", "融资", "战略融资", "A轮", "B轮", "C轮", "天使轮", "seed round", "valued at", "valuation"]),
    ("收购并购", ["acquires", "acquisition", "acquired", "收购", "并购", "merger"]),
    ("IPO上市", ["ipo", "ipo filing", "goes public", "上市"]),
    ("政策法规", ["medicaid", "medicare", "cms", "fda", "政策", "法规"]),
    ("产品发布", ["launches", "launching", "unveils", "introduces", "debuts", "发布", "上线", "推出"]),
    ("行业趋势", ["market", "report", "趋势", "洞察", "研究报告", "industry"]),
    ("人事变动", ["appoints", "hires", "ceo", "任命", "高管"]),
]


def detect_tags(text):
    tags = []
    for tag, kws in TAG_MAP:
        if any(kw.lower() in text.lower() for kw in kws):
            tags.append(tag)
            if len(tags) >= 3:
                break
    return tags[:3]


def detect_event(text):
    for event, kws in EVENT_MAP:
        if any(kw.lower() in text.lower() for kw in kws):
            return event
    return "行业趋势"


def detect_amount(text):
    """Extract funding amount if present."""
    patterns = [
        r"\$\s?([\d.]+(?:\s?[mb])?\s?(?:million|billion|m|b)?)",
        r"([\d.]+\s?(?:亿|万)\s?(?:元|美元|人民币)?)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""


def gen_recommendation(article, tags):
    text = f"{article.get('title','')} {article.get('summary','')}"
    primary = tags[0] if tags else "行业趋势"
    amount = detect_amount(text)
    rec = f"{primary}事件"
    if amount:
        rec += f"，涉及金额 {amount}。"
    rec += CHINA_REF.get(primary, "值得关注其对国内银发经济的参照意义。")
    return rec


def main():
    # Load raw
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    print(f"Raw articles: {len(raw)}")

    # Filter by signal_score
    filtered = [a for a in raw if a.get("signal_score", 0) >= MIN_SIGNAL]
    print(f"After signal_score>={MIN_SIGNAL}: {len(filtered)}")

    # Sort by signal_score desc, then date desc
    filtered.sort(key=lambda a: (a.get("signal_score", 0), a.get("date", "")), reverse=True)

    # Load existing scored
    existing = []
    if os.path.exists(SCORED_FILE):
        with open(SCORED_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing_urls = {e.get("url", "") for e in existing}
    existing_titles = {e.get("title", "")[:30] for e in existing}
    print(f"Existing scored: {len(existing)}")

    # Build new entries
    max_id = max([e.get("id", 0) for e in existing], default=0)
    new_entries = []
    for a in filtered:
        url = a.get("url", "")
        title = a.get("title", "")
        # Dedup against existing
        if url in existing_urls or title[:30] in existing_titles:
            continue
        signal = a.get("signal_score", 0)
        final_score = min(10.0, round(signal, 1))
        if final_score >= 7.0:
            category = "high"
        elif final_score >= 5.0:
            category = "watch"
        else:
            category = "archive"
        tags = detect_tags(f"{title} {a.get('summary','')}")
        event = detect_event(f"{title} {a.get('summary','')}")
        if event not in tags and len(tags) < 3:
            tags.append(event)
        recommendation = gen_recommendation(a, tags)
        max_id += 1
        entry = {
            "title": title,
            "final_score": final_score,
            "category": category,
            "tags": tags[:3],
            "recommendation": recommendation,
            "id": max_id,
            "summary": a.get("summary", ""),
            "url": url,
            "source": a.get("source", ""),
            "date": a.get("date", ""),
            "viral": False,
            "view": "curated" if category != "archive" else "raw",
            "region": "overseas" if is_overseas(a.get("source", "")) else "domestic",
        }
        new_entries.append(entry)

    print(f"New entries to add: {len(new_entries)}")
    high = sum(1 for e in new_entries if e["category"] == "high")
    watch = sum(1 for e in new_entries if e["category"] == "watch")
    print(f"  high: {high}, watch: {watch}, archive: {len(new_entries)-high-watch}")

    merged = existing + new_entries
    # Sort by date desc
    merged.sort(key=lambda e: e.get("date", ""), reverse=True)

    with open(SCORED_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(merged)} total to {SCORED_FILE}")


def is_overseas(source_name):
    """Simple check: if source name is in our overseas set, or pure ASCII."""
    overseas_names = {
        "FinSMEs", "Pulse 2.0", "Senior Housing News", "Business Wire", "TechCrunch",
        "PR Newswire", "Coverager", "Modern Healthcare", "FemTech Insider", "BetaKit",
        "MobiHealthNews", "Business Standard", "The AI Journal", "Hospice News",
        "McKnight's Senior Living", "McKnight's Home Care", "Home Health Care News",
        "HomeCare Magazine", "Fierce Healthcare", "Yahoo Finance", "Axios",
        "Creating A New Healthcare", "AgeTech.com", "AgeTech News", "StartUp Health",
        "Crunchbase News", "The Gerontechnologist", "Forbes", "Bloomberg Law News",
        "TipRanks", "TradingView", "ThinkAdvisor", "Drug Topics", "MSN", "MediaPost",
        "Investopedia", "The Business Journals", "San Diego Business Journal",
        "Healthcare Finance News", "American Hospital Association", "AHCA/NCAL",
        "Medical Economics", "Reinsurance News", "CoStar", "Alzheimer's News Today",
        "Center for Retirement Research", "Pension Policy International",
        "simplywall.st", "Quiver Quantitative", "livemint.com", "NST Online",
        "The Hindu", "Pandaily", "USA Today", "Patch", "Newsday", "Investing.com",
        "WorldAtlas", "KATV", "The Denver Post", "ABC7 WWSB", "12News", "KING5.com",
    }
    if source_name in overseas_names:
        return True
    # Fallback: pure ASCII = overseas
    return all(ord(c) < 128 for c in source_name) and len(source_name) > 2


if __name__ == "__main__":
    main()
