# -*- coding: utf-8 -*-
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))

def lcs_len(a, b):
    if not a or not b: return 0
    a, b = re.sub(r"\s", "", a), re.sub(r"\s", "", b)
    n, m = len(a), len(b)
    if n * m > 4_000_000:
        a, b = a[:2000], b[:2000]; n, m = len(a), len(b)
    dp = [0] * (m + 1); best = 0
    for i in range(1, n + 1):
        prev = 0
        for j in range(1, m + 1):
            tmp = dp[j]
            if a[i-1] == b[j-1]:
                dp[j] = prev + 1
                if dp[j] > best: best = dp[j]
            else:
                dp[j] = 0
            prev = tmp
    return best

def lcs_sub(a, b):
    a, b = re.sub(r"\s", "", a), re.sub(r"\s", "", b)
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1]==b[j-1]:
                dp[i][j]=dp[i-1][j-1]+1
    # find max
    bi, bj, bl = 0,0,0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if dp[i][j]>bl:
                bl=dp[i][j]; bi=i; bj=j
    return a[bi-bl:bi]

def main():
    serial = sys.argv[1]
    dr = json.load(open("drafts_v5/draft_%s.json" % serial, encoding="utf-8"))
    db = json.load(open(DB, encoding="utf-8"))
    ctx = {}
    for e in db:
        if str(e.get("serial",""))==serial:
            ctx = e; break
    tmp = dict(ctx)
    for k in ("recommend","desc_cn","silver_reason","payor_model"):
        if k in dr and dr[k] is not None:
            tmp[k] = dr[k]
    rec = tmp["recommend"]
    fields = [("desc_cn", tmp.get("desc_cn")), ("silver_reason", tmp.get("silver_reason"))]
    hl = tmp.get("highlights") or []
    if isinstance(hl, list):
        for i,h in enumerate(hl):
            if isinstance(h,str) and h.strip():
                fields.append(("highlights[%d]"%i, h))
    for fname, ftext in fields:
        if not ftext: continue
        ov = lcs_len(rec, ftext)
        if ov >= 8:
            sub = lcs_sub(rec, ftext)
            print("%s: LCS=%d  sub=%r" % (fname, ov, sub))
    # integrity check
    cl = len(re.sub(r"\s","",rec))
    half = cl//2
    DW = ["殡葬","康复","养老","保险","陪伴","机器人","食品","辅具","护理","地产","医疗","诊所","健身","社交","旅游","教育","理财","服装","营养","药品","器械","家居","出行","传媒","数据"]
    fd = [w for w in DW if w in rec[:half]]
    sd = [w for w in DW if w in rec[half:]]
    print("len=%d front_dom=%s back_dom=%s" % (cl, fd, sd))

main()
