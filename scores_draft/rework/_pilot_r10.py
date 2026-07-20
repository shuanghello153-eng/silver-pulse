import json, os, re, sys
sys.path.insert(0,'.')
import check_single as C
serials=["#0342","#0343","#0344","#0345","#0346","#0347","#0348","#0349","#0352","#0353","#0519","#0520"]
recs=[]
for s in serials:
    d=json.load(open(f'drafts_v4/draft_{s}.json',encoding='utf-8'))
    recs.append((s,d['recommend']))
def _norm(t):return re.sub(r"\s","",t or "")
def _tris(t):
    t=_norm(t);return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _cs(t):return set(_norm(t))
cs=[_cs(r) for s,r in recs];tr=[_tris(r) for s,r in recs]
inv={}
for i,x in enumerate(tr):
    for g in x:inv.setdefault(g,[]).append(i)
fails=set();pairs=0
for i in range(len(recs)):
    seen=set()
    for g in tr[i]:
        for j in inv.get(g,[]):
            if j<=i or j in seen:continue
            seen.add(j)
            a,b=cs[i],cs[j]
            if not a or not b:continue
            if len(a&b)/len(a|b)<=0.5:continue
            if recs[i][1]==recs[j][1] or C.lcs_len(recs[i][1],recs[j][1])>=15:
                pairs+=1;fails.add(recs[i][0]);fails.add(recs[j][0])
print(f"12家互比: R10雷同对={pairs}, 涉及={len(fails)}")
# 也和主库已干净620比一下，确认不撞
db=json.load(open('../../../data/enterprise/all_enterprises.json',encoding='utf-8'))
def _norm2(t):return re.sub(r"\s","",t or "")
def _tris2(t):
    t=_norm2(t);return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
dbrec=[(e['serial'],e['recommend']) for e in db if isinstance(e.get('recommend'),str)]
dbcs=[set(_norm2(r)) for s,r in dbrec];dbtr=[_tris2(r) for s,r in dbrec]
dbinv={}
for i,x in enumerate(dbtr):
    for g in x:dbinv.setdefault(g,[]).append(i)
# 仅用这12家的trigram查库
hit=0
for i in range(len(recs)):
    seen=set()
    for g in tr[i]:
        for j in dbinv.get(g,[]):
            if j in seen:continue
            seen.add(j)
            a=cs[i];b=dbcs[j]
            if not a or not b:continue
            if len(a&b)/len(a|b)<=0.5:continue
            if C.lcs_len(recs[i][1],dbrec[j][1])>=15:
                hit+=1
print(f"与全主库R10撞车(>=15): {hit} 处")
