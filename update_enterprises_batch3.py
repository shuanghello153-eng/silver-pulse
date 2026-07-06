#!/usr/bin/env python3
"""
update_enterprises_batch3.py — Batch update founded + website_url (batch 3).
Overseas companies.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data/enterprise/all_enterprises.json")

updates = {
    # Overseas
    "Inspiren": {"founded": "2016", "website_url": "https://www.inspiren.com"},
    "Accompany Health": {"founded": "2022", "website_url": "https://www.accompanyhealth.com"},
    "Ageless Innovation": {"founded": "2018", "website_url": "https://agelessinnovation.com"},
    "BrightSpring": {"founded": "1974", "website_url": "https://www.brightspringhealth.com"},
    "Encompass Health": {"founded": "1984", "website_url": "https://www.encompasshealth.com"},
    "Gentiva": {"founded": "1999", "website_url": "https://www.gentiva.com"},
    "National HealthCare Corporation": {"founded": "1971", "website_url": "https://nhccare.com"},
    "Solera Health": {"founded": "2015", "website_url": "https://www.soleranetwork.com"},
    "Coffee Cherry": {"founded": "2014", "website_url": ""},
    "lyflynks": {"founded": "2017", "website_url": ""},
}

def main():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    for ent in data:
        name = ent.get("name", "")
        if name in updates:
            upd = updates[name]
            changed = False
            if upd.get("founded") and not ent.get("founded"):
                ent["founded"] = upd["founded"]
                changed = True
            if upd.get("website_url") and not ent.get("website_url"):
                ent["website_url"] = upd["website_url"]
                changed = True
            if changed:
                updated_count += 1
                print(f"  Updated: {name} -> founded={ent.get('founded')}, website={ent.get('website_url')}")

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nTotal updated: {updated_count}/{len(data)}")

    founded_count = sum(1 for e in data if e.get("founded"))
    website_count = sum(1 for e in data if e.get("website_url"))
    print(f"founded coverage: {founded_count}/{len(data)} ({founded_count/len(data)*100:.0f}%)")
    print(f"website_url coverage: {website_count}/{len(data)} ({website_count/len(data)*100:.0f}%)")

if __name__ == "__main__":
    main()
