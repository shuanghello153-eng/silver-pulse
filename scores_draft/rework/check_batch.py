import sys,json
sys.path.insert(0,'.')
from check_single import validate
from recs import RECS
b=sys.argv[1]
d=json.load(open(f"batches_full/batch_src_{b}.json",encoding="utf-8"))
others=list(RECS.values())
fails={}
for e in d:
    s=e['serial']
    rec=dict(e); rec['recommend']=RECS[s]
    iss=validate(rec, others=others, skip=["R10","R6","R7","R8"])
    if iss: fails[s]=iss
print(f"== batch {b}: {len(d)} checked, {len(fails)} fails ==")
for s,iss in fails.items():
    print(s, iss)
