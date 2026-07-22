#!/usr/bin/env python3
"""Merge AgeClub new entries into all_enterprises.json (truth source).
- Backup existing file first
- Merge 313 new entries (safety: skip if name already exists)
- Append AgeClub supply info to 6 existing duplicate enterprises
- Save, report
"""
import json
import shutil
import os
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "enterprise")
EXISTING = os.path.join(DATA, "all_enterprises.json")
NEW = os.path.join(DATA, "ageclub_new_entries.json")

# --- backup ---
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak = os.path.join(DATA, f"all_enterprises.json.bak_ageclub_{stamp}")
shutil.copy2(EXISTING, bak)
print(f"Backup: {bak}")

with open(EXISTING, "r", encoding="utf-8") as f:
    existing = json.load(f)
with open(NEW, "r", encoding="utf-8") as f:
    ageclub = json.load(f)

# --- merge new entries ---
existing_names = {e.get("name", "").strip().lower() for e in existing}
new_entries = ageclub.get("new_entries", [])
added = 0
skipped_dup = 0
for ne in new_entries:
    nm = (ne.get("name") or "").strip()
    if not nm:
        skipped_dup += 1
        continue
    if nm.lower() in existing_names:
        skipped_dup += 1
        continue
    # minimal field normalization
    rec = {
        "name": nm,
        "region": ne.get("region", ""),
        "tag_l1": ne.get("tag_l1") or [],
        "tag_l2": ne.get("tag_l2") or [],
        "tags": ne.get("tags") or [],
        "description": ne.get("description", ""),
        "recommend": ne.get("recommend", ""),
        "source": ne.get("source", "AgeClub供需对接"),
        "website_url": ne.get("website_url", ""),
        "crunchbase_url": ne.get("crunchbase_url", ""),
        "funding_latest": ne.get("funding_latest"),
        "funding_total": ne.get("funding_total"),
        "investors": ne.get("investors"),
        "founded": ne.get("founded", ""),
        "stage": ne.get("stage", ""),
        "payor_model": ne.get("payor_model", ""),
    }
    existing.append(rec)
    existing_names.add(nm.lower())
    added += 1

print(f"Added {added} new entries; skipped {skipped_dup} (empty/dup)")

# --- supplement 6 exact matches with AgeClub supply info ---
# Map: existing name -> AgeClub supply text (from source markdown)
supplies = {
    "福建百龄康养": "12 家连锁养老院",
    "上海地宝防滑防护科技有限公司": "防滑、无障碍扶手、淋浴辅具",
    "江西哦咔科技": "社区养老院运营",
    "时尚奶奶团": "100 个中老年 IP 矩阵",
    "浙江三网科技": "养老定位手环、防跌倒报警器",
    "美适浴": "100% 防摔倒适老开门浴缸",
}
# normalize keys for matching (some names may differ slightly)
sup_keys = {k.lower(): v for k, v in supplies.items()}
supplied = 0
for e in existing:
    nm = e.get("name", "")
    nml = nm.lower()
    if nml in sup_keys:
        add_text = sup_keys[nml]
        note = f"（AgeClub供需对接补充：{add_text}）"
        cur = e.get("description") or ""
        if note not in cur:
            e["description"] = (cur + " " + note).strip() if cur else note
            # also tag source if not already
            if "AgeClub供需对接" not in (e.get("source") or ""):
                e["source"] = (e.get("source") or "") + "; AgeClub供需对接"
            supplied += 1
            print(f"  + Supplemented: {nm}")

print(f"Supplemented {supplied} existing enterprises")

# --- save ---
with open(EXISTING, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"Total enterprises: {len(existing)} (was {len(existing)-added})")
