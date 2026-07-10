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
import html
import hashlib
from datetime import datetime, timedelta

import config
from config import (
    SITE_TITLE, SITE_SUBTITLE, OUTPUT_DIR, DATA_DIR,
    NEWS_EVENT_TYPES, NEWS_DOMAINS, TAG_POOL,
    OVERSEAS_SOURCE_NAMES, SOURCES, SOURCE_NAME_TO_TIER,
)

from ui_common import COMMON_CSS as CSS_STYLES, SIDEBAR, THEME_JS, FEEDBACK_CSS, FEEDBACK_JS
from ui_common import sp_card_actions, sp_note_placeholder

OVERSEAS_SOURCE_NAMES = OVERSEAS_SOURCE_NAMES  # alias for clarity
ALL_TAG_NAMES = set(TAG_POOL.keys())
BUILD_STAMP = datetime.now().strftime("%Y%m%d%H%M%S")

_esc = html.escape


def _url_hash(url):
    """Stable short hash of a URL for use as an HTML anchor id."""
    return hashlib.md5((url or "").encode("utf-8")).hexdigest()[:10]


def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


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

    if any(kw in text for kw in ["ipo", "上市", "敲钟", "挂牌", "公开募股",
                                  "goes public", "listed on", "listing",
                                  "首次公开发行", "新股上市", "港交所", "纳斯达克"]):
        return "IPO上市"

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
        _reg = config.get_source_region(src)
        s['region'] = _reg if _reg else ('overseas' if is_overseas_source(src) else ('domestic' if src else 'unknown'))
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
        _reg = config.get_source_region(src)
        r['region'] = _reg if _reg else ('overseas' if is_overseas_source(src) else ('domestic' if src else 'unknown'))
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
    raw_summary = (art.get("summary_cn") or art.get("summary") or art.get("raw_content", "") or "")[:300]
    summary = deduplicate_summary(title, raw_summary)
    tags = art.get("tags", []) or []
    view = art.get("view", "curated")
    region = art.get("region", "unknown")
    event_type = art.get("event_type", "其他事件")
    domains = art.get("domains", []) or []
    # 卡片去重：标签若与领域同名（如"健康服务"既是领域又是兜底标签），
    # 只在领域徽章展示一次，避免「同一词双显」。
    _domain_set = set(domains)
    tags = [t for t in tags if t and t not in _domain_set]
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

    # Recommendation (only if not empty) — ★ 前缀，对齐企业库紧凑风格
    rec = art.get("recommendation", "")
    rec_html = '<p class="feed-rec">★ %s</p>' % rec if rec else ""

    # Card structure: meta → class → title → summary → rec → tags(bottom)
    url_hash = _url_hash(url)
    entity_name = art.get("entity_name", "") or ""
    src_search = art.get("source", "") or ""
    # 评分面板（与精选卡片完全一致：评分 + 6 维 + 收藏）
    fs = art.get("final_score") or 0
    ds = art.get("dim_scores") or {}
    dims = [
        ("产业", ds.get("industry")),
        ("信号", ds.get("signal")),
        ("文笔", ds.get("writing")),
        ("中文契合", ds.get("cn_fit")),
        ("时效", ds.get("urgency")),
        ("反常", ds.get("novelty")),
    ]
    # 6 维评分芯片
    dim_html = "".join(
        '<span class="dim-chip">%s <b>%s</b></span>' % (k, _fmt_score(v)) for k, v in dims
    )
    fav_html = '<button class="fav-btn" data-type="news" data-id="%s"><span class="ico">☆</span><span class="lbl">收藏</span></button>' % url_hash
    score_html = (
        '<div class="sel-scores">'
        '<span class="badge-score %s" title="评分">%s</span>'
        '<span class="dim-line">%s</span>'
        '%s'
        '</div>'
    ) % (_score_class(fs), _fmt_score(fs), dim_html, fav_html)
    # 列表内操作按钮（不再显示 / 备注 / 已读）
    actions_html = sp_card_actions("news", url_hash, with_read=True)
    actions_line = '<div class="feed-tags" style="margin-top:6px;">%s</div>' % actions_html
    # 卡片底部备注占位（点击编辑，仅存本机）
    note_html = sp_note_placeholder("news", url_hash)
    extra = []
    cl = art.get("cluster_id", "") or ""
    if entity_name:
        extra.append('<span class="badge-tag">主体 %s</span>' % _esc(entity_name))
    if cl:
        extra.append('<span class="badge-domain" title="该资讯与同主题其他资讯被系统归为一组，便于横向对比">同主题</span>')
    extra_html = '<div class="feed-tags">%s</div>' % " ".join(extra) if extra else ""
    novelty = float(art.get("novelty") or 0)
    signal = float(art.get("signal") or (art.get("dim_scores") or {}).get("signal") or 0)
    funded = 1 if (art.get("event_type") == "融资" or "融资" in (art.get("tags") or [])) else 0
    tier = SOURCE_NAME_TO_TIER.get(src_search, art.get("tier") or "")
    card = (
        '<div class="feed-item" id="news-%s" data-card-id="%s" data-view="%s" data-score="%s" '
        'data-date="%s" data-event="%s" data-domains="%s" '
        'data-tags="%s" data-region="%s" '
        'data-entity="%s" data-source="%s" data-tier="%s" '
        'data-novelty="%s" data-signal="%s" data-funded="%s">\n'
        '  <div class="feed-time">%s</div>\n'
        '  <div class="feed-body">\n'
        '    %s\n'
        '    %s\n'
        '    <h3 class="feed-title"><a href="%s" target="_blank" rel="noopener">%s</a></h3>\n'
        '%s'
        '%s\n'
        '%s\n'
        '%s\n'
        '%s\n'
        '%s\n'
        '%s\n'
        '  </div>\n'
        '</div>'
    ) % (
        url_hash, url_hash, view, _fmt_score(fs), date or "", event_type, ",".join(domains),
        ",".join(tags), region,
        entity_name, src_search, SOURCE_NAME_TO_TIER.get(src_search, art.get("tier") or ""),
        novelty, signal, funded,
        date or "",
        meta_html,
        class_html,
        url, title,
        summary_html,
        rec_html,
        score_html,
        actions_line,
        extra_html,
        tag_html,
        note_html,
    )
    return card


def is_selected(art):
    """Selection rule for the 精选 (Selected) view.

    is_curated True, OR final_score >= tiered watch threshold:
    T1 watch>=4.0, T2 watch>=5.0, T3 watch>=6.0. Falls back to
    final_score>=5.0 when tier is missing.
    """
    if art.get("is_curated"):
        return True
    s = art.get("final_score") or 0
    t = art.get("tier")
    thr = {1: 4.0, 2: 5.0, 3: 6.0}.get(t, 5.0)
    return s >= thr


def _fmt_score(v):
    try:
        return "%.1f" % float(v)
    except Exception:
        return "-" if v in (None, "") else str(v)


def _score_class(score):
    """Return color-tier CSS suffix for badge-score: s-high(≥7) / s-mid(4–6.9) / s-low(<4)."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "s-low"
    if s >= 7.0:
        return "s-high"
    elif s >= 4.0:
        return "s-mid"
    return "s-low"


def build_selected_card_html(art):
    """Build a 精选 card that mirrors the full news-list card style, but also
    shows the recommendation reason, the 5 dim scores + final_score, and any
    entity/cluster tag. Uses only existing fields from scored_latest.json."""
    title = art.get("title_cn") or art.get("title", "Untitled")
    url = art.get("url", "#")
    source_raw = art.get("source", "Unknown")
    source = translate_source_name(source_raw)
    date = art.get("date", "")
    raw_summary = (art.get("summary_cn") or art.get("summary") or art.get("raw_content", "") or "")[:300]
    summary = deduplicate_summary(title, raw_summary)
    tags = art.get("tags", []) or []
    region = art.get("region", "unknown")
    event_type = art.get("event_type", "其他事件")
    domains = art.get("domains", []) or []
    # 卡片去重：标签若与领域同名，只在领域徽章展示一次（避免双显）
    _domain_set = set(domains)
    tags = [t for t in tags if t and t not in _domain_set]
    viral = art.get("viral", False)

    region_tag = ""
    if region == "overseas":
        region_tag = '<span class="badge-region region-overseas">海外</span>'
    elif region == "domestic":
        region_tag = '<span class="badge-region region-domestic">国内</span>'
    viral_badge = '<span class="viral-tag">🔥</span>' if viral else ''

    event_badge = '<span class="badge-event">%s</span>' % event_type
    domain_badges = "".join('<span class="badge-domain">%s</span>' % d for d in domains[:3])
    tag_badges = "".join('<span class="badge-tag">%s</span>' % t for t in tags[:5])

    meta_parts = ['<span class="feed-source">%s</span>' % source]
    if region_tag:
        meta_parts.append(region_tag)
    if viral_badge:
        meta_parts.append(viral_badge)
    meta_html = '<div class="feed-meta">%s</div>' % " ".join(meta_parts)

    class_parts = [event_badge]
    if domain_badges:
        class_parts.append(domain_badges)
    class_html = '<div class="feed-class">%s</div>' % " ".join(class_parts)
    tag_html = '<div class="feed-tags">%s</div>' % tag_badges if tag_badges else ""

    summary_html = '<p class="feed-summary">%s</p>' % summary if summary else ""

    # 推荐理由 — actual field in scored_latest.json is `recommendation`
    rec = art.get("recommendation", "") or art.get("recommendation_reason", "")
    rec_html = '<p class="feed-rec">★ %s</p>' % rec if rec else ""

    # 评分面板：评分 + 5 维评分
    fs = art.get("final_score") or 0
    ds = art.get("dim_scores") or {}
    dims = [
        ("产业", ds.get("industry")),
        ("信号", ds.get("signal")),
        ("文笔", ds.get("writing")),
        ("中文契合", ds.get("cn_fit")),
        ("时效", ds.get("urgency")),
        ("反常", ds.get("novelty")),
    ]
    # 6 维人话解释（悬停可见）
    # 6 维评分芯片
    dim_html = "".join(
        '<span class="dim-chip">%s <b>%s</b></span>' % (k, _fmt_score(v)) for k, v in dims
    )
    url_hash = _url_hash(url)
    fav_html = '<button class="fav-btn" data-type="news" data-id="%s"><span class="ico">☆</span><span class="lbl">收藏</span></button>' % url_hash
    score_html = (
        '<div class="sel-scores">'
        '<span class="badge-score %s" title="评分">%s</span>'
        '<span class="dim-line">%s</span>'
        '%s'
        '</div>'
    ) % (_score_class(fs), _fmt_score(fs), dim_html, fav_html)
    # 列表内操作按钮（不再显示 / 备注 / 已读）
    actions_html = sp_card_actions("news", url_hash, with_read=True)
    actions_line = '<div class="feed-tags" style="margin-top:6px;">%s</div>' % actions_html
    # 卡片底部备注占位（点击编辑，仅存本机）
    note_html = sp_note_placeholder("news", url_hash)

    # 主体 / 聚类 标签
    extra = []
    ent = art.get("entity_name", "") or ""
    cl = art.get("cluster_id", "") or ""
    if ent:
        extra.append('<span class="badge-tag">主体 %s</span>' % _esc(ent))
    if cl:
        extra.append('<span class="badge-domain" title="该资讯与同主题其他资讯被系统归为一组，便于横向对比">同主题</span>')
    extra_html = '<div class="feed-tags">%s</div>' % " ".join(extra) if extra else ""

    entity_name = art.get("entity_name", "") or ""
    src_search = art.get("source", "") or ""
    novelty = float(art.get("novelty") or 0)
    signal = float(art.get("signal") or (art.get("dim_scores") or {}).get("signal") or 0)
    funded = 1 if (art.get("event_type") == "融资" or "融资" in (art.get("tags") or [])) else 0
    card = (
        '<div class="feed-item" id="news-%s" data-card-id="%s" data-view="selected" data-score="%s" '
        'data-date="%s" data-event="%s" data-domains="%s" '
        'data-tags="%s" data-region="%s" '
        'data-entity="%s" data-source="%s" data-tier="%s" '
        'data-novelty="%s" data-signal="%s" data-funded="%s">\n'
        '  <div class="feed-time">%s</div>\n'
        '  <div class="feed-body">\n'
        '    %s\n'
        '    %s\n'
        '    <h3 class="feed-title"><a href="%s" target="_blank" rel="noopener">%s</a></h3>\n'
        '%s'
        '%s\n'
        '%s\n'
        '%s\n'
        '%s\n'
        '%s\n'
        '  </div>\n'
        '</div>'
    ) % (
        url_hash, url_hash, _fmt_score(fs), date or "", event_type, ",".join(domains),
        ",".join(tags), region,
        entity_name, src_search, SOURCE_NAME_TO_TIER.get(src_search, art.get("tier") or ""),
        novelty, signal, funded,
        date or "",
        meta_html,
        class_html,
        url, title,
        summary_html,
        rec_html,
        score_html,
        actions_line,
        extra_html,
        note_html,
    )
    return card


def read_update_log():
    p = os.path.join(DATA_DIR, "update_log.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def write_update_log(log):
    p = os.path.join(DATA_DIR, "update_log.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def update_update_log(selected_count):
    """Update data/update_log.json: refresh today's count or prepend a new entry.

    Returns the resulting log list so the caller can render the timeline.
    """
    log = read_update_log()
    today = datetime.now().strftime("%Y-%m-%d")
    updated = False
    for e in log:
        if e.get("date") == today:
            e["count"] = selected_count
            updated = True
            break
    if not updated:
        log.insert(0, {"date": today, "count": selected_count})
    write_update_log(log)
    return log


def build_timeline_html(log):
    if not log:
        return ""
    entries = []
    for e in log:
        d = e.get("date", "")
        c = e.get("count", 0)
        entries.append(
            '<div class="timeline-entry" data-date="%s">'
            '<span class="timeline-date">📅 %s</span>'
            '<span class="timeline-count">精选 %s 条</span>'
            '</div>' % (_esc(d), _esc(d), _esc(str(c)))
        )
    return (
        '<div class="update-timeline" id="update-timeline">'
        '<div class="timeline-title">🕒 精选更新时间线（每日精选条数）</div>'
        '<div class="timeline-list">%s</div>'
        '</div>' % "\n".join(entries)
    )


# === CSS Stylesheet ===

JS_SCRIPT = """
let activeView='curated';
let activeRegion='all';
let activeEvent='all';
let activeDomain='all';
let activeTag='all';
let searchTerm='';
let sortMode='score';
let sortDir='desc';
let activeTime='all';
window.spReapply=updateDisplay;
const feedItems=document.querySelectorAll('.feed-item');
const feedContainer=document.getElementById('feed-container');
const selectedContainer=document.getElementById('selected-container');

function sortContainer(c){
  if(!c)return;
  const items=Array.from(c.querySelectorAll('.feed-item'));
  items.sort(function(a,b){
    if(sortMode==='date'){
      return (b.dataset.date||'')<(a.dataset.date||'')?-1:1;
    }
    if(sortMode==='signal'){
      const sa=parseFloat(a.dataset.signal)||0, sb=parseFloat(b.dataset.signal)||0;
      if(sb!==sa) return sb-sa;
      return (parseFloat(b.dataset.score)||0)-(parseFloat(a.dataset.score)||0);
    }
    const va=parseFloat(a.dataset.score)||0, vb=parseFloat(b.dataset.score)||0;
    let cmp = vb-va;
    if(sortDir==='asc') cmp=-cmp;
    return cmp;
  });
  items.forEach(function(it){c.appendChild(it);});
}

function updateDisplay(){
  let visible=0;
  feedItems.forEach(item=>{
    const v=item.dataset.view;
    const evt=item.dataset.event||'';
    const doms=item.dataset.domains||'';
    const tgs=item.dataset.tags||'';
    const reg=item.dataset.region||'';
    const titleEl=item.querySelector('.feed-title');
    const summaryEl=item.querySelector('.feed-summary');
    const title=titleEl?titleEl.textContent.toLowerCase():'';
    const summary=summaryEl?summaryEl.textContent.toLowerCase():'';
    const entity=(item.dataset.entity||'').toLowerCase();
    const source=(item.dataset.source||'').toLowerCase();
    const vm=(activeView==='curated') ? (v==='selected') : (v==='curated'||v==='raw');
    if(!vm){ item.style.display='none'; return; }
    const rm=activeRegion==='all'||reg===activeRegion;
    const em=activeEvent==='all'||evt===activeEvent;
    const dm=activeDomain==='all'||doms.split(',').includes(activeDomain);
    const tm=activeTag==='all'||tgs.split(',').includes(activeTag);
    const sm=searchTerm===''||title.includes(searchTerm)||summary.includes(searchTerm)||entity.includes(searchTerm)||source.includes(searchTerm)||tgs.toLowerCase().includes(searchTerm);
    const hiddenMatch=(window.spShowHidden===true)||(item.dataset.hide!=='1');
    const readMatch=(window.spUnreadOnly===true)?(item.dataset.read!=='1'):true;
    const dateStr=item.dataset.date||'';
    let tmTime=true;
    if(activeTime!=='all'&&dateStr){
      const days={'1w':7,'2w':14,'1m':30,'3m':90}[activeTime]||0;
      const cut=new Date();cut.setDate(cut.getDate()-days);
      const d=new Date(dateStr.replace(/-/g,'/'));
      tmTime = d>=cut;
    }
    if(rm&&em&&dm&&tm&&sm&&tmTime&&hiddenMatch&&readMatch){
      item.style.display='flex';
      visible++;
    }else{item.style.display='none'}
  });
  if(activeView==='curated'){
    if(feedContainer) feedContainer.style.display='none';
    if(selectedContainer) selectedContainer.style.display='block';
  }else{
    if(feedContainer) feedContainer.style.display='block';
    if(selectedContainer) selectedContainer.style.display='none';
  }
  sortContainer(activeView==='curated'?selectedContainer:feedContainer);
  const s=document.getElementById('header-stats');
  s.textContent='更新于 %s · 数据 %s · 共 '+visible+' 条';
  const es=document.getElementById('empty-state');
  if(es) es.classList.toggle('hidden', visible>0);
}

function setView(view){
  activeView=view;activeEvent='all';activeDomain='all';activeTag='all';searchTerm='';
  const si=document.getElementById('search-input');if(si)si.value='';
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
// 排序箭头：评分↓ → 评分↑ → 时间↓ → 信号↓ 循环
function cycleSort(){
  if(sortMode==='score'&&sortDir==='desc'){sortDir='asc';}
  else if(sortMode==='score'&&sortDir==='asc'){sortMode='date';sortDir='desc';}
  else if(sortMode==='date'){sortMode='signal';sortDir='desc';}
  else{sortMode='score';sortDir='desc';}
  const btn=document.getElementById('sort-btn');
  if(btn){
    if(sortMode==='date'){btn.textContent='时间 ↓';btn.classList.remove('active');}
    else if(sortMode==='signal'){btn.textContent='信号 ↓';btn.classList.add('active');}
    else{btn.textContent='评分 '+(sortDir==='desc'?'↓':'↑');btn.classList.add('active');}
  }
  updateDisplay();
}
const sbEl=document.getElementById('sort-btn');
if(sbEl){sbEl.addEventListener('click',cycleSort);}
// 时间筛选
document.querySelectorAll('.filter-btn[data-time]').forEach(btn=>{
  btn.addEventListener('click',function(){
    document.querySelectorAll('.filter-btn[data-time]').forEach(b=>b.classList.remove('active'));
    this.classList.add('active');activeTime=this.dataset.time;
    try{localStorage.setItem('sp_time_filter',activeTime);}catch(e){}
    updateDisplay();
  });
});
(function(){
  var st=null;try{st=localStorage.getItem('sp_time_filter');}catch(e){}
  if(st){
    activeTime=st;
    document.querySelectorAll('.filter-btn[data-time]').forEach(function(b){b.classList.toggle('active',b.dataset.time===st);});
  }
})();
updateDisplay();

function toggleMoreTags(){{
  const box=document.getElementById('more-tags-box');
  const btn=document.getElementById('toggle-more-tags');
  if(!box||!btn)return;
  if(box.style.display==='none'){{box.style.display='';btn.textContent='收起 ▲';btn.classList.add('active');}}
  else{{box.style.display='none';const n=box.querySelectorAll('.filter-btn').length;btn.textContent='+'+n;btn.classList.remove('active');}}
}}
"""


def _build_signal_line(merged, dates):
    """近7日事件类型计数，压缩成 header 一行小字（替代原选题雷达大块）。"""
    if not dates:
        return ""
    try:
        ref = max(dates)
        ref_d = datetime.strptime(ref, "%Y-%m-%d")
    except Exception:
        return ""
    cut = ref_d - timedelta(days=7)
    sig = {}
    for art in merged:
        d = art.get("date", "")
        try:
            dd = datetime.strptime(d, "%Y-%m-%d")
        except Exception:
            continue
        if dd >= cut:
            ev = art.get("event_type", "其他事件") or "其他事件"
            sig[ev] = sig.get(ev, 0) + 1
    if not sig:
        return ""
    top = sorted(sig.items(), key=lambda kv: -kv[1])[:6]
    return ('<div class="header-signal">📊 近7日信号：'
            + " · ".join("%s %d" % (k, v) for k, v in top) + "</div>")


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

    # Tag pills: show TOP-N + "more" toggle (避免标签膨胀时炸屏)
    _TAG_SHOW = 8
    if len(tag_list) > _TAG_SHOW:
        _shown = tag_list[:_TAG_SHOW]
        _rest  = tag_list[_TAG_SHOW:]
        _tag_btns = "".join(
            f'<button class="filter-btn" data-group="tag" data-value="{t}">{t}</button>' for t in _shown
        )
        _tag_btns += (
            f'<button class="filter-btn filter-btn-more" id="toggle-more-tags" onclick="toggleMoreTags()">+{len(_rest)}</button>'
            f'<div id="more-tags-box" style="display:none;">'
            + "".join(f'<button class="filter-btn" data-group="tag" data-value="{t}">{t}</button>' for t in _rest)
            + '</div>'
        )
    else:
        _tag_btns = "".join(
            f'<button class="filter-btn" data-group="tag" data-value="{t}">{t}</button>' for t in tag_list
        )

    curated_count = sum(1 for a in merged if a.get("view") == "curated")
    total_count = len(merged)
    domestic_curated = sum(1 for a in merged if a.get("view") == "curated" and a.get("region") == "domestic")
    overseas_curated = sum(1 for a in merged if a.get("view") == "curated" and a.get("region") == "overseas")

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    dates = [a.get("date") for a in merged
             if isinstance(a.get("date"), str) and a.get("date")]
    data_date_str = max(dates) if dates else "未知"

    # Build cards
    cards_html = "".join(build_card_html(art) for art in merged)

    # Build 精选 (Selected) view cards — 按综合评分降序（与全量同款卡片）
    selected = [a for a in merged if is_selected(a)]
    selected.sort(key=lambda a: (a.get("final_score", 0) or 0), reverse=True)
    selected_html = "".join(build_selected_card_html(a) for a in selected)
    selected_count = len(selected)
    update_log = update_update_log(selected_count)

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
    js = (JS_SCRIPT % (today_str, data_date_str))

    # 信号概览（近7日事件类型计数，压缩成 header 一行，替代原选题雷达大块）
    signal_line = _build_signal_line(merged, dates)

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
        '<style>%s%s</style>' % (CSS_STYLES, FEEDBACK_CSS),
        '</head>\n<body>',

        # Sidebar (unified component)
        SIDEBAR("index"),

        # Main content
        '<div class="main">',
        # ===== 顶部工具条（A5：不常用按钮收进「更多」，顶部只留筛选栏）=====
        '<div class="top-tools" id="top-tools">',
        '<button class="tools-more-btn" id="tools-more-btn" title="导出 / 同步 / 设置" onclick="spToggleTools()"><span class="ico">⋯</span><span class="lbl">更多</span></button>',
        '<div class="top-tools-more" id="tools-more">',
        '<a class="dl-btn" href="weekly_topics.json" download>⬇ 下载选题JSON</a>',
        '<button class="sync-fav" title="同步收藏到云端仓库（首次需配置Token）" onclick="spGhSync()">☁ 同步云端</button>',
        '<button class="sync-set" title="配置 GitHub Token" onclick="spGhSettings()">⚙ 设置</button>',
        '</div>',
        '</div>',
        '<div class="header">',
        '<div class="header-top" style="display:flex;align-items:center;gap:12px;">',
        '<h2>银发经济每周速览</h2>',
        '<div class="header-stats" id="header-stats">更新于 %s · 数据 %s · 共 %s 条</div>' % (today_str, data_date_str, total_count),
        '</div>',
        '<div class="filter-bar">',
        '<div class="view-pills">',
        '<button class="view-pill active" id="pill-curated" onclick="setView(\'curated\')">精选(%s)</button>' % selected_count,
        '<button class="view-pill" id="pill-all" onclick="setView(\'all\')">全量(%s)</button>' % total_count,
        '</div>',
        '<div class="region-pills" id="region-pills">',
        '<button class="region-pill active" data-region="all">全部</button>',
        '<button class="region-pill" data-region="domestic">国内(%s)</button>' % domestic_curated,
        '<button class="region-pill" data-region="overseas">海外(%s)</button>' % overseas_curated,
        '</div>',
        '<input class="search-inline" type="text" id="search-input" placeholder="搜索标题/摘要/标签...">',
        '<span class="filter-label">排序</span>',
        '<button class="sort-arrow active" id="sort-btn" title="点击切换：评分↓ / 评分↑ / 时间↓ / 信号↓">评分 ↓</button>',
        '<button class="fav-filter-btn" onclick="spToggleFavFilter()" title="只看已收藏">🔖 已收藏<span class="fav-cnt">0</span></button>',
        '<button class="toolbar-filter-btn" id="hide-toggle" title="显示被「不再显示」隐藏的卡片">🙈 显示已隐藏</button>',
        '<button class="toolbar-filter-btn" id="unread-toggle" title="只看未读资讯（与收藏无关）">👁 只看未读</button>',
        '</div></div>',
        signal_line,

        # Filter section — 两行分组（事件+领域 / 标签+时间），统一风格
        '<div class="filter-section" id="filter-section">',
        '  <div class="filter-row">',
        '    <span class="filter-label">事件</span>',
        '    <div class="filter-btns">',
        '      <button class="filter-btn active" data-group="event" data-value="all">全部</button>',
        event_buttons,
        '    </div>',
        '    <span class="filter-label" style="margin-left:16px;">领域</span>',
        '    <div class="filter-btns">',
        '      <button class="filter-btn active" data-group="domain" data-value="all">全部</button>',
        domain_buttons,
        '    </div>',
        '  </div>',
        '  <div class="filter-row">',
        '    <span class="filter-label">标签</span>',
        '    <div class="filter-btns" id="tag-btns-wrap">',
        '      <button class="filter-btn active" data-group="tag" data-value="all">全部</button>',
        _tag_btns,
        '    </div>',
        '    <span class="filter-label" style="margin-left:16px;">时间</span>',
        '    <div class="filter-btns">',
        '      <button class="filter-btn active" data-time="all">全部</button>',
        '      <button class="filter-btn" data-time="1w">近1周</button>',
        '      <button class="filter-btn" data-time="2w">近2周</button>',
        '      <button class="filter-btn" data-time="1m">近1月</button>',
        '      <button class="filter-btn" data-time="3m">近3月</button>',
        '    </div>',
        '  </div>',
        '</div>',

        # 收藏标签筛选条（仅 fav-mode 下显示）
        '<div class="filter-row fav-tag-filter" id="fav-tag-filter">',
        '  <span class="filter-label">收藏标签</span>',
        '  <div class="filter-btns" id="fav-tag-pills"></div>',
        '</div>',

        # 精选 (Selected) view: selected cards（按评分降序，与全量同款）
        '<div id="selected-container">',
        selected_html,
        '</div>',

        # Feed container (全量 view)
        '<div id="feed-container">',
        cards_html,
        '</div>',

        # Empty state (shown when filters yield nothing)
        '<div class="empty-state hidden" id="empty-state">',
        '<div class="es-ico">🔍</div>',
        '<div class="es-text">没有符合条件的资讯，试试调整筛选或搜索词</div>',
        '</div>',

        # Footer
        '<div class="footer">',
        '<p>Silver Pulse 银脉 · 银发经济投融资每周速览</p>',
        '<p>Powered by WorkBuddy · 海外 + 中文双源覆盖</p>',
        '</div>',

        # Close main + body
        '</div>',
        '\n<script>\n%s\n</script>\n%s\n%s\n</body>\n</html>' % (js, THEME_JS, FEEDBACK_JS),
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


def main():
    """Entry point for the daily pipeline (run_daily.py)."""
    from scorer import load_scored
    articles = load_scored()
    return generate_html(articles)
