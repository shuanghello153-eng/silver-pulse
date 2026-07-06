#!/usr/bin/env python3
"""
merge_v2.py — 企业数据四源融合（v3）
来源：现有 + Stage书籍108家 + 选题库V4 504条 + 中国mapping 374家
输出：新schema all_enterprises.json
Schema: name, region, category_l1, category_l2, tags, description, highlights,
        funding_latest, funding_total, investors, founded, value_score,
        source, crunchbase_url, website_url, serial
"""
import json
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "enterprise"

# Import config for categories
import sys
sys.path.insert(0, str(BASE_DIR))
from config import ENTERPRISE_CATEGORIES

# ============================================================
# 13-class L1 -> L2 classification
# ============================================================
# Build keyword -> (l1, l2) lookup from config
L1_KEYWORDS = {}
L2_KEYWORDS = {}
for l1_label, info in ENTERPRISE_CATEGORIES.items():
    # L1 keywords: the category name itself + common terms
    l1_kws = [l1_label]
    L1_KEYWORDS[l1_label] = l1_kws

    for l2 in info["l2"]:
        if l1_label not in L2_KEYWORDS:
            L2_KEYWORDS[l1_label] = {}
        # L2 keywords derived from L2 name
        l2_kw = l2.replace("&", "").replace(" ", "").lower()
        L2_KEYWORDS[l1_label][l2] = l2_kw

# Detailed keyword mapping for raw category text -> L1 + L2
# This maps common raw category strings to specific L1/L2
RAW_CATEGORY_MAP = {
    # 购物渠道
    "线上渠道": ("购物渠道", "线上渠道"),
    "线下渠道": ("购物渠道", "线下渠道"),
    "电视购物": ("购物渠道", "电视购物"),
    "会员营销": ("购物渠道", "会员营销"),
    "私域": ("购物渠道", "私域渠道"),
    "电商": ("购物渠道", "线上渠道"),
    "零售": ("购物渠道", "线下渠道"),
    "团购": ("购物渠道", "线上渠道"),
    "连锁": ("购物渠道", "线下渠道"),
    "药店": ("购物渠道", "线下渠道"),
    "采购": ("购物渠道", "特殊渠道"),
    "批发": ("购物渠道", "特殊渠道"),
    # 日常用品
    "老年鞋": ("日常用品", "老年鞋"),
    "老年服饰": ("日常用品", "老年服饰"),
    "老年护肤": ("日常用品", "老年护肤"),
    "染发": ("日常用品", "染发剂"),
    "假发": ("日常用品", "假发"),
    "纸尿裤": ("日常用品", "家用医疗"),
    "成人失禁": ("养老用品", "成人失禁"),  # override
    "日用品": ("日常用品", "家用医疗"),
    "消费品牌": ("日常用品", "家用医疗"),
    "个护": ("日常用品", "老年护肤"),
    "洗浴": ("日常用品", "家用医疗"),
    "apparel": ("日常用品", "老年服饰"),
    "footwear": ("日常用品", "老年鞋"),
    "skincare": ("日常用品", "老年护肤"),
    "beauty": ("日常用品", "老年护肤"),
    "cosmetic": ("日常用品", "老年护肤"),
    "fashion": ("日常用品", "老年服饰"),
    "personal care": ("日常用品", "家用医疗"),
    "hygiene": ("日常用品", "家用医疗"),
    # 健康食品
    "保健品": ("健康食品", "保健品&OTC"),
    "OTC": ("健康食品", "保健品&OTC"),
    "中药": ("健康食品", "中式养生"),
    "养生": ("健康食品", "中式养生"),
    "益生菌": ("健康食品", "益生菌"),
    "小分子肽": ("健康食品", "小分子肽"),
    "特医食品": ("健康食品", "特医食品"),
    "蛋白粉": ("健康食品", "蛋白粉"),
    "无糖": ("健康食品", "无糖&低GI"),
    "低GI": ("健康食品", "无糖&低GI"),
    "羊奶": ("健康食品", "成人羊奶"),
    "代工厂": ("健康食品", "代工厂"),
    "健康食品": ("健康食品", "保健品&OTC"),
    "营养": ("健康食品", "保健品&OTC"),
    "膳食": ("健康食品", "保健品&OTC"),
    "食品": ("健康食品", "保健品&OTC"),
    "supplement": ("健康食品", "保健品&OTC"),
    "nutrition": ("健康食品", "保健品&OTC"),
    "vitamin": ("健康食品", "保健品&OTC"),
    "保健": ("健康食品", "保健品&OTC"),
    "滋补": ("健康食品", "中式养生"),
    "食疗": ("健康食品", "中式养生"),
    # 老年文娱
    "旅游": ("老年文娱", "老年旅游"),
    "教育": ("老年文娱", "老年教育"),
    "社交平台": ("老年文娱", "社交平台"),
    "广场舞": ("老年文娱", "广场舞"),
    "相亲": ("老年文娱", "老年相亲"),
    "健身": ("老年文娱", "老年健身"),
    "音乐": ("老年文娱", "老年音乐"),
    "再就业": ("健康服务", "再就业"),  # override
    "文娱": ("老年文娱", "社交平台"),
    "直播": ("老年文娱", "社交平台"),
    "内容": ("老年文娱", "社交平台"),
    "社区": ("老年文娱", "社交平台"),
    "travel": ("老年文娱", "老年旅游"),
    "education": ("老年文娱", "老年教育"),
    "social": ("老年文娱", "社交平台"),
    "dating": ("老年文娱", "老年相亲"),
    "fitness": ("老年文娱", "老年健身"),
    "entertainment": ("老年文娱", "社交平台"),
    "learning": ("老年文娱", "老年教育"),
    "companionship": ("老年文娱", "社交平台"),
    "communication": ("老年文娱", "社交平台"),
    "leisure": ("老年文娱", "社交平台"),
    "hobby": ("老年文娱", "社交平台"),
    "creative": ("老年文娱", "社交平台"),
    "content": ("老年文娱", "社交平台"),
    "life story": ("老年文娱", "社交平台"),
    "memory": ("老年文娱", "社交平台"),
    "photo": ("老年文娱", "社交平台"),
    "游戏": ("老年文娱", "社交平台"),
    "老人互助": ("老年文娱", "社交平台"),
    "会员制": ("老年文娱", "社交平台"),
    "APP": ("老年文娱", "社交平台"),
    "AI": ("老年文娱", "社交平台"),
    # 健康服务
    "健康服务": ("健康服务", "健康养生"),
    "慢病": ("健康服务", "慢病管理"),
    "血压": ("健康服务", "血压血糖"),
    "血糖": ("健康服务", "血压血糖"),
    "睡眠": ("健康服务", "睡眠监测"),
    "摔倒": ("健康服务", "摔倒监测"),
    "陪诊": ("健康服务", "陪诊服务"),
    "体检": ("健康服务", "健康养生"),
    "中医": ("健康服务", "健康养生"),
    "健康养生": ("健康服务", "健康养生"),
    "chronic": ("健康服务", "慢病管理"),
    "monitoring": ("健康服务", "健康养生"),
    "telehealth": ("健康服务", "慢病管理"),
    "wearable": ("健康服务", "健康养生"),
    "fall prevention": ("健康服务", "摔倒监测"),
    "fall detection": ("健康服务", "摔倒监测"),
    "rpm": ("健康服务", "慢病管理"),
    "remote patient": ("健康服务", "慢病管理"),
    "medication": ("健康服务", "慢病管理"),
    "scam": ("健康服务", "健康养生"),
    "fraud": ("健康服务", "健康养生"),
    "vital": ("健康服务", "健康养生"),
    "healthcare provider": ("健康服务", "健康养生"),
    "medical": ("健康服务", "健康养生"),
    "clinic": ("健康服务", "健康养生"),
    "telemedicine": ("健康服务", "慢病管理"),
    "远程医疗": ("健康服务", "慢病管理"),
    "健康监测": ("健康服务", "健康养生"),
    "可穿戴": ("健康服务", "健康养生"),
    "防摔": ("健康服务", "摔倒监测"),
    "用药": ("健康服务", "慢病管理"),
    "糖尿病": ("健康服务", "血压血糖"),
    "慢性肾病": ("健康服务", "慢病管理"),
    "眼动追踪": ("健康服务", "健康养生"),
    "数字健康": ("健康服务", "健康养生"),
    "数字疗法": ("健康服务", "慢病管理"),
    "MSK": ("健康服务", "健康养生"),
    "在线锻炼": ("健康服务", "健康养生"),
    "health service": ("健康服务", "健康养生"),
    # 适老化改造
    "适老": ("适老化改造", "适老家居产品"),
    "改造": ("适老化改造", "适老家居产品"),
    "智能养老": ("适老化改造", "智能养老用品"),
    "智慧养老软件": ("适老化改造", "智慧养老软件"),
    "家居产品": ("适老化改造", "适老家居产品"),
    "供应链": ("适老化改造", "综合供应链"),
    "规划设计": ("适老化改造", "适老规划设计"),
    "aging in place": ("适老化改造", "适老家居产品"),
    "renovation": ("适老化改造", "适老家居产品"),
    "smart home": ("适老化改造", "智能养老用品"),
    "home modification": ("适老化改造", "适老家居产品"),
    "accessibility": ("适老化改造", "适老家居产品"),
    "resident engagement": ("适老化改造", "智慧养老软件"),
    "tech training": ("适老化改造", "智慧养老软件"),
    "digital literacy": ("适老化改造", "智慧养老软件"),
    # 行业服务
    "行业媒体": ("行业服务", "行业媒体"),
    "行业展会": ("行业服务", "行业展会"),
    "咨询": ("行业服务", "咨询研究"),
    "金融理财": ("行业服务", "金融理财"),
    "保险科技": ("行业服务", "金融理财"),
    "insurtech": ("行业服务", "金融理财"),
    "wealth management": ("行业服务", "金融理财"),
    "exhibition": ("行业服务", "行业展会"),
    "conference": ("行业服务", "行业展会"),
    "annuity": ("行业服务", "金融理财"),
    "年金险": ("行业服务", "金融理财"),
    "养老金融": ("行业服务", "金融理财"),
    "金融科技适老": ("行业服务", "金融理财"),
    "适老金融": ("行业服务", "金融理财"),
    "行业资讯": ("行业服务", "行业媒体"),
    # 养老地产
    "养老地产": ("养老地产", "运营商"),
    "地产": ("养老地产", "运营商"),
    "CCRC": ("养老地产", "运营商"),
    "养老院": ("养老地产", "运营商"),
    "养老社区": ("养老地产", "运营商"),
    "护理院": ("养老地产", "运营商"),
    "运营商": ("养老地产", "运营商"),
    "养老公寓": ("养老地产", "运营商"),
    "中介": ("养老地产", "养老院中介"),
    "real estate": ("养老地产", "运营商"),
    "senior housing": ("养老地产", "运营商"),
    "senior living": ("养老地产", "运营商"),
    "nursing home": ("养老地产", "运营商"),
    "housing": ("养老地产", "运营商"),
    "adult day": ("养老地产", "运营商"),
    "居住": ("养老地产", "运营商"),
    "社区养老": ("养老地产", "运营商"),
    "assisted living": ("养老地产", "运营商"),
    "independent living": ("养老地产", "运营商"),
    # 养老服务
    "居家养老": ("养老服务", "专业级护理"),
    "家政": ("养老服务", "传统家政"),
    "护理": ("养老服务", "专业级护理"),
    "护工": ("养老服务", "专业级护理"),
    "长护险": ("养老服务", "长护险"),
    "助餐": ("养老服务", "老年助餐"),
    "助浴": ("养老服务", "助浴助洁"),
    "照护": ("养老服务", "专业级护理"),
    "陪护": ("养老服务", "院内陪护"),
    "院内陪护": ("养老服务", "院内陪护"),
    "养老运营": ("养老服务", "专业级护理"),
    "home care": ("养老服务", "专业级护理"),
    "caregiving": ("养老服务", "专业级护理"),
    "nursing": ("养老服务", "专业级护理"),
    "meal": ("养老服务", "老年助餐"),
    "bathing": ("养老服务", "助浴助洁"),
    "caregiver": ("养老服务", "专业级护理"),
    "everyday assistance": ("养老服务", "专业级护理"),
    "companion": ("养老服务", "专业级护理"),
    "陪伴": ("养老服务", "专业级护理"),
    "助洁": ("养老服务", "助浴助洁"),
    "养老服务": ("养老服务", "专业级护理"),
    "日常照护": ("养老服务", "专业级护理"),
    "民政服务": ("养老服务", "民政服务"),
    # 养老用品
    "轮椅": ("养老用品", "肢体障碍"),
    "护理床": ("养老用品", "肢体障碍"),
    "拐杖": ("养老用品", "肢体障碍"),
    "助行器": ("养老用品", "肢体障碍"),
    "代步车": ("养老用品", "肢体障碍"),
    "假肢": ("养老用品", "肢体障碍"),
    "洗澡": ("养老用品", "肢体障碍"),
    "坐便": ("养老用品", "肢体障碍"),
    "视觉": ("养老用品", "视觉障碍"),
    "听觉": ("养老用品", "听觉障碍"),
    "呼吸": ("养老用品", "呼吸障碍"),
    "吞咽": ("养老用品", "吞咽障碍"),
    "咀嚼": ("养老用品", "咀嚼障碍"),
    "辅具": ("养老用品", "肢体障碍"),
    "养老用品": ("养老用品", "肢体障碍"),
    "assistive": ("养老用品", "肢体障碍"),
    "wheelchair": ("养老用品", "肢体障碍"),
    "mobility": ("养老用品", "肢体障碍"),
    "hearing": ("养老用品", "听觉障碍"),
    "vision": ("养老用品", "视觉障碍"),
    "prosthetic": ("养老用品", "肢体障碍"),
    "助听": ("养老用品", "听觉障碍"),
    "助视": ("养老用品", "视觉障碍"),
    "听力": ("养老用品", "听觉障碍"),
    "视力": ("养老用品", "视觉障碍"),
    "智能用品": ("养老用品", "智能用品"),
    # 康复设备
    "康复": ("康复设备", "运动康复"),
    "运动康复": ("康复设备", "运动康复"),
    "手部康复": ("康复设备", "手部康复"),
    "外骨骼": ("康复设备", "外骨骼"),
    "精神": ("康复设备", "精神&神经"),
    "神经": ("康复设备", "精神&神经"),
    "肿瘤康复": ("康复设备", "肿瘤康复"),
    "康复机器人": ("康复设备", "外骨骼"),
    "设备": ("康复设备", "运动康复"),
    "器械": ("康复设备", "运动康复"),
    "rehabilitation": ("康复设备", "运动康复"),
    "exoskeleton": ("康复设备", "外骨骼"),
    "medical device": ("康复设备", "运动康复"),
    "rehab": ("康复设备", "运动康复"),
    "physical therapy": ("康复设备", "运动康复"),
    "robot": ("康复设备", "外骨骼"),
    # 失智老人赛道
    "失智": ("失智老人赛道", "照护机构"),
    "认知症": ("失智老人赛道", "照护机构"),
    "认知障碍": ("失智老人赛道", "照护机构"),
    "阿尔茨海默": ("失智老人赛道", "照护机构"),
    "痴呆": ("失智老人赛道", "照护机构"),
    "早筛": ("失智老人赛道", "病情早筛"),
    "认知训练": ("失智老人赛道", "认知症产品"),
    "认知产品": ("失智老人赛道", "认知症产品"),
    "脑健康": ("失智老人赛道", "病情早筛"),
    "dementia": ("失智老人赛道", "照护机构"),
    "Alzheimer": ("失智老人赛道", "照护机构"),
    "cognitive": ("失智老人赛道", "认知症产品"),
    "brain health": ("失智老人赛道", "病情早筛"),
    "memory care": ("失智老人赛道", "照护机构"),
    "早期检测": ("失智老人赛道", "病情早筛"),
    "大脑训练": ("失智老人赛道", "认知症产品"),
    "脑科学": ("失智老人赛道", "病情早筛"),
    # 产业资本/投资机构
    "投资": ("产业资本/投资机构", "消费背景"),
    "资本": ("产业资本/投资机构", "消费背景"),
    "基金": ("产业资本/投资机构", "消费背景"),
    "风投": ("产业资本/投资机构", "消费背景"),
    "VC": ("产业资本/投资机构", "消费背景"),
    "PE": ("产业资本/投资机构", "消费背景"),
    "天使": ("产业资本/投资机构", "种子投资背景"),
    "上市公司": ("产业资本/投资机构", "相关上市公司"),
    "投资机构": ("产业资本/投资机构", "消费背景"),
    "venture": ("产业资本/投资机构", "消费背景"),
    "capital": ("产业资本/投资机构", "消费背景"),
    "investor": ("产业资本/投资机构", "消费背景"),
    "incubator": ("产业资本/投资机构", "种子投资背景"),
    "accelerator": ("产业资本/投资机构", "种子投资背景"),
    "孵化": ("产业资本/投资机构", "种子投资背景"),
    "funding": ("产业资本/投资机构", "消费背景"),
    "融资": ("产业资本/投资机构", "消费背景"),
    "国资": ("产业资本/投资机构", "国资背景"),
    "消费背景": ("产业资本/投资机构", "消费背景"),
    "医疗背景": ("产业资本/投资机构", "严肃医疗背景"),
}


def classify_enterprise(category_raw: str) -> tuple:
    """Classify raw category text into (l1, l2) using the 13-class system."""
    if not category_raw:
        return ("行业服务", "行业媒体")  # default

    text = category_raw

    # First, try exact match in RAW_CATEGORY_MAP
    for kw, (l1, l2) in RAW_CATEGORY_MAP.items():
        if kw.lower() in text.lower():
            return (l1, l2)

    # Fallback: try matching L2 keywords
    for l1_label, l2s in L2_KEYWORDS.items():
        for l2_label, l2_kw in l2s.items():
            if l2_kw and l2_kw in text.lower().replace(" ", ""):
                return (l1_label, l2_label)

    # Final fallback
    return ("行业服务", "行业媒体")


def normalize_region(val: str) -> str:
    """Unify region to '国内' or '海外'"""
    if not val:
        return "国内"
    val = str(val).strip().lower()
    if val in ("overseas", "海外", "us", "usa", "united states", "uk", "japan", "jpn",
               "germany", "france", "canada", "australia", "israel", "singapore", "sweden",
               "switzerland", "netherlands", "korea", "south korea"):
        return "海外"
    return "国内"


def normalize_funding(funding_info: dict) -> tuple:
    """Extract standardized (funding_latest, funding_total) from various formats"""
    if not funding_info or not isinstance(funding_info, dict):
        return None, None

    latest = {}
    total = {}

    date = (funding_info.get("date") or funding_info.get("latest_date") or
            funding_info.get("latest_date_display"))
    amount = (funding_info.get("amount") or funding_info.get("latest_amount") or
              funding_info.get("latest_amount_display"))
    round_ = (funding_info.get("round") or funding_info.get("latest_round"))
    total_amt = (funding_info.get("total_amount") or funding_info.get("total_amount_display"))

    if date:
        latest["date"] = str(date)
    if amount:
        latest["amount"] = str(amount)
    if round_:
        latest["round"] = str(round_)

    if total_amt:
        total["amount"] = str(total_amt)

    parts = []
    if latest.get("round"):
        parts.append(latest["round"])
    if latest.get("amount"):
        parts.append(latest["amount"])
    if latest.get("date"):
        parts.append(f"({latest['date']})")
    if parts:
        latest["display"] = " ".join(parts)

    if total.get("amount"):
        total["display"] = f"累计{total['amount']}"

    return (latest if latest else None, total if total else None)


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_name_key(name: str) -> str:
    """Standardize name for dedup"""
    if not name:
        return ""
    key = name.lower().strip()
    key = re.sub(r'[^\w\s]', '', key)
    key = re.sub(r'\s+', '', key)
    for suffix in ['inc', 'llc', 'ltd', 'corp', 'co', 'limited', 'corporation',
                   'company', 'group', 'plc', 'ag', 'gmbh', 'sa', 'sas']:
        key = re.sub(rf'\b{suffix}\b', '', key)
    key = key.strip()
    return key


def build_new_item(name, region, cat_l1, cat_l2, description, funding_info,
                   investors=None, source="", source_url=None,
                   founded=None, tags=None, highlights=None):
    """Build a standardized enterprise item with the new schema."""
    fund_latest, fund_total = normalize_funding(funding_info or {})
    return {
        "serial": None,
        "name": name,
        "region": region,
        "category_l1": cat_l1,
        "category_l2": cat_l2,
        "tags": tags or [],
        "description": (description or "")[:200],
        "highlights": highlights or "",
        "funding_latest": fund_latest,
        "funding_total": fund_total,
        "investors": investors,
        "founded": founded,
        "value_score": None,
        "source": source,
        "crunchbase_url": None,
        "website_url": source_url,
    }


def merge_all():
    print("=" * 60)
    print("企业数据四源融合 v3 (13类 schema)")
    print("=" * 60)

    # 1. Load sources
    existing = load_json(DATA_DIR / "all_enterprises.json")
    stage_book = load_json(DATA_DIR / "stage_book_companies.json")
    xlsx_data = load_json(DATA_DIR / "xlsx_companies.json")
    mapping_data = load_json(DATA_DIR / "mapping_companies.json")

    print(f"\n加载数据源:")
    print(f"  现有企业库: {len(existing)} 条")
    print(f"  Stage书籍:  {len(stage_book)} 条")
    print(f"  选题库V4:    {len(xlsx_data)} 条")
    print(f"  中国mapping: {len(mapping_data)} 条")

    # 2. Dedup indices
    seen_keys = set()
    seen_names_cn = set()
    merged = []

    # 3. Process existing enterprises
    for item in existing:
        name = item.get("name", "")
        key = extract_name_key(name)
        if key:
            seen_keys.add(key)
        name_cn = item.get("name_cn", "")
        if name_cn:
            seen_names_cn.add(name_cn.lower().strip())

        # Determine display name: prefer Chinese if available, else English
        display_name = name_cn or name

        cat_raw = item.get("category_raw") or item.get("category", "")
        l1, l2 = classify_enterprise(cat_raw)

        region = normalize_region(item.get("region", ""))

        # Funding from old schema
        old_funding = item.get("funding", {})
        if isinstance(old_funding, dict):
            fund_latest, fund_total = normalize_funding(old_funding)
        else:
            fund_latest, fund_total = None, None

        investors = item.get("investors") or (old_funding.get("investors") if isinstance(old_funding, dict) else None)
        source_url = item.get("url") or item.get("source_url")

        new_item = build_new_item(
            name=display_name,
            region=region,
            cat_l1=l1,
            cat_l2=l2,
            description=item.get("description") or item.get("business_summary", ""),
            funding_info=old_funding,
            investors=investors,
            source=item.get("source") or "选题库",
            source_url=source_url,
        )
        # Preserve existing highlights if present
        if item.get("highlights"):
            new_item["highlights"] = item["highlights"]
        merged.append(new_item)

    print(f"\n现有企业库已转换: {len(merged)} 条")

    # 4. Merge Stage book
    stage_added = 0
    stage_skipped = 0
    for item in stage_book:
        name = item.get("name", "")
        key = extract_name_key(name)
        if key and key in seen_keys:
            stage_skipped += 1
            continue
        if key:
            seen_keys.add(key)
        name_cn = item.get("name_cn", "")
        if name_cn and name_cn.lower().strip() in seen_names_cn:
            stage_skipped += 1
            continue
        if name_cn:
            seen_names_cn.add(name_cn.lower().strip())

        display_name = name_cn or name
        cat_raw = item.get("category_raw", "")
        l1, l2 = classify_enterprise(cat_raw)

        new_item = build_new_item(
            name=display_name,
            region="海外",
            cat_l1=l1,
            cat_l2=l2,
            description=item.get("description", ""),
            funding_info=item.get("funding_info", {}),
            source="Stage(not Age)书籍",
        )
        merged.append(new_item)
        stage_added += 1

    print(f"Stage书籍: 新增 {stage_added}, 去重跳过 {stage_skipped}")

    # 5. Merge 选题库V4
    xlsx_added = 0
    xlsx_skipped = 0
    for item in xlsx_data:
        name = item.get("name", "")
        key = extract_name_key(name)
        if key and key in seen_keys:
            xlsx_skipped += 1
            continue
        if key:
            seen_keys.add(key)
        name_cn = item.get("name_cn", "")
        if name_cn and name_cn.lower().strip() in seen_names_cn:
            xlsx_skipped += 1
            continue
        if name_cn:
            seen_names_cn.add(name_cn.lower().strip())

        display_name = name_cn or name
        cat_raw = item.get("category_raw", "")
        l1, l2 = classify_enterprise(cat_raw)
        region = normalize_region(item.get("region", ""))

        new_item = build_new_item(
            name=display_name,
            region=region,
            cat_l1=l1,
            cat_l2=l2,
            description=item.get("description", ""),
            funding_info=item.get("funding_info", {}),
            source="选题库V4",
        )
        merged.append(new_item)
        xlsx_added += 1

    print(f"选题库V4: 新增 {xlsx_added}, 去重跳过 {xlsx_skipped}")

    # 6. Merge 中国mapping
    map_added = 0
    map_skipped = 0
    for item in mapping_data:
        name = item.get("name", "")
        key = extract_name_key(name)
        if key and key in seen_keys:
            map_skipped += 1
            continue
        if key:
            seen_keys.add(key)
        name_cn = item.get("name_cn", "")
        if name_cn and name_cn.lower().strip() in seen_names_cn:
            map_skipped += 1
            continue
        if name_cn:
            seen_names_cn.add(name_cn.lower().strip())

        display_name = name_cn or name
        cat_raw = item.get("category_raw", "")
        l1, l2 = classify_enterprise(cat_raw)
        region = normalize_region(item.get("region", ""))

        new_item = build_new_item(
            name=display_name,
            region=region,
            cat_l1=l1,
            cat_l2=l2,
            description=item.get("description", ""),
            funding_info=item.get("funding_info", {}),
            source="中国银发经济行业mapping",
        )
        merged.append(new_item)
        map_added += 1

    print(f"中国mapping: 新增 {map_added}, 去重跳过 {map_skipped}")

    # 7. Serial numbering: domestic first, then overseas
    domestic = [item for item in merged if item["region"] == "国内"]
    overseas = [item for item in merged if item["region"] == "海外"]
    ordered = domestic + overseas
    for i, item in enumerate(ordered, 1):
        item["serial"] = f"#{i:04d}"

    # 8. Stats
    total = len(ordered)
    d_count = len(domestic)
    o_count = len(overseas)

    cat_dist = {}
    for item in ordered:
        l1 = item["category_l1"]
        cat_dist[l1] = cat_dist.get(l1, 0) + 1

    print(f"\n{'=' * 60}")
    print(f"融合完成!")
    print(f"  总计: {total} 家企业")
    print(f"  国内: {d_count} 家")
    print(f"  海外: {o_count} 家")
    print(f"\n分类分布:")
    for l1_label in ENTERPRISE_CATEGORIES.keys():
        count = cat_dist.get(l1_label, 0)
        print(f"  {l1_label}: {count}")

    # 9. Save
    save_json(DATA_DIR / "all_enterprises.json", ordered)
    print(f"\n已保存到: {DATA_DIR / 'all_enterprises.json'}")

    return ordered


if __name__ == "__main__":
    merge_all()
