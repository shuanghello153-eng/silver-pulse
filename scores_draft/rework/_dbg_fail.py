import json, importlib.util, sys, re
sys.path.insert(0,".")
import check_single as C
spec=importlib.util.spec_from_file_location("wr","write_recommends.py")
wr=importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
RECS,FIXES=wr.RECS,wr.FIXES
d=json.load(open('batches_full/batch_patch_gap.json',encoding='utf-8'))
by={x['serial']:x for x in d}

FAIL=["#1312"]

def lcs_sub(a,b):
    a=re.sub(r"\s","",a); b=re.sub(r"\s","",b)
    n,m=len(a),len(b)
    if n==0 or m==0: return ""
    dp=[[0]*(m+1) for _ in range(n+1)]
    for i in range(1,n+1):
        for j in range(1,m+1):
            if a[i-1]==b[j-1]: dp[i][j]=dp[i-1][j-1]+1
    bi,bj=0,0; best=0
    for i in range(1,n+1):
        for j in range(1,m+1):
            if dp[i][j]>best: best=dp[i][j]; bi,bj=i,j
    if best==0: return ""
    return a[bi-best:bi]

def field_texts(e):
    pairs=[]
    if e.get('desc_cn'): pairs.append(('desc_cn',e['desc_cn']))
    if e.get('silver_reason'): pairs.append(('silver_reason',e['silver_reason']))
    for i,h in enumerate(e.get('highlights') or []):
        if isinstance(h,str) and h.strip(): pairs.append((f'hl[{i}]',h))
    fl=e.get('funding_latest') or {}
    if isinstance(fl,dict) and fl.get('display'): pairs.append(('fund_latest',fl['display']))
    ft=e.get('funding_total') or {}
    if isinstance(ft,dict) and ft.get('display'): pairs.append(('fund_total',ft['display']))
    if e.get('description'): pairs.append(('description',e['description']))
    return pairs

for serial in FAIL:
    e=dict(by[serial]); e['recommend']=RECS[serial]
    fix=FIXES.get(serial)
    if fix:
        for k,v in fix.items():
            if v: e[k]=v
    errs=C.validate(e,skip={'R10'})
    print("="*70); print(serial, "=>", errs)
    print("  RECOMMEND:", e['recommend'])
    print("  desc_cn(%d):"%len(e.get('desc_cn') or ''), e.get('desc_cn'))
    print("  silver_reason(%d):"%len(e.get('silver_reason') or ''), e.get('silver_reason'))
    print("  highlights:", e.get('highlights'))
    fl=e.get('funding_latest') or {}
    ft=e.get('funding_total') or {}
    print("  fund_latest:", fl.get('display') if isinstance(fl,dict) else fl)
    print("  fund_total:", ft.get('display') if isinstance(ft,dict) else ft)
    rec=e['recommend']
    for fname,ft in field_texts(e):
        thr=8
        if fname.startswith(('desc_cn','silver','description')): thr=10
        s=lcs_sub(rec,ft)
        if len(s)>=thr:
            print(f"  >>LCS[{fname}]={len(s)}::「{s}」")
