#!/usr/bin/env python3
"""Check specific enterprise records."""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data/enterprise/all_enterprises.json")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for name in ["Papa", "Honor", "Chapter", "Brookdale Senior Living", "共比邻", "兴趣岛", "南京新百", "安杰莱"]:
    for e in data:
        if e["name"] == name:
            print(f"{name}: founded={e.get('founded','')}, website={e.get('website_url','')}")
            break
