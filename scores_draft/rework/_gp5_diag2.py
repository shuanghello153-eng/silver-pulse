# -*- coding: utf-8 -*-
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", ".."))
DB = os.path.join(BASE, "data/enterprise/all_enterprises.json")
d = json.load(open(DB, encoding="utf-8"))

def lcs_sub(a, b):
    a = re.sub(r"\s", "", a or "")
    b = re.sub(r"\s", "", b or "")
    if not a or not b:
        return "", 0
    n, m = len(a), len(b)
    dp = [0]*(m+1)
    best = 0; end = 0
    for i in range(1, n+1):
        prev = 0
        for j in range(1, m+1):
            tmp = dp[j]
            if a[i-1] == b[j-1]:
                dp[j] = prev + 1
                if dp[j] > best:
                    best = dp[j]; end = i
            else:
                dp[j] = 0
            prev = tmp
    return (a[end-best:end], best)

serials = ["#0808","#0809","#0811","#0812","#0813","#0814","#0815","#0819","#0822","#0825","#0826"]
for s in serials:
    fp = os.path.join(HERE, "drafts_v5", "draft_%s.json" % s)
    rec = json.load(open(fp, encoding="utf-8"))
    r = rec["recommend"]
    # DB context for funding
    ctx = {}
    for e in d:
        if "#"+str(e.get("serial","")).lstrip("#") == s.lstrip("#"):
            ctx = e; break
    fields = [("desc_cn", rec.get("desc_cn","")), ("silver_reason", rec.get("silver_reason",""))]
    fl = (ctx.get("funding_latest") or {}).get("display") or ""
    if fl: fields.append(("funding_latest", fl))
    ft = (ctx.get("funding_total") or {}).get("display") or ""
    if ft: fields.append(("funding_total", ft))
    print("====", s)
    for fn, ftxt in fields:
        sub, ln = lcs_sub(r, ftxt)
        if ln >= 8:
            print("   [%s] LCS=%d : ...%s..." % (fn, ln, sub))
