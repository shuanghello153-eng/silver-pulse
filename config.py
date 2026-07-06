"""
Silver Pulse configuration — sources, classification, scoring weights, thresholds.
v5.0: 13-class enterprise categorization, event-type news classification,
     L1/L2 source hierarchy, tag pool, data filtering logic docs.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================================================================
# 1. ENTERPRISE CATEGORIZATION (13 L1 + 70 L2)
# ================================================================
# Enterprise L1 categories (no numbering in display)
# L2 subcategories map to each L1
ENTERPRISE_CATEGORIES = {
    "购物渠道": {
        "label": "购物渠道",
        "l2": ["线上渠道", "线下渠道", "电视购物", "会员营销", "私域渠道", "特殊渠道"],
    },
    "日常用品": {
        "label": "日常用品",
        "l2": ["老年鞋", "老年服饰", "老年护肤", "染发剂", "假发", "家用医疗"],
    },
    "健康食品": {
        "label": "健康食品",
        "l2": ["代工厂", "线上渠道", "线下渠道", "保健品&OTC", "中式养生",
                "益生菌", "小分子肽", "特医食品", "蛋白粉", "无糖&低GI", "成人羊奶"],
    },
    "老年文娱": {
        "label": "老年文娱",
        "l2": ["老年旅游", "老年教育", "社交平台", "广场舞", "老年相亲", "老年健身", "老年音乐"],
    },
    "健康服务": {
        "label": "健康服务",
        "l2": ["再就业", "健康养生", "摔倒监测", "睡眠监测", "血压血糖", "慢病管理", "陪诊服务"],
    },
    "适老化改造": {
        "label": "适老化改造",
        "l2": ["智慧养老软件", "适老规划设计", "适老家居产品", "智能养老用品", "综合供应链"],
    },
    "行业服务": {
        "label": "行业服务",
        "l2": ["行业媒体", "行业展会", "咨询研究", "金融理财"],
    },
    "养老地产": {
        "label": "养老地产",
        "l2": ["运营商", "养老院中介", "护工培训"],
    },
    "养老服务": {
        "label": "养老服务",
        "l2": ["传统家政", "民政服务", "长护险", "专业级护理", "院内陪护", "老年助餐", "助浴助洁", "临终关怀"],
    },
    "养老用品": {
        "label": "养老用品",
        "l2": ["肢体障碍", "视觉障碍", "听觉障碍", "呼吸障碍", "吞咽障碍",
                "咀嚼障碍", "成人失禁", "智能用品"],
    },
    "康复设备": {
        "label": "康复设备",
        "l2": ["运动康复", "手部康复", "外骨骼", "精神&神经", "肿瘤康复"],
    },
    "失智老人赛道": {
        "label": "失智老人赛道",
        "l2": ["病情早筛", "照护机构", "认知症产品"],
    },
    "产业资本/投资机构": {
        "label": "产业资本/投资机构",
        "l2": ["消费背景", "严肃医疗背景", "国资背景", "种子投资背景", "相关上市公司"],
    },
}

# For internal use: code mapping (not shown in UI)
ENTERPRISE_CATEGORY_CODES = {
    "购物渠道": "01",
    "日常用品": "02",
    "健康食品": "03",
    "老年文娱": "04",
    "健康服务": "05",
    "适老化改造": "06",
    "行业服务": "07",
    "养老地产": "08",
    "养老服务": "09",
    "养老用品": "10",
    "康复设备": "11",
    "失智老人赛道": "12",
    "产业资本/投资机构": "13",
}

# ================================================================
# 2. NEWS CATEGORIZATION (event-type L1 + domain L2)
# ================================================================
# News is classified by EVENT TYPE (L1) + DOMAIN INVOLVED (L2)
# L2 domain labels reuse enterprise L1 category names for consistency
NEWS_EVENT_TYPES = {
    "融资": {"label": "融资", "desc": "企业获得新一轮融资"},
    "收购并购": {"label": "收购并购", "desc": "企业被收购或并购交易"},
    "政策法规": {"label": "政策法规", "desc": "政府政策、监管法规出台"},
    "产品发布": {"label": "产品发布", "desc": "新产品或新服务上线"},
    "行业趋势": {"label": "行业趋势", "desc": "行业报告、数据研究、趋势分析"},
    "人事变动": {"label": "人事变动", "desc": "高管加入/离职、创始人动态"},
    "其他事件": {"label": "其他事件", "desc": "不属于以上类型的重要事件"},
}

# L2: domain involved (reuse enterprise L1 names)
NEWS_DOMAINS = list(ENTERPRISE_CATEGORIES.keys())

# ================================================================
# 3. TAG POOL
# ================================================================
# Tags are free-form but maintained in a pool for consistency.
# Max 5 tags per enterprise/article.
# Tag types: capital signal, endorsement, stage, special markers
TAG_POOL = {
    # Capital signals
    "融资过亿": {"type": "capital", "desc": "累计融资超过1亿人民币或等值美元"},
    "已被收购": {"type": "capital", "desc": "企业已被收购"},
    "IPO上市": {"type": "capital", "desc": "企业已上市"},
    "已退市": {"type": "capital", "desc": "企业已退市"},
    # Endorsement
    "AARP旗下": {"type": "endorsement", "desc": "AARP体系内企业或合作方"},
    "Khosla投资": {"type": "endorsement", "desc": "Khosla Ventures投资企业"},
    "YC孵化": {"type": "endorsement", "desc": "Y Combinator孵化"},
    "政府支持": {"type": "endorsement", "desc": "获得政府资金或政策支持"},
    # Stage
    "种子轮": {"type": "stage", "desc": "处于种子轮阶段"},
    "成长期": {"type": "stage", "desc": "处于成长期"},
    "成熟期": {"type": "stage", "desc": "处于成熟期"},
    "已倒闭": {"type": "stage", "desc": "企业已停止运营"},
    # Special markers
    "对标标的": {"type": "special", "desc": "值得中国创业者深度参考的企业"},
    "模式创新": {"type": "special", "desc": "商业模式有独特创新"},
    "中国市场已有同类": {"type": "special", "desc": "中国已有类似企业/产品"},
    "订阅制": {"type": "special", "desc": "商业模式为订阅制"},
    "B2B2C": {"type": "special", "desc": "商业模式为B2B2C"},
    "硬件+服务": {"type": "special", "desc": "硬件+服务结合模式"},
    # Geographic (for overseas enterprises)
    "日本": {"type": "geo", "desc": "日本企业"},
    "以色列": {"type": "geo", "desc": "以色列企业"},
    "欧洲": {"type": "geo", "desc": "欧洲企业"},
}

# ================================================================
# 4. SOURCES — L1 (domain) + L2 (channel URL)
# ================================================================
# Each source has:
#   name:       display name
#   l1_domain:  primary website domain (for display)
#   l2_channels: list of (channel_name, channel_url, collection_method)
#   tier:       1=T1核心 2=T2扩展 3=T3参考
#   region:     "overseas" / "domestic"
#   notes:      optional notes
#
# collection_method: "rss" / "google_news" / "manual" / "api"
# ================================================================

SOURCES = {
    # === T1 Overseas Core ===
    "homehealthcarenews": {
        "name": "Home Health Care News",
        "l1_domain": "homehealthcarenews.com",
        "l2_channels": [
            ("funding", "https://homehealthcarenews.com/category/funding/", "rss"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "居家护理行业核心媒体，有专门funding频道",
    },
    "mcknightssenior": {
        "name": "McKnight's Senior Living",
        "l1_domain": "mcknightsseniorliving.com",
        "l2_channels": [
            ("daily_briefing", "https://www.mcknightsseniorliving.com/home/news/daily-briefing/", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "mcknightshomecare": {
        "name": "McKnight's Home Care",
        "l1_domain": "mcknightshomecare.com",
        "l2_channels": [
            ("news", "https://www.mcknightshomecare.com/", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "hospicenews": {
        "name": "Hospice News",
        "l1_domain": "hospicenews.com",
        "l2_channels": [
            ("home", "https://hospicenews.com/", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "seniorhousingnews": {
        "name": "Senior Housing News",
        "l1_domain": "seniorhousingnews.com",
        "l2_channels": [
            ("feed", "https://seniorhousingnews.com/feed/", "rss"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "",
    },
    "thegerontechnologist": {
        "name": "The Gerontechnologist",
        "l1_domain": "thegerontechnologist.com",
        "l2_channels": [
            ("articles", "https://thegerontechnologist.com/articles/", "rss"),
            ("podcast", "https://thegerontechnologist.com/podcast/", "rss"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "AgeTech Map来源，有文章+播客两个频道",
    },
    "fiercehealthcare": {
        "name": "FierceHealthcare",
        "l1_domain": "fiercehealthcare.com",
        "l2_channels": [
            ("venture_capital", "https://www.fiercehealthcare.com/keyword/venture-capital-vc", "google_news"),
            ("funding_round", "https://www.fiercehealthcare.com/keyword/funding-round", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "VC和funding两个频道分开监控",
    },
    "crunchbase_news": {
        "name": "Crunchbase News",
        "l1_domain": "news.crunchbase.com",
        "l2_channels": [
            ("health_wellness_biotech", "https://news.crunchbase.com/sections/health-wellness-biotech/", "rss"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "Crunchbase官方融资资讯，专注health/wellness/biotech",
    },
    # === T1/T2 Overseas — RSS works ===
    "mobihealthnews": {
        "name": "MobiHealthNews",
        "l1_domain": "mobihealthnews.com",
        "l2_channels": [
            ("investor", "https://www.mobihealthnews.com/categories/investor", "google_news"),
            ("news", "https://www.mobihealthnews.com/news", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "数字健康核心媒体，investor频道专门报道融资",
    },
    # === T2 Overseas — Google News proxy ===
    "startuphealth": {
        "name": "StartUp Health",
        "l1_domain": "startuphealth.com",
        "l2_channels": [
            ("blog", "https://www.startuphealth.com/startup-health-blog", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "每周投融资资讯，关注health transformation企业",
    },
    "agetechnews": {
        "name": "AgeTech News",
        "l1_domain": "agetech.news",
        "l2_channels": [
            ("home", "https://www.agetech.news/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "已断更，保留在信源库做历史参考",
    },
    "agetechcollaborative": {
        "name": "AgeTech Collaborative",
        "l1_domain": "home.agetechcollaborative.org",
        "l2_channels": [
            ("startup_directory", "https://home.agetechcollaborative.org/startup/directory", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "AARP旗下AgeTech企业库，手动入库",
    },
    "maryfurlong": {
        "name": "Mary Furlong",
        "l1_domain": "maryfurlong.com",
        "l2_channels": [
            ("shop", "https://www.maryfurlong.com/shop-2/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "企业库+高管访谈，手动入库",
    },
    "inc5000": {
        "name": "INC.5000",
        "l1_domain": "inc.com",
        "l2_channels": [
            ("inc5000_2024", "https://www.inc.com/inc5000/2024", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "每年8月出结果，健康产品/健康服务赛道",
    },
    "a2collective": {
        "name": "A2 Collective",
        "l1_domain": "a2collective.ai",
        "l2_channels": [
            ("awardees", "https://www.a2collective.ai/awardees", "manual"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "往届获奖者，已放弃，保留参考",
    },
    # === T2 Overseas — no RSS, Google News proxy ===
    "creatinganewhealthcare": {
        "name": "Creating A New Healthcare",
        "l1_domain": "creatinganewhealthcare.com",
        "l2_channels": [
            ("podcast", "https://www.creatinganewhealthcare.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "Dr. Zeev Neuwirth播客",
    },
    "finsmes": {
        "name": "FinSMEs",
        "l1_domain": "finsmes.com",
        "l2_channels": [
            ("home", "https://www.finsmes.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "融资新闻聚合，无RSS，用Google News代理",
    },
    "prnewswire": {
        "name": "PR Newswire",
        "l1_domain": "prnewswire.com",
        "l2_channels": [
            ("healthcare", "https://www.prnewswire.com/news-releases/healthcare-hospital-management/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "新闻稿平台，无RSS",
    },
    "femtechinsider": {
        "name": "FemTech Insider",
        "l1_domain": "femtechinsider.com",
        "l2_channels": [
            ("home", "https://femtechinsider.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "女性健康科技，与银发女性健康相关",
    },
    "axios_health": {
        "name": "Axios Pro Health Tech Deals",
        "l1_domain": "axios.com",
        "l2_channels": [
            ("health_tech_deals", "https://www.axios.com/pro/health-tech-deals", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "需付费，Google News代理采集摘要",
    },
    "hitconsultant": {
        "name": "HIT Consultant",
        "l1_domain": "hitconsultant.net",
        "l2_channels": [
            ("home", "https://hitconsultant.net/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "医疗IT媒体",
    },
    "pulse2": {
        "name": "Pulse 2.0",
        "l1_domain": "pulse2.com",
        "l2_channels": [
            ("home", "https://pulse2.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "科技创业媒体",
    },
    "businesswire": {
        "name": "Business Wire",
        "l1_domain": "businesswire.com",
        "l2_channels": [
            ("healthcare", "https://www.businesswire.com/portal/en/newsroom/healthcare/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "新闻稿平台，无RSS",
    },
    "techcrunch": {
        "name": "TechCrunch",
        "l1_domain": "techcrunch.com",
        "l2_channels": [
            ("health_biotech", "https://techcrunch.com/category/healthcare-biotech/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "科技媒体，healthcare-biotech板块",
    },
    "betakit": {
        "name": "BetaKit",
        "l1_domain": "betakit.com",
        "l2_channels": [
            ("home", "https://betakit.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "加拿大科技媒体",
    },
    "coverager": {
        "name": "Coverager",
        "l1_domain": "coverager.com",
        "l2_channels": [
            ("home", "https://coverager.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "保险科技媒体",
    },
    "yahoofinance": {
        "name": "Yahoo Finance",
        "l1_domain": "finance.yahoo.com",
        "l2_channels": [
            ("markets", "https://finance.yahoo.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "雅虎财经，覆盖上市银发企业",
    },
    "modernhealthcare": {
        "name": "Modern Healthcare",
        "l1_domain": "modernhealthcare.com",
        "l2_channels": [
            ("home", "https://www.modernhealthcare.com/", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "现代医疗杂志",
    },
    "homecaremag": {
        "name": "HomeCare Magazine",
        "l1_domain": "homecaremag.com",
        "l2_channels": [
            ("news", "https://www.homecaremag.com/news", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "居家护理杂志",
    },
    # === T2 Chinese sources via Google News ===
    "ageclub": {
        "name": "AgeClub",
        "l1_domain": "ageclub.net",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:ageclub.net+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "国内银发经济头部媒体",
    },
    "36kr_silver": {
        "name": "36氪-银发经济",
        "l1_domain": "36kr.com",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:36kr.com+银发+OR+养老+OR+老年+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "36氪银发经济板块",
    },
    "vcbeat_aging": {
        "name": "动脉网-养老医疗",
        "l1_domain": "vcbeat.top",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:vcbeat.top+养老+OR+银发+OR+老年+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "动脉网养老医疗板块，域名索引问题导致采集量低",
    },
    "silver_economy_cn": {
        "name": "Google News - 银发经济",
        "l1_domain": "news.google.com",
        "l2_channels": [
            ("silver_economy", "https://news.google.com/rss/search?q=银发经济+OR+养老+OR+老年产业+OR+健康养老+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "Google News中文银发经济关键词聚合",
    },
    # === T3 Broad overseas ===
    "silver_economy_news": {
        "name": "Google News - Silver Economy",
        "l1_domain": "news.google.com",
        "l2_channels": [
            ("broad", "https://news.google.com/rss/search?q=%22senior+care%22+OR+%22home+health%22+OR+%22aging+technology%22+OR+%22AgeTech%22+OR+%22elderly+care%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "宽覆盖海外银发经济新闻",
    },
    "aging_tech_news": {
        "name": "Google News - Aging Tech",
        "l1_domain": "news.google.com",
        "l2_channels": [
            ("broad", "https://news.google.com/rss/search?q=%22aging+in+place%22+OR+%22senior+living%22+OR+%22elderly+care%22+OR+%22long-term+care%22+OR+%22assisted+living%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "宽覆盖Aging Tech新闻",
    },
}

# ================================================================
# 5. DATA COLLECTION & FILTERING LOGIC
# ================================================================
# (Documented here, rendered in about.html)
#
# === What gets collected ===
# T1 sources (tier=1): always collected, full text when possible
# T2 sources (tier=2): collected, summary only
# T3 sources (tier=3): collected, used for relevance pre-filter only
#
# === Why these articles (not others) ===
# Relevance pre-filter: article must match RELEVANCE_KEYWORDS (English or Chinese)
# Irrelevance filter: article matching IRRELEVANT_KEYWORDS is discarded
# Geographic filter: articles tagged "domestic" come from Chinese sources;
#   "overseas" from overseas sources. Region is determined by source, not content.
#
# === Scoring (paused, field reserved) ===
# Score dimensions: industry(35%) + signal(30%) + writing(20%) + timeliness(15%)
# Currently PAUSED — score fields exist in data but are not displayed.
# Once re-enabled: >=7.0 -> star(high-value), 5.0-6.9 -> watch
#
# === Update frequency ===
# Scheduled: daily at 07:00 (Asia/Shanghai)
# Lookback window: past 7 days
# Estimated token cost per run: ~15-25K tokens (collector ~10K + scorer ~5-15K)

# === Overseas source names (for region detection in UI) ===
OVERSEAS_SOURCE_NAMES = set(
    s["name"] for s in SOURCES.values() if s.get("region") == "overseas"
)

# === Relevance keywords ===
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
    # Chinese
    "银发", "养老", "老年", "老龄化", "长者", "退休",
    "居家护理", "居家照护", "康复", "慢病", "认知症", "痴呆",
    "阿尔茨海默", "失智", "失能", "适老", "长寿",
    "护理院", "养老院", "敬老院", "养老社区",
    "康养", "医养", "助老", "陪护", "康护",
    "融资", "收购", "并购", "投资", "IPO", "上市",
    "A轮", "B轮", "C轮", "天使轮", "种子轮",
]

CN_RELEVANCE_KEYWORDS = [
    "银发", "养老", "老年", "老龄化", "长者", "退休",
    "居家护理", "居家照护", "康复", "慢病", "认知症",
    "康养", "医养", "助老", "陪护",
]

IRRELEVANT_KEYWORDS = [
    "pediatric", "pediatrics", "children", "infant", "neonatal",
    "pregnancy", "maternity", "adolescent", "teen", "child",
]

# ================================================================
# 6. SCORING (reserved, paused)
# ================================================================
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

HIGH_VALUE_THRESHOLD = 7.0
WATCH_THRESHOLD = 5.0

# ================================================================
# 7. DISPLAY & LANGUAGE RULES
# ================================================================
# - All UI text in Chinese
# - Original English names (enterprise names, website names) kept in English
# - Numbers: Chinese formatting (e.g., "5000万" not "50 million")
# - Dates: YYYY-MM-DD format
# - Tags: Chinese, 2-6 chars, max 5 per item

SITE_TITLE = "Silver Pulse 银脉"
SITE_SUBTITLE = "全球银发经济投融资每日速览"

# ================================================================
# 8. SILVER FINANCE ACCOUNTS (for viral detection)
# ================================================================
SILVER_FINANCE_ACCOUNTS = {
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
    "video_account": [
        {"name": "AgeClub视频号", "platform": "视频号", "type": "行业内容"},
        {"name": "银龄网视频号", "platform": "视频号", "type": "行业内容"},
        {"name": "方文养老产业观察", "platform": "视频号", "type": "行业解读"},
        {"name": "小王养老指南", "platform": "视频号", "type": "养老科普"},
        {"name": "了不起的银发圈", "platform": "视频号", "type": "社区内容"},
        {"name": "金龄银发研究院", "platform": "视频号", "type": "研究内容"},
        {"name": "长青研究社", "platform": "视频号", "type": "研究内容"},
    ],
    "douyin": [
        {"name": "AgeClub抖音", "platform": "抖音", "type": "行业内容"},
        {"name": "银龄网抖音", "platform": "抖音", "type": "行业内容"},
        {"name": "方文说养老", "platform": "抖音", "type": "行业解读"},
        {"name": "小王聊养老", "platform": "抖音", "type": "养老科普"},
        {"name": "了不起的银发圈", "platform": "抖音", "type": "社区内容"},
        {"name": "金龄研究院", "platform": "抖音", "type": "研究内容"},
    ],
}

VIRAL_THRESHOLDS = {
    "wechat_read_count": 5000,
    "video_likes": 500,
}

# ================================================================
# 9. AUTOMATION
# ================================================================
MAX_ARTICLES_TO_SCORE = 30
MAX_ARTICLE_AGE_DAYS = 7
