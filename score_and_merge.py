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
import config
from collector import is_job_spam
from selection.signal_strength import compute_signal_strength

DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, f"raw_{datetime.now().strftime('%Y%m%d')}.json")
SCORED_FILE = os.path.join(DATA_DIR, "scored_latest.json")

MIN_SIGNAL = 4.0  # Exclude noise (signal_score < 4.0 = no meaningful positive signal)

# Tag detection: 2026-07-10 T34 重构 —— 标签只保留「交叉维度」，不再与分类重复。
# 词表与规则统一在 config.ARTICLE_TAG_POOL / ARTICLE_TAG_RULES，
# 实际打标委托 selection.tagger.detect_cross_tags（单一事实来源）。
from selection.tagger import detect_cross_tags

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


def gen_recommendation(article, tags, event_type=""):
    text = f"{article.get('title','')} {article.get('summary','')}"
    # 主标签以「事件类型」为锚（标签已不再承载分类，避免理由前缀与分类重复）
    primary = event_type or (tags[0] if tags else "行业趋势")
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

    # Filter by signal_score (manual seeds bypass: they are curated stock data)
    filtered = [a for a in raw if a.get("manual") or a.get("signal_score", 0) >= MIN_SIGNAL]
    print(f"After signal_score>={MIN_SIGNAL} (manual kept): {len(filtered)}")

    # Sort by signal_score desc, then date desc
    filtered.sort(key=lambda a: (a.get("signal_score", 0), a.get("date", "")), reverse=True)

    # Load existing scored
    existing = []
    if os.path.exists(SCORED_FILE):
        with open(SCORED_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    # Drop stale job-spam that leaked into scored in earlier (pre-filter) runs
    if existing:
        _before = len(existing)
        existing = [e for e in existing if not is_job_spam(e.get("title", ""))]
        if len(existing) != _before:
            print(f"Dropped {_before - len(existing)} stale job-spam from existing scored")
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
        event = detect_event(f"{title} {a.get('summary','')}")
        # 子赛道 domains（与 event_type 不同轴），既存 entry 也用于 tags 兜底补足
        try:
            from generator import classify_domain
            domains = classify_domain(title, a.get('summary', ''), [])
        except Exception:
            domains = []
        tags = detect_cross_tags(title, a.get('summary', ''),
                                 event_type=event,
                                 novelty=a.get('novelty', 0),
                                 region=config.get_source_region(a.get('source', ''))
                                 or (config.SOURCES.get(a.get('source_id', ''), {}) or {}).get('region') or "",
                                 domains=domains)
        recommendation = gen_recommendation(a, tags, event_type=event)
        # 信号强度脚本分（0~10，零成本）：0722 后仅 >=5 的文章喂强模
        _src_id = a.get("source_id", "")
        _tier = config.SOURCES.get(_src_id, {}).get("tier", 2)
        _sig_str, _sig_bd = compute_signal_strength(
            {"title": title, "summary": a.get("summary", ""), "date": a.get("date", "")},
            source_tier=_tier,
        )
        max_id += 1
        entry = {
            "title": title,
            "final_score": final_score,
            "signal_score": signal,
            "signal_strength": _sig_str,
            "signal_breakdown": _sig_bd,
            "category": category,
            "tags": tags[:5],
            "event_type": event,
            "domains": domains,
            "recommendation": recommendation,
            "id": max_id,
            "summary": a.get("summary", ""),
            "url": url,
            "source": a.get("source", ""),
            "date": a.get("date", ""),
            "viral": False,
            "view": "curated" if category != "archive" else "raw",
            "region": config.get_source_region(a.get("source", ""))
            or config.SOURCES.get(a.get("source_id", ""), {}).get("region")
            or ("overseas" if is_overseas(a.get("source", "")) else "domestic"),
        }
        new_entries.append(entry)

    print(f"New entries to add: {len(new_entries)}")
    high = sum(1 for e in new_entries if e["category"] == "high")
    watch = sum(1 for e in new_entries if e["category"] == "watch")
    print(f"  high: {high}, watch: {watch}, archive: {len(new_entries)-high-watch}")

    merged = existing + new_entries
    # Normalize region from config (source of truth) for ALL entries, so
    # previously-stored items from domestic sources (e.g. AgeClub) are corrected.
    for e in merged:
        rn = config.get_source_region(e.get("source", ""))
        if rn:
            e["region"] = rn
    # Sort by date desc
    merged.sort(key=lambda e: e.get("date", ""), reverse=True)

    with open(SCORED_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(merged)} total to {SCORED_FILE}")

    # 企业实体名回填（事件聚类主规则 entity_name+event_type 依赖此字段）。
    # 关键：即便单独跑 score_and_merge.py，也要在本步内把 entity_name 落库，
    # 不依赖 run_daily 后续编排，避免「entity_name 100% 为空」回归。
    # 优先企业库精确匹配，未命中走兜底规则；匹配不到留空，绝不瞎填。
    try:
        from selection import enrich_entity
        enrich_entity.run_daily_step()
    except Exception as e:  # noqa: BLE001
        print("  [WARN] enrich_entity 失败（不影响已落库评分）: %s" % e)


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
