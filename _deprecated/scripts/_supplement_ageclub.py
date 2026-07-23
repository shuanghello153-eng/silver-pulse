#!/usr/bin/env python3
"""Supplement remaining 4 AgeClub duplicates by substring match (merge already done)."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "enterprise")
EXISTING = os.path.join(DATA, "all_enterprises.json")

# AgeClub supply text keyed by distinctive substring
supplies = {
    "百龄康养": "12 家连锁养老院",
    "哦咔科技": "社区养老院运营",
    "三网科技": "养老定位手环、防跌倒报警器",
    "美适浴": "100% 防摔倒适老开门浴缸",
}

with open(EXISTING, "r", encoding="utf-8") as f:
    existing = json.load(f)

supplied = 0
for key, add_text in supplies.items():
    for e in existing:
        nm = e.get("name", "")
        if key in nm:
            note = f"（AgeClub供需对接补充：{add_text}）"
            cur = e.get("description") or ""
            if note not in cur:
                e["description"] = (cur + " " + note).strip() if cur else note
                if "AgeClub供需对接" not in (e.get("source") or ""):
                    e["source"] = (e.get("source") or "") + "; AgeClub供需对接"
                supplied += 1
                print(f"  + Supplemented: {nm}")
            break
    else:
        print(f"  ! No match for key: {key}")

with open(EXISTING, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"Supplemented {supplied} more enterprises (total supplements now 6)")
