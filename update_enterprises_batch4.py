#!/usr/bin/env python3
"""Batch 4: Update founded + website_url for 9 more companies."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "enterprise" / "all_enterprises.json"

UPDATES = {
    "Sonic Healthcare": {"founded": "1987", "website_url": "https://www.sonichealthcare.com"},
    "Labcorp": {"founded": "1969", "website_url": "https://www.labcorp.com"},
    "Heartland Dental": {"founded": "1997", "website_url": "https://heartland.com"},
    "Lifespace Communities": {"founded": "1976", "website_url": "https://www.lifespacecommunities.com"},
    "Discovery Senior Living": {"founded": "1991", "website_url": "https://discoveryseniorliving.com"},
    "Innovative Renal Care": {"website_url": "https://innovativerenal.com"},
    "全民K歌": {"founded": "2014", "website_url": "https://kg.qq.com"},
    "品驰医疗": {"founded": "2008", "website_url": "https://www.pinsmedical.com"},
    "互邦医疗": {"founded": "1990", "website_url": "http://www.hubang.net.cn"},
}

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        enterprises = json.load(f)
    
    updated = 0
    for ent in enterprises:
        name = ent.get("name", "")
        if name in UPDATES:
            for key, val in UPDATES[name].items():
                if not ent.get(key):
                    ent[key] = val
                    print(f"  {name}: {key} = {val}")
            updated += 1
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)
    
    print(f"\nUpdated {updated} enterprises.")

if __name__ == "__main__":
    main()
