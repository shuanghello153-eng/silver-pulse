#!/usr/bin/env python3
"""
merge_v2.py — 企业数据四源融合（v2）
来源：现有796家 + Stage书籍108家 + 选题库V4 504条 + 中国mapping 374家
输出：统一16字段schema的all_enterprises.json
"""

import json
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "enterprise"

# ============================================================
# 15类分类映射（编码01-15）
# ============================================================
CATEGORY_MAP = {
    # 01 购物渠道/平台
    "01": {
        "label": "购物渠道/平台",
        "keywords": ["渠道", "电商", "购物", "零售", "线上渠道", "线下渠道", "电视购物",
                     "会员营销", "私域", "团购", "连锁", "药店", "特许经营",
                     "retail", "ecommerce", "marketplace", "channel", "platform",
                     "shopping", "采购", "批发"]
    },
    # 02 日常用品/消费
    "02": {
        "label": "日常用品/消费",
        "keywords": ["鞋", "服饰", "护肤", "染发", "假发", "纸尿裤", "成人失禁",
                     "成人纸尿裤", "日用品", "日常用品", "消费品牌", "个护", "洗浴",
                     "consumer", "apparel", "footwear", "skincare",
                     "everyday", "daily", "personal care", "hygiene",
                     "beauty", "cosmetic", "fashion", "染发剂"]
    },
    # 03 健康食品/营养
    "03": {
        "label": "健康食品/营养",
        "keywords": ["保健品", "OTC", "中药", "养生", "益生菌", "小分子肽",
                     "特医食品", "蛋白粉", "无糖", "低GI", "羊奶", "代工厂",
                     "健康食品", "营养", "膳食", "食品", "supplement", "nutrition",
                     "food", "vitamin", "保健", "滋补", "食疗"]
    },
    # 04 老年文娱/社交
    "04": {
        "label": "老年文娱/社交",
        "keywords": ["旅游", "教育", "社交平台", "广场舞", "相亲", "健身",
                     "音乐", "再就业", "文娱", "直播", "内容", "社区",
                     "travel", "education", "social", "fitness", "dating",
                     "entertainment", "learning", "companionship", "communication",
                     "community", "leisure", "hobby", "creative", "content",
                     "legacy", "life story", "memory", "photo", "游戏",
                     "在线平台", "老人互助", "匹配服务", "综合平台", "数字化",
                     "数字平台", "会员制", "APP", "平台", "AI"]
    },
    # 05 健康服务/医疗
    "05": {
        "label": "健康服务/医疗",
        "keywords": ["健康服务", "慢病管理", "血压", "血糖", "睡眠监测",
                     "摔倒监测", "陪诊", "体检", "中医", "养生服务",
                     "health service", "chronic", "monitoring", "telehealth",
                     "wearable", "fall prevention", "fall detection", "rpm",
                     "remote patient", "medication", "scam", "fraud",
                     "medication management", "vital", "healthcare provider",
                     "medical", "clinic", "telemedicine", "远程医疗",
                     "scam protection", "fraud protection", "健康监测",
                     "慢病", "远程", "可穿戴", "防摔", "用药",
                     "服药管理", "AI健康教练", "糖尿病", "慢性肾病",
                     "眼动追踪", "数字健康", "数字疗法", "数字疗法/MSK",
                     "嵌入式健康", "MSK", "在线锻炼"]
    },
    # 06 适老化改造
    "06": {
        "label": "适老化改造",
        "keywords": ["适老", "改造", "智能养老", "智慧养老软件", "家居产品",
                     "供应链", "规划设计", "aging in place", "renovation", "smart home",
                     "home modification", "accessibility", "智能用品",
                     "resident engagement", "tech training", "digital literacy"]
    },
    # 07 行业服务/金融
    "07": {
        "label": "行业服务/金融",
        "keywords": ["行业媒体", "行业展会", "养老金融", "养老理财", "保险科技",
                     "insurtech", "wealth management", "retirement financial",
                     "exhibition", "conference", "行业资讯",
                     "annuity", "年金险", "养老金融产品",
                     "金融科技适老", "适老金融"]
    },
    # 08 养老地产/居住
    "08": {
        "label": "养老地产/居住",
        "keywords": ["养老地产", "地产", "CCRC", "养老院", "养老社区", "护理院",
                     "运营商", "养老公寓", "中介", "real estate", "senior housing",
                     "senior living", "nursing home", "housing",
                     "adult day", "adult day care", "居住", "社区养老",
                     "assisted living", "independent living"]
    },
    # 09 养老服务/护理
    "09": {
        "label": "养老服务/护理",
        "keywords": ["居家养老", "家政", "护理", "护工", "长护险", "助餐",
                     "助浴", "照护", "陪护", "院内陪护", "养老运营",
                     "home care", "caregiving", "nursing", "meal", "bathing",
                     "caregiver", "for caregivers", "everyday assistance",
                     "personal care", "日常照护", "养老服务",
                     "companion", "陪伴", "助洁"]
    },
    # 10 养老用品/辅具
    "10": {
        "label": "养老用品/辅具",
        "keywords": ["轮椅", "护理床", "拐杖", "助行器", "代步车", "假肢",
                     "洗澡", "坐便", "视觉", "听觉", "呼吸", "吞咽", "咀嚼",
                     "辅具", "养老用品", "assistive", "wheelchair", "mobility",
                     "hearing", "vision", "prosthetic", "助听", "助视",
                     "听力", "视力"]
    },
    # 11 康复设备/器械
    "11": {
        "label": "康复设备/器械",
        "keywords": ["康复", "运动康复", "手部康复", "外骨骼", "精神", "神经",
                     "肿瘤康复", "康复机器人", "设备", "器械",
                     "rehabilitation", "exoskeleton", "medical device",
                     "rehab", "physical therapy", "robot"]
    },
    # 12 失智老人/认知症
    "12": {
        "label": "失智老人/认知症",
        "keywords": ["失智", "认知症", "认知障碍", "阿尔茨海默", "痴呆",
                     "早筛", "认知训练", "认知产品", "脑健康",
                     "dementia", "Alzheimer", "cognitive", "brain health",
                     "memory care", "认知", "早期检测", "病情早筛",
                     "大脑训练", "脑科学"]
    },
    # 13 产业资本/投资
    "13": {
        "label": "产业资本/投资",
        "keywords": ["投资", "资本", "基金", "风投", "VC", "PE", "天使",
                     "上市公司", "投资机构", "venture", "capital", "investor",
                     "incubator", "accelerator", "孵化", "crunchbase",
                     "funding", "融资"]
    },
    # 14 临终关怀
    "14": {
        "label": "临终关怀",
        "keywords": ["临终", "安宁", "缓和医疗", "生命末期", "殡葬",
                     "hospice", "palliative", "end of life", "funeral",
                     "estate planning", "遗产", "遗嘱"]
    },
    # 15 出行/交通
    "15": {
        "label": "出行/交通",
        "keywords": ["出行", "交通", "配送", "代驾", "出行服务",
                     "transportation", "mobility service", "ride", "delivery",
                     "driving", "transport", "出行平台"]
    },
}


def classify_category(category_raw: str) -> tuple:
    """根据原始分类返回 (category_code, category_label)"""
    if not category_raw:
        return ("07", "行业服务/金融")  # 兜底

    text = category_raw.lower()
    # 按编码顺序遍历，先匹配到的优先
    # 注意：07（行业服务/金融）有"保险"等宽泛关键词，放后面检查
    # 但01-06, 08-15的关键词更具体，优先匹配
    for code in [f"{i:02d}" for i in range(1, 16)]:
        info = CATEGORY_MAP[code]
        for kw in info["keywords"]:
            if kw.lower() in text:
                return (code, info["label"])
    # 兜底
    return ("07", "行业服务/金融")


def normalize_region(val: str) -> str:
    """统一region为中文"""
    if not val:
        return "国内"
    val = str(val).strip().lower()
    if val in ("overseas", "海外", "us", "usa", "united states", "uk", "japan", "jpn",
               "germany", "france", "canada", "australia", "israel", "singapore", "sweden",
               "switzerland", "netherlands", "korea", "south korea"):
        return "海外"
    return "国内"


def normalize_funding(funding_info: dict) -> tuple:
    """从各种funding格式提取标准化 (funding_latest, funding_total)"""
    if not funding_info or not isinstance(funding_info, dict):
        return None, None

    latest = {}
    total = {}

    # 尝试多个字段名
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

    # display
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
    """提取名字的标准化key用于去重"""
    if not name:
        return ""
    # 小写、去空格、去特殊字符
    key = name.lower().strip()
    key = re.sub(r'[^\w\s]', '', key)
    key = re.sub(r'\s+', '', key)
    # 去掉常见后缀
    for suffix in ['inc', 'llc', 'ltd', 'corp', 'co', 'limited', 'corporation',
                   'company', 'group', 'plc', 'ag', 'gmbh', 'sa', 'sas']:
        key = re.sub(rf'\b{suffix}\b', '', key)
    key = key.strip()
    return key


def merge_all():
    print("=" * 60)
    print("企业数据四源融合 v2")
    print("=" * 60)

    # 1. 加载所有数据源
    existing = load_json(DATA_DIR / "all_enterprises.json")
    stage_book = load_json(DATA_DIR / "stage_book_companies.json")
    xlsx_data = load_json(DATA_DIR / "xlsx_companies.json")
    mapping_data = load_json(DATA_DIR / "mapping_companies.json")

    print(f"\n加载数据源:")
    print(f"  现有企业库: {len(existing)} 条")
    print(f"  Stage书籍:  {len(stage_book)} 条")
    print(f"  选题库V4:    {len(xlsx_data)} 条")
    print(f"  中国mapping: {len(mapping_data)} 条")

    # 2. 构建已存在企业的name索引（用于去重）
    seen_keys = set()
    seen_names_cn = set()
    merged = []

    # 3. 先处理现有企业（作为基础）
    for item in existing:
        name = item.get("name", "")
        key = extract_name_key(name)
        if key:
            seen_keys.add(key)

        name_cn = item.get("name_cn", "")
        if name_cn:
            seen_names_cn.add(name_cn.lower().strip())

        # 转换旧schema
        cat_raw = item.get("category_raw") or item.get("category", "")
        cat_code, cat_label = classify_category(cat_raw)

        # region
        region_raw = item.get("region", "")
        region = normalize_region(region_raw)

        # funding
        old_funding = item.get("funding", {})
        if isinstance(old_funding, dict):
            fund_latest, fund_total = normalize_funding(old_funding)
        else:
            fund_latest, fund_total = None, None

        # investors
        investors = item.get("investors") or (old_funding.get("investors") if isinstance(old_funding, dict) else None)

        new_item = {
            "serial": None,  # 稍后统一编号
            "name": name,
            "name_cn": item.get("name_cn") or item.get("name_cn"),
            "region": region,
            "region_code": 1 if region == "国内" else 2,
            "category": cat_raw,
            "category_code": cat_code,
            "category_label": cat_label,
            "description": item.get("description") or item.get("business_summary", ""),
            "funding_latest": fund_latest,
            "funding_total": fund_total,
            "investors": investors,
            "source": item.get("source") or "选题库",
            "source_url": item.get("url") or item.get("source_url"),
            "value_score": None,
            "value_tier": None,
        }
        merged.append(new_item)

    print(f"\n现有企业库已转换: {len(merged)} 条")

    # 4. 合并Stage书籍企业
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

        cat_raw = item.get("category_raw", "")
        cat_code, cat_label = classify_category(cat_raw)
        fund_latest, fund_total = normalize_funding(item.get("funding_info", {}))

        new_item = {
            "serial": None,
            "name": name,
            "name_cn": name_cn,
            "region": "海外",
            "region_code": 2,
            "category": cat_raw,
            "category_code": cat_code,
            "category_label": cat_label,
            "description": (item.get("description") or "")[:80],
            "funding_latest": fund_latest,
            "funding_total": fund_total,
            "investors": None,
            "source": "Stage(not Age)书籍",
            "source_url": None,
            "value_score": None,
            "value_tier": None,
        }
        merged.append(new_item)
        stage_added += 1

    print(f"Stage书籍: 新增 {stage_added}, 去重跳过 {stage_skipped}")

    # 5. 合并选题库V4企业
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

        cat_raw = item.get("category_raw", "")
        cat_code, cat_label = classify_category(cat_raw)
        fund_latest, fund_total = normalize_funding(item.get("funding_info", {}))
        region = normalize_region(item.get("region", ""))

        new_item = {
            "serial": None,
            "name": name,
            "name_cn": name_cn,
            "region": region,
            "region_code": 1 if region == "国内" else 2,
            "category": cat_raw,
            "category_code": cat_code,
            "category_label": cat_label,
            "description": (item.get("description") or "")[:80],
            "funding_latest": fund_latest,
            "funding_total": fund_total,
            "investors": None,
            "source": "选题库V4",
            "source_url": None,
            "value_score": None,
            "value_tier": None,
        }
        merged.append(new_item)
        xlsx_added += 1

    print(f"选题库V4: 新增 {xlsx_added}, 去重跳过 {xlsx_skipped}")

    # 6. 合并中国mapping企业
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

        cat_raw = item.get("category_raw", "")
        cat_code, cat_label = classify_category(cat_raw)
        fund_latest, fund_total = normalize_funding(item.get("funding_info", {}))
        region = normalize_region(item.get("region", ""))

        new_item = {
            "serial": None,
            "name": name,
            "name_cn": name_cn or name,
            "region": region,
            "region_code": 1 if region == "国内" else 2,
            "category": cat_raw,
            "category_code": cat_code,
            "category_label": cat_label,
            "description": (item.get("description") or "")[:80],
            "funding_latest": fund_latest,
            "funding_total": fund_total,
            "investors": None,
            "source": "中国银发经济行业mapping",
            "source_url": None,
            "value_score": None,
            "value_tier": None,
        }
        merged.append(new_item)
        map_added += 1

    print(f"中国mapping: 新增 {map_added}, 去重跳过 {map_skipped}")

    # 7. 统一编号（先国内后海外，每个区域内按原始顺序）
    domestic = [item for item in merged if item["region"] == "国内"]
    overseas = [item for item in merged if item["region"] == "海外"]

    # 国内排前，海外排后
    ordered = domestic + overseas
    for i, item in enumerate(ordered, 1):
        item["serial"] = f"#{i:04d}"

    # 8. 统计
    total = len(ordered)
    d_count = len(domestic)
    o_count = len(overseas)

    # 分类分布
    cat_dist = {}
    for item in ordered:
        cl = item["category_label"]
        cat_dist[cl] = cat_dist.get(cl, 0) + 1

    print(f"\n" + "=" * 60)
    print(f"融合完成!")
    print(f"  总计: {total} 家企业")
    print(f"  国内: {d_count} 家")
    print(f"  海外: {o_count} 家")
    print(f"\n分类分布:")
    for code in [f"{i:02d}" for i in range(1, 16)]:
        label = CATEGORY_MAP[code]["label"]
        count = cat_dist.get(label, 0)
        print(f"  {code} {label}: {count}")

    # 9. 保存
    save_json(DATA_DIR / "all_enterprises.json", ordered)
    print(f"\n已保存到: {DATA_DIR / 'all_enterprises.json'}")

    return ordered


if __name__ == "__main__":
    merge_all()
