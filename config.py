"""
Silver Pulse configuration — sources, scoring weights, thresholds.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Sources ===
# Each source has a feed_url (RSS) and optional web_url (for fallback).
# type: "rss" = direct RSS feed, "rss_http" = RSS via requests (needs headers),
#        "google_news" = Google News RSS proxy
SOURCES = {
    # T1 Overseas core — direct RSS works
    "fiercehealthcare": {
        "name": "FierceHealthcare",
        "feed_url": "https://www.fiercehealthcare.com/rss/xml",
        "type": "rss",
        "tier": 1,
        "region": "overseas",
    },
    "crunchbase_news": {
        "name": "Crunchbase News",
        "feed_url": "https://news.crunchbase.com/feed/",
        "type": "rss",
        "tier": 1,
        "region": "overseas",
    },
    "thegerontechnologist": {
        "name": "TheGerontechnologist",
        "feed_url": "https://thegerontechnologist.com/feed/",
        "type": "rss",
        "tier": 1,
        "region": "overseas",
    },
    "seniorhousingnews": {
        "name": "Senior Housing News",
        "feed_url": "https://seniorhousingnews.com/feed/",
        "type": "rss",
        "tier": 1,
        "region": "overseas",
    },
    # T1 Overseas — RSS needs HTTP headers
    "homehealthcarenews": {
        "name": "Home Health Care News",
        "feed_url": "https://homehealthcarenews.com/feed/",
        "type": "rss_http",
        "tier": 1,
        "region": "overseas",
    },
    # T1 Overseas — 403 blocked, use Google News proxy
    "mcknights_senior": {
        "name": "McKnight's Senior Living",
        "feed_url": "https://news.google.com/rss/search?q=site:mcknightsseniorliving.com+when:7d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news",
        "tier": 1,
        "region": "overseas",
    },
    "mobihealthnews": {
        "name": "MobiHealthNews",
        "feed_url": "https://news.google.com/rss/search?q=site:mobihealthnews.com+when:7d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news",
        "tier": 1,
        "region": "overseas",
    },
    # Broad silver economy news via Google News
    "silver_economy_news": {
        "name": "Google News - Silver Economy",
        "feed_url": "https://news.google.com/rss/search?q=%22senior+care%22+OR+%22home+health%22+OR+%22aging+technology%22+OR+%22AgeTech%22+OR+%22elderly+care%22+when:7d&hl=en-US&gl=US&ceid=US:en",
        "type": "google_news",
        "tier": 2,
        "region": "overseas",
    },
    # Chinese sources via Google News
    "silver_economy_cn": {
        "name": "Google News - 银发经济",
        "feed_url": "https://news.google.com/rss/search?q=%E9%93%B6%E5%8F%91%E7%BB%8F%E6%B5%8E+OR+%E5%85%BB%E8%80%81+OR+%E8%80%81%E5%B9%B4%E4%BA%A7%E4%B8%9A+OR+%E5%81%A5%E5%BA%B7%E5%85%BB%E8%80%81+when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "type": "google_news",
        "tier": 2,
        "region": "domestic",
    },
    "ageclub": {
        "name": "AgeClub",
        "feed_url": "https://news.google.com/rss/search?q=site:ageclub.net+when:7d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "type": "google_news",
        "tier": 2,
        "region": "domestic",
    },
}

# === Scoring ===
SCORING_DIMENSIONS = [
    {"name": "industry", "label": "行业相关度", "weight": 0.35, "max_score": 10,
     "description": "与银发经济核心赛道的关联程度"},
    {"name": "signal", "label": "信号强度", "weight": 0.30, "max_score": 10,
     "description": "融资金额、收购规模、参与方分量"},
    {"name": "writing", "label": "写作潜力", "weight": 0.20, "max_score": 10,
     "description": "故事性、独特角度、中国可借鉴性"},
    {"name": "timeliness", "label": "时效紧迫度", "weight": 0.15, "max_score": 10,
     "description": "新闻热度窗口，是否应本周处理"},
]

# Score thresholds
HIGH_VALUE_THRESHOLD = 7.0   # >= 7.0 -> star
WATCH_THRESHOLD = 5.0         # 5.0-6.9 -> watch
# < 5.0 -> archive

# === Tags ===
INDUSTRY_TAGS = [
    "居家养老", "健康监测", "数字疗法", "认知症", "远程医疗",
    "保险科技", "康复辅具", "药物管理", "社交陪伴", "慢病管理",
    "智慧养老", "辅助生活", "临终关怀", "养老地产", "老年消费",
    "护理人力", "金融科技", "出行交通", "营养健康", "长寿科技",
]

EVENT_TAGS = ["融资", "收购", "IPO", "产品发布", "战略合作", "政策法规", "财报"]

# Daily keywords for relevance pre-filter
RELEVANCE_KEYWORDS = [
    "senior", "elderly", "aging", "age tech", "agetech", "older adult",
    "older adults", "aging population", "silver economy",
    "home care", "home health", "hospice", "assisted living",
    "long-term care", "long term care", "nursing home",
    "caregiver", "caregiving", "cognitive", "dementia", "alzheimer",
    "medicare", "medicaid", "retirement", "pace program",
    "value-based care", "social determinants",
    # Funding keywords
    "funding", "raises", "raises series", "investment", "acquisition",
    "acquires", "merger", "ipo", "seed round", "series a", "series b",
    "series c", "venture", "startup",
]

# Chinese relevance keywords
CN_RELEVANCE_KEYWORDS = [
    "银发", "养老", "老年", "老龄化", "长者", "退休",
    "居家护理", "居家照护", "康复", "慢病", "认知症", "痴呆",
    "阿尔茨海默", "失智", "失能", "适老", "长寿",
    "护理院", "养老院", "敬老院", "养老社区",
    "康养", "医养", "助老", "陪护", "康护",
    # Funding/business keywords in Chinese
    "融资", "收购", "并购", "投资", "IPO", "上市",
    "A轮", "B轮", "C轮", "天使轮", "种子轮",
    # AgeClub specific categories
    "大公司", "投融资", "行业风向",
]

# Irrelevant keywords (filter out)
IRRELEVANT_KEYWORDS = [
    "pediatric", "pediatrics", "children", "infant", "neonatal",
    "pregnancy", "maternity", "adolescent", "teen", "child",
]

# === Output ===
SITE_TITLE = "Silver Pulse 银脉"
SITE_SUBTITLE = "全球银发经济投融资每日速览"

# === Overseas source names (for region detection in UI) ===
OVERSEAS_SOURCES = {
    "FierceHealthcare", "Crunchbase News", "TheGerontechnologist",
    "Senior Housing News", "Home Health Care News",
    "McKnight's Senior Living", "MobiHealthNews",
    "Bloomberg Law News", "Aging in Place Technology News",
    "Forbes", "TechCrunch",
}

# === 银发财经头部账号清单 (用于爆款监测 + 选题参考) ===
SILVER_FINANCE_ACCOUNTS = {
    # 微信公众号 — 头部
    "wechat_official": [
        {"name": "AgeClub", "platform": "公众号", "type": "行业研究", "note": "银发经济头部媒体，行业风向标"},
        {"name": "36氪", "platform": "公众号", "type": "科技/创投", "note": "科技创投媒体，有银发经济板块"},
        {"name": "动脉网", "platform": "公众号", "type": "医疗健康", "note": "医疗健康产业媒体，覆盖养老赛道"},
        {"name": "方文养老产业观察", "platform": "公众号", "type": "养老产业", "note": "方文的养老产业观察号"},
        {"name": "银龄网", "platform": "公众号", "type": "银发综合", "note": "银发经济资讯平台"},
        {"name": "小王养老指南", "platform": "公众号", "type": "养老指南", "note": "养老行业实操指南"},
        {"name": "金龄银发研究院", "platform": "公众号", "type": "研究机构", "note": "银发经济研究智库"},
        {"name": "长青研究社", "platform": "公众号", "type": "研究机构", "note": "长寿经济研究"},
        {"name": "了不起的银发圈", "platform": "公众号", "type": "社区/内容", "note": "银发经济社群内容"},
        {"name": "艾年", "platform": "公众号", "type": "自运营", "note": "我们的公众号"},
    ],
    # 视频号
    "video_account": [
        {"name": "AgeClub视频号", "platform": "视频号", "type": "行业内容"},
        {"name": "银龄网视频号", "platform": "视频号", "type": "行业内容"},
        {"name": "方文养老产业观察", "platform": "视频号", "type": "行业解读"},
        {"name": "小王养老指南", "platform": "视频号", "type": "养老科普"},
        {"name": "了不起的银发圈", "platform": "视频号", "type": "社区内容"},
        {"name": "金龄银发研究院", "platform": "视频号", "type": "研究内容"},
        {"name": "长青研究社", "platform": "视频号", "type": "研究内容"},
    ],
    # 抖音
    "douyin": [
        {"name": "AgeClub抖音", "platform": "抖音", "type": "行业内容"},
        {"name": "银龄网抖音", "platform": "抖音", "type": "行业内容"},
        {"name": "方文说养老", "platform": "抖音", "type": "行业解读"},
        {"name": "小王聊养老", "platform": "抖音", "type": "养老科普"},
        {"name": "了不起的银发圈", "platform": "抖音", "type": "社区内容"},
        {"name": "金龄研究院", "platform": "抖音", "type": "研究内容"},
    ],
}

# === 爆款阈值 ===
VIRAL_THRESHOLDS = {
    "wechat_read_count": 5000,      # 公众号单篇阅读量 > 5000 算爆款
    "video_likes": 500,             # 视频号/抖音 喜欢数 > 500 算爆款
}

# === Automation ===
# Max articles to score per run (to control cost)
MAX_ARTICLES_TO_SCORE = 30
# Max days to look back for articles
MAX_ARTICLE_AGE_DAYS = 7
