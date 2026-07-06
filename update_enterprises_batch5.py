#!/usr/bin/env python3
"""Batch 5: Update founded + website_url for overseas companies (web search results)."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "enterprise" / "all_enterprises.json"

UPDATES = {
    # Overseas companies
    "Athulya Senior Care": {"founded": "2016", "website_url": "https://www.athulyaseniorcare.com"},
    "Blooming Health": {"founded": "2020", "website_url": "https://www.bloominghealth.ai"},
    "CarePredict": {"founded": "2013", "website_url": "https://www.carepredict.com"},
    "Cariloop": {"founded": "2012", "website_url": "https://cariloop.com"},
    "Cera Care": {"founded": "2015", "website_url": "https://www.cerahq.com"},
    "Empathy": {"founded": "2020", "website_url": "https://www.helloempathy.com"},
    "ForSight Robotics": {"founded": "2020", "website_url": "https://forsightrobotics.com"},
    "Habitat Health": {"founded": "2023", "website_url": "https://www.habitathealth.com"},
    "Hinge Health": {"founded": "2014", "website_url": "https://www.hingehealth.com"},
    "Homethrive": {"founded": "2016", "website_url": "https://homethrive.com"},
    "IntusCare": {"founded": "2019", "website_url": "https://intuscare.com"},
    "Rippl Care": {"founded": "2021", "website_url": "https://www.ripplcare.com"},
    "Seen Health": {"founded": "2024", "website_url": "https://www.seenhealth.org"},
    "Silvernest": {"founded": "2015", "website_url": "https://www.silvernest.com"},
    "Sprinter Health": {"founded": "2021", "website_url": "https://www.sprinterhealth.com"},
    "Sword Health": {"founded": "2015", "website_url": "https://swordhealth.com"},
    "Tombot": {"founded": "2017", "website_url": "https://tombot.com"},
    "True Link Financial": {"founded": "2012", "website_url": "https://www.truelinkfinancial.com"},
    "Vesta Healthcare": {"founded": "2018", "website_url": "https://www.vestahealthcare.com"},
    "Vytalize Health": {"founded": "2014", "website_url": "https://www.vytalizehealth.com"},
    "Wellthy": {"founded": "2014", "website_url": "https://wellthy.com"},
    "Amedisys": {"founded": "1982", "website_url": "https://www.amedisys.com"},
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
