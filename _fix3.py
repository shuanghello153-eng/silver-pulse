# -*- coding: utf-8 -*-
"""把仍嵌套在 age_uk 内的新源(如 silvereco)拎到 SOURCES 顶层。"""
lines = open("config.py", encoding="utf-8").read().split("\n")
keys = ['silvereco','tracxn_age_tech','seedtable_elder','being_patient','addf_portfolio','dementia_care_central','alzheimers_net','hearingtracker']

def bracket_close(lines, start):
    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth == 0 and i > start:
            return i
    return len(lines) - 1

# age_uk 范围
start = next(i for i, l in enumerate(lines) if l.strip().startswith('"age_uk":'))
close = bracket_close(lines, start)

# 找嵌套在 age_uk 内的 8 源
nested = {}
for key in keys:
    for i in range(start, close):
        if lines[i].strip().startswith(f'"{key}":'):
            kc = bracket_close(lines, i)
            nested[key] = lines[i:kc + 1]
            break

skip = set()
for key, blk in nested.items():
    for x in range(len(lines)):
        if lines[x:x+len(blk)] == blk:
            for y in range(x, x+len(blk)):
                skip.add(y)
            break

new = [l for i, l in enumerate(lines) if i not in skip]

# 在 new 里找 age_uk 闭合，把嵌套块插到其后
s2 = next(i for i, l in enumerate(new) if l.strip().startswith('"age_uk":'))
c2 = bracket_close(new, s2)
at = c2 + 1
inserted = []
for key in keys:
    if key in nested:
        inserted += nested[key]
new[at:at] = inserted

open("config.py", "w", encoding="utf-8").write("\n".join(new))
print(f"从 age_uk 拎出顶层: {list(nested.keys())}")
