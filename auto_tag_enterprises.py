"""Auto-generate tags for all enterprises based on existing data fields.
Tags are derived from category_l1, category_l2, description, highlights, funding info.
Uses TAG_POOL from config.py as the controlled vocabulary, plus auto-generated functional tags.
"""
import json
import re

DATA_FILE = "data/enterprise/all_enterprises.json"

# Tag keywords mapping - if any of these keywords appear in description/highlights/category,
# the corresponding tag is added
TAG_RULES = {
    # Capital signals - based on funding data
    "融资过亿": {
        "keywords": ["亿", "100M", "$100", "200M", "$200", "300M", "$300", "500M", "$500",
                      "billion", "B round", "C round", "D round", "Series E"],
        "check_funding": True,  # Also check if funding amount >= 1亿
    },
    "已被收购": {
        "keywords": ["被收购", "acquired by", "acquisition", "收购完成"],
        "check_desc": True,
    },
    "IPO上市": {
        "keywords": ["上市", "IPO", "listed on", "NYSE", "NASDAQ", "publicly traded", "went public"],
        "check_desc": True,
    },
    # Endorsement tags
    "YC孵化": {
        "keywords": ["Y Combinator", "YC ", "Y Combinator-backed"],
        "check_desc": True,
    },
    "政府支持": {
        "keywords": ["政府", "government", "CMS", "Medicare", "Medicaid", "NIH", "NHS", "公共财政"],
        "check_desc": True,
    },
    # Special markers
    "订阅制": {
        "keywords": ["subscription", "订阅", "monthly", "SaaS", "membership"],
        "check_desc": True,
    },
    "B2B2C": {
        "keywords": ["B2B2C", "B2B", "health plan", "employer", "payer", "保险合作"],
        "check_desc": True,
    },
    "硬件+服务": {
        "keywords": ["device", "wearable", "sensor", "硬件", "设备", "monitor", "硬件+服务"],
        "check_desc": True,
    },
    "模式创新": {
        "keywords": ["AI-powered", "AI-driven", "innovative", "first-of-its-kind", "novel"],
        "check_desc": True,
    },
    # Geographic tags for overseas
    "日本": {
        "keywords": ["Japan", "Japanese", "Tokyo", "日本", "东京"],
        "check_desc": True,
    },
    "以色列": {
        "keywords": ["Israel", "Israeli", "Tel Aviv", "以色列"],
        "check_desc": True,
    },
    "欧洲": {
        "keywords": ["UK", "British", "London", "Europe", "European", "German", "France", "Paris",
                      "Netherlands", "Swedish", "Sweden", "英国", "伦敦", "德国", "法国", "荷兰", "瑞典"],
        "check_desc": True,
    },
}

# Functional tags based on category_l2 mapping
FUNCTIONAL_TAG_MAP = {
    "居家护理": ["home care", "居家"],
    "远程医疗": ["telehealth", "telemedicine", "remote", "远程"],
    "慢病管理": ["chronic", "慢病", "diabetes", "糖尿病"],
    "认知症": ["dementia", "Alzheimer", "cognitive", "认知", "失智"],
    "摔倒监测": ["fall", "摔倒", "跌倒"],
    "睡眠监测": ["sleep", "睡眠"],
    "智慧养老": ["smart", "AI", "智能", "platform", "平台"],
    "适老化": ["accessibility", "适老", "aging-in-place", "home modification"],
    "金融理财": ["financial", "finance", "wealth", "retirement planning", "理财"],
    "老年文娱": ["entertainment", "social", "community", "文娱", "社交"],
}

def check_funding_amount(ent):
    """Check if funding indicates >= 1亿 RMB (~$14M USD)"""
    fl = ent.get('funding_latest') or {}
    ft = ent.get('funding_total') or {}

    for fund in [fl, ft]:
        if not isinstance(fund, dict):
            continue
        amount = fund.get('amount', '') or ''
        display = fund.get('display', '') or ''
        combined = f"{amount} {display}"

        # Check for 亿 (Chinese hundred million)
        if '亿' in combined:
            return True
        # Check for $14M+ or 100M+
        patterns = [r'\$(\d+)M', r'\$(\d+)B', r'(\d+)M\s', r'\$(\d+)\s*million']
        for p in patterns:
            match = re.search(p, combined, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if 'B' in p or num >= 100:
                    return True
    return False

def generate_tags(ent):
    """Generate tags for a single enterprise"""
    tags = []
    desc = (ent.get('description') or '').lower()
    highlights = (ent.get('highlights') or '').lower()
    cat_l1 = ent.get('category_l1') or ''
    cat_l2 = ent.get('category_l2') or ''
    text = f"{desc} {highlights} {cat_l1} {cat_l2}"

    # Apply TAG_RULES
    for tag_name, rule in TAG_RULES.items():
        keywords = rule.get('keywords', [])
        matched = False

        if rule.get('check_funding') and check_funding_amount(ent):
            matched = True

        if rule.get('check_desc', True):
            for kw in keywords:
                if kw.lower() in text:
                    matched = True
                    break

        if matched and tag_name not in tags:
            tags.append(tag_name)

    # Apply functional tags based on category_l2
    for func_tag, keywords in FUNCTIONAL_TAG_MAP.items():
        for kw in keywords:
            if kw.lower() in text:
                if func_tag not in tags:
                    tags.append(func_tag)
                break

    # Add category_l2 as a tag if it exists and is meaningful
    if cat_l2 and cat_l2 not in tags and len(cat_l2) <= 10:
        tags.append(cat_l2)

    # Limit to 5 tags max (per config.py TAG_POOL rule)
    return tags[:5]

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        enterprises = json.load(f)

    updated = 0
    total_tags = 0

    for ent in enterprises:
        existing_tags = ent.get('tags') or []
        if existing_tags:
            continue  # Skip if already has tags

        new_tags = generate_tags(ent)
        if new_tags:
            ent['tags'] = new_tags
            updated += 1
            total_tags += len(new_tags)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated} enterprises with tags")
    print(f"Total tags added: {total_tags}")
    print(f"Average tags per enterprise: {total_tags/updated:.1f}" if updated else "No updates")

    # Show sample
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        enterprises = json.load(f)
    print("\n--- Sample tags ---")
    for ent in enterprises[:10]:
        if ent.get('tags'):
            print(f"  {ent['name']}: {ent['tags']}")

if __name__ == "__main__":
    main()
