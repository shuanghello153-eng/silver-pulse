"""
Collect articles from AgeTech & senior care news sources.
RSS-first approach: direct RSS, RSS via HTTP, or Google News RSS proxy.
No more 403 errors — RSS feeds don't block, and Google News acts as proxy for stubborn sites.
"""
import json
import os
import re
import hashlib
from datetime import datetime, timezone, timedelta, time
from email.utils import parsedate_to_datetime

import feedparser
import requests

from config import (
    SOURCES, DATA_DIR, RELEVANCE_KEYWORDS, CN_RELEVANCE_KEYWORDS,
    IRRELEVANT_KEYWORDS, SILVER_STRONG_KEYWORDS, SILVER_WEAK_KEYWORDS,
    MAX_ARTICLE_AGE_DAYS,
    SIGNAL_KEYWORDS_POSITIVE, SIGNAL_KEYWORDS_NEGATIVE, SOURCE_TIER_WEIGHTS,
    MAX_ARTICLES_TO_SCORE,
)

CACHE_FILE = os.path.join(DATA_DIR, "history.json")

# === 静音模式（降本）：详细日志写文件，stdout 只留一行摘要 ===
# 自动化任务读 stdout 计 token，逐源打印是主要浪费源。改为写
# data/run_logs/collector_YYYYMMDD.log，模型侧只看到 collect_all 末行摘要。
import logging
_RUNLOG_DIR = os.path.join(DATA_DIR, "run_logs")
os.makedirs(_RUNLOG_DIR, exist_ok=True)
_COLLECT_LOG = os.path.join(_RUNLOG_DIR, f"collector_{datetime.now().strftime('%Y%m%d')}.log")
_col_logger = logging.getLogger("silver_collector")
if not _col_logger.handlers:
    _ch = logging.FileHandler(_COLLECT_LOG, encoding="utf-8")
    _ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _col_logger.addHandler(_ch)
    _col_logger.setLevel(logging.INFO)
def _clog(msg):
    """详细日志写文件（不进 stdout）。"""
    _col_logger.info(msg)

# 动态噪音封禁名单（由 noise_spike_guard 自动维护，连续2天 spike 时写入）
# 格式: {"domains": [...]} —— 这些源域名产出的条目直接判为不相关
NOISE_BLOCKLIST_PATH = os.path.join(DATA_DIR, "noise_blocklist.json")
_NOISE_BLOCK_DOMAINS = set()
try:
    _bl = json.load(open(NOISE_BLOCKLIST_PATH, "r", encoding="utf-8"))
    if isinstance(_bl, dict) and _bl.get("domains"):
        _NOISE_BLOCK_DOMAINS = set(_bl["domains"])
except Exception:
    _NOISE_BLOCK_DOMAINS = set()

# Optional direct-RSS fallback for a few key google_news sources (verified feeds).
# Left intentionally small; the main resilience comes from rss -> google_news fallback.
DIRECT_RSS_FALLBACK = {
    # source_id: direct_rss_url  (only add after verifying the feed works)
}

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def load_history():
    """Load previously collected article URLs to avoid duplicates."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"urls": {}, "last_cleanup": None}


def save_history(history):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def url_hash(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]


def is_duplicate(url, history):
    return url_hash(url) in history["urls"]


def mark_seen(url, history):
    history["urls"][url_hash(url)] = datetime.now(timezone.utc).isoformat()


def clean_old_entries(history, days=30):
    """Remove entries older than N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    history["urls"] = {
        k: v for k, v in history["urls"].items() if v > cutoff
    }
    history["last_cleanup"] = datetime.now(timezone.utc).isoformat()


def is_relevant(text, entity_name=None):
    """Two-tier relevance gate (2026-07-08 收紧).

    强词命中（养老/银发/照护/认知症/Medicare…） => 相关。
    仅弱词命中（融资/机器人/AI/科技 等泛词，无银发上下文） => 不相关，除非
    主体 entity_name 在企业库已知银发企业名单中。
    目的：挡掉"复旦95后机器人大佬"这类泛科技/机器人融资稿。
    """
    if not text:
        return False
    text_lower = text.lower()
    # 动态噪音封禁（noise_spike_guard 自动维护）：命中封禁源域名直接判不相关
    if _NOISE_BLOCK_DOMAINS:
        src = (entity_name or "").lower()
        for blk in _NOISE_BLOCK_DOMAINS:
            if blk and blk.lower() in src:
                return False
    for kw in IRRELEVANT_KEYWORDS:
        if kw.lower() in text_lower:
            return False
    # 强词命中即相关
    for kw in SILVER_STRONG_KEYWORDS:
        if (kw.lower() in text_lower) or (kw in text):
            return True
    # 仅弱词：需主体是企业库已知银发企业才算相关
    weak_hit = False
    for kw in SILVER_WEAK_KEYWORDS:
        if (kw.lower() in text_lower) or (kw in text):
            weak_hit = True
            break
    if weak_hit:
        if entity_name:
            from enterprise_names import ENT_NAME_SET  # 延迟导入，避免循环
            if entity_name.strip().lower() in ENT_NAME_SET:
                return True
        return False
    return False


def strip_html(text):
    """Remove HTML tags from text and normalize whitespace."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'&amp;', '&', clean)
    clean = re.sub(r'&lt;', '<', clean)
    clean = re.sub(r'&gt;', '>', clean)
    clean = re.sub(r'&quot;', '"', clean)
    clean = re.sub(r'&#39;', "'", clean)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def parse_feed_date(date_str):
    """Parse various date formats from RSS feeds into YYYY-MM-DD."""
    if not date_str:
        return ""

    # Strip HTML if present
    date_str = strip_html(date_str)

    # Try RFC 2822 (standard RSS date format: "Mon, 01 Jul 2026 12:00:00 GMT")
    try:
        dt = parsedate_to_datetime(date_str)
        if dt:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # Try ISO format
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d", "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S"]:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Try "Jul 1, 2026" format (FierceHealthcare style)
    for fmt in ["%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y"]:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Try regex extraction for common patterns
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\w{3}, \d{1,2} \w{3} \d{4})",
        r"(\d{1,2} \w{3,9} \d{4})",
        r"(\w{3} \d{1,2}, \d{4})",
    ]
    for p in patterns:
        match = re.search(p, date_str)
        if match:
            extracted = match.group(1)
            for fmt in ["%Y-%m-%d", "%a, %d %b %Y", "%d %B %Y", "%d %b %Y",
                        "%b %d, %Y", "%B %d, %Y"]:
                try:
                    dt = datetime.strptime(extracted, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

    return date_str[:10] if len(date_str) >= 10 else ""


def is_within_days(date_str, max_days=MAX_ARTICLE_AGE_DAYS):
    """Check if a date string is within the last N days."""
    if not date_str or len(date_str) < 10:
        return True  # If no date, keep it (better safe than sorry)

    try:
        article_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        cutoff = datetime.now() - timedelta(days=max_days)
        return article_date >= cutoff
    except ValueError:
        return True  # Can't parse date, keep it


def clean_google_news_url(url):
    """Extract the actual article URL from Google News redirect URL."""
    if "news.google.com" in url:
        # Google News URLs look like: https://news.google.com/articles/XXXX?...
        # or https://news.google.com/rss/articles/XXXX
        # Try to extract the actual URL from the path
        match = re.search(r'[?&]url=(https?://[^&]+)', url)
        if match:
            return match.group(1)
        # If we can't extract, keep the Google News URL (it still works as a redirect)
    return url


def extract_summary(entry):
    """Extract a clean summary from a feed entry."""
    # Try multiple fields
    for field in ["summary", "description", "subtitle"]:
        text = entry.get(field, "")
        if text:
            # Strip HTML tags
            clean = re.sub(r'<[^>]+>', '', text)
            clean = re.sub(r'\s+', ' ', clean).strip()
            if len(clean) > 20:
                return clean[:500]
    return ""


# 招聘帖垃圾过滤：VC 的 "Top" / 职业页常把招聘信息当资讯喂进来
_JOB_ROLE_RE = re.compile(
    r"\b(senior|staff|principal|lead|junior|associate|entry[ -]level)\b.*@", re.I
)
_JOB_COMPANY_RE = re.compile(
    r"@\s*(affirm|okta|yammer|google|meta|apple|tesla|netflix|amazon|uber|lyft|"
    r"airbnb|stripe|databricks|snowflake|openai|anthropic|cohere|scale\s*ai|"
    r"microsoft|salesforce|nvidia|palantir)\b", re.I
)
_JOB_PHRASE_RE = re.compile(
    r"(we'?re\s+hiring|we\s+are\s+hiring|job\s+opening|apply\s+now|now\s+hiring|"
    r"careers\s+at|join\s+our\s+team|\bis\s+hiring|are\s+hiring|hiring\s+for|"
    r"job\s+description|vacancy|recruitment)", re.I
)


def is_job_spam(title):
    """True if the title looks like a job posting rather than an insight/article."""
    if not title:
        return False
    if _JOB_ROLE_RE.search(title):
        return True
    if _JOB_COMPANY_RE.search(title):
        return True
    if _JOB_PHRASE_RE.search(title):
        return True
    return False


def _build_manual_article(seed):
    """Build an article dict from a manual seed entry (data/manual_news.json)."""
    url = seed.get("url")
    title = seed.get("title")
    if not url or not title:
        return None
    sid = seed.get("source_id") or ""
    sname = seed.get("source") or (SOURCES.get(sid, {}).get("name") if sid else "Manual")
    return {
        "title": title,
        "url": url,
        "source": sname,
        "source_id": sid,
        "date": seed.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "summary": seed.get("summary", ""),
        "manual": True,
        "signal_score": 8.0,
        "tags": seed.get("tags", []),
    }


def collect_from_rss(source_id, feed_url, source_type, source_name):
    """
    Collect articles from an RSS feed.
    Handles three types: direct RSS, RSS via HTTP (with headers), Google News RSS.
    """
    try:
        if source_type == "rss":
            # Direct RSS — fetch via requests WITH timeout, then parse.
            # feedparser.parse(url) uses urllib without a timeout and can hang
            # the whole pipeline on a slow/dead feed, so we never call it on a URL.
            resp = requests.get(feed_url, headers=HTTP_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        elif source_type == "rss_http":
            # RSS via requests with headers (for sites that block feedparser)
            resp = requests.get(feed_url, headers=HTTP_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        elif source_type == "google_news":
            # Google News RSS proxy
            if "news.google.com" in feed_url:
                # Already a Google News RSS URL (e.g. AgeClub, 36kr)
                target_url = feed_url
            else:
                # Direct site/channel URL → wrap in Google News RSS proxy.
                # 精准监控二级频道：若频道路径含信号词(invest/fund/venture/ipo
                # 等)，把该词加入查询，避免只查整站导致频道语义丢失。
                from urllib.parse import quote
                clean = feed_url.split("//")[-1].rstrip("/")
                parts = clean.split("/")
                domain = parts[0]
                path_kw = ""
                if len(parts) > 1:
                    seg = parts[-1] if parts[-1] else (parts[-2] if len(parts) > 2 else "")
                    seg = seg.replace("-", " ").replace("_", " ")
                    if any(w in seg.lower() for w in
                           ["invest", "fund", "venture", "vc", "ipo", "merger",
                            "acqui", "capital", "financ", "deal", "aging", "senior", "care"]):
                        path_kw = seg
                q = f"site:{domain}"
                if path_kw:
                    q += f"+{quote(path_kw)}"
                target_url = f"https://news.google.com/rss/search?q={q}+when:7d&hl=en-US"
            resp = requests.get(target_url, headers=HTTP_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        else:
            _clog(f"[{source_name}] Unknown type: {source_type}")
            return []

        entries = feed.get("entries", [])
        if not entries:
            _clog(f"[{source_name}] No entries found")
            return []

        articles = []
        for entry in entries:
            title = strip_html(entry.get("title", ""))
            if not title or len(title) < 10:
                continue
            # Skip job-posting spam (VC "Top" / career pages surface hiring listings)
            if is_job_spam(title):
                _clog(f"[{source_name}] Skipped job-spam: {title[:60]}")
                continue

            # Get URL
            url = entry.get("link", "")
            if not url:
                continue
            url = clean_google_news_url(url)

            # Get date
            date_str = ""
            for date_field in ["published", "updated", "created"]:
                raw_date = entry.get(date_field, "")
                if raw_date:
                    date_str = parse_feed_date(raw_date)
                    if date_str:
                        break

            # Get summary
            summary = extract_summary(entry)

            # Get source (for Google News, the source is in the entry)
            actual_source = source_name
            if source_type == "google_news":
                src = entry.get("source", {})
                if isinstance(src, dict) and src.get("title"):
                    actual_source = src["title"]
                elif isinstance(src, str):
                    actual_source = src

            article = {
                "title": title,
                "url": url,
                "source": actual_source,
                "source_id": source_id,
                "date": date_str,
                "summary": summary,
            }
            articles.append(article)

        _clog(f"[{source_name}] Collected {len(articles)} articles")
        return articles

    except Exception as e:
        _clog(f"[{source_name}] Error: {type(e).__name__}: {e}")
        return []


def _google_news_url_for_domain(domain, hl="en-US"):
    """Build a Google News RSS search URL that monitors an entire domain."""
    from urllib.parse import quote
    clean = domain.split("//")[-1].rstrip("/")
    domain = clean.split("/")[0]
    return f"https://news.google.com/rss/search?q={quote('site:' + domain)}+when:7d&hl={hl}"


def _fallback_for_channel(source_id, source_config, channel_url, channel_method):
    """Return (fallback_url, fallback_method) or None.

    Resilience chain (network ON is assumed; this only triggers when a specific
    source fails so one dead feed never zeroes out the whole day's collection):
      - rss / rss_http  -> google_news site:domain   (covers 403 / empty direct feeds)
      - google_news      -> known direct RSS (if listed in DIRECT_RSS_FALLBACK)
    """
    if channel_method in ("rss", "rss_http"):
        domain = source_config.get("l1_domain", "")
        if domain:
            return (_google_news_url_for_domain(domain), "google_news")
    elif channel_method == "google_news":
        direct = DIRECT_RSS_FALLBACK.get(source_id)
        if direct:
            return (direct, "rss")
    return None


def score_article(article, source_config):
    """
    Score an article based on signal keywords + source tier weight.
    Returns a numeric signal_score (higher = more newsworthy).
    
    Scoring logic:
    1. Base score from source tier: T1=3, T2=2, T3=1
    2. + Positive keyword matches (capital events, launches, partnerships)
    3. - Negative keyword matches (webinars, awards, lists, job posts)
    4. + Bonus for multiple positive signals (stacking)
    """
    text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    
    # Base: source tier weight
    tier = source_config.get("tier", 3)
    score = SOURCE_TIER_WEIGHTS.get(tier, 1)
    
    # Positive signals
    positive_hits = 0
    for kw, weight in SIGNAL_KEYWORDS_POSITIVE.items():
        if kw.lower() in text:
            score += weight
            positive_hits += 1
    
    # Stacking bonus: multiple positive signals = stronger story
    if positive_hits >= 3:
        score += 3
    elif positive_hits >= 2:
        score += 1
    
    # Negative signals
    for kw, weight in SIGNAL_KEYWORDS_NEGATIVE.items():
        if kw.lower() in text:
            score += weight  # weight is negative, so this subtracts
    
    return round(score, 1)


def collect_all(history=None):
    """
    Run all collectors, deduplicate, pre-filter by relevance and date.
    Returns list of unique relevant articles (with 'relevant' flag).
    """
    if history is None:
        history = load_history()

    all_articles = []

    for source_id, source_config in SOURCES.items():
        source_name = source_config["name"]
        _clog(f"Collecting from {source_name}...")

        all_channel_articles = []
        for channel_name, channel_url, channel_method in source_config.get("l2_channels", []):
            if channel_method == "manual":
                _clog(f"  [{channel_name}] Skipping manual channel")
                continue

            channel_articles = collect_from_rss(
                source_id, channel_url, channel_method, source_name
            )
            # Fallback: if the primary method returned nothing (403 / empty /
            # timeout), try the alternative so one dead feed never empties the day.
            if not channel_articles:
                fb = _fallback_for_channel(
                    source_id, source_config, channel_url, channel_method
                )
                if fb:
                    fb_url, fb_method = fb
                    _clog(f"  [{channel_name}] primary empty -> fallback ({fb_method})")
                    channel_articles = collect_from_rss(
                        source_id, fb_url, fb_method, source_name
                    )
            all_channel_articles.extend(channel_articles)

        new_count = 0
        for article in all_channel_articles:
            if is_duplicate(article["url"], history):
                continue
            mark_seen(article["url"], history)
            all_articles.append(article)
            new_count += 1

        _clog(f"  -> {new_count} new articles")

    # 存量手动种子注入（如 YouTube 历史爆款视频）：绕过 7 天日期限制，持久进入情报台
    manual_path = os.path.join(DATA_DIR, "manual_news.json")
    if os.path.exists(manual_path):
        try:
            with open(manual_path, encoding="utf-8") as _mf:
                seeds = json.load(_mf) or []
            _injected = 0
            for _seed in seeds:
                _art = _build_manual_article(_seed)
                if not _art:
                    continue
                # 策划种子：始终注入，不受 history 去重影响（存量精选应每轮出现）
                all_articles.append(_art)
                _injected += 1
            if _injected:
                _clog(f"[manual] injected {_injected} seed articles")
        except Exception as _e:
            _clog(f"[manual] load error: {_e}")

    save_history(history)

    # Filter by date and relevance, then score
    relevant_articles = []
    for art in all_articles:
        text = f"{art['title']} {art.get('summary', '')}"

        # Relevance check
        if is_relevant(text):
            art["relevant"] = True
        else:
            art["relevant"] = False

        # Date check — skip articles older than MAX_ARTICLE_AGE_DAYS
        if not is_within_days(art.get("date", ""), MAX_ARTICLE_AGE_DAYS):
            continue

        # Only keep relevant articles
        if art["relevant"]:
            # Score the article
            source_id = art.get("source_id", "")
            source_config = SOURCES.get(source_id, {})
            art["signal_score"] = score_article(art, source_config)
            relevant_articles.append(art)

    # Sort by signal_score descending (primary), then date descending (secondary)
    relevant_articles.sort(
        key=lambda a: (a.get("signal_score", 0), a.get("date", "0000-00-00")),
        reverse=True
    )

    # Keep only Top N articles for AI scoring
    top_articles = relevant_articles[:MAX_ARTICLES_TO_SCORE]
    
    # Also sort the top articles by date for display
    top_articles.sort(
        key=lambda a: a.get("date", "0000-00-00"), reverse=True
    )

    # 静音：stdout 只输出一行摘要，详细日志见 data/run_logs/collector_*.log
    print(f"[collector] 完成: {len(relevant_articles)} 条相关 / {len(all_articles)} 新 / {len(top_articles)} 待评分")

    # Store full relevant set for external save (full dashboard update)
    collect_all._last_relevant = relevant_articles

    # Persist the FULL relevant set so downstream steps (score_and_merge) can read
    # it — regardless of whether collect_all is invoked as a module (run_daily.py)
    # or run directly as a script. (Previously this save lived only in __main__,
    # so module calls never wrote the raw file and broke the whole pipeline.)
    out_file = os.path.join(DATA_DIR, f"raw_{datetime.now().strftime('%Y%m%d')}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(relevant_articles, f, ensure_ascii=False, indent=2)
    _clog(f"Saved {len(relevant_articles)} relevant articles to {out_file}")

    # Top 5 预览写入日志（不进 stdout）
    if top_articles:
        for a in sorted(top_articles, key=lambda x: x.get("signal_score", 0), reverse=True)[:5]:
            _clog(f"Top: [{a.get('signal_score', 0):.1f}] [{a['source']}] {a['title'][:70]} | {a['date']}")

    return top_articles


if __name__ == "__main__":
    articles = collect_all()
    print("\n--- Recent articles ---")
    for a in articles[:10]:
        print(f"  [{a['source']}] {a['title'][:70]} | {a['date']} | {a['url'][:60]}")
