# -*- coding: utf-8 -*-
import json, sys, re
import check_single as C

serial = sys.argv[1]
data = json.load(open('batches_full/batch_src_044.json', encoding='utf-8'))
e = next(x for x in data if x['serial']==serial)
dr = json.load(open('drafts_v4/draft_%s.json'%serial.replace('#',''), encoding='utf-8'))
rec = dr['recommend']
txt = re.sub(r"\s","",rec)

def lcs_sub(a,b):
    a,b = re.sub(r"\s","",a), re.sub(r"\s","",b)
    if not a or not b: return ""
    n,m=len(a),len(b)
    if n*m>4000000: a,b=a[:2000],b[:2000]
    dp=[[0]*(m+1) for _ in range(n+1)]
    end=0;length=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if a[i-1]==b[j-1]:
                dp[i][j]=dp[i-1][j-1]+1
                if dp[i][j]>length:
                    length=dp[i][j]; end=i
    return a[end-length:end]

pairs = C._field_texts(e)
thr={"desc_cn":10,"silver_reason":10,"description":10,"highlights":8,"funding_latest":8,"funding_total":8}
for fname,ftext in pairs:
    t=8
    for p,tt in thr.items():
        if fname.startswith(p): t=tt;break
    s=lcs_sub(txt,ftext)
    if len(s)>=t:
        print("[%s thr=%d len=%d] %s"%(fname,t,len(s),s))
print("---- full recommend ----")
print(rec)
print("len(去空白)=",len(txt))
