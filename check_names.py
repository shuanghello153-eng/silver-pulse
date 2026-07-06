#!/usr/bin/env python3
"""Check enterprise names for matching."""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data/enterprise/all_enterprises.json")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find names containing keywords
keywords = ["Papa", "Honor", "Brookdale", "Chapter", "Amedisys", "Home Instead"]
for kw in keywords:
    matches = [e["name"] for e in data if kw.lower() in e.get("name", "").lower()]
    print(f"'{kw}' matches: {matches}")

# Also check for some Chinese companies
cn_keywords = ["共比邻", "兴趣岛", "南京新百", "安杰莱", "织生", "迈步", "远也"]
for kw in cn_keywords:
    matches = [e["name"] for e in data if kw in e.get("name", "")]
    print(f"'{kw}' matches: {matches}")
