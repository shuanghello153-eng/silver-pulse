#!/usr/bin/env python3
"""Batch 7: Update founded + website_url for more overseas companies (batch 3)."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "enterprise" / "all_enterprises.json"

UPDATES = {
    "Birdie": {"founded": "2017", "website_url": "https://www.birdie.care"},
    "Beta Bionics": {"founded": "2015", "website_url": "https://www.betabionics.com"},
    "b.well Connected Health": {"founded": "2015", "website_url": "https://www.icanbwell.com"},
    "Author Health": {"founded": "2023", "website_url": "https://authorhealth.com"},
    "Auxa Health": {"founded": "2023", "website_url": "https://www.auxahealth.com"},
    "Better Health": {"founded": "2019", "website_url": "https://joinbetter.com"},
    "Alloy": {"founded": "2022", "website_url": "https://www.myalloy.com"},
    "Aktiia": {"founded": "2018", "website_url": "https://healthcare.aktiia.com"},
    "9amHealth": {"founded": "2021", "website_url": "https://9am.health"},
    "Age Bold": {"founded": "2020", "website_url": "https://www.agebold.com"},
    "Lifeway Mobility": {"founded": "2005", "website_url": "https://www.lifewaymobility.com"},
    "Artis Senior Living": {"founded": "2012", "website_url": "https://artisseniorliving.com"},
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
