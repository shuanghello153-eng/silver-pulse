"""
Merge search results from agents into all_enterprises.json.
Updates founded and website_url fields for companies that have missing data.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ENTERPRISE_FILE = os.path.join(BASE, "data", "enterprise", "all_enterprises.json")
RESULTS_DIR = os.path.join(BASE, "data", "enterprise", "search_results")

def main():
    # Load enterprise data
    with open(ENTERPRISE_FILE, "r", encoding="utf-8") as f:
        enterprises = json.load(f)

    # Build serial -> enterprise mapping
    serial_map = {}
    name_map = {}
    for ent in enterprises:
        serial_map[ent["serial"]] = ent
        name_map[ent["name"].lower().strip()] = ent

    # Load all search results
    all_results = []
    if not os.path.exists(RESULTS_DIR):
        print("No results directory found!")
        return

    for fname in sorted(os.listdir(RESULTS_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(RESULTS_DIR, fname), "r", encoding="utf-8") as f:
                results = json.load(f)
            all_results.extend(results)
            print(f"Loaded {fname}: {len(results)} entries")

    print(f"\nTotal search results: {len(all_results)}")

    # Apply updates
    updated_founded = 0
    updated_website = 0
    updated_both = 0
    matched = 0
    not_matched = 0

    for result in all_results:
        serial = result.get("serial", "")
        name = result.get("name", "")
        founded = result.get("founded")
        website = result.get("website_url")

        # Try to match by serial first, then by name
        ent = serial_map.get(serial)
        if not ent:
            ent = name_map.get(name.lower().strip())
        if not ent:
            # Try partial name match
            for ename, eent in name_map.items():
                if name.lower().strip() in ename or ename in name.lower().strip():
                    ent = eent
                    break

        if not ent:
            not_matched += 1
            continue

        matched += 1
        changed = False

        # Update founded
        if founded and not ent.get("founded"):
            if isinstance(founded, str) and founded.strip().isdigit():
                year = int(founded.strip())
                if 1950 <= year <= 2025:
                    ent["founded"] = str(year)
                    updated_founded += 1
                    changed = True
            elif isinstance(founded, int) and 1950 <= founded <= 2025:
                ent["founded"] = str(founded)
                updated_founded += 1
                changed = True

        # Update website_url
        if website and not ent.get("website_url"):
            if isinstance(website, str) and website.startswith("http"):
                # Clean up URL
                website = website.rstrip("/.,;)")
                ent["website_url"] = website
                updated_website += 1
                changed = True

        if changed:
            updated_both += 1

    print(f"\nMatched: {matched}, Not matched: {not_matched}")
    print(f"Updated founded: {updated_founded}")
    print(f"Updated website: {updated_website}")
    print(f"Total companies changed: {updated_both}")

    # Save
    with open(ENTERPRISE_FILE, "w", encoding="utf-8") as f:
        json.dump(enterprises, f, ensure_ascii=False, indent=2)

    # Final stats
    total = len(enterprises)
    has_founded = sum(1 for d in enterprises if d.get("founded"))
    has_website = sum(1 for d in enterprises if d.get("website_url"))
    has_investors = sum(1 for d in enterprises if d.get("investors") and d["investors"] not in ["", "未披露", "未公开"])
    has_ft = sum(1 for d in enterprises if d.get("funding_total") and d["funding_total"].get("amount") and d["funding_total"]["amount"] not in ["", "未披露", "未公开"])

    print(f"\n=== Final Stats ===")
    print(f"Total: {total}")
    print(f"Has founded: {has_founded} ({has_founded*100//total}%)")
    print(f"Has website: {has_website} ({has_website*100//total}%)")
    print(f"Has investors: {has_investors} ({has_investors*100//total}%)")
    print(f"Has funding_total: {has_ft} ({has_ft*100//total}%)")

if __name__ == "__main__":
    main()
