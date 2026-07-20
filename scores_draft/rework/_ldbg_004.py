# -*- coding: utf-8 -*-
import json, os, sys, re
HERE = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/scores_draft/rework"
sys.path.insert(0, HERE)
from _gen_w4_2_004 import RECOMMENDS
from check_single import _field_texts

def lcs_sub(a, b):
    a, b = re.sub(r"\s","",a), re.sub(r"\s","",b)
    if not a or not b: return ""
    n,m=len(a),len(b)
    dp=[[0]*(m+1) for _ in range(n+1)]
    bt=[[0]*(m+1) for _ in range(n+1)]
    best=0; bi=0; bj=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if a[i-1]==b[j-1]:
                dp[i][j]=dp[i-1][j-1]+1; bt[i][j]=1
            else:
                dp[i][j]=0
            if dp[i][j]>best: best=dp[i][j]; bi=i; bj=j
    s=""; i,j=bi,bj
    while i>0 and j>0 and bt[i][j]==1:
        s=a[i-1]+s; i-=1; j-=1
    return s

BATCH="004"
data=json.load(open(os.path.join(HERE,"batches_full",f"batch_src_{BATCH}.json"),encoding="utf-8"))
for e in data:
    s=e["serial"]; r=RECOMMENDS.get(s,"")
    if not r: continue
    for fname,ftext in _field_texts(e):
        sub=lcs_sub(r,ftext)
        if len(sub)>=8:
            print(f"[{s}] {fname} LCS={len(sub)}: 「{sub}」")
