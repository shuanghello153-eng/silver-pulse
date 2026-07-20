import json, os, sys, glob, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_single as C
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(HERE, "drafts_v4")
files = sorted(glob.glob(os.path.join(DD, "draft_*.json")))
by_serial = defaultdict(list)
for fp in files:
    try: d = json.load(open(fp, encoding="utf-8"))
    except: continue
    s = d.get("serial","")
    if s: by_serial[s].append(d)
draft_list = [max(lst, key=lambda d: C.content_len(d.get("recommend") or "")) for s,lst in by_serial.items()]
recs = [(d.get("serial"), d.get("recommend","")) for d in draft_list if isinstance(d.get("recommend"),str)]

def _norm(t): return re.sub(r"\s","",t or "")
def _trigrams(t):
    t=_norm(t); return set(t[i:i+3] for i in range(len(t)-2)) if len(t)>=3 else set(t)
def _charset(t): return set(_norm(t))
char_sets=[_charset(r) for s,r in recs]
tris=[_trigrams(r) for s,r in recs]
inv={}
for i,tr in enumerate(tris):
    for g in tr: inv.setdefault(g,[]).append(i)

fails=[]
for i in range(len(recs)):
    seen=set()
    for g in tris[i]:
        for j in inv.get(g,[]):
            if j<=i or j in seen: continue
            seen.add(j)
            sa,sb=char_sets[i],char_sets[j]
            if not sa or not sb: continue
            if len(sa&sb)/len(sa|sb)<=0.5: continue
            si,ri=recs[i]; sj,rj=recs[j]
            L=C.lcs_len(ri,rj)
            if ri==rj or L>=15:
                ja=set(_norm(ri)); jb=set(_norm(rj))
                jac=len(ja&jb)/len(ja|jb) if (ja|jb) else 0
                fails.append((si,sj,ri,rj,L,jac))
print(f"R10失败对总数: {len(fails)}")
random.seed(7)
sample=random.sample(fails, min(8,len(fails)))
for si,sj,ri,rj,lcs,jac in sample:
    print("\n"+"="*55)
    print(f"对 {si} vs {sj} | LCS={lcs} Jaccard={jac:.2f}")
    print(f"  [{si}] {ri}")
    print(f"  [{sj}] {rj}")
