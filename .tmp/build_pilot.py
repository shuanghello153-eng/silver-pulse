import json, os
data=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
by_serial={e["serial"]:e for e in data}
def fl_get(e):
    fl=e.get("funding_latest")
    if isinstance(fl,dict): return fl
    return {}
def ent_signal(e):
    s=0.0
    fl=fl_get(e)
    disp=(fl.get("display") or fl.get("amount") or "")
    rnd=(fl.get("round") or "")
    if disp and "未披露" not in disp and "未公开" not in disp and "未公开披露" not in disp:
        s+=3
    if rnd in ("IPO","上市","并购","被收购","收购"): s+=4
    elif rnd in ("C轮","D轮","E轮","战略融资","战略"): s+=3
    elif rnd in ("B轮",): s+=2
    elif rnd in ("A轮","Pre-A","A+轮"): s+=1
    nc=e.get("news_coverage")
    if isinstance(nc,dict):
        s+=min(nc.get("news_count",0)/10.0,3.0)
        if nc.get("news_quality")=="high": s+=1
    vs=e.get("value_score")
    if isinstance(vs,(int,float)): s+=vs/50.0
    if e.get("region")=="海外": s+=0.5
    return round(s,2)
ranked=[(ent_signal(e), e["serial"]) for e in data]
ranked.sort(key=lambda x:-x[0])
top25=[s for _,s in ranked[:25]]
print("=== TOP 25 signal ===")
for i,s in enumerate(top25,1):
    e=by_serial[s]
    fl=fl_get(e)
    print(f"{i:2d}. {s} {e.get('name')}({e.get('name_cn')}) sig={ent_signal(e)} fund={fl.get('display','')!r} tags={e.get('tag_l1')}")
os.makedirs("scores_draft",exist_ok=True)
json.dump(top25, open("scores_draft/pilot25_serials.json","w"), ensure_ascii=False)

# snapshot before
before={s:by_serial[s] for s in top25}
json.dump(before, open("scores_draft/pilot25_before.json","w"), ensure_ascii=False, indent=1)

# build 5 packets of 5
def trim(e):
    return {
      "serial":e.get("serial"),"name":e.get("name"),"name_cn":e.get("name_cn"),
      "region":e.get("region"),"founded":e.get("founded"),"stage":e.get("stage"),
      "source":e.get("source"),"website_url":e.get("website_url"),
      "desc_cn":(e.get("desc_cn") or "")[:400],
      "description":(e.get("description") or "")[:400],
      "funding_latest":fl_get(e),"funding_total":(e.get("funding_total") if isinstance(e.get("funding_total"),dict) else {}),
      "investors":e.get("investors"),"payor_model":e.get("payor_model"),
      "tag_l1":e.get("tag_l1"),"tag_l2":e.get("tag_l2"),
      "business_tags":(e.get("business_tags") if isinstance(e.get("business_tags"),dict) else {}),
      "news_coverage":(e.get("news_coverage") if isinstance(e.get("news_coverage"),dict) else {}),
      "highlights":e.get("highlights"),
    }
packets=[]
for i in range(0,25,5):
    pk=[trim(by_serial[s]) for s in top25[i:i+5]]
    packets.append(pk)
json.dump(packets, open("scores_draft/pilot_packets.json","w"), ensure_ascii=False, indent=1)
print("\npackets built:", len(packets), "each", [len(p) for p in packets])
