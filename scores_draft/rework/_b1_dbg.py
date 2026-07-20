# -*- coding: utf-8 -*-
import json, os, re, sys
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts_v4")

def lcs_sub(a, b):
    a, b = re.sub(r"\s","",a), re.sub(r"\s","",b)
    n, m = len(a), len(b)
    if n*m > 4_000_000:
        a, b = a[:2000], b[:2000]; n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    best, bi = 0, 0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if a[i-1]==b[j-1]:
                dp[i][j]=dp[i-1][j-1]+1
                if dp[i][j]>best:
                    best=dp[i][j]; bi=i
            else:
                dp[i][j]=0
    sub = a[bi-best:bi] if best>0 else ""
    return best, sub

targets = sys.argv[1:] or ['#0662','#0876','#0771','#0782','#0797','#0828','#0874','#1027','#1075','#1076','#1106','#1107','#1111','#1188','#1201']
for serial in targets:
    p = os.path.join(OUT, "draft_%s.json"%serial)
    d = json.load(open(p, encoding="utf-8"))
    r = d.get("recommend") or ""
    dc = d.get("desc_cn") or ""
    print("\n==== %s ====" % serial)
    # desc_cn overlap
    L, s = lcs_sub(r, dc)
    if L >= 10:
        print("  [desc_cn] LCS(%d): '%s'" % (L, s))
    # highlights
    for i, h in enumerate(d.get("highlights") or []):
        if not isinstance(h, str): continue
        L, s = lcs_sub(r, h)
        if L >= 8:
            print("  [hl%d] LCS(%d): '%s'" % (i, L, s))
    # funding displays
    fl = (d.get("funding_latest") or {})
    if isinstance(fl, dict) and fl.get("display"):
        L, s = lcs_sub(r, fl["display"])
        if L >= 8: print("  [fund_latest] LCS(%d): '%s'"%(L,s))
    ft = (d.get("funding_total") or {})
    if isinstance(ft, dict) and ft.get("display"):
        L, s = lcs_sub(r, ft["display"])
        if L >= 8: print("  [fund_total] LCS(%d): '%s'"%(L,s))
