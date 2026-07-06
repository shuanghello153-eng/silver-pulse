#!/usr/bin/env python3
"""
update_enterprises_batch1.py — Batch update founded + website_url for enterprises.
Data collected from WebSearch results.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data/enterprise/all_enterprises.json")

# Collected data: {name: {founded: "...", website_url: "..."}}
updates = {
    # Chinese companies
    "AgeClub": {"founded": "2016", "website_url": "https://ageclub.net"},
    "博斯腾": {"founded": "2016", "website_url": "http://www.bestcovered.com/"},
    "善诊": {"founded": "2015", "website_url": "https://shanzhen.com"},
    "清雷": {"founded": "2019", "website_url": "https://qingleitech.com"},
    "清雷科技": {"founded": "2019", "website_url": "https://qingleitech.com"},
    "程天": {"founded": "2017", "website_url": "https://www.roboct.com"},
    "CareVoice": {"founded": "2014", "website_url": "https://www.thecarevoice.com"},
    "Gyenno": {"founded": "2015", "website_url": "https://www.fftai.cn"},
    "享睡Sleepace": {"founded": "2011", "website_url": "http://www.sleepace.com"},
    "鱼跃医疗": {"founded": "1998", "website_url": "https://www.yuwell.com"},
    "爱康医疗": {"founded": "2003", "website_url": "https://www.ak-medical.net"},
    "小年糕": {"founded": "2014", "website_url": "https://www.xnioz.com"},
    "美篇": {"founded": "2015", "website_url": "https://www.meipian.cn"},
    "悦心健康": {"founded": "1993", "website_url": "https://www.everjoyhealth.com"},
    "可靠股份": {"founded": "2001", "website_url": "https://www.cocohealthcare.com"},

    # Overseas companies
    "Papa": {"founded": "2017", "website_url": "https://www.papa.com"},
    "Honor": {"founded": "2014", "website_url": "https://www.honorcare.com"},
    "Brookdale Senior Living": {"founded": "1978", "website_url": "https://www.brookdale.com"},
    "Amedisys": {"founded": "1982", "website_url": "https://www.amedisys.com"},
    "Chapter": {"founded": "2013", "website_url": "https://www.getchapter.com"},
    "Home Instead": {"founded": "1994", "website_url": "https://www.homeinstead.com"},
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

    # Check new coverage
    founded_count = sum(1 for e in data if e.get("founded"))
    website_count = sum(1 for e in data if e.get("website_url"))
    print(f"founded coverage: {founded_count}/{len(data)} ({founded_count/len(data)*100:.0f}%)")
    print(f"website_url coverage: {website_count}/{len(data)} ({website_count/len(data)*100:.0f}%)")

if __name__ == "__main__":
    main()
