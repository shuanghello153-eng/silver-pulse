#!/usr/bin/env python3
"""
add_crunchbase_links.py — 为所有企业自动生成Crunchbase搜索链接

策略：
- 所有企业都生成 Crunchbase 搜索URL: https://www.crunchbase.com/textsearch?q=<company_name>
- 海外企业用英文名搜索（Crunchbase主要是英文数据库）
- 国内企业也生成搜索链接，用户可用于校验是否有Crunchbase记录
- URL编码企业名称以处理特殊字符
"""
import json
import os
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "enterprise")


def make_crunchbase_url(name):
    """Generate a Crunchbase search URL for a company name."""
    if not name:
        return None
    # URL encode the company name
    encoded = urllib.parse.quote(name)
    return f"https://www.crunchbase.com/textsearch?q={encoded}"


def main():
    path = os.path.join(DATA_DIR, "all_enterprises.json")
    with open(path, "r", encoding="utf-8") as f:
        enterprises = json.load(f)

    total = len(enterprises)
    added = 0
    skipped = 0

    for ent in enterprises:
        name = ent.get("name", "")
        existing_cb = ent.get("crunchbase_url")

        if existing_cb and isinstance(existing_cb, str) and existing_cb.strip():
            # Already has a real Crunchbase URL, keep it
            skipped += 1
        else:
            # Generate search URL
            url = make_crunchbase_url(name)
            if url:
                ent["crunchbase_url"] = url
                added += 1

    # Write back
    with open(path, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"Total enterprises: {total}")
    print(f"Crunchbase search URLs added: {added}")
    print(f"Already had real URL (skipped): {skipped}")

    # Print samples
    print("\n--- Sample (first 5 overseas) ---")
    count = 0
    for ent in enterprises:
        if ent.get("region") == "海外":
            print(f"  {ent['name']}: {ent.get('crunchbase_url', 'N/A')}")
            count += 1
            if count >= 5:
                break

    print("\n--- Sample (first 5 domestic) ---")
    count = 0
    for ent in enterprises:
        if ent.get("region") == "国内":
            print(f"  {ent['name']}: {ent.get('crunchbase_url', 'N/A')}")
            count += 1
            if count >= 5:
                break

    # Final coverage
    has_cb = sum(1 for e in enterprises if e.get("crunchbase_url"))
    print(f"\nFinal crunchbase_url coverage: {has_cb}/{total} ({has_cb*100//total}%)")


if __name__ == "__main__":
    main()
