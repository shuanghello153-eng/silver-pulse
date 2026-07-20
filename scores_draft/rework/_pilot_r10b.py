import json, os, re, sys
sys.path.insert(0,'.')
import check_single as C
DB = os.path.normpath(os.path.join('.', '..', '..', 'data/enterprise/all_enterprises.json'))
serials=["#0342","#0343","#0344","#0345","#0346","#0347","#0348","#0349","#0352","#0353","#0519","#0520"]
recs=[(s, json.load(open(f'drafts_v4/draft_{s}.json',encoding='utf-8'))['recommend']) for s in serials]
def _n(t):return re.sub(r"\s","",t or "")
def _t(t):
    t=_n(t);return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
db=json.load(open(DB,encoding='utf-8'))
dbrec=[(e['serial'],e['recommend']) for e in db if isinstance(e.get('recommend'),str) and e['serial'] not in serials]
dbcs=[set(_n(r)) for s,r in dbrec];dbtr=[_t(r) for s,r in dbrec]
dbinv={}
for i,x in enumerate(dbtr):
    for g in x:dbinv.setdefault(g,[]).append(i)
hit=0;hitser=[]
for s,r in recs:
    tr=_t(r);cs=set(_n(r))
    seen=set()
    for g in tr:
        for j in dbinv.get(g,[]):
            if j in seen:continue
            seen.add(j)
            if len(cs&dbcs[j])/len(cs|dbcs[j])<=0.5:continue
            if C.lcs_len(r,dbrec[j][1])>=15:
                hit+=1;hitser.append((s,dbrec[j][0]))
print(f"试点12家 vs 主库其余 {len(dbrec)} 家: R10撞车(>=15)={hit}")
for a,b in hitser[:10]:print(f"  撞: {a} <-> {b}")
