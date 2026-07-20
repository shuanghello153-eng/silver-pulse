# -*- coding: utf-8 -*-
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

def lcs_sub(a, b):
    a = re.sub(r"\s","",a); b=re.sub(r"\s","",b)
    n,m=len(a),len(b)
    if n==0 or m==0: return ""
    dp=[[0]*(m+1) for _ in range(n+1)]
    bt=[[0]*(m+1) for _ in range(n+1)]
    best=0; bi=bj=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if a[i-1]==b[j-1]:
                dp[i][j]=dp[i-1][j-1]+1
                bt[i][j]=1
            else:
                dp[i][j]=0
            if dp[i][j]>best:
                best=dp[i][j]; bi=i; bj=j
    # reconstruct
    s=""
    i,j=bi,bj
    while i>0 and j>0 and bt[i][j]==1:
        s=a[i-1]+s; i-=1; j-=1
    return s

import re
def main():
    targets = sys.argv[1:] if len(sys.argv)>1 else []
    for b in ['025','026','027']:
        d=json.load(open(f'batches_full/batch_src_{b}.json',encoding='utf-8'))
        for e in d:
            s=e['serial']
            if targets and s not in targets: continue
            fp=os.path.join(HERE,'drafts_v4',f'draft_{s}.json')
            if not os.path.exists(fp): continue
            dr=json.load(open(fp,encoding='utf-8'))
            rec=dr.get('recommend','')
            # build fields to compare: my desc_cn, my silver, batch highlights, batch funding, batch description
            fields=[]
            if 'desc_cn' in dr: fields.append(('my_desc_cn',dr['desc_cn']))
            if 'silver_reason' in dr: fields.append(('my_silver',dr['silver_reason']))
            hl=e.get('highlights') or []
            if isinstance(hl,list):
                for i,h in enumerate(hl):
                    if isinstance(h,str) and h.strip(): fields.append((f'hl{i}',h))
            fl=e.get('funding_latest') or {}
            if isinstance(fl,dict) and fl.get('display'): fields.append(('fund_latest',fl['display']))
            ft=e.get('funding_total') or {}
            if isinstance(ft,dict) and ft.get('display'): fields.append(('fund_total',ft['display']))
            desc_en=e.get('description') or ''
            if desc_en: fields.append(('description',desc_en))
            for fname,ftxt in fields:
                sub=lcs_sub(rec,ftxt)
                if len(sub)>=8:
                    print(f'{s} | {fname} | LCS={len(sub)} | "{sub}"')
    print('---done---')
if __name__=='__main__':
    main()
