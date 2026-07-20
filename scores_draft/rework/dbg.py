# -*- coding: utf-8 -*-
"""调试：对给定 serial，打印 recommend 与各字段的精确最长公共子串。"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_w4_3 import REC, load_items, FIX

def lcs_sub(a, b):
    a, b = re.sub(r"\s", "", a), re.sub(r"\s", "", b)
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return ""
    dp = [[0]*(m+1) for _ in range(n+1)]
    best, bi, bj = 0, 0, 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]; bi, bj = i, j
            else:
                dp[i][j] = 0
    return a[bi-best:bi] if best > 0 else ""

def field_texts(it):
    pairs = []
    if it.get("desc_cn"): pairs.append(("desc_cn", it["desc_cn"]))
    if it.get("silver_reason"): pairs.append(("silver_reason", it["silver_reason"]))
    for i, h in enumerate(it.get("highlights") or []):
        if isinstance(h, str) and h.strip(): pairs.append((f"highlights[{i}]", h))
    fl = it.get("funding_latest") or {}
    if isinstance(fl, dict) and fl.get("display"): pairs.append(("funding_latest", fl["display"]))
    ft = it.get("funding_total") or {}
    if isinstance(ft, dict) and ft.get("display"): pairs.append(("funding_total", ft["display"]))
    if it.get("description"): pairs.append(("description", it["description"]))
    return pairs

targets = sys.argv[1:] or list(REC.keys())
items = load_items()
for serial in targets:
    rec = REC.get(serial)
    if not rec:
        print(f"[{serial}] 不在 REC"); continue
    it = items.get(serial, {})
    ctx = dict(it); ctx["recommend"] = rec
    fx = FIX.get(serial, {})
    for k in ("desc_cn","silver_reason","payor_model"):
        if k in fx: ctx[k] = fx[k]
    print(f"\n========== {serial} ({it.get('name')}) ==========")
    print("REC:", rec)
    for fname, ftext in field_texts(ctx):
        s = lcs_sub(rec, ftext)
        if len(s) >= 8:
            print(f"  LCS[{fname}] ({len(s)}字): 「{s}」")
