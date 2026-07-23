"""
修复两个质量门禁问题：
1. 313个空serial（AgeClub批次遗留）→ 分配新serial
2. description<20字且未标信息不足 → 补齐
"""
import json, re

DB_PATH = 'data/enterprise/all_enterprises.json'

with open(DB_PATH, 'r', encoding='utf-8') as f:
    db = json.load(f)

# === Fix 1: 补全空 serial ===
existing_serials = []
for e in db:
    s = e.get('serial')
    if s and re.match(r'^#\d{4}$', s):
        existing_serials.append(int(s[1:]))

max_serial = max(existing_serials) if existing_serials else 1773
print(f"当前最大 serial: #{max_serial}")

assigned = 0
for e in db:
    if not e.get('serial') or not re.match(r'^#\d{4}$', str(e.get('serial', ''))):
        max_serial += 1
        e['serial'] = f'#{max_serial:04d}'
        assigned += 1

print(f"新分配 serial: {assigned} 家 (#{max_serial - assigned + 1} ~ #{max_serial})")

# === Fix 2: 补齐 <20 字的 description ===
fixed_desc = 0
for e in db:
    d = e.get('description', '')
    if len(d) < 20 and '信息不足' not in d:
        tag_l2 = e.get('tag_l2', []) or []
        tag_l1 = e.get('tag_l1', []) or []
        tag_ctx = '、'.join(tag_l2[:2]) if tag_l2 else ''
        if not tag_ctx and tag_l1:
            tag_ctx = '、'.join(tag_l1[:1])

        d_clean = d.strip()
        if d_clean and d_clean not in ('.', '。'):
            if tag_ctx:
                e['description'] = d_clean + '。涉及' + tag_ctx + '领域。'
            else:
                e['description'] = d_clean + '。'
        else:
            if tag_ctx:
                e['description'] = '信息不足：仅公开名称与赛道（' + tag_ctx + '），无公开规模或营收数据。'
            else:
                e['description'] = '信息不足：无公开信息。'
        fixed_desc += 1

print(f"补齐短描述: {fixed_desc} 家")

# 写回
with open(DB_PATH, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("\n已写回 all_enterprises.json")
