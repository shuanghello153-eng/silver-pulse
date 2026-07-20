# -*- coding: utf-8 -*-
"""w4-fix 诊断：对给定 serials 打印卡片关键字段 + 当前 recommend + 与卡片字段的 LCS 冲突。
用法：python _w4_diag.py 0793 0816 ...
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
db = json.load(open(DB, encoding="utf-8"))
by = {str(x.get("serial", "")).lstrip("#"): x for x in db}

def lcs_sub(a, b):
    a, b = re.sub(r"\s", "", a or ""), re.sub(r"\s", "", b or "")
    if not a or not b:
        return 0, ""
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    end = best = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]; end = i
            else:
                dp[i][j] = 0
    return best, a[end-best:end]

THR = {"desc_cn":10,"silver_reason":10,"description":10,"highlights":8,"funding_latest":8,"funding_total":8}

for s in sys.argv[1:]:
    e = by.get(s)
    if not e:
        print("### %s NOT IN DB" % s); continue
    # 优先读 legacy 无#文件（这些 serial 只有 legacy），否则 #文件
    d = None
    for fn in ("drafts_v4/draft_%s.json"%s, "drafts_v4/draft_#%s.json"%s):
        if os.path.exists(fn):
            d = json.load(open(fn, encoding="utf-8")); break
    if not d:
        print("### %s NO DRAFT" % s); continue
    tmp = dict(e)
    for k in ("recommend","desc_cn","silver_reason","payor_model"):
        if k in d and d[k] is not None: tmp[k] = d[k]
    rec = d.get("recommend","")
    iss = validate(tmp)
    print("="*70)
    print("### #%s %s  信号=%s  付费DB=%s  付费draft=%s" % (s, e.get("name"), e.get("signal_strength"), e.get("payor_model"), d.get("payor_model")))
    print("  funding:", e.get("funding_latest"), "total:", e.get("funding_total"))
    print("  highlights:", e.get("highlights"))
    print("  desc_cn:", (e.get("desc_cn") or "")[:160])
    print("  description:", str(e.get("description"))[:160])
    print("  silver_reason:", e.get("silver_reason"))
    print("  RECOMMEND(%d): %s" % (len(rec), rec))
    print("  ISSUES:", iss)
    if any(i.startswith("R-field-dedup") for i in iss):
        c = dict(e)
        for k in ("desc_cn","silver_reason","payor_model"):
            if k in d and d[k] is not None: c[k] = d[k]
        for fld in ("desc_cn","silver_reason","description","highlights","funding_latest","funding_total"):
            ft = c.get(fld)
            if isinstance(ft, str): texts=[ft]
            elif isinstance(ft, list): texts=[str(x) for x in ft]
            elif isinstance(ft, dict): texts=[str(ft.get("display"))] if ft.get("display") else []
            else: texts=[]
            for tv in texts:
                if not tv: continue
                ln, sub = lcs_sub(rec, tv)
                t = 8
                for p, th in THR.items():
                    if fld.startswith(p): t = th; break
                if ln >= t:
                    print("     LCS[%s]>=%d: …%s…" % (fld, t, sub))
