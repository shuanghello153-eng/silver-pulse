#!/usr/bin/env python3
"""Batch 8: Update founded + website_url for more overseas companies (batch 4)."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "enterprise" / "all_enterprises.json"

UPDATES = {
    "Bioniq": {"founded": "2019", "website_url": "https://www.bioniq.com"},
    "Axle Health": {"founded": "2020", "website_url": "https://www.axlehealth.com"},
    "Arbital Health": {"founded": "2023", "website_url": "https://arbitalhealth.com"},
    "Brightside Health": {"founded": "2017", "website_url": "https://www.brightside.com"},
    "Bone Health Technologies": {"founded": "2018", "website_url": "https://www.bonehealthtech.com"},
    "Bloom Nutrition": {"founded": "2019", "website_url": "https://bloomnu.com"},
    "Bobbie": {"founded": "2018", "website_url": "https://www.hibobbie.com"},
    "After.com": {"founded": "2020", "website_url": "https://www.after.com"},
}

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        enterprises = json.load(f)
    
    updated = 0
    not_found = set(UPDATES.keys())
    
    for ent in enterprises:
        name = ent.get("name", "")
        if name in UPDATES:
            not_found.discard(name)
            for key, val in UPDATES[name].items():
                if not ent.get(key):
                    ent[key] = val
                    print(f"  {name}: {key} = {val}")
            updated += 1
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)
    
    print(f"\nUpdated {updated} enterprises.")
    if not_found:
        print(f"Not found in DB: {not_found}")

if __name__ == "__main__":
    main()
