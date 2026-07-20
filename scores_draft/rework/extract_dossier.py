import json,sys
batches=["068","069","070","071","072","073","074","075"]
base="batches_full"
with open("dossier_all.txt","w",encoding="utf-8") as out:
    for b in batches:
        d=json.load(open(f"{base}/batch_src_{b}.json",encoding="utf-8"))
        for e in d:
            s=e.get("serial","")
            nm=e.get("name_cn") or e.get("name","")
            tags=(e.get("tag_l1") or [])+(e.get("tag_l2") or [])
            region=e.get("region","")
            dc=e.get("desc_cn","") or ""
            sr=e.get("silver_reason","") or ""
            hl=e.get("highlights") or []
            hl=" | ".join(hl) if isinstance(hl,list) else str(hl)
            fl=e.get("funding_latest","")
            ft=e.get("funding_total","")
            pm=e.get("payor_model","")
            sc=f"信号{e.get('signal_strength','')} 信息{e.get('info_score','')} 差异{e.get('diff_score','')} 复制{e.get('copy_score','')} 价值{e.get('research_value','')}"
            verdict=e.get("silver_verdict","")
            out.write(f"==== {s} | {nm} | {region} | {verdict}\n")
            out.write(f"TAGS: {tags}\n")
            out.write(f"DESC: {dc}\n")
            out.write(f"SILVER: {sr}\n")
            out.write(f"HIGHLIGHTS: {hl}\n")
            out.write(f"FUNDING: latest={fl} | total={ft}\n")
            out.write(f"PAYOR: {pm}\n")
            out.write(f"SCORES: {sc}\n")
            out.write("\n")
print("done")
