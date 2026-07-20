import json, sys, traceback
sys.path.insert(0,'.')
from check_single import validate
from recs import RECS

batches=["068","069","070","071","072","073","074","075"]
src={}; order=[]
for b in batches:
    d=json.load(open(f"batches_full/batch_src_{b}.json",encoding="utf-8"))
    for e in d:
        src[e['serial']]=e; order.append(e['serial'])

others=list(RECS.values())
rec_fails={}; src_fails={}; errs={}
for s in order:
    try:
        e=dict(src[s]); e['recommend']=RECS[s]
        iss=validate(e, others=others, skip=["R10","R6","R7","R8"])
        if iss: rec_fails[s]=iss
        iss2=validate(e, others=others, skip=["R10","R1","R2","R3","R4","R5","R-name","R-field-dedup","R-integrity","R-novelty","R-jargon","R-noabs"])
        if iss2: src_fails[s]=iss2
    except Exception as ex:
        errs[s]=traceback.format_exc()

out={"rec_fails":rec_fails,"src_fails":src_fails,"errs":errs}
json.dump(out, open("selfcheck_result.json","w"), ensure_ascii=False, indent=1)
print("rec_fails",len(rec_fails),"src_fails",len(src_fails),"errs",len(errs))
