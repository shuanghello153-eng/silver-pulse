"""
HTML generator for Silver Pulse daily brief — v4.
Event-type L1 classification + domain L2 (reuse enterprise categories).
Tags displayed separately from categories.
Search box inline with tag bar (compact).
Empty fields hidden in cards.
"""
import json
import os
import glob
import re
from datetime import datetime

from config import (
    SITE_TITLE, SITE_SUBTITLE, OUTPUT_DIR, DATA_DIR,
    NEWS_EVENT_TYPES, NEWS_DOMAINS, TAG_POOL,
    OVERSEAS_SOURCE_NAMES, SOURCES,
)

OVERSEAS_SOURCE_NAMES = OVERSEAS_SOURCE_NAMES  # alias for clarity
ALL_TAG_NAMES = set(TAG_POOL.keys())
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")


def load_raw_articles():
    raw_files = sorted(glob.glob(os.path.join(DATA_DIR, "raw_*.json")), reverse=True)
    if not raw_files:
        return []
    with open(raw_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def title_match(t1, t2):
    t1_clean = re.sub(r'\s+', '', t1.lower())[:50]
    t2_clean = re.sub(r'\s+', '', t2.lower())[:50]
    return t1_clean == t2_clean or (len(t1_clean) > 20 and t1_clean[:30] == t2_clean[:30])


def is_overseas_source(source_name):
    """Determine if a source is overseas.
    Uses fuzzy matching: check exact match first, then normalized match
    (ignore spaces/apostrophes), then check if source name is predominantly
    English (non-CJK characters) which indicates overseas."""
    s = source_name.strip()
    if not s:
        return False
    # Exact match
    if s in OVERSEAS_SOURCE_NAMES:
        return True
    # Normalized match (remove spaces, apostrophes, lowercase)
    def normalize(name):
        return name.lower().replace(" ", "").replace("'", "").replace("\u2019", "")
    s_norm = normalize(s)
    for os_name in OVERSEAS_SOURCE_NAMES:
        if normalize(os_name) == s_norm:
            return True
    # If source name is all English (no CJK characters), treat as overseas
    # This catches Forbes, Seeking Alpha, Bloomberg Law News, etc.
    has_cjk = any('\u4e00' <= c <= '\u9fff' for c in s)
    if not has_cjk and len(s) > 2:
        return True
    return False


def deduplicate_summary(title, summary):
    """Remove title-summary duplication: if summary starts with the title, strip it."""
    if not title or not summary:
        return summary or ""
    title_clean = title.strip()
    summary_clean = summary.strip()
    # Check if summary starts with the title (common in RSS feeds)
    if summary_clean[:len(title_clean)] == title_clean:
        remainder = summary_clean[len(title_clean):].lstrip("：:。.，, \n\r\t")
        return remainder if remainder else summary_clean
    # Check first 15 chars overlap
    if len(title_clean) > 10 and summary_clean[:15] == title_clean[:15]:
        # Try to find a delimiter after the overlap
        for delim in ["：", ":", "。", ".", "—", "-", "，", ","]:
            idx = summary_clean.find(delim, 10, 40)
            if idx >= 0:
                remainder = summary_clean[idx+1:].lstrip(" \n\r\t")
                if remainder:
                    return remainder
    return summary_clean


def translate_source_name(name):
    """Translate common English source names to Chinese for display."""
    translations = {
        "Home Health Care News": "家庭健康护理新闻",
        "McKnight's Senior Living": "McKnight's养老社区",
        "Senior Housing News": "养老住房新闻",
        "Hospice News": "临终关怀新闻",
        "Crunchbase News": "Crunchbase新闻",
        "TheGerontechnologist": "老年科技评论",
        "FierceHealthcare": "Fierce医疗",
        "MobiHealthNews": "移动健康新闻",
        "McKnight's Home Care": "McKnight's居家护理",
        "Google News": "谷歌新闻",
        # Extended translations
        "StockStory": "StockStory股票分析",
        "매일경제": "每日经济（韩国）",
        "streamlinefeed.co.ke": "StreamlineFeed（肯尼亚）",
        "digitalmore.co": "Digitalmore数字新闻",
        "PR Newswire": "PR新闻社",
        "Business Wire": "商业新闻社",
        "Yahoo Finance": "雅虎财经",
        "TechCrunch": "TechCrunch",
        "BetaKit": "BetaKit创投",
        "Pulse 2.0": "Pulse 2.0科技",
        "Modern Healthcare": "现代医疗",
        "HomeCare Magazine": "居家护理杂志",
        "FinSMEs": "FinSMEs创投",
        "HIT Consultant": "HIT医疗咨询",
        "Coverager": "Coverager保险",
        "Axios Pro Health Tech Deals": "Axios医疗交易",
        "FemTech Insider": "女性科技内幕",
        "Creating A New Healthcare": "新医疗",
        "StartUp Health": "StartUp Health",
        "AgeTech News": "AgeTech News",
        "Inc.": "Inc.杂志",
        "A2 Collective": "A2 Collective",
        "Agetech News": "Agetech News",
        "Fierce Biotech": "Fierce生物科技",
        "BioSpace": "BioSpace生物",
        "CISION": "CISION新闻",
        "GlobeNewswire": "环球新闻社",
        "EIN Presswire": "EIN新闻社",
        "Accesswire": "Accesswire新闻社",
        "Send2Press": "Send2Press新闻",
        "KoreaTechDesk": "韩国科技",
        "Korea IT Times": "韩国IT时报",
        "Chosun Biz": "朝鲜Biz",
        "KED Global": "韩国经济日报",
    }
    return translations.get(name.strip(), name)


def classify_event_type(title, summary, tags):
    """Classify article into one of NEWS_EVENT_TYPES based on keywords."""
    text = (title + " " + summary).lower() if title and summary else (title or "").lower()

    # Priority-ordered keyword matching
    if any(kw in text for kw in ["收购", "acquisition", "acquires", "merger", "并购", "被收购", "合并",
                                  "收购了", "被买", "buyout", "takeover", "合并了", "并购了",
                                  "sold to", "bought by", "acquired by"]):
        return "收购并购"

    if any(kw in text for kw in ["融资", "funding", "raises", "raised", "investment", "invest",
                                  "series a", "series b", "series c", "seed round", "天使轮",
                                  "a轮", "b轮", "c轮", "种子轮", "ipo", "上市",
                                  "venture capital", "vc", "round of funding",
                                  "secures funding", "secures investment", "获得投资",
                                  "获投", "获融", "capital raise", "funding round",
                                  "closes round", "raises $", "raised $",
                                  "融资过亿", "pre-series", "pre-a", "pre-seed"]):
        return "融资"

    if any(kw in text for kw in ["政策", "法规", "regulation", "policy", "medicare", "medicaid",
                                  "bill", "法案", "监管", "政府", "补贴", "长护险",
                                  "legislation", "fda", "cms", "rule", "规定",
                                  "指导意见", "管理办法", "条例"]):
        return "政策法规"

    if any(kw in text for kw in ["发布", "launch", "launched", "unveil", "unveiled", "announce",
                                  "announced", "新品", "上线", "新产品", "新服务",
                                  "product launch", "roll out", "rolled out", "debuts",
                                  "推出", "首发", "发布新"]):
        return "产品发布"

    if any(kw in text for kw in ["趋势", "report", "研究", "预测", "行业", "市场规模", "growth",
                                  "forecast", "trend", "insight", "analysis", "数据",
                                  "白皮书", "报告", "蓝皮书", "年度报告", "survey",
                                  "market size", "cagr", "compound annual",
                                  "outlook", "landscape"]):
        return "行业趋势"

    if any(kw in text for kw in ["高管", "ceo", "cfo", "coo", "cto", "加入", "离职", "离职",
                                  "任命", "离职", "人事", "joined", "leaves", "resigns",
                                  "appointed", "executive", "leadership", "换帅",
                                  "创始人", "联合创始人", "stepping down", "takes over"]):
        return "人事变动"

    return "其他事件"


def classify_domain(title, summary, tags):
    """Classify article into one or more NEWS_DOMAINS based on keywords."""
    text = (title + " " + summary).lower() if title and summary else (title or "").lower()
    matched = []

    # Map domain keywords to enterprise L1 categories — expanded for better coverage
    domain_keywords = {
        "购物渠道": ["购物", "电商", "retail", "shopping", "consumer", "渠道", "私域", "会员",
                     "京东", "淘宝", "拼多多", "商超", "超市", "直播带货", "d2c", "dtc", "品牌",
                     "brand", "连锁", "franchise", "分销", "distribution"],
        "日常用品": ["鞋", "服饰", "护肤", "染发", "假发", "shoes", "clothing", "skincare",
                     "hair", "cosmetic", "用品", "日常", "纸尿裤", "牙膏", "洗发", "美容",
                     "beauty", "wig", "染发剂", "成人用品", "卫生"],
        "健康食品": ["食品", "保健品", "营养", "益生菌", "蛋白", "羊奶", "无糖",
                     "supplement", "nutrition", "protein", "dietary", "otc",
                     "维生素", "钙片", "鱼油", "辅酶", "膳食", "功能食品", "特医食品",
                     "formula", "健康饮品", "奶制品", "organic", "有机"],
        "老年文娱": ["旅游", "教育", "社交", "广场舞", "相亲", "健身", "音乐",
                     "travel", "education", "social", "dance", "fitness", "music",
                     "entertainment", "leisure", "lifestyle", "老年大学", "老年教育",
                     "银发旅游", "康养旅游", "老年社交", "社区活动", "书法", "摄影",
                     "hobby", "兴趣", "课程", "school", "学习"],
        "健康服务": ["健康", "养生", "摔倒", "睡眠", "血压", "血糖", "慢病", "陪诊",
                     "health", "wellness", "fall detection", "sleep", "blood pressure",
                     "chronic", "monitoring", "remote patient", "telehealth",
                     "digital health", "care management", "互联网医疗", "在线问诊",
                     "慢病管理", "健康管理", "体检", "筛查", "体检中心", "数字医疗",
                     "远程医疗", "smart health", "医疗ai", "辅助诊断"],
        "适老化改造": ["适老", "改造", "智慧养老", "智能家居", "家居", "iot",
                       "smart home", "home modification", "accessibility", "aging in place",
                       "无障碍", "扶手", "防滑", "智能门锁", "紧急呼叫", "跌倒检测",
                       "传感器", "sensor", "适老化", "居家改造"],
        "行业服务": ["媒体", "展会", "咨询", "研究", "金融", "理财",
                     "media", "conference", "consulting", "research", "finance",
                     "investment", "capital", "fund", "协会", "智库", "杂志",
                     "行业报告", "白皮书", "峰会", "论坛", "评奖", "认证",
                     "标准", "培训", "培训服务", "数据平台", "信息平台"],
        "养老地产": ["地产", "住房", "社区", "运营商", "养老院", "中介",
                     "real estate", "housing", "community", "residential", "property",
                     "养老社区", "养老公寓", "senior living", "assisted living facility",
                     "ccrc", "nursing home", "护理院", "康养小镇", "养老小镇",
                     "退休社区", "retirement community", "长者社区", "ccrcs"],
        "养老服务": ["护理", "家政", "民政", "长护", "助餐", "助浴", "助洁", "临终",
                     "care", "nursing", "home care", "caregiver", "assisted living",
                     "long-term care", "hospice", "personal care", "duty care",
                     "居家养老", "社区养老", "机构养老", "照护", "护理员",
                     "caregiving", "居家护理", "上门服务", "日间照料", "喘息服务"],
        "养老用品": ["轮椅", "拐杖", "助听器", "眼镜", "失禁", "护理垫",
                     "wheelchair", "walker", "cane", "hearing aid", "incontinence",
                     "mobility", "assistive device", "daily living aid",
                     "助行器", "老花镜", "放大镜", "防走失", "智能药盒", "护理床",
                     "马桶椅", "洗澡椅", "安全扶手", "成人纸尿裤"],
        "康复设备": ["康复", "外骨骼", "运动康复", "手部康复", "神经康复",
                     "rehab", "rehabilitation", "exoskeleton", "physical therapy",
                     "robotic", "recovery", "理疗", "康复训练", "康复机器人",
                     "pt", "ot", "言语治疗", "occupational therapy", "康复中心"],
        "失智老人赛道": ["认知症", "痴呆", "阿尔茨海默", "失智", "早筛",
                         "dementia", "alzheimer", "cognitive", "memory care",
                         "cognitive impairment", "mci", "认知障碍", "脑健康",
                         "脑科学", "neuroscience", "neurodegenerative", "帕金森",
                         "parkinson", "脑萎缩", "认知训练", "脑力训练"],
        "产业资本/投资机构": ["投资机构", "基金", "vc", "pe", "资本", "风投",
                             "venture capital", "private equity", "fund", "investor",
                             "family office", "angel", "incubator", "lp", "gp",
                             "加速器", "孵化器", "母基金", "fof", "投资平台",
                             "资产管理", "asset management", "sovereign wealth"],
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in text for kw in keywords):
            matched.append(domain)

    if not matched:
        # Default: check if funding/acquisition related → "产业资本/投资机构"
        if any(kw in text for kw in ["funding", "融资", "raises", "investment", "收购",
                                      "acquisition", "merger", "ipo", "vc", "资本"]):
            matched.append("产业资本/投资机构")
        else:
            matched.append("健康服务")  # broadest fallback

    return matched


def merge_articles(scored, raw):
    scored_urls = {}
    scored_titles = {}
    for s in scored:
        url = (s.get('url', '') or '').split('?')[0].rstrip('/')
        if url:
            scored_urls[url] = s
        title = (s.get('title', '') or '').strip()
        if title:
            scored_titles[re.sub(r'\s+', '', title.lower())] = s

    merged = []
    seen_raw_urls = set()

    for s in scored:
        s['view'] = 'curated'
        src = s.get('source', '')
        s['region'] = 'overseas' if is_overseas_source(src) else ('domestic' if src else 'unknown')
        # Classify event type + domain
        title_text = s.get("title_cn") or s.get("title", "")
        summary_text = s.get("summary", "") or s.get("raw_content", "")
        tags_text = s.get("tags", [])
        s["event_type"] = classify_event_type(title_text, summary_text, tags_text)
        s["domains"] = classify_domain(title_text, summary_text, tags_text)
        # Keep all tags for filtering (both TAG_POOL and free-form tags)
        # Tags that look like domain names are also added to domains for domain filtering
        raw_tags = s.get("tags", [])
        clean_tags = [t for t in raw_tags if t and t not in {"raw", "curated"}]
        s["tags"] = clean_tags
        # Also add non-TAG_POOL tags to domains for dual filtering
        domain_tags = [t for t in raw_tags if t not in ALL_TAG_NAMES and t not in {"raw", "curated"}]
        if domain_tags:
            existing_domains = s.get("domains", [])
            s["domains"] = list(set(existing_domains + domain_tags))
        merged.append(s)
        url = (s.get('url', '') or '').split('?')[0].rstrip('/')
        if url:
            seen_raw_urls.add(url)

    for r in raw:
        url = (r.get('url', '') or '').split('?')[0].rstrip('/')
        if url and url in scored_urls:
            continue
        if url and url in seen_raw_urls:
            continue
        title = (r.get('title', '') or '').strip()
        title_key = re.sub(r'\s+', '', title.lower())
        if title_key in scored_titles:
            continue
        duplicate = False
        for st_key, st in scored_titles.items():
            if title_match(title, st.get('title', '')):
                duplicate = True
                break
        if duplicate:
            continue

        r['view'] = 'raw'
        r['final_score'] = 0
        r['category'] = 'raw'
        r['tags'] = []
        r['recommendation'] = ''
        r['viral'] = False
        src = r.get('source', '')
        r['region'] = 'overseas' if is_overseas_source(src) else ('domestic' if src else 'unknown')
        # Classify event type + domain for raw articles too
        title_text = r.get("title_cn") or r.get("title", "")
        summary_text = r.get("summary", "") or r.get("raw_content", "")
        r["event_type"] = classify_event_type(title_text, summary_text, [])
        r["domains"] = classify_domain(title_text, summary_text, [])
        merged.append(r)
        if url:
            seen_raw_urls.add(url)

    return merged


def build_card_html(art):
    title = art.get("title_cn") or art.get("title", "Untitled")
    url = art.get("url", "#")
    source_raw = art.get("source", "Unknown")
    source = translate_source_name(source_raw)
    date = art.get("date", "")
    raw_summary = (art.get("summary") or art.get("raw_content", "") or "")[:300]
    summary = deduplicate_summary(title, raw_summary)
    tags = art.get("tags", [])
    view = art.get("view", "curated")
    region = art.get("region", "unknown")
    event_type = art.get("event_type", "其他事件")
    domains = art.get("domains", [])
    is_viral = art.get("viral", False)

    # Build region badge
    region_tag = ""
    if region == "overseas":
        region_tag = '<span class="badge-region region-overseas">海外</span>'
    elif region == "domestic":
        region_tag = '<span class="badge-region region-domestic">国内</span>'

    # Build viral badge
    viral_badge = '<span class="viral-tag">🔥</span>' if is_viral else ''

    # Build event type badge (highlighted)
    event_badge = '<span class="badge-event">%s</span>' % event_type

    # Build domain badges (secondary)
    domain_badges = "".join(
        '<span class="badge-domain">%s</span>' % d for d in domains[:3]
    )

    # Build tag badges (from TAG_POOL)
    tag_badges = "".join(
        '<span class="badge-tag">%s</span>' % t for t in tags[:5]
    )

    # Build meta line: source + region + viral
    meta_parts = ['<span class="feed-source">%s</span>' % source]
    if region_tag:
        meta_parts.append(region_tag)
    if viral_badge:
        meta_parts.append(viral_badge)
    meta_html = '<div class="feed-meta">%s</div>' % " ".join(meta_parts)

    # Build classification line: event type + domains
    class_parts = [event_badge]
    if domain_badges:
        class_parts.append(domain_badges)
    class_html = '<div class="feed-class">%s</div>' % " ".join(class_parts)

    # Tags at the bottom (after recommendation)
    tag_html = '<div class="feed-tags">%s</div>' % tag_badges if tag_badges else ""

    # Build summary (only if not empty after dedup)
    summary_html = '<p class="feed-summary">%s</p>' % summary if summary else ""

    # Recommendation (only if not empty) — AI analysis, shown in blue
    rec = art.get("recommendation", "")
    rec_html = '<p class="feed-rec">%s</p>' % rec if rec else ""

    # Card structure: meta → class → title → summary → rec → tags(bottom)
    card = (
        '<div class="feed-item" data-view="%s" '
        'data-date="%s" data-event="%s" data-domains="%s" '
        'data-tags="%s" data-region="%s">\n'
        '  <div class="feed-time">%s</div>\n'
        '  <div class="feed-body">\n'
        '    %s\n'
        '    %s\n'
        '    <h3 class="feed-title"><a href="%s" target="_blank" rel="noopener">%s</a></h3>\n'
        '%s'
        '%s\n'
        '%s\n'
        '  </div>\n'
        '</div>'
    ) % (
        view, date or "", event_type, ",".join(domains),
        ",".join(tags), region,
        date or "",
        meta_html,
        class_html,
        url, title,
        summary_html,
        rec_html,
        tag_html,
    )
    return card


# === CSS Stylesheet ===
CSS_STYLES = """
:root{--bg:#f5f5f5;--sidebar-bg:#fff;--card-bg:#fff;--text:#1a1a1a;
--text-secondary:#666;--text-muted:#999;--border:#e8e8e8;--accent:#0891b2;
--accent-light:#ecfeff;--radius:8px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;display:flex;min-height:100vh}
.sidebar{width:200px;background:var(--sidebar-bg);border-right:1px solid var(--border);position:fixed;top:0;left:0;height:100vh;overflow-y:auto;padding:20px 0;flex-shrink:0;z-index:10}
.sidebar-logo{padding:0 16px 16px;border-bottom:1px solid var(--border);margin-bottom:12px}
.sidebar-logo h1{font-size:18px;font-weight:700;color:var(--accent)}
.logo-sub{font-size:11px;color:var(--text-muted);margin-top:2px}
.nav-section{padding:4px 0}
.nav-label{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;padding:6px 16px 4px;font-weight:600}
.nav-item{display:block;padding:8px 16px 8px 24px;font-size:13px;color:var(--text-secondary);text-decoration:none;cursor:pointer;border-left:3px solid transparent;transition:all .15s;position:relative}
.nav-item:hover{background:#fafafa;color:var(--text)}
.nav-item.active{background:var(--accent-light);color:var(--accent);border-left-color:var(--accent);font-weight:600}
.nav-divider{height:1px;background:var(--border);margin:8px 16px}
.main{flex:1;margin-left:200px;max-width:980px;width:calc(100% - 200px);padding:24px 32px 60px}
.header{margin-bottom:20px}
.header-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.header h2{font-size:20px;font-weight:700}
.header-stats{font-size:12px;color:var(--text-muted)}
.view-pills{display:inline-flex;gap:3px;background:var(--bg);padding:2px;border-radius:18px;margin-bottom:0}
.view-pill{padding:4px 14px;border-radius:16px;border:none;background:transparent;cursor:pointer;font-size:12px;font-weight:500;color:var(--text-secondary);transition:all .15s}
.view-pill.active{background:var(--card-bg);color:var(--text);box-shadow:0 1px 3px rgba(0,0,0,.08);font-weight:600}
.filter-bar{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px}
.region-pills{display:inline-flex;gap:3px;vertical-align:middle}
.region-pill{padding:4px 12px;border-radius:16px;border:1px solid var(--border);background:var(--card-bg);cursor:pointer;font-size:11px;color:var(--text-secondary);transition:all .15s;white-space:nowrap}
.region-pill.active{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.filter-section{margin-bottom:12px}
.filter-row{display:flex;align-items:center;gap:5px;margin-bottom:4px;flex-wrap:wrap}
.filter-label{font-size:11px;color:var(--text-muted);min-width:36px;font-weight:600}
.filter-btns{display:flex;flex-wrap:wrap;gap:3px;flex:1}
.filter-btn{padding:2px 9px;border-radius:12px;border:1px solid var(--border);background:var(--card-bg);font-size:11px;cursor:pointer;color:var(--text-secondary);white-space:nowrap;transition:all .12s}
.filter-btn:hover{border-color:var(--accent);color:var(--accent)}
.filter-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.search-inline{padding:4px 12px;border:1px solid var(--border);border-radius:12px;font-size:11px;outline:none;background:var(--card-bg);color:var(--text);width:160px;transition:all .15s;flex-shrink:0}
.search-inline:focus{border-color:var(--accent);box-shadow:0 0 0 2px rgba(8,145,178,.08);width:220px}

/* Feed cards */
.feed-item{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid var(--border)}
.feed-item:last-child{border-bottom:none}
.feed-time{flex-shrink:0;width:48px;font-size:12px;font-weight:700;color:var(--text-muted);padding-top:2px;text-align:right}
.feed-body{flex:1;min-width:0}
.feed-meta{display:flex;align-items:center;gap:5px;margin-bottom:2px;flex-wrap:wrap}
.feed-source{font-size:11px;color:var(--text-muted);font-weight:500}
.feed-class{display:flex;align-items:center;gap:3px;margin-bottom:4px;flex-wrap:wrap}
.feed-title{font-size:14px;font-weight:600;line-height:1.4;margin-bottom:2px}
.feed-title a{color:var(--text);text-decoration:none}
.feed-title a:hover{color:var(--accent)}
.feed-summary{font-size:12px;color:var(--text-secondary);line-height:1.5;margin-bottom:3px}
.feed-rec{font-size:12px;color:var(--accent);line-height:1.45;margin-bottom:3px;border-left:2px solid var(--accent);padding-left:7px}
.feed-tags{display:flex;flex-wrap:wrap;gap:3px;margin-top:4px}

/* Badges */
.badge-region{font-size:10px;padding:1px 6px;border-radius:9px;font-weight:600}
.badge-region.region-overseas{background:#ecfdf5;color:#065f46}
.badge-region.region-domestic{background:#eff6ff;color:#1e40af}
.badge-event{font-size:10px;padding:1px 7px;border-radius:3px;background:#fef3c7;color:#92400e;font-weight:600}
.badge-domain{font-size:10px;padding:1px 7px;border-radius:3px;background:#f0f0f0;color:var(--text-secondary);font-weight:500}
.badge-tag{font-size:10px;padding:1px 7px;border-radius:3px;background:#e0f2fe;color:#0369a1;font-weight:500}
.viral-tag{font-size:13px;font-weight:700;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}

.footer{text-align:center;padding:32px 0 16px;font-size:12px;color:var(--text-muted);border-top:1px solid var(--border);margin-top:24px}
.hidden{display:none!important}
@media(max-width:768px){.sidebar{display:none}.main{margin-left:0;width:100%;padding:16px;max-width:100%}.feed-time{width:42px;font-size:11px}.feed-title{font-size:14px}.search-inline{width:100px}.search-inline:focus{width:140px}}
"""


JS_SCRIPT = """
let activeView='curated';
let activeRegion='all';
let activeEvent='all';
let activeDomain='all';
let activeTag='all';
let searchTerm='';
const items=document.querySelectorAll('.feed-item');

function updateDisplay(){
  let visible=0;
  items.forEach(item=>{
    const v=item.dataset.view;
    const evt=item.dataset.event||'';
    const doms=item.dataset.domains||'';
    const tgs=item.dataset.tags||'';
    const reg=item.dataset.region||'';
    const titleEl=item.querySelector('.feed-title');
    const summaryEl=item.querySelector('.feed-summary');
    const title=titleEl?titleEl.textContent.toLowerCase():'';
    const summary=summaryEl?summaryEl.textContent.toLowerCase():'';

    const vm=activeView==='all'||v==='curated'||v==='raw';
    const rm=activeRegion==='all'||reg===activeRegion;
    const em=activeEvent==='all'||evt===activeEvent;
    const dm=activeDomain==='all'||doms.split(',').includes(activeDomain);
    const tm=activeTag==='all'||tgs.split(',').includes(activeTag);
    const sm=searchTerm===''||title.includes(searchTerm)||summary.includes(searchTerm);
    if(vm&&rm&&em&&dm&&tm&&sm){
      item.style.display='flex';
      visible++;
    }else{item.style.display='none'}
  });
  const s=document.getElementById('header-stats');
  s.textContent='更新于 %s · 共 '+visible+' 条';
}

function setView(view){
  activeView=view;activeEvent='all';activeDomain='all';activeTag='all';searchTerm='';
  document.getElementById('search-input').value='';
  document.getElementById('pill-curated').classList.toggle('active',view==='curated');
  document.getElementById('pill-all').classList.toggle('active',view==='all');
  document.querySelectorAll('.filter-btn[data-group="event"]').forEach(b=>b.classList.toggle('active',b.dataset.value==='all'));
  document.querySelectorAll('.filter-btn[data-group="domain"]').forEach(b=>b.classList.toggle('active',b.dataset.value==='all'));
  document.querySelectorAll('.filter-btn[data-group="tag"]').forEach(b=>b.classList.toggle('active',b.dataset.value==='all'));
  document.querySelectorAll('.region-pill').forEach(b=>b.classList.toggle('active',b.dataset.region==='all'));
  activeRegion='all';updateDisplay();
}

document.querySelectorAll('.region-pill').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.region-pill').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeRegion=this.dataset.region;updateDisplay();
  });
});
document.querySelectorAll('.filter-btn[data-group="event"]').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.filter-btn[data-group="event"]').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeEvent=this.dataset.value;updateDisplay();
  });
});
document.querySelectorAll('.filter-btn[data-group="domain"]').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.filter-btn[data-group="domain"]').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeDomain=this.dataset.value;updateDisplay();
  });
});
document.querySelectorAll('.filter-btn[data-group="tag"]').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.filter-btn[data-group="tag"]').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeTag=this.dataset.value;updateDisplay();
  });
});
document.getElementById('search-input').addEventListener('input',function(){
  searchTerm=this.value.toLowerCase().trim();updateDisplay();
});
updateDisplay();
"""


def generate_html(scored_articles=None, output_path=None):
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "index.html")

    if scored_articles is None:
        from scorer import load_scored
        scored_articles = load_scored()

    raw_articles = load_raw_articles()
    merged = merge_articles(scored_articles, raw_articles)
    merged.sort(key=lambda a: a.get("date", "0000-00-00"), reverse=True)

    # Collect present event types, domains, tags from all articles
    present_events = set()
    present_domains = set()
    present_tags = set()
    for art in merged:
        evt = art.get("event_type", "")
        if evt:
            present_events.add(evt)
        for d in art.get("domains", []):
            present_domains.add(d)
        for t in art.get("tags", []):
            if t and t not in {"raw", "curated"}:
                present_tags.add(t)

    # Order: follow config order
    event_list = [e for e in NEWS_EVENT_TYPES.keys() if e in present_events]
    domain_list = [d for d in NEWS_DOMAINS if d in present_domains]
    tag_list = sorted(present_tags)

    curated_count = sum(1 for a in merged if a.get("view") == "curated")
    total_count = len(merged)
    domestic_curated = sum(1 for a in merged if a.get("view") == "curated" and a.get("region") == "domestic")
    overseas_curated = sum(1 for a in merged if a.get("view") == "curated" and a.get("region") == "overseas")

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build cards
    cards_html = "".join(build_card_html(art) for art in merged)

    # Build filter buttons
    event_buttons = "".join(
        '<button class="filter-btn" data-group="event" data-value="%s">%s</button>' % (e, e) for e in event_list
    )
    domain_buttons = "".join(
        '<button class="filter-btn" data-group="domain" data-value="%s">%s</button>' % (d, d) for d in domain_list
    )
    tag_buttons = "".join(
        '<button class="filter-btn" data-group="tag" data-value="%s">%s</button>' % (t, t) for t in tag_list
    )

    # Inject values into JS template
    js = JS_SCRIPT % (today_str,)

    # Assemble full HTML
    parts = [
        '<!-- build:%s -->\n' % BUILD_STAMP,
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">',
        '<meta http-equiv="Pragma" content="no-cache">',
        '<meta http-equiv="Expires" content="0">',
        '<title>%s</title>' % SITE_TITLE,
        '<style>%s</style>' % CSS_STYLES,
        '</head>\n<body>',

        # Sidebar
        '<div class="sidebar">',
        '<div class="sidebar-logo">',
        '<h1>Silver Pulse 银脉</h1>',
        '<p class="logo-sub">Silver Pulse</p>',
        '</div>',
        '<div class="nav-section">',
        '<div class="nav-label">内容</div>',
        '<a href="index.html" class="nav-item active">资讯看板</a>',
        '<a href="enterprise.html" class="nav-item">企业库</a>',
        '<a href="about.html" class="nav-item">网站说明</a>',
        '</div>',
        '</div>',

        # Main content
        '<div class="main">',
        '<div class="header">',
        '<div class="header-top">',
        '<h2>银发经济每日速览</h2>',
        '<div class="header-stats" id="header-stats">更新于 %s · 共 %s 条</div>' % (today_str, total_count),
        '</div>',
        '<div class="filter-bar">',
        '<div class="view-pills">',
        '<button class="view-pill active" id="pill-curated" onclick="setView(\'curated\')">精选(%s)</button>' % curated_count,
        '<button class="view-pill" id="pill-all" onclick="setView(\'all\')">全量(%s)</button>' % total_count,
        '</div>',
        '<div class="region-pills" id="region-pills">',
        '<button class="region-pill active" data-region="all">全部</button>',
        '<button class="region-pill" data-region="domestic">国内(%s)</button>' % domestic_curated,
        '<button class="region-pill" data-region="overseas">海外(%s)</button>' % overseas_curated,
        '</div>',
        '<input class="search-inline" type="text" id="search-input" placeholder="搜索标题或摘要...">',
        '</div></div>',

        # Filter section (event type + domain + tags + search)
        '<div class="filter-section" id="filter-section">',
        # Event type row
        '<div class="filter-row">',
        '<span class="filter-label">事件:</span>',
        '<div class="filter-btns">',
        '<button class="filter-btn active" data-group="event" data-value="all">全部</button>',
        event_buttons,
        '</div>',
        '</div>',
        # Domain row
        '<div class="filter-row">',
        '<span class="filter-label">领域:</span>',
        '<div class="filter-btns">',
        '<button class="filter-btn active" data-group="domain" data-value="all">全部</button>',
        domain_buttons,
        '</div>',
        '</div>',
        # Tag row
        '<div class="filter-row">',
        '<span class="filter-label">标签:</span>',
        '<div class="filter-btns">',
        '<button class="filter-btn active" data-group="tag" data-value="all">全部</button>',
        tag_buttons,
        '</div>',
        '</div>',
        '</div>',

        # Feed container
        '<div id="feed-container">',
        cards_html,
        '</div>',

        # Footer
        '<div class="footer">',
        '<p>Silver Pulse 银脉 · 银发经济投融资每日速览</p>',
        '<p>Powered by WorkBuddy · 海外 + 中文双源覆盖</p>',
        '</div>',

        # Close main + body
        '</div>',
        '\n<script>\n%s\n</script>\n</body>\n</html>' % js,
    ]

    html = "\n".join(parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also write to project root for GitHub Pages
    root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(root_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated: %s" % output_path)
    print("Articles: %s total (%s curated)" % (total_count, curated_count))
    print("Event types: %s" % event_list)
    print("Domains: %s" % domain_list)
    print("Tags: %s" % tag_list)
    return output_path


if __name__ == "__main__":
    from scorer import load_scored
    articles = load_scored()
    if articles:
        generate_html(articles)
    else:
        print("No scored articles found.")
