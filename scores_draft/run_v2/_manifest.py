# -*- coding: utf-8 -*-
import json, os, glob
BASE="G:/workbuddy/2026-06-28-23-34-20/silver-pulse"
RUN=os.path.join(BASE,"scores_draft/run")
RUNV2=os.path.join(BASE,"scores_draft/run_v2")
DB=json.load(open(os.path.join(BASE,"data/enterprise/all_enterprises.json"),encoding="utf-8"))
by={e["serial"]:e for e in DB}

# legacy out files (both padded and not)
legacy_out=set()
for f in glob.glob(os.path.join(RUN,"out","batch_*out.json")):
    bn=os.path.basename(f).replace("_out.json","")  # batch_000 or batch_0
    num=bn.split("_")[-1]
    legacy_out.add(int(num))

manifest=[]
for i in range(126):
    fp=os.path.join(RUN,"inbox",f"batch_{i:03d}.json")
    if not os.path.exists(fp): 
        print("MISSING inbox", i); continue
    b=json.load(open(fp,encoding="utf-8"))
    ents=b["enterprises"]
    serials=[e["serial"] for e in ents]
    scored_in_db=sum(1 for s in serials if by.get(s,{}).get("research_value") is not None)
    manifest.append({
        "batch":i,
        "tier":b.get("tier"),
        "n":len(serials),
        "serials":serials,
        "scored_in_db":scored_in_db,
        "has_legacy_out": i in legacy_out,
    })
json.dump(manifest,open(os.path.join(RUNV2,"manifest.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)

# stats
scored_batches=[m for m in manifest if m["scored_in_db"]==m["n"]]
mix_batches=[m for m in manifest if 0<m["scored_in_db"]<m["n"]]
unscored_batches=[m for m in manifest if m["scored_in_db"]==0]
print("总批次数:",len(manifest))
print("全评分批(已有分):",len(scored_batches))
print("混合批:",len(mix_batches))
print("全未评分批(需联网):",len(unscored_batches))
print("需联网批次的 serial 数:", sum(m["n"] for m in unscored_batches))
print("tier 分布:", {t:sum(1 for m in manifest if m["tier"]==t) for t in set(m["tier"] for m in manifest)})
# check any serial missing in DB
miss=[s for m in manifest for s in m["serials"] if s not in by]
print("库中缺失的 serial 数:", len(miss), miss[:10])
