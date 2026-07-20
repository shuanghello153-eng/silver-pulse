# -*- coding: utf-8 -*-
"""Debug: print max-LCS substring per field for given serial(s)."""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import _field_texts

def lcs_sub(a, b):
    a, b = re.sub(r"\s", "", a or ""), re.sub(r"\s", "", b or "")
    if not a or not b:
        return 0, ""
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    end = 0; best = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]; end = i
            else:
                dp[i][j] = 0
    return best, a[end-best:end]

batch = sys.argv[1]
serials = sys.argv[2:]
src = json.load(open(batch, encoding="utf-8"))
ctx = {e["serial"]: e for e in src}
thr = {"desc_cn":10,"silver_reason":10,"description":10,"highlights":8,"funding_latest":8,"funding_total":8}
for e in src:
    if serials and e["serial"] not in serials:
        continue
    rec = e.get("recommend")
    if not isinstance(rec, str):
        continue
    print("="*60, e["serial"])
    for fname, ftext in _field_texts(e):
        t = 8
        for p,tv in thr.items():
            if fname.startswith(p):
                t = tv; break
        ln, sub = lcs_sub(rec, ftext)
        if ln >= t:
            print(f"  [{ln}>= {t}] {fname}: ...{sub}...")
