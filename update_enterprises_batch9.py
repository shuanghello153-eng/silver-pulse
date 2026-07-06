#!/usr/bin/env python3
"""Batch 9: Update founded + website_url for more overseas companies (batch 5)."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "enterprise" / "all_enterprises.json"

UPDATES = {
    "Devoted Health": {"founded": "2017", "website_url": "https://www.devoted.com"},
    "Cityblock Health": {"founded": "2017", "website_url": "https://www.cityblock.com"},
    "Hello Heart": {"founded": "2013", "website_url": "https://www.helloheart.com"},
    "CVS Health": {"founded": "1963", "website_url": "https://www.cvshealth.com"},
    "GoodRx": {"founded": "2011", "website_url": "https://www.goodrx.com"},
    "DarioHealth": {"founded": "2011", "website_url": "https://www.dariohealth.com"},
    "Elektra Health": {"founded": "2019", "website_url": "https://www.elektrahealth.com"},
    "Headway": {"founded": "2019", "website_url": "https://headway.co"},
    "Hippocratic AI": {"founded": "2023", "website_url": "https://hippocraticai.com"},
    "Embr Labs": {"founded": "2014", "website_url": "https://embrlabs.com"},
    "Cerebral": {"founded": "2020", "website_url": "https://cerebral.com"},
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
