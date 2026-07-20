# -*- coding: utf-8 -*-
import json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_single as C

DB = os.path.normpath(os.path.join(HERE, "..", "..", "data/enterprise/all_enterprises.json"))
DRAFTS = os.path.join(HERE, "drafts_v4")

def lcs_substring(a, b):
    a, b = re.sub(r"\s","",a), re.sub(r"\s","",b)
    n,m=len(a),len(b)
    dp=[[0]*(m+1) for _ in range(n+1)]
    end=0;length=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if a[i-1]==b[j-1]:
                dp[i][j]=dp[i-1][j-1]+1
                if dp[i][j]>length:
                    length=dp[i][j];end=i
    return a[end-length:end] if length else ""

db=json.load(open(DB,encoding="utf-8"))
idx={e.get("serial"):e for e in db}

targets=["#0256","#0788","#0801","#0805","#0862","#0890","#0905","#0876","#0828","#1111","#1488","#1500"]
for serial in targets:
    fp=os.path.join(DRAFTS,f"draft_{serial}.json")
    d=json.load(open(fp,encoding="utf-8"))
    rec=d.get("recommend") or ""
    e=idx.get(serial)
    pairs=C._field_texts(e)
    # also include draft desc_cn/silver (merge overrides)
    for k in ("desc_cn","silver_reason"):
        if d.get(k):
            pairs.append((k+"_draft",d[k]))
    print("="*60); print(serial)
    for fname,ftext in pairs:
        s=lcs_substring(rec,ftext)
        thr=8
        for pfx,t in {"desc_cn":10,"silver_reason":10,"description":10,"highlights":8,"funding_latest":8,"funding_total":8}.items():
            if fname.startswith(pfx): thr=t;break
        if len(s)>=thr:
            print(f"  [{fname}] overlap={len(s)} >= {thr} :: «{s}»")
