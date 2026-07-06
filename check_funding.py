#!/usr/bin/env python3
"""Check funding display formats and fix them."""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

with open(os.path.join(DATA_DIR, "enterprise/all_enterprises.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== funding_latest display samples ===")
count = 0
for e in data:
    fl = e.get("funding_latest")
    if fl and isinstance(fl, dict) and fl.get("display"):
        print(f"  {e['name']}: {fl['display']}")
        count += 1
        if count >= 15:
            break

print()
print("=== funding_total display samples ===")
count = 0
for e in data:
    ft = e.get("funding_total")
    if ft and isinstance(ft, dict) and ft.get("display") and ft["display"] != "累计未披露":
        print(f"  {e['name']}: {ft['display']}")
        count += 1
        if count >= 10:
            break

print()
print("=== funding_latest with amount field ===")
count = 0
for e in data:
    fl = e.get("funding_latest")
    if fl and isinstance(fl, dict) and fl.get("amount"):
        print(f"  {e['name']}: amount={fl['amount']}, round={fl.get('round','')}, date={fl.get('date','')}, display={fl.get('display','')}")
        count += 1
        if count >= 10:
            break

print()
print("=== funding_total with amount field ===")
count = 0
for e in data:
    ft = e.get("funding_total")
    if ft and isinstance(ft, dict) and ft.get("amount"):
        print(f"  {e['name']}: amount={ft['amount']}, display={ft.get('display','')}")
        count += 1
        if count >= 10:
            break
