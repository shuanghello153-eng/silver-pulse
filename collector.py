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
    IRRELEVANT_KEYWORDS,
    MAX_ARTICLE_AGE_DAYS,
)

CACHE_FILE = os.path.join(DATA_DIR, "history.json")

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


def is_relevant(text):
    """Quick keyword pre-check: is this likely about senior care / aging?
    Supports both English and Chinese keywords."""
    text_lower = text.lower()
    for kw in IRRELEVANT_KEYWORDS:
        if kw.lower() in text_lower:
            return False
    # Check English keywords
    for kw in RELEVANCE_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    # Check Chinese keywords
    for kw in CN_RELEVANCE_KEYWORDS:
        if kw in text:
            return True
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


def collect_from_rss(source_id, feed_url, source_type, source_name):
    """
    Collect articles from an RSS feed.
    Handles three types: direct RSS, RSS via HTTP (with headers), Google News RSS.
    """
    try:
        if source_type == "rss":
            # Direct RSS via feedparser
            feed = feedparser.parse(feed_url)
        elif source_type == "rss_http":
            # RSS via requests with headers (for sites that block feedparser)
            resp = requests.get(feed_url, headers=HTTP_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        elif source_type == "google_news":
            # Google News RSS proxy
            resp = requests.get(feed_url, headers=HTTP_HEADERS, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
        else:
            print(f"  [{source_name}] Unknown type: {source_type}")
            return []

        entries = feed.get("entries", [])
        if not entries:
            print(f"  [{source_name}] No entries found")
            return []

        articles = []
        for entry in entries:
            title = strip_html(entry.get("title", ""))
            if not title or len(title) < 10:
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

        print(f"  [{source_name}] Collected {len(articles)} articles")
        return articles

    except Exception as e:
        print(f"  [{source_name}] Error: {type(e).__name__}: {e}")
        return []


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
        print(f"Collecting from {source_name}...")

        all_channel_articles = []
        for channel_name, channel_url, channel_method in source_config.get("l2_channels", []):
            if channel_method == "manual":
                print(f"  [{channel_name}] Skipping manual channel")
                continue

            channel_articles = collect_from_rss(
                source_id, channel_url, channel_method, source_name
            )
            all_channel_articles.extend(channel_articles)

        new_count = 0
        for article in all_channel_articles:
            if is_duplicate(article["url"], history):
                continue
            mark_seen(article["url"], history)
            all_articles.append(article)
            new_count += 1

        print(f"  -> {new_count} new articles")

    save_history(history)

    # Filter by date and relevance
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
            relevant_articles.append(art)

    # Sort by date descending
    relevant_articles.sort(
        key=lambda a: a.get("date", "0000-00-00"), reverse=True
    )

    print(f"\nTotal: {len(all_articles)} new articles, "
          f"{len(relevant_articles)} relevant")
    return relevant_articles


if __name__ == "__main__":
    articles = collect_all()
    out_file = os.path.join(DATA_DIR, f"raw_{datetime.now().strftime('%Y%m%d')}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(articles)} relevant articles to {out_file}")
    print("\n--- Recent articles ---")
    for a in articles[:10]:
        print(f"  [{a['source']}] {a['title'][:70]} | {a['date']} | {a['url'][:60]}")
