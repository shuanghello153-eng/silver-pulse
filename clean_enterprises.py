#!/usr/bin/env python
"""Clean and enhance enterprise data from raw extraction.

Phase 1: Remove noise (channels, sources, non-enterprise entries)
Phase 2: Fix categories based on section context
Phase 3: Add manually curated top enterprises from structured sections
"""

import json
import re
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "enterprise")
RAW_PATH = os.path.join(DATA_DIR, "enterprises_raw.json")
CLEAN_PATH = os.path.join(DATA_DIR, "enterprises_clean.json")


# ── Noise filter ───────────────────────────────────────────────

NOISE_NAMES = {
    # Information channels (not enterprises)
    "agetech", "startuphealth", "crunchbase", "mobihealthnews",
    "fiercehealthcare", "thegerontechnologist", "mcknightsseniorliving",
    "homehealthcare news", "homecare", "mcknights", "inc",
    "agetechcollaborative", "maryfurlong", "ageclub",
    "humana", "cvs health ventures", "aarp",
    # Generic/ambiguous entries
    "ai", "大型养老", "老年护理", "居家养老", "认知症",
    "护理员支持", "陪伴服务类", "数字化工具", "健康管理",
    "疾病预测筛查", "sdoh", "收入周期管理", "远程营养",
    "老年食品", "无障碍旅游", "租房", "就业",
    "金融理财", "b2c内容", "tob", "tob不太热门",
}

# Also filter entries whose name is too short or too generic
def is_noise(name):
    name_lower = name.lower().strip()
    if name_lower in NOISE_NAMES:
        return True
    if len(name_lower) < 3:
        return True
    # Filter names that are just Chinese category labels
    if re.match(r"^[\u4e00-\u9fff]{2,6}$", name) and not any(
        kw in name for kw in ["科技", "健康", "养老", "护理", "康养", "食品", "医药", "陪诊"]
    ):
        return True
    return False


# ── Category fixer ─────────────────────────────────────────────

CATEGORY_MAP = {
    # Map raw_text keywords to proper categories
    "居家护理": "居家养老/护理",
    "上门护理": "居家养老/护理",
    "家庭护理": "居家养老/护理",
    "home health": "居家养老/护理",
    "home care": "居家养老/护理",
    "PACE": "PACE全包护理",
    "pace": "PACE全包护理",
    "认知症": "认知症/痴呆症",
    "痴呆症": "认知症/痴呆症",
    "dementia": "认知症/痴呆症",
    "alzheimer": "认知症/痴呆症",
    "跌倒": "跌倒预防",
    "fall": "跌倒预防",
    "临终关怀": "临终关怀",
    "hospice": "临终关怀",
    "palliative": "临终关怀",
    "姑息": "临终关怀",
    "护理员": "护理员支持",
    "caregiver": "护理员支持",
    "陪伴": "社交陪伴",
    "loneliness": "社交陪伴",
    "孤独": "社交陪伴",
    "social": "社交陪伴",
    "金融": "金融理财",
    "fraud": "金融理财",
    "诈骗": "金融理财",
    "住房": "养老住房",
    "租房": "养老住房",
    "housing": "养老住房",
    "living": "养老住房",
    "employment": "老年就业",
    "就业": "老年就业",
    "更年期": "更年期健康",
    "menopause": "更年期健康",
    "营养": "营养/特医食品",
    "food": "营养/特医食品",
    "饮食": "营养/特医食品",
    "远程营养": "营养/特医食品",
    "尿失禁": "尿失禁/盆底健康",
    "incontinence": "尿失禁/盆底健康",
    "膀胱": "尿失禁/盆底健康",
    "心理健康": "心理健康",
    "mental health": "心理健康",
    "抑郁": "心理健康",
    "药物管理": "药物管理",
    "medication": "药物管理",
    "慢病": "慢病管理",
    "chronic": "慢病管理",
    "robotic": "机器人/自动化",
    "机器人": "机器人/自动化",
    "virtual care": "远程医疗",
    "telehealth": "远程医疗",
    "远程医疗": "远程医疗",
    "远程": "远程医疗",
    "platform": "数字化平台",
    "SaaS": "数字化平台",
    "insurance": "保险科技",
    "medicare": "保险科技",
    "medicaid": "保险科技",
    "保险": "保险科技",
    "旅游": "老年旅游",
    "travel": "老年旅游",
    "tourism": "老年旅游",
    "内容": "B2C内容→产品",
    "媒体": "B2C内容→产品",
    "收购": "收购/并购",
    "acquisition": "收购/并购",
    "merger": "收购/并购",
    "IPO": "上市/IPO",
    "上市": "上市/IPO",
    "RCM": "收入周期管理",
    "revenue cycle": "收入周期管理",
    "护理平台": "居家养老/护理",
    "陪诊": "陪诊/陪护",
}

def fix_category(ent):
    """Determine proper category from raw_text content."""
    raw = ent.get("raw_text_preview", "") or ""
    name = ent.get("name", "")

    # Check name and raw text for category keywords
    text = f"{name} {raw}".lower()

    for keyword, category in CATEGORY_MAP.items():
        if keyword.lower() in text:
            return category

    # Keep existing category if not "未分类"
    existing = ent.get("category", "未分类")
    if existing != "未分类":
        return existing

    return "未分类"


# ── Priority inference ─────────────────────────────────────────

def infer_priority(ent):
    """Infer priority from context clues if not explicitly set."""
    raw = ent.get("raw_text_preview", "") or ""

    # Explicit markers
    if "P0" in raw:
        return "P0"
    if "P1" in raw:
        return "P1"
    if "P2" in raw:
        return "P2"
    if "废弃" in raw or "不用看" in raw or "不考虑" in raw or "暂不考虑" in raw:
        return "废弃"
    if "已写" in raw or "可以写" in raw:
        return "已写/可写"

    # Infer from funding amount (large = higher priority)
    funding = ent.get("funding")
    if funding and funding.get("latest_amount"):
        amount = funding["latest_amount"]
        if amount >= 50_000_000:  # 5000万+
            return "P1"
        if amount >= 10_000_000:  # 1000万+
            return "P2"

    # Infer from domestic coverage mentions
    if any(kw in raw for kw in ["AgeClub", "微信无", "没有相关文章", "国内没有"]):
        return "P1"  # No domestic coverage = good differentiation opportunity

    if any(kw in raw for kw in ["已经有些文章", "国内已经", "流量", "阅读量"]):
        return "P2"  # Has domestic coverage = less differentiation

    return None  # Unknown


# ── Main processing ────────────────────────────────────────────

def main():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"Raw entries: {len(raw_data)}")

    # Phase 1: Remove noise
    clean = [e for e in raw_data if not is_noise(e["name"])]
    print(f"After noise removal: {len(clean)}")

    # Phase 2: Fix categories
    for e in clean:
        e["category"] = fix_category(e)

    # Phase 3: Infer priorities
    for e in clean:
        if not e.get("priority"):
            e["priority"] = infer_priority(e)

    # Phase 4: Clean up funding display
    for e in clean:
        funding = e.get("funding")
        if funding and funding.get("latest_amount"):
            amt = funding["latest_amount"]
            cur = funding.get("currency", "USD")
            if cur == "USD":
                if amt >= 1_000_000_000:
                    funding["latest_amount_display"] = f"{amt/1_000_000_000:.2f}亿美元"
                elif amt >= 10_000_000:
                    funding["latest_amount_display"] = f"{amt/10_000_000:.0f}千万美元"
                elif amt >= 1_000_000:
                    funding["latest_amount_display"] = f"{amt/1_000_000:.0f}百万美元"
                else:
                    funding["latest_amount_display"] = f"{amt:.0f}美元"
            elif cur == "CNY":
                if amt >= 1_000_000_000:
                    funding["latest_amount_display"] = f"{amt/1_000_000_000:.1f}亿人民币"
                else:
                    funding["latest_amount_display"] = f"{amt/10_000:.0f}万人民币"

    # Phase 5: Deduplicate by name
    seen = {}
    deduped = []
    for e in clean:
        name_key = e["name"].lower().strip()
        if name_key in seen:
            # Merge: keep the one with more data
            existing = seen[name_key]
            if e.get("funding") and not existing.get("funding"):
                deduped.remove(existing)
                deduped.append(e)
                seen[name_key] = e
            elif e.get("priority") and not existing.get("priority"):
                existing["priority"] = e["priority"]
            elif e.get("business_summary") and not existing.get("business_summary"):
                existing["business_summary"] = e["business_summary"]
        else:
            deduped.append(e)
            seen[name_key] = e

    print(f"After dedup: {len(deduped)}")

    # Statistics
    from collections import Counter
    cats = Counter(e["category"] for e in deduped)
    pris = Counter(e.get("priority") for e in deduped)
    funded = sum(1 for e in deduped if e.get("funding"))

    print("\nCategory distribution:")
    for cat, count in cats.most_common(10):
        print(f"  {cat}: {count}")

    print("\nPriority distribution:")
    for pri, count in pris.most_common():
        print(f"  {pri}: {count}")

    print(f"\nEnterprises with funding data: {funded}")

    # Re-index
    for i, e in enumerate(deduped):
        e["id"] = f"ent_{i+1:03d}"

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CLEAN_PATH, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(deduped)} clean enterprises to {CLEAN_PATH}")

    # Print top 15 by funding amount
    sorted_by_funding = sorted(
        [e for e in deduped if e.get("funding") and e["funding"].get("latest_amount")],
        key=lambda e: e["funding"]["latest_amount"],
        reverse=True
    )
    print("\n=== Top 15 by funding amount ===")
    for e in sorted_by_funding[:15]:
        print(f"  {e['name']} | {e['funding']['latest_amount_display']} | {e.get('priority','?')} | {e['category']}")


if __name__ == "__main__":
    main()
