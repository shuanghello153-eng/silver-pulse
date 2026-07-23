#!/usr/bin/env python3
"""Merge AgeClub enriched batch files back into all_enterprises.json.
Only updates AgeClub-sourced enterprises; updates specific fields.
Backup before writing.
"""
import json, os, re, shutil, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data/enterprise")
SRC = os.path.join(DATA, "all_enterprises.json")

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak = os.path.join(DATA, f"all_enterprises.json.bak_enriched_{ts}")
shutil.copy2(SRC, bak)
print(f"Backup: {bak}")

# Load current enterprises
with open(SRC, 'r', encoding='utf-8') as f:
    ents = json.load(f)

# Build name index (normalized lowercase)
def norm(s):
    return re.sub(r'[\s\u3000()（）【】\[\].,，。、]', '', (s or '').lower())

ent_by_norm = {}
for e in ents:
    ent_by_norm.setdefault(norm(e.get('name', '')), []).append(e)

# Load all enriched batches
enriched = []
for i in range(1, 6):
    p = os.path.join(DATA, f"ageclub_enriched_batch{i}.json")
    with open(p, 'r', encoding='utf-8') as f:
        enriched.extend(json.load(f))
print(f"Loaded {len(enriched)} enriched records")

# Fields to update from enriched data (only if enriched has meaningful value)
UPDATE_FIELDS = ['website_url', 'founded', 'stage', 'funding_latest', 'funding_total',
                 'recommend', 'crunchbase_url', 'payor_model', 'tag_l1', 'tag_l2']

def has_value(v):
    if v is None: return False
    if isinstance(v, str):
        return v.strip() not in ('', '未搜到', '未披露', '未公开')
    if isinstance(v, list):
        return len(v) > 0
    if isinstance(v, dict):
        # For funding dicts, check display
        disp = v.get('display', '')
        return disp not in ('', '未披露', '未公开') and bool(re.search(r'\d', disp))
    return True

# Track updates
updated = 0
matched_ents = set()
for rec in enriched:
    rec_name = rec.get('name', '')
    key = norm(rec_name)
    targets = ent_by_norm.get(key, [])
    if not targets:
        print(f"  WARN: not found in DB: {rec_name}")
        continue
    # Assume single match (no dups by name)
    e = targets[0]
    matched_ents.add(id(e))
    changed = False
    for fld in UPDATE_FIELDS:
        new_v = rec.get(fld)
        if has_value(new_v):
            old_v = e.get(fld)
            # Only overwrite if old is empty or new is better
            if not has_value(old_v):
                e[fld] = new_v
                changed = True
            elif fld in ('tag_l1', 'tag_l2'):
                # Merge tag sets (keep existing + add new)
                merged = list(dict.fromkeys((old_v or []) + (new_v or [])))
                if merged != (old_v or []):
                    e[fld] = merged
                    changed = True
            # For other fields with existing value, keep existing (don't overwrite good data)
    if changed:
        updated += 1

print(f"Updated {updated} enterprises")

# Write back
with open(SRC, 'w', encoding='utf-8') as f:
    json.dump(ents, f, ensure_ascii=False, indent=1)

# Quick stats: how many AgeClub entries now have key fields
ageclub = [e for e in ents if 'AgeClub' in (e.get('source') or '')]
print(f"\nAgeClub total: {len(ageclub)}")
for fld in ['website_url', 'founded', 'stage', 'recommend', 'payor_model']:
    cnt = sum(1 for e in ageclub if has_value(e.get(fld)))
    print(f"  {fld}: {cnt}/{len(ageclub)} 有值")
fund_cnt = sum(1 for e in ageclub if isinstance(e.get('funding_latest'), dict) and has_value(e.get('funding_latest')))
print(f"  funding_latest (含金额): {fund_cnt}/{len(ageclub)}")
print(f"\nTotal enterprises: {len(ents)}")
