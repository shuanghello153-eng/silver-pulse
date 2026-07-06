#!/usr/bin/env python3
"""Find enterprises that need founded/website_url completion."""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE_PATH = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Priority 1: has funding but no founded and no website
priority1 = []
# Priority 2: has funding but no founded
priority2_founded = []
# Priority 3: has funding but no website
priority2_website = []
# Priority 4: no funding, no founded, no website (lower priority)
priority3 = []

for e in data:
    has_funding = False
    fl = e.get("funding_latest")
    if fl and isinstance(fl, dict) and fl.get("display"):
        if "未披露" not in fl.get("display", ""):
            has_funding = True

    has_founded = bool(e.get("founded"))
    has_website = bool(e.get("website_url"))

    if has_funding and not has_founded and not has_website:
        priority1.append(e["name"])
    elif has_funding and not has_founded:
        priority2_founded.append(e["name"])
    elif has_funding and not has_website:
        priority2_website.append(e["name"])
    elif not has_founded and not has_website:
        priority3.append(e["name"])

print(f"Priority 1 (has funding, missing both founded+website): {len(priority1)}")
print(f"Priority 2a (has funding, missing founded): {len(priority2_founded)}")
print(f"Priority 2b (has funding, missing website): {len(priority2_website)}")
print(f"Priority 3 (no funding, missing both): {len(priority3)}")

# Show priority 1 names (first 50)
print("\n=== Priority 1 (first 50) ===")
for name in priority1[:50]:
    print(f"  {name}")

# Show priority 2a names (first 30, excluding priority1)
p2a_only = [n for n in priority2_founded if n not in priority1]
print(f"\n=== Priority 2a only (first 30, has website but no founded) ===")
for name in p2a_only[:30]:
    print(f"  {name}")
