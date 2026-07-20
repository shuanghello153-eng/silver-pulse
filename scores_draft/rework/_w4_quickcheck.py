# -*- coding: utf-8 -*-
"""w4-fix: 快速逐草稿门禁检查（不做 R10 跨企业，留给合并阶段）。
输出：drafts_v4 中未过 check_single 的 serial -> issues。
用法：python _w4_quickcheck.py [--write-fails fails.json]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate

BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")

db = json.load(open(DB, encoding="utf-8"))
by = {str(x.get("serial", "")).lstrip("#"): x for x in db}

# 仅以 canonical 的 draft_#*.json 作为权威状态
canon = [f for f in os.listdir("drafts_v4")
         if f.startswith("draft_#") and f.endswith(".json")]
fails = {}
passn = 0
for f in sorted(canon):
    d = json.load(open(os.path.join("drafts_v4", f), encoding="utf-8"))
    s = str(d.get("serial", "")).lstrip("#")
    ctx = by.get(s, {})
    tmp = dict(ctx)
    for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
        if k in d and d[k] is not None:
            tmp[k] = d[k]
    iss = validate(tmp)  # others=None -> 跳过 R10
    if iss:
        fails[s] = iss
    else:
        passn += 1

# 额外：扫描 legacy 无#文件（draft_XXXX.json），若其本身不过门禁则会在合并时污染结果
legacy_bad = {}
for f in os.listdir("drafts_v4"):
    if f.startswith("draft_") and not f.startswith("draft_#") and f.endswith(".json"):
        d = json.load(open(os.path.join("drafts_v4", f), encoding="utf-8"))
        s = str(d.get("serial", "")).lstrip("#")
        ctx = by.get(s, {})
        tmp = dict(ctx)
        for k in ("recommend", "desc_cn", "silver_reason", "payor_model"):
            if k in d and d[k] is not None:
                tmp[k] = d[k]
        iss = validate(tmp)
        if iss:
            legacy_bad[s] = iss

print("canonical drafts:", len(canon))
print("PASS:", passn, " FAIL:", len(fails))
print("legacy 无#文件且不过门禁(需同步):", len(legacy_bad))
if "--write-fails" in sys.argv:
    out = sys.argv[sys.argv.index("--write-fails") + 1]
    json.dump(fails, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("wrote", out)
# 按 issue 类型聚合
from collections import Counter
c = Counter()
for s, iss in fails.items():
    for it in iss:
        c[it.split(":")[0]] += 1
print("--- issue 类型分布 ---")
for k, v in c.most_common():
    print(f"  {k}: {v}")
print("--- 前 20 个失败 serial ---")
for i, (s, iss) in enumerate(fails.items()):
    if i >= 20:
        break
    print(s, iss)
