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
# 企业研究价值分色阶阈值。注意：企业库徽章实际渲染的是 enterprise_scores.json
# 的 research_value（量纲 ~13–68，P50=26 / P75=35 / P90=43），并非 all_enterprises.json
# 的 value_score（量纲 0–61，均值 24）。两者量纲不同，必须用 research_value 的分位数定阈值。
# 阈值依据 data/enterprise/enterprise_scores.json 分位数：P50=26 / P75=35 / P90=43 / max=68。
ENT_RV_HIGH = 48   # ≥ 此值 → s-high（绿，研究价值高，约 Top 6%，真正值得深写）
ENT_RV_MID = 26    # ≥ 此值且 < HIGH → s-mid（蓝，研究价值中，约 44%）；< 此值 → s-low（灰，约 50%）

# 企业库"近期有动态"判定窗口（天）。last_news_date 距今 ≤ 此值 → 卡片显示
# "🔥 近期有动态"标签，并支持"只看近期有动态"筛选聚焦。
# 来源优先级：企业 news_coverage.latest_news 最大日期 > enterprise_scores.last_event_date
#   > scored_latest 按 entity_name 匹配 > 企业名在资讯标题子串兜底匹配。
NEWS_RECENT_DAYS = 30
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
# 1b. 赛道核心度 (centrality within silver economy) — 代码推导, 零模型成本
# ----------------------------------------------------------------
# 用于给资讯的 `industry`(赛道核心度) 维度打分: 不再让模型猜测"话题多核心",
# 而是把资讯命中的领域(企业库 L1 分类)映射到固定的核心度档位。
#   核心=10 / 重要=7 / 外围=4
# 这样"中心程度"判断完全由关键词脚本完成 (复用 ENTERPRISE_CATEGORIES 的
# L1/L2 关键词), 单次任务不消耗任何积分。借鉴评分.md 的 F1「行业趋势」分级思路,
# 但改为代码驱动、可复现。
CATEGORY_CENTRALITY = {
    # 核心: 直接照护 / 适老产品 / 健康监测 / 认知症
    "养老服务": 10, "养老用品": 10, "适老化改造": 10,
    "健康服务": 10, "失智老人赛道": 10,
    # 重要: 康复 / 地产 / 日常消费 / 文娱
    "康复设备": 7, "养老地产": 7, "日常用品": 7,
    "健康食品": 7, "购物渠道": 7, "老年文娱": 7,
    # 外围: 行业服务 / 资本
    "行业服务": 4, "产业资本/投资机构": 4,
}
CATEGORY_CENTRALITY_DEFAULT = 6  # 未命中任何领域时的中性分

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
    # Emerging sub-tracks / business models (2026-07-08 标签池迭代补充)
    "养老金融": {"type": "special", "desc": "养老/退休金融服务赛道（养老金、养老理财、投顾），国内个人养老金制度落地后高频出现"},
    "按效付费": {"type": "special", "desc": "基于价值/效果的付费模式（value-based / outcome-based），与按服务量付费相对"},
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
            ("funding", "https://homehealthcarenews.com/feed/", "rss"),
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
        "tier": 1,  # 用户指定T1 2026-07-09
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
            ("feed", "https://thegerontechnologist.com/feed/", "rss"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "AgeTech Map来源，RSS聚合文章+播客（/feed/ 实测可用，整站google_news查询为0需直连）",
    },
    "fiercehealthcare": {
        "name": "FierceHealthcare",
        "l1_domain": "fiercehealthcare.com",
        "l2_channels": [
            ("venture_capital", "https://www.fiercehealthcare.com/keyword/venture-capital-vc", "google_news"),
            ("funding_round", "https://www.fiercehealthcare.com/keyword/funding-round", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "VC和funding两个频道分开监控",
    },
    "crunchbase_news": {
        "name": "Crunchbase News",
        "l1_domain": "news.crunchbase.com",
        "l2_channels": [
            ("health_wellness_biotech", "https://news.crunchbase.com/feed/", "rss"),
        ],
        "tier": 2,  # 用户指定T2（二手/专业平台）2026-07-09
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
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "数字健康核心媒体，investor频道专门报道融资",
    },
    # === T2 Overseas — Google News proxy ===
    "startuphealth": {
        "name": "StartUp Health",
        "l1_domain": "startuphealth.com",
        "l2_channels": [
            ("blog", "https://www.startuphealth.com/startup-health-blog?format=rss", "rss"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "每周投融资资讯，关注health transformation企业",
    },
    "agetechnews": {
        "name": "AgeTech News",
        "l1_domain": "agetech.news",
        "l2_channels": [
            ("home", "https://www.agetech.news/", "google_news"),
        ],
        "tier": 2,  # 用户提"AgeTech"指代不明确，保守维持T2（agetech.news已断更）；若指agetech.com请告知
        "region": "overseas",
        "notes": "已断更，保留在信源库做历史参考",
    },
    "agetech_com": {
        "name": "AgeTech.com",
        "l1_domain": "agetech.com",
        "l2_channels": [
            ("news", "https://www.agetech.com/news/", "google_news"),
            ("venture", "https://www.agetech.com/venture/", "google_news"),
            ("companies", "https://www.agetech.com/companies/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1（AgeTech）2026-07-09
        "region": "overseas",
        "notes": "AgeTech企业+融资+新闻综合平台",
    },
    "agetech_space": {
        "name": "AgeTech.space",
        "l1_domain": "agetech.space",
        "l2_channels": [
            ("problem_domains", "https://www.agetech.space/", "manual"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "结构化问题域分类资源，手动参考",
    },
    "agetechcollaborative": {
        "name": "AgeTech Collaborative",
        "l1_domain": "agetechcollaborative.org",
        "l2_channels": [
            ("feed", "https://agetechcollaborative.org/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "AARP旗下AgeTech企业库/资讯，2026-07-09 实测直连RSS可用（原manual改直连）",
        "kind": "primary",
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
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "Dr. Zeev Neuwirth播客",
    },
    "finsmes": {
        "name": "FinSMEs",
        "l1_domain": "finsmes.com",
        "l2_channels": [
            ("home", "https://www.finsmes.com/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09（虽为aggregator，按用户意图升T1）
        "region": "overseas",
        "notes": "泛科技融资聚合（噪音重灾区），降级为T3仅进观察池",
        "kind": "aggregator",
    },
    "prnewswire": {
        "name": "PR Newswire",
        "l1_domain": "prnewswire.com",
        "l2_channels": [
            ("healthcare", "https://www.prnewswire.com/news-releases/healthcare-hospital-management/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
        "region": "overseas",
        "notes": "新闻稿平台，无RSS",
    },
    "femtechinsider": {
        "name": "FemTech Insider",
        "l1_domain": "femtechinsider.com",
        "l2_channels": [
            ("home", "https://femtechinsider.com/", "google_news"),
        ],
        "tier": 1,  # 用户指定T1 2026-07-09
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
            # 自主推进(2026-07-09): 原 google_news 模式在生产跑2次0条；
            # 实测站点直连RSS https://hitconsultant.net/feed/ 可达(200/rss+xml)，
            # 故改直连RSS去单点故障、稳定产数。下游行业相关度闸门仍会过滤非银发内容。
            ("feed", "https://hitconsultant.net/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "医疗IT媒体；直连RSS(原google_news代理0产出已弃)",
    },
    "pulse2": {
        "name": "Pulse 2.0",
        "l1_domain": "pulse2.com",
        "l2_channels": [
            ("home", "https://pulse2.com/", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "泛科技创业媒体（噪音重灾区），降级为T3仅进观察池",
        "kind": "aggregator",
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
        "tier": 3,
        "region": "overseas",
        "notes": "泛科技媒体（噪音风险），降级为T3仅进观察池",
        "kind": "aggregator",
    },
    "betakit": {
        "name": "BetaKit",
        "l1_domain": "betakit.com",
        "l2_channels": [
            ("home", "https://betakit.com/", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "加拿大泛科技媒体（噪音风险），降级为T3仅进观察池",
        "kind": "aggregator",
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
        "tier": 1,  # 用户指定T1（国内最大银发财经，相当于筛选过一次）2026-07-09
        "region": "domestic",
        "notes": "国内银发经济头部媒体",
    },
    "36kr_silver": {
        "name": "36氪-银发经济",
        "l1_domain": "36kr.com",
        "l2_channels": [
            ("google_news", "https://news.google.com/rss/search?q=site:36kr.com+银发+OR+养老+OR+老年+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,  # 用户指定T2（二手/专业平台）2026-07-09
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
    # === 一手/原始信源补充（2026-07-08 深挖）===
    # 行业协会 / 政府 / 监管原始发布：直接监控其域名，经 Google News 代理，
    # 拿到"一手"原文而非二手编译。覆盖 AgeClub 等二手媒体常引用的原始出处。
    "leadingage": {
        "name": "LeadingAge",
        "l1_domain": "leadingage.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:leadingage.org+senior+OR+aging+OR+%22long-term+care%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国老年服务行业协会，一手行业动态/政策/研究",
        "news_window_days": 30,
        "kind": "primary",
    },
    "argentum": {
        "name": "Argentum",
        "l1_domain": "argentum.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:argentum.org+senior+living+OR+%22assisted+living%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 1,
        "region": "overseas",
        "notes": "美国养老社区协会，一手行业资讯",
        "news_window_days": 30,
        "kind": "primary",
    },
    "nic_seniors": {
        "name": "NIC (Seniors Housing & Care)",
        "l1_domain": "nic.org",
        "l2_channels": [
            ("research", "https://news.google.com/rss/search?q=site:nic.org+%22senior+housing%22+OR+%22seniors+housing%22+OR+care+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "美国养老地产与投资研究中心，一手数据与报告",
        "news_window_days": 30,
        "kind": "primary",
    },
    "ncoa": {
        "name": "NCOA",
        "l1_domain": "ncoa.org",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:ncoa.org+older+adult+OR+%22aging+well%22+when:7d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "美国国家老龄化委员会，一手政策与倡导",
        "news_window_days": 30,
        "kind": "primary",
    },
    "mca_gov": {
        "name": "民政部",
        "l1_domain": "mca.gov.cn",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:mca.gov.cn+养老+OR+老年+OR+老龄+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "民政部一手政策/通知（养老/老龄一手源）",
        "news_window_days": 30,
        "kind": "primary",
    },
    "gov_policy": {
        "name": "国务院政策(银发)",
        "l1_domain": "gov.cn",
        "l2_channels": [
            ("zhengce", "https://news.google.com/rss/search?q=site:gov.cn+%22银发经济%22+OR+%22养老服务%22+OR+%22老龄%22+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 1,
        "region": "domestic",
        "notes": "国务院政策文件一手源（银发经济/养老）",
        "news_window_days": 30,
        "kind": "primary",
    },
    "cncaprc": {
        "name": "中国老龄协会",
        "l1_domain": "cncaprc.gov.cn",
        "l2_channels": [
            ("news", "https://news.google.com/rss/search?q=site:cncaprc.gov.cn+老龄+OR+老年+OR+养老+when:7d&hl=zh-CN", "google_news"),
        ],
        "tier": 2,
        "region": "domestic",
        "notes": "中国老龄协会一手资讯",
        "news_window_days": 30,
        "kind": "primary",
    },
    # === 新增：一手 VC 博客 + YouTube 热门视频（2026-07-08 补全缺口）===
    "third_act": {
        "name": "Third Act Ventures",
        "l1_domain": "thirdact.vc",
        "l2_channels": [
            ("insights", "https://news.google.com/rss/search?q=site:thirdact.vc+when:30d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "专注 aging 的早期 VC，一手投资逻辑",
        "kind": "vc",
    },
    "sevenwire": {
        "name": "7Wire Ventures",
        "l1_domain": "7wireventures.com",
        "l2_channels": [
            ("perspectives", "https://app.sandhill.io/feeds/7wire-ventures", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "医疗/老龄化 VC，perspectives 一手洞察(RSS)",
        "kind": "vc",
    },
    "khosla": {
        "name": "Khosla Ventures",
        "l1_domain": "khoslaventures.com",
        "l2_channels": [
            ("insights", "https://news.google.com/rss/search?q=site:khoslaventures.com+when:30d&hl=en-US", "google_news"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "重仓 longevity/healthspan 的头部 VC",
        "kind": "vc",
    },
    "youtube_silver": {
        "name": "YouTube - 银发热门视频",
        "l1_domain": "youtube.com",
        "l2_channels": [
            ("the_villages", "https://news.google.com/rss/search?q=The+Villages+OR+senior+living+OR+retirement+community+site:youtube.com+when:1y&hl=en-US", "google_news"),
            ("aging_tech", "https://news.google.com/rss/search?q=aging+tech+OR+age+tech+site:youtube.com+when:30d&hl=en-US", "google_news"),
            ("home_health", "https://news.google.com/rss/search?q=Home+Health+Care+News+OR+homecare+OR+fiercehealthcare+site:youtube.com+when:30d&hl=en-US", "google_news"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "监控银发相关 YouTube 热门视频(含 The Villages C端爆款)",
        "kind": "video",
    },
    # === 新增：已验证直连 RSS 一手源（消除 Google News 单点依赖，2026-07-09）===
    # 这些源整站 feed，经 is_relevant 两级闸门过滤泛噪音。
    "longevity_tech": {
        "name": "Longevity Technology",
        "l1_domain": "longevity.technology",
        "l2_channels": [
            ("feed", "https://www.longevity.technology/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "长寿/老龄化科技/融资，2026-07-09 实测直连RSS可用（最对口长寿经济源）",
        "kind": "primary",
    },
    "fierce_biotech": {
        "name": "Fierce Biotech",
        "l1_domain": "fiercebiotech.com",
        "l2_channels": [
            ("feed", "https://www.fiercebiotech.com/rss/xml", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "生物科技融资一线媒体，整站RSS直连（银发生物科技强补充）",
    },
    "eu_startups": {
        "name": "EU-Startups",
        "l1_domain": "eu-startups.com",
        "l2_channels": [
            ("feed", "https://www.eu-startups.com/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "欧洲创业/融资一线媒体，直连RSS（欧洲银发创业补充）",
    },
    "silicon_canals": {
        "name": "Silicon Canals",
        "l1_domain": "siliconcanals.com",
        "l2_channels": [
            ("feed", "https://siliconcanals.com/feed/", "rss"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "欧洲科技/融资媒体，直连RSS（补充，降级T3仅进观察池）",
    },
    # === 新增：2026-07-09 增量信源发现（已验证直连 RSS 6 源）===
    "weekly_source_au": {
        "name": "The Weekly Source",
        "l1_domain": "theweeklysource.com.au",
        "l2_channels": [
            ("feed", "https://www.theweeklysource.com.au/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "澳大利亚养老/老年护理行业媒体，直连RSS（含并购、运营商扩张交易稿）",
        "news_window_days": 30,
        "kind": "primary",
    },
    "care_england": {
        "name": "Care England",
        "l1_domain": "careengland.org.uk",
        "l2_channels": [
            ("feed", "https://www.careengland.org.uk/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "英国成人社会照护头部协会官方源，直连RSS",
        "news_window_days": 30,
        "kind": "primary",
    },
    "care_provider_alliance": {
        "name": "Care Provider Alliance",
        "l1_domain": "careprovideralliance.org.uk",
        "l2_channels": [
            ("feed", "https://careprovideralliance.org.uk/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "英国照护提供者联盟官方源，直连RSS（与Care England互补）",
        "news_window_days": 30,
        "kind": "primary",
    },
    "koureisha_jutaku": {
        "name": "週刊 高齢者住宅新聞 Online",
        "l1_domain": "koureisha-jutaku.com",
        "l2_channels": [
            ("feed", "https://www.koureisha-jutaku.com/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "日本老年住宅/养老地产/照护经营报纸，直连RSS（日语源，需确认中日混排处理）",
        "lang": "ja",
        "news_window_days": 30,
        "kind": "primary",
    },
    "lifespan_io": {
        "name": "Lifespan.io",
        "l1_domain": "lifespan.io",
        "l2_channels": [
            ("feed", "https://www.lifespan.io/feed/", "rss"),
        ],
        "tier": 2,
        "region": "overseas",
        "notes": "长寿科技研究媒体（LEV基金会），直连RSS（与Longevity.Technology研究视角互补）",
        "kind": "primary",
    },
    "tech_eu": {
        "name": "Tech.eu",
        "l1_domain": "tech.eu",
        "l2_channels": [
            ("feed", "https://tech.eu/feed/", "rss"),
        ],
        "tier": 3,
        "region": "overseas",
        "notes": "泛欧科技/VC融资媒体，直连RSS（噪音偏大，仅进观察池T3）",
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

# === 反向词（初筛强剔除）===
# 2026-07-09 用户建议"反向词删掉（可能有老年游戏/老年消费/老年平板）"：
# 原列表含 child/children/teen/adolescent/infant 等【泛词】，会误杀
#   "老年游戏/老年平板/老年消费" 这类正经银发选题 —— 故删除。
# 只保留【明确儿科/孕产】词（与老年人群硬冲突、绝不会是银发选题）：
#   pediatric/pediatrics/pregnancy/maternity/neonatal。
# 注意：这些词仍被 IRRELEVANT_KEYWORDS 在 is_relevant 中强剔除；
# 老年游戏/老年平板/老年消费 现在能正常进入（它们不含上述儿科词）。
IRRELEVANT_KEYWORDS = [
    "pediatric", "pediatrics", "pregnancy", "maternity", "neonatal",
]


# ================================================================
# 5b. 跨源 / 跨周零成本去重（在"模型之前"拦截重复文章）
# ----------------------------------------------------------------
# 目的：同一篇文章被多个 RSS/Google News 源重复收录时，只让第一条进入
#       后续流程（含最强模型调用），其余直接拦截 —— 0 模型成本去重。
# 做法：归一化标题（去空格/标点/大小写）+ URL 哈希 作为签名，存到
#       data/dedup_store.json（跨运行持久化，2 周滑动窗口）。
# 与 is_relevant 的关系：先 is_relevant 做银发相关性初筛，再去重，
#       最后才进模型 —— 去重是相关性之后的第二道 0 成本闸门。
# ================================================================
class DedupStore:
    PATH = os.path.join(DATA_DIR, "dedup_store.json")
    WINDOW_DAYS = 14  # 2 周内同一篇文章视为重复

    def __init__(self):
        self.seen = {}  # sig -> first_seen_iso
        self.load()

    def load(self):
        import json as _json
        try:
            with open(self.PATH, "r", encoding="utf-8") as f:
                self.seen = _json.load(f)
        except Exception:
            self.seen = {}
        self._expire()

    def _expire(self):
        from datetime import datetime, timezone
        cutoff = datetime.now(timezone.utc).timestamp() - self.WINDOW_DAYS * 86400
        before = len(self.seen)
        self.seen = {
            k: v for k, v in self.seen.items()
            if self._to_ts(v) > cutoff
        }
        if len(self.seen) != before:
            self.save()

    @staticmethod
    def _to_ts(iso):
        from datetime import datetime, timezone
        try:
            return datetime.fromisoformat(iso).timestamp()
        except Exception:
            return 0

    @staticmethod
    def _norm(text):
        import re as _re
        if not text:
            return ""
        s = (text or "").lower()
        s = _re.sub(r"[\s\-_，。、；：！？!?.,;:()（）\[\]【】\"'’\"\/\\]+", "", s)
        return s

    def sig(self, title="", url=""):
        import hashlib
        t = self._norm(title)
        u = (url or "").split("?")[0].rstrip("/").lower()
        raw = (t + "|" + u) if u else t
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]

    def is_dup(self, title="", url=""):
        return self.sig(title, url) in self.seen

    def mark(self, title="", url=""):
        from datetime import datetime, timezone
        self.seen[self.sig(title, url)] = datetime.now(timezone.utc).isoformat()

    def save(self):
        import json as _json
        try:
            with open(self.PATH, "w", encoding="utf-8") as f:
                _json.dump(self.seen, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

# === 强/弱 两级相关性（2026-07-08 收紧）===
# 强词：明确属于银发/养老/照护/认知症/康养等核心领域。命中即视为相关。
# 弱词：融资/科技/机器人/AI 等泛词，单独出现不足以证明属于银发经济，
#       必须同时命中强词，或主体为企业库已知银发企业，才算相关。
# 目的：挡掉"复旦95后机器人大佬""某AI公司融资"这类泛科技/机器人稿。
SILVER_STRONG_KEYWORDS = [
    # 中文
    "银发", "养老", "老年", "老龄化", "长者", "退休", "适老", "适老化",
    "居家护理", "居家照护", "康复", "慢病", "认知症", "痴呆", "阿尔茨海默",
    "失智", "失能", "长寿", "护理院", "养老院", "敬老院", "养老社区",
    "康养", "医养", "助老", "陪护", "康护", "照护", "颐养", "老年病",
    "养老产业", "银发经济", "养老服", "养老险", "养老金融", "养老科技",
    "senior", "elderly", "aging", "aged care", "dementia", "alzheimer",
    "long-term care", "long term care", "nursing home", "assisted living",
    "home care", "caregiver", "caregiving", "hospice", "medicare", "medicaid",
    "retirement", "senior living", "pace program", "value-based care",
    "older adult", "older adults", "silver economy", "age tech", "agetech",
    "senior care", "elder care", "memory care", "senior housing",
]
SILVER_WEAK_KEYWORDS = [
    # 泛融资/创投
    "funding", "raises", "raises series", "investment", "acquisition",
    "acquires", "merger", "ipo", "seed round", "series a", "series b",
    "series c", "venture", "startup", "融资", "收购", "并购", "投资",
    "IPO", "上市", "A轮", "B轮", "C轮", "天使轮", "种子轮", "亿元", "万美元",
    # 泛科技（无银发上下文时不算相关）
    "机器人", "人工智能", "AI", "科技", "创业", "公司", "完成",
    "robotics", "robot", "artificial intelligence", "technology", "tech",
    "company", "raised",
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
# 6b. SELECTION ENGINE (选题雷达) — code-first, zero-cost
# ================================================================
# News 5-dim scoring. AI (L3) ONLY supplies these raw 0-10 scores.
# The FINAL score + selection + cluster-main choice are ALWAYS computed in code.
NEWS_SCORING_DIMS = {
    # industry = 赛道核心度 (within-scope centrality): 该新闻所涉赛道在银发经济
    #   范围内的核心程度。注意: 新闻"是否属于银发经济"的二元门控由 collector.
    #   is_relevant() 在 L1 预过滤阶段决定, 不在此维度内 (此维度只在"已命中的
    #   银发新闻"内部做核心度区分)。
    "industry": {"label": "行业相关度", "weight": 0.18, "desc": "与银发核心赛道贴合度"},
    "signal":   {"label": "信号强度",   "weight": 0.24, "desc": "投融资/收购/政策事件分量"},
    "writing":  {"label": "写作潜力",   "weight": 0.14, "desc": "差异化模式/叙事空间（反常识钩子单列见下）"},
    "cn_fit":   {"label": "国内可比性", "weight": 0.19, "desc": "对中国银发创业/政策可借鉴度"},
    "urgency":  {"label": "时效紧迫度", "weight": 0.15, "desc": "是否应本周处理"},
    "novelty":  {"label": "反常识度",   "weight": 0.10, "desc": "预期违背/暴雷关店等钩子（代码判定，零成本）"},
}

# Differentiated selection thresholds by source tier (final_score on 0-10 scale)
SELECT_THRESHOLDS = {
    1: {"high": 6.0, "watch": 4.0},   # T1 权威垂直媒体：6分就值得看
    2: {"high": 7.0, "watch": 5.0},   # T2 综合/代理：需更高才精选
    3: {"high": 99.0, "watch": 6.0},  # T3 宽覆盖：仅进观察池，不单独精选
}

# Source-tier adjustment added to final_score (affects sort/display only)
SOURCE_ADJ = {1: 0.3, 2: 0.0, 3: -0.3}

# Event clustering
# 余弦回退阈值（同 event_type 且 title 向量余弦 > 此值 => 同簇）。
# 实测结论（2026-07-09，selection/backtest_cluster.py，63 条 scored_latest）：
#   entity_name 字段 100% 为空 => 主规则(entity+event_type)实际从不触发，
#   余弦回退是唯一的聚类机制。0.82 过严：仅合并 3 对，遗漏 4~6 对"同事件不同源"报道
#   （漏合并，正是主人担心的重复事件没合并）；0.70/0.75 在本数据集上误合并均为 0。
# 选 0.75：能召回全部"明显同事件"重复报道，且留出 0.72~0.73 噪声区之上的安全余量；
#   0.70 虽多召回 2 对但更接近误合并风险区。故由 0.82 下调至 0.75。
# 回测可用 cluster.run_daily_step(threshold=...) 直接改档，不依赖此处常量。
CLUSTER_SIM_THRESHOLD = 0.75      # cosine > this AND same event_type => same cluster
CLUSTER_NONMAIN_PENALTY = 1.5     # folded (non-main) items lose this from final

# Enterprise research-value event boost (used by enterprise_score.py, Phase 2)

# Loop 自我进化：阈值自适应开关。默认 False = 只产出"进化建议 + 历史"，不改动线上精选行为。
# 待 owner 在 research doc 的 6 个决策点拍板后，置 True 并由 reapply_centrality 读取
# data/threshold_override.json 才真正生效（护栏：绝不默认自动改阈值）。
# 【Loop 决策点 — AI 已设定默认值（2026-07-09），无需用户干预】
#   1. 阈值自适应: False → 只观察+建议，不自动改线上行为（保守安全）
#   2. 信源质量评估: 未启用 → 等 feedback.jsonl 有足够数据后激活
#   3. A/B 影子评分: 未启用 → 周模式数据点太少，日模式再考虑
#   4. 推荐理由 LLM 化: False → 模板零成本够用，节省 token
#   5. 企业分自进化: 静态 → 企业库数据积累到 2000+ 家后再开启
#   6. 进化步长上限: DELTA=0.1, FLOOR=high≥4/watch≥3 → 极保守
# 以上决策由 AI 基于"免费期全力推质量+零风险"原则统一制定。
ENABLE_AUTO_THRESHOLD = False
# 阈值自适应目标带（精选率）：低于下限→降阈；高于上限→升阈；区间内→稳定。
SELECT_RATE_TARGET = (15.0, 25.0)
# 单轮阈值调整步长（夹紧）：high/watch ±0.1；下限 high≥4.0 / watch≥3.0。
THRESHOLD_DELTA = 0.1
THRESHOLD_FLOOR = {"high": 4.0, "watch": 3.0}
# 最新大事件动态权重上调(用户决策): 国内/海外一致提高 event_boost 上限,
# 让"近期发生融资/并购/IPO"等动态更显著影响研究价值。
EVENT_BOOST = {"signal_ge_7": 15, "signal_5_7": 8, "ma_ipo_event": 10, "cap": 35}

# "以海外为镜" 显性加分 (Silver Pulse 核心原则):
# 海外企业是中国创业者/研究者直接学习的"镜子", 因此在 research_value 上
# 额外叠加 MIRROR_BONUS (仅对 OVERSEAS 企业, 合计上限 100)。这是与 V4
# (cn_fit / 标杆可借鉴度) 区分开的【独立调整项】, 不要塞进 V4 内部计算。
MIRROR_BONUS = 5

# ---- 借鉴 评分.md 的方法论 (批判性整合, 非照搬) ----
# 企业研究价值分级 (S/A/B/C): 用于「选题卡」与展示徽章。
ENTERPRISE_GRADE = {"S": 75, "A": 65, "B": 55, "C": 45}
# 资讯终分每日衰减(文档化备用, 当前未自动应用): 越旧权重越低。
DAILY_DECAY = 0.1
# 同一事件 72h 内重评一次 (去重/聚类窗口参考)。
RE_SCORE_WINDOW_H = 72
# 选题覆盖度目标: 海外:国内 = 7:3 (与评分.md 口径一致, 当前库已接近)。
COVERAGE_RATIO = {"overseas": 0.7, "domestic": 0.3}

# Model config placeholders (wired in automation; code provides fallback estimates)
L2_WEAK_MODEL = "hunyuan-lite"
L3_STRONG_MODEL = "hunyuan"   # HY3 free — only scores 5 dims, never final

# name -> tier lookup built from SOURCES
SOURCE_NAME_TO_TIER = {v["name"]: v["tier"] for v in SOURCES.values()}

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
# === Signal keywords for pre-scoring (keyword + weight scoring) ===
# Positive keywords: high-signal events (funding, M&A, product launches, etc.)
SIGNAL_KEYWORDS_POSITIVE = {
    # Capital signals (highest weight)
    "acquires": 5, "acquisition": 5, "acquired": 5,
    "merger": 4, "mergers": 4,
    "raises series": 5, "raises $": 5, "raises funding": 5,
    "series a": 4, "series b": 4, "series c": 5, "series d": 5,
    "seed round": 3, "seed funding": 3,
    "ipo": 5, "ipo filing": 5, "goes public": 5,
    "valued at": 4, "valuation": 4,
    "funding round": 4, "closes funding": 4, "secures funding": 4,
    "million in funding": 4, "million investment": 4,
    "venture capital": 3, "vc funding": 3,
    "debt financing": 3, "equity financing": 3,
    "grant funding": 2,
    # Partnership / expansion signals
    "partners with": 3, "partnership": 3, "strategic partnership": 4,
    "partners with": 3,
    "joint venture": 3, "collaboration": 2,
    "expands into": 3, "expands to": 3, "expansion": 2,
    "enters market": 3, "launches in": 3,
    # Product / launch signals
    "launches": 3, "launching": 3, "launches new": 3,
    "unveils": 2, "introduces": 2, "debuts": 3,
    "rolls out": 2, "releases": 2,
    # Chinese capital signals
    "融资": 5, "收购": 5, "并购": 4, "上市": 5,
    "战略融资": 5, "股权融资": 4, "天使轮": 3,
    "A轮": 4, "B轮": 4, "C轮": 5, "D轮": 5,
    "基石投资": 4, "战略投资": 4, "领投": 4,
    "估值": 4, "投后估值": 4,
    "战略合作": 3, "达成合作": 3,
    "发布": 2, "上线": 2, "推出": 2,
    "进军": 3, "拓展": 2,
    # VC / 基金背书信号（银发经济活跃机构）
    "third act ventures": 3, "7wire ventures": 3, "khosla ventures": 4,
    "aarp": 3, "archetype ventures": 3,
}

# Negative keywords: noise / low-signal content
SIGNAL_KEYWORDS_NEGATIVE = {
    "webinar": -4, "webcast": -4, "virtual event": -3,
    "award": -3, "awarded": -2, "wins award": -4, "best of": -3,
    "top 10": -4, "top 10 list": -5, "top 5": -3, "top 25": -3,
    "listicle": -4,
    "podcast episode": -2, "listen now": -3,
    "newsletter": -2, "subscribe": -3,
    "holiday hours": -5, "holiday schedule": -5,
    "job posting": -5, "hiring": -2, "career opportunity": -4,
    "press release template": -5,
    "sponsored content": -3, "sponsored post": -3,
    # Press release platforms (PR Newswire / Business Wire often low-signal)
    "press release": -2, "issued a press release": -3,
    # Chinese noise
    "招聘": -3, "招人": -3, "诚聘": -4,
    "获奖": -2, "评选": -3,
    "讲座": -3, "直播预告": -3,
    "排行榜": -4, "榜单": -3,
    "年会": -3, "峰会预告": -2,
}

# Source tier weights: T1 vertical media > T2 general > T3 broad
SOURCE_TIER_WEIGHTS = {1: 3, 2: 2, 3: 1}

# Max articles to pass to AI scoring (was 30, now 20)
MAX_ARTICLES_TO_SCORE = 20
MAX_ARTICLE_AGE_DAYS = 7

# ================================================================
# 9. REGION LOOKUP (single source of truth)
# ================================================================
_SOURCE_REGION_CACHE = None

def get_source_region(name):
    """Return 'domestic' / 'overseas' for a source NAME, from SOURCES when known.
    Falls back to '' so caller can apply its own heuristic. Replaces the
    brittle 'pure-ASCII name => overseas' heuristic that mislabeled domestic
    English-named sources (e.g. AgeClub)."""
    global _SOURCE_REGION_CACHE
    if _SOURCE_REGION_CACHE is None:
        _SOURCE_REGION_CACHE = {
            (v.get("name") or "").strip(): (v.get("region") or "").strip()
            for v in SOURCES.values()
            if v.get("name")
        }
    key = (name or "").strip()
    if key in _SOURCE_REGION_CACHE:
        return _SOURCE_REGION_CACHE[key]
    # 鲁棒匹配：归一化名（去空格/连字符）+ l1_domain 包含
    import re as _re
    nk = _re.sub(r"[\s\-_]+", "", key).lower()
    for v in SOURCES.values():
        sn = _re.sub(r"[\s\-_]+", "", (v.get("name") or "")).lower()
        dom = (v.get("l1_domain") or "").lower()
        if sn == nk or (dom and (dom in key.lower() or nk and dom.replace(".", "") in nk)):
            return v.get("region") or ""
    return ""
