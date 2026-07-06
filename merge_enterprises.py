"""
融合三源数据 → all_enterprises.json
1. 现有 494 家（111 海外 + 383 国内）
2. Market Map 322 家（海外，URL域名推断名称）
3. 书籍深度 14 家（ElliQ/Papa/Intuition Robotics等，有丰富上下文）

策略：
- 名称标准化（lowercase + remove spaces/special chars）做模糊匹配去重
- Market Map 新企业 → 添加为新记录，region=overseas, category_raw=Market Map subcat, category_mapped=12类映射
- 书籍深度信息 → 补充到已有企业的 description 字段
- 为新企业分配 id（从 max_id+1 开始）
"""
import json
import re
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "enterprise")

# === Market Map subcat → 12-category mapping (from extract_agetech_map.py) ===
CATEGORY_MAPPING = {
    "RPM": "智慧养老/AI/数字疗法",
    "Resident Engagement": "智慧养老/AI/数字疗法",
    "Smart Home": "智慧养老/AI/数字疗法",
    "Rehabilitation": "康复设备",
    "PERS": "智慧养老/AI/数字疗法",
    "Wearables": "智慧养老/AI/数字疗法",
    "Operations": "智慧养老/AI/数字疗法",
    "Medication Management": "健康服务/医疗",
    "Fall Prevention & Detection": "康复设备",
    "Retirement 2.0": "养老地产/居住",
    "Fitness Wellness Monitoring": "健康服务/医疗",
    "Insurtech": "保险科技/金融",
    "Everyday assistance": "养老用品",
    "Tech training": "养老用品",
    "Finance": "保险科技/金融",
    "Transportation": "养老用品",
    "Assistive Tech": "养老用品",
    "Scam & fraud protection": "保险科技/金融",
    "Cognitive Care": "认知症",
    "For Caregivers": "养老服务/护理",
    "Companionship & Communication": "老年文娱/社交",
    "Tech-Enabled Home Care": "养老服务/护理",
    "For Healthcare Providers": "健康服务/医疗",
    "Housing": "养老地产/居住",
    "End of Life Planning": "健康服务/医疗",
    "Legacy / For Adult Day": "老年文娱/社交",
}


def normalize_name(name):
    """Normalize company name for fuzzy matching: lowercase, remove spaces/special chars."""
    if not name:
        return ''
    s = name.lower().strip()
    # Remove common suffixes
    for suffix in [' inc', ' llc', ' ltd', ' corp', ' co', ' ltd.', ' inc.',
                   ' company', ' corporation', ' limited', ' gmbh', ' pty']:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    # Remove all non-alphanumeric
    s = re.sub(r'[^a-z0-9]', '', s)
    return s


def build_dedup_index(enterprises):
    """Build a lookup index: normalized_name -> enterprise index."""
    index = {}
    for i, e in enumerate(enterprises):
        key = normalize_name(e.get('name', ''))
        if key:
            if key in index:
                # Collision - keep the first one but note the duplicate
                pass
            else:
                index[key] = i
    return index


def load_data():
    """Load all three data sources."""
    # 1. Existing enterprises
    with open(os.path.join(DATA_DIR, 'all_enterprises.json'), 'r', encoding='utf-8') as f:
        existing = json.load(f)

    # 2. Market Map raw data
    with open(os.path.join(DATA_DIR, 'agetech_map_raw.json'), 'r', encoding='utf-8') as f:
        map_raw = json.load(f)

    # 3. Book deep info
    with open(os.path.join(DATA_DIR, 'book_deep_info.json'), 'r', encoding='utf-8') as f:
        book_info = json.load(f)

    return existing, map_raw, book_info


def merge_book_info(enterprises, book_info):
    """Merge book deep info into existing enterprises."""
    book_matched = 0
    book_added = 0

    # Build index of existing enterprises
    dedup_index = build_dedup_index(enterprises)

    for book_entry in book_info:
        name = book_entry['name']
        norm_key = normalize_name(name)

        # Try to find in existing enterprises
        match_idx = dedup_index.get(norm_key)

        # Also try alternative names
        if match_idx is None:
            # Try common variations
            alt_names = []
            if name == 'UpsideHom':
                alt_names = ['UpsideHōM', 'UpsideHom', 'Upside']
            elif name == 'OATS':
                alt_names = ['Older Adults Technology Services', 'OATS']
            elif name == 'Apple':
                alt_names = ['Apple']
            elif name == 'AARP':
                alt_names = ['AARP', 'AARP Innovation Labs', 'AARP Innovation Labs / AgeTech Collaborative']
            elif name == 'Elder':
                alt_names = ['Elder', 'Elder.com']
            elif name == 'Aging2.0':
                alt_names = ['Aging2.0 Collective', 'Aging2.0']
            elif name == 'Uber':
                alt_names = ['Uber Health']
            elif name == 'Via':
                alt_names = ['Via']

            for alt in alt_names:
                alt_key = normalize_name(alt)
                if alt_key in dedup_index:
                    match_idx = dedup_index[alt_key]
                    break

        if match_idx is not None:
            # Update existing entry with book info
            e = enterprises[match_idx]
            if book_entry.get('description') and not e.get('description'):
                e['description'] = book_entry['description']
            elif book_entry.get('description') and len(book_entry['description']) > len(e.get('description', '')):
                # Use the longer/more detailed description
                e['description'] = book_entry['description']

            # Add book-specific fields
            if book_entry.get('founder'):
                e['founder'] = book_entry['founder']
            if book_entry.get('founding_year'):
                e['founding_year'] = book_entry['founding_year']
            if book_entry.get('funding'):
                e['book_funding_mention'] = book_entry['funding']

            # Add source tag
            sources = e.get('source', '')
            if 'AgeTech Revolution Book' not in sources:
                e['source'] = f"{sources} + AgeTech Revolution Book" if sources else "AgeTech Revolution Book"

            # Add book mention count
            e['book_mentions'] = book_entry['mention_count']

            # Store key contexts for reference
            if book_entry.get('key_contexts'):
                e['book_context'] = book_entry['key_contexts'][0][:500]

            book_matched += 1
            print(f"  [Book→Existing] {name} matched: {e['name']}")
        else:
            # Add as new enterprise from book
            max_id = max([int(e.get('id', 0)) for e in enterprises if str(e.get('id', '')).isdigit()], default=0) if enterprises else 0
            max_id = max(max_id, len(enterprises))  # Ensure uniqueness
            new_e = {
                'id': max_id + 1,
                'name': name,
                'category': '智慧养老/AI/数字疗法',  # Default, will be refined later
                'category_raw': 'AgeTech Revolution Book',
                'category_mapped': '智慧养老/AI/数字疗法',
                'priority': 'P2',
                'funding': '',
                'business_summary': book_entry.get('description', '')[:300],
                'domestic_coverage': '',
                'suggestion': '',
                'tags': ['book-featured'],
                'region': 'overseas',
                'description': book_entry.get('description', ''),
                'source': 'AgeTech Revolution Book',
                'book_mentions': book_entry['mention_count'],
            }
            if book_entry.get('founder'):
                new_e['founder'] = book_entry['founder']
            if book_entry.get('founding_year'):
                new_e['founding_year'] = book_entry['founding_year']
            if book_entry.get('location'):
                new_e['location'] = book_entry['location']

            enterprises.append(new_e)
            # Update dedup index
            dedup_index[norm_key] = len(enterprises) - 1
            book_added += 1
            print(f"  [Book→New] {name} added (mentions: {book_entry['mention_count']})")

    print(f"\nBook info: {book_matched} matched existing, {book_added} added new")
    return enterprises


def merge_market_map(enterprises, map_raw):
    """Merge Market Map companies into existing enterprises."""
    map_matched = 0
    map_added = 0

    # Build fresh dedup index
    dedup_index = build_dedup_index(enterprises)

    for map_entry in map_raw:
        name = map_entry.get('name', '')
        norm_key = normalize_name(name)

        if not norm_key:
            continue

        # Check for duplicates
        match_idx = dedup_index.get(norm_key)

        # Also check URL domain as alternative match
        if match_idx is None and map_entry.get('url'):
            domain = map_entry['url'].replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
            domain_key = normalize_name(domain.split('.')[0]) if '.' in domain else ''
            if domain_key and domain_key in dedup_index:
                match_idx = dedup_index[domain_key]

        if match_idx is not None:
            # Update existing entry with Market Map category info
            e = enterprises[match_idx]

            # Add Market Map category if not present
            map_subcat = map_entry.get('category_raw', '')
            if map_subcat and not e.get('category_raw'):
                e['category_raw'] = map_subcat
                e['category_mapped'] = CATEGORY_MAPPING.get(map_subcat, '其他')

            # Add source tag
            sources = e.get('source', '')
            if 'Market Map' not in sources:
                e['source'] = f"{sources} + Market Map" if sources else "Market Map"

            # Add URL if not present
            if map_entry.get('url') and not e.get('url'):
                e['url'] = map_entry['url']

            map_matched += 1
        else:
            # Add as new enterprise from Market Map
            max_id = max([int(e.get('id', 0)) for e in enterprises if str(e.get('id', '')).isdigit()], default=0) if enterprises else 0
            max_id = max(max_id, len(enterprises))  # Ensure uniqueness
            map_subcat = map_entry.get('category_raw', '')
            category_mapped = CATEGORY_MAPPING.get(map_subcat, '其他')

            new_e = {
                'id': max_id + 1,
                'name': name,
                'category': category_mapped,
                'category_raw': map_subcat,
                'category_mapped': category_mapped,
                'priority': 'P2',
                'funding': '',
                'business_summary': '',
                'domestic_coverage': '',
                'suggestion': '',
                'tags': ['market-map-2025'],
                'region': 'overseas',
                'description': '',
                'source': 'Market Map 2025',
                'url': map_entry.get('url', ''),
            }
            enterprises.append(new_e)
            dedup_index[norm_key] = len(enterprises) - 1
            map_added += 1

    print(f"Market Map: {map_matched} matched existing, {map_added} added new")
    return enterprises


def verify_regions(enterprises):
    """Ensure all enterprises have a valid region."""
    for e in enterprises:
        region = e.get('region', '')
        # Normalize region values
        if region in ('china', '国内', 'domestic'):
            e['region'] = '国内'
        elif region in ('overseas', '海外'):
            e['region'] = '海外'
        elif not region:
            # Infer from source
            source = e.get('source', '')
            if '中国企业图谱' in source or '许之怿' in source:
                e['region'] = '国内'
            elif 'Stage' in source or 'Market Map' in source or 'Book' in source:
                e['region'] = '海外'
            else:
                # Check if name is Chinese
                if re.search(r'[\u4e00-\u9fff]', e.get('name', '')):
                    e['region'] = '国内'
                else:
                    e['region'] = '海外'
    return enterprises


def main():
    print("=" * 60)
    print("Fusing three data sources into all_enterprises.json")
    print("=" * 60)

    # Load all data
    existing, map_raw, book_info = load_data()
    print(f"\nLoaded: {len(existing)} existing, {len(map_raw)} Market Map, {len(book_info)} book deep info")

    # Step 1: Merge book info into existing
    print("\n--- Step 1: Merge Book Deep Info ---")
    enterprises = merge_book_info(existing, book_info)
    print(f"Total after book merge: {len(enterprises)}")

    # Step 2: Merge Market Map companies
    print("\n--- Step 2: Merge Market Map Companies ---")
    enterprises = merge_market_map(enterprises, map_raw)
    print(f"Total after Market Map merge: {len(enterprises)}")

    # Step 3: Verify regions
    print("\n--- Step 3: Verify Regions ---")
    enterprises = verify_regions(enterprises)

    # Stats
    overseas = sum(1 for e in enterprises if e.get('region') == 'overseas')
    domestic = sum(1 for e in enterprises if e.get('region') == '国内')
    print(f"Final: {len(enterprises)} total ({overseas} overseas + {domestic} domestic)")

    # Category distribution
    cat_dist = {}
    for e in enterprises:
        cat = e.get('category_mapped') or e.get('category', '未分类')
        cat_dist[cat] = cat_dist.get(cat, 0) + 1
    print("\nCategory distribution:")
    for cat, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Priority distribution
    pri_dist = {}
    for e in enterprises:
        pri = e.get('priority', 'P2')
        pri_dist[pri] = pri_dist.get(pri, 0) + 1
    print("\nPriority distribution:")
    for pri, count in sorted(pri_dist.items()):
        print(f"  {pri}: {count}")

    # Save
    output_path = os.path.join(DATA_DIR, 'all_enterprises.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == '__main__':
    main()
