import json, collections
data=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
def ent_signal(e):
    s=0.0
    fl=e.get("funding_latest") or {}
    disp=(fl.get("display") or fl.get("amount") or "")
    rnd=(fl.get("round") or "")
    if disp and "未披露" not in disp and "未公开" not in disp and "未公开披露" not in disp:
        s+=3
    if rnd in ("IPO","上市","并购","被收购","收购"): s+=4
    elif rnd in ("C轮","D轮","E轮","战略融资","战略"): s+=3
    elif rnd in ("B轮",): s+=2
    elif rnd in ("A轮","Pre-A","A+轮"): s+=1
    nc=e.get("news_coverage") or {}
    if isinstance(nc,dict):
        s+=min(nc.get("news_count",0)/10.0,3.0)
        if nc.get("news_quality")=="high": s+=1
    vs=e.get("value_score")
    if isinstance(vs,(int,float)): s+=vs/50.0
    # overseas slightly prioritized for 借鉴价值 signal diversity
    if e.get("region")=="海外": s+=0.5
    return round(s,2)
ranked=[(ent_signal(e), e.get("serial"), e.get("name"), e.get("name_cn"), (e.get("funding_latest") or {}).get("display",""), e.get("tag_l1"), e.get("region")) for e in data]
ranked.sort(key=lambda x:-x[0])
print("=== TOP 25 by enterprise signal ===")
for i,(sc,serial,name,ncn,fl,tl,reg) in enumerate(ranked[:25],1):
    print(f"{i:2d}. {serial} {name}({ncn}) sig={sc} fund={fl!r} tags={tl} reg={reg}")
# also dump serials list for snapshot
import os
os.makedirs("scores_draft",exist_ok=True)
json.dump([r[1] for r in ranked[:25]], open("scores_draft/pilot25_serials.json","w"), ensure_ascii=False)
