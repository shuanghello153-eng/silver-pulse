# -*- coding: utf-8 -*-
"""诊断 _gen_w4_2_007.py 中每条 recommend 与各字段的实际最长公共子串。"""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DB = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/data/enterprise/all_enterprises.json"

src = open("_gen_w4_2_007.py", encoding="utf-8").read()
block = src.split("def ser(")[0]
ns = {"__file__": "_gen_w4_2_007.py", "__name__": "g7"}
exec(block, ns)
R = ns["RECOMMENDS"]

d = json.load(open(DB, encoding="utf-8"))
by = {str(e.get("serial", "")).lstrip("#"): e for e in d}

def lcs_sub(a, b):
    a = re.sub(r"\s", "", a); b = re.sub(r"\s", "", b)
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    end = 0; length = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]+1
                if dp[i][j] > length:
                    length = dp[i][j]; end = i
    return a[end-length:end] if length > 0 else ""

def fval(x):
    if isinstance(x, dict): return x.get("display", "") or ""
    return ""

for s in R:
    e = by.get(s.lstrip("#"), {})
    pairs = [("desc_cn", e.get("desc_cn", "")), ("silver_reason", e.get("silver_reason", "")),
             ("description", e.get("description", ""))]
    for i, h in enumerate(e.get("highlights") or []):
        pairs.append((f"hl[{i}]", h))
    pairs.append(("fl", fval(e.get("funding_latest"))))
    pairs.append(("ft", fval(e.get("funding_total"))))
    hits = []
    for fn, val in pairs:
        sub = lcs_sub(R[s], val)
        ln = len(sub)
        if ln >= 7:
            hits.append((ln, fn, sub))
    hits.sort(reverse=True)
    if hits:
        print("="*70, s)
        for ln, fn, sub in hits[:4]:
            print(f"  [{ln}] {fn}: {sub}")
