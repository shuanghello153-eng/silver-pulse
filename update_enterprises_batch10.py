"""Batch 10: Update 12 companies with founded + website_url"""
import json

DATA_FILE = "data/enterprise/all_enterprises.json"

UPDATES = {
    "Grow Therapy": {"founded": "2020", "website_url": "https://www.growtherapy.com"},
    "Grayce": {"founded": "2019", "website_url": "https://www.withgrayce.com"},
    "Glooko": {"founded": "2010", "website_url": "https://www.glooko.com"},
    "Harbor Health": {"founded": "2022", "website_url": "https://www.harborhealth.com"},
    "Concerto Care": {"founded": "2004", "website_url": "https://www.concertocare.com"},
    "CareCentrix": {"founded": "1996", "website_url": "https://www.carecentrix.com"},
    "Gennev": {"founded": "2015", "website_url": "https://gennev.com"},
    "Hazel": {"founded": "2015", "website_url": "https://www.hazel.com"},
    "Eight Sleep": {"founded": "2014", "website_url": "https://www.eightsleep.com"},
    "HealthSnap": {"founded": "2015", "website_url": "https://healthsnap.io"},
    "Foodsmart": {"founded": "2011", "website_url": "https://www.foodsmart.com"},
    "HarmonyCares": {"founded": "1993", "website_url": "https://harmonycares.com"},
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
                    print(f"  Updated {name}: {key} = {val}")
            updated += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    print(f"\nUpdated: {updated}")
    if not_found:
        print(f"Not found in DB: {not_found}")

if __name__ == "__main__":
    main()
