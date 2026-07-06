#!/usr/bin/env python3
"""Batch 6: Update founded + website_url for more companies (web search batch 2)."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "enterprise" / "all_enterprises.json"

UPDATES = {
    # Overseas
    "Oak Street Health": {"founded": "2012", "website_url": "https://www.oakstreethealth.com"},
    "Tivity Health": {"founded": "1981", "website_url": "https://www.tivityhealth.com"},
    "SilverSneakers": {"founded": "1992", "website_url": "https://www.silversneakers.com"},
    "Cala Health": {"founded": "2014", "website_url": "https://calahealth.com"},
    "Synapticure": {"founded": "2019", "website_url": "https://www.synapticure.com"},
    "Abbvie": {"founded": "2013", "website_url": "https://www.abbvie.com"},
    "August Health": {"founded": "2020", "website_url": "https://www.augusthealth.com"},
    "The Villages": {"founded": "1970", "website_url": "https://www.thevillages.com"},
    "Amplifon": {"founded": "1950", "website_url": "https://www.amplifon.com"},
    # Domestic
    "可靠护理": {"founded": "2001", "website_url": "https://cocohealthcare.com"},
    "圣德医养": {"founded": "2009", "website_url": "http://www.singdeyy.com"},
    "松龄护老": {"founded": "1989", "website_url": "https://www.pinecaregroup.com"},
    "锦欣康养": {"founded": "2014", "website_url": "https://jx-care.com"},
    "豪悦护理": {"founded": "2008", "website_url": "https://www.hz-haoyue.com"},
    "兆观智能": {"founded": "2014", "website_url": "http://www.megahealth.cn"},
    "孝爱宝": {"founded": "2015", "website_url": "https://www.iyiou.com/company/xiaoaibao"},
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
