import json, re, os
data=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
by={e["serial"]:e for e in data}

def parse_amount(text):
    if not text: return 0,None
    m=re.search(r"\$\s?([\d.]+)\s*(b|bn|billion|m|mn|million)",text,re.I)
    if m:
        v=float(m.group(1)); u=m.group(2).lower()
        return (v*1e9 if u.startswith("b") else v*1e6),"USD"
    m=re.search(r"([\d.]+)\s*(亿|万)\s*(元|美元|人民币|￥|¥)?",text)
    if m:
        v=float(m.group(1)); u=m.group(2)
        cur="USD" if (m.group(3) and "美元" in m.group(3)) else "CNY"
        return (v*1e8 if u=="亿" else v*1e4),cur
    return 0,None
FUND_OVER=[(1e9,5),(1e8,4),(5e7,3),(1e7,2),(5e6,1),(1e6,0.5)]
FUND_DOM=[(1e9,6),(1e8,5),(5e7,4),(1e7,3),(5e6,2),(1e6,1),(5e5,0.5)]
MA_TIERS=[(1e10,6),(5e9,5),(1e9,4),(1e8,3),(5e7,2),(1e7,1)]
def ent_signal(e):
    fl=e.get("funding_latest") or {}
    if not isinstance(fl,dict): fl={}
    disp=(fl.get("display") or fl.get("amount") or ""); rnd=(fl.get("round") or ""); stage=(e.get("stage") or "")
    blob=f"{disp} {rnd} {stage}".lower()
    score=0.3
    if any(k in blob for k in ["ipo","上市","纳斯达克","敲钟","挂牌"]): score+=6
    if any(k in blob for k in ["融资","轮","raises","series"]):
        val,cur=parse_amount(str(disp))
        if val>0:
            tbl=FUND_OVER if cur=="USD" else FUND_DOM
            for low,sc in tbl:
                if val>=low: score+=sc; break
    if any(k in blob for k in ["收购","并购","merger","acquir"]):
        val,cur=parse_amount(str(disp))
        if val>0:
            for low,sc in MA_TIERS:
                if val>=low: score+=sc; break
    d=fl.get("date") or ""
    if d:
        try:
            from datetime import datetime,timezone
            dd=datetime.strptime(str(d)[:10],"%Y-%m-%d").replace(tzinfo=timezone.utc)
            days=(datetime.now(timezone.utc)-dd).days
            score+= 2.5 if days<=7 else 2.0 if days<=30 else 1.5 if days<=60 else 1.0 if days<=180 else 0.5 if days<=365 else 0.25
        except: score+=0.25
    else: score+=0.25
    nc=e.get("news_coverage")
    if isinstance(nc,dict):
        cnt=nc.get("news_count",0) or 0
        score+= 1.0 if cnt>=20 else 0.5 if cnt>=10 else 0
    return round(min(10.0,score),2)

# (1) 修正25家信号+综合分
serials=json.load(open("scores_draft/pilot25_serials.json",encoding="utf-8"))
for s in serials:
    e=by[s]
    sig=ent_signal(e)
    e["signal_strength"]=sig
    info=e.get("info_score"); diff=e.get("diff_score"); copy=e.get("copy_score")
    if None not in (info,diff,copy):
        e["research_value"]=round((sig*0.3+info*0.3+diff*0.2+copy*0.2)*10,1)
json.dump(data,open("data/enterprise/all_enterprises.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("25家信号已修正并写回")

# 全量信号缓存(不写库,供后续批次)
allsig={e["serial"]:ent_signal(e) for e in data}
json.dump(allsig,open("scores_draft/all_signals.json","w"),ensure_ascii=False)
print("全量信号缓存已存, 样例:", {k:allsig[k] for k in serials[:3]})

# (2) 30-new 研究包
new30=json.load(open("scores_draft/new30_serials.json",encoding="utf-8"))
def trim(e):
    fl=e.get("funding_latest") or {}
    if not isinstance(fl,dict): fl={}
    return {"serial":e["serial"],"name":e.get("name"),"name_cn":e.get("name_cn"),
      "region":e.get("region"),"founded":e.get("founded"),"stage":e.get("stage"),
      "source":e.get("source"),"website_url":e.get("website_url"),
      "desc_cn":(e.get("desc_cn") or "")[:500],"description":(e.get("description") or "")[:500],
      "funding_latest":fl,"funding_total":(e.get("funding_total") if isinstance(e.get("funding_total"),dict) else {}),
      "investors":e.get("investors"),"payor_model":e.get("payor_model"),
      "tag_l1":e.get("tag_l1"),"tag_l2":e.get("tag_l2"),
      "business_tags":(e.get("business_tags") if isinstance(e.get("business_tags"),dict) else {}),
      "news_coverage":(e.get("news_coverage") if isinstance(e.get("news_coverage"),dict) else {}),
      "highlights":e.get("highlights")}
packets=[]; idx=0
for i in range(0,30,5):
    packets.append([trim(by[s]) for s in new30[i:i+5]])
json.dump(packets,open("scores_draft/new30_packets.json","w"),ensure_ascii=False,indent=1)
print("30-new 研究包已建:", [len(p) for p in packets])

# (3) 25家 推荐理由重写证据包(给子智能体)
SILVER_KW=["养老","老年","银发","适老","康养","长者","退休","老龄","老人","养护","助老","长辈","照护","护理","陪诊","慢病","护工","长护险","康复","营养","听力","认知","失能","痴呆"]
def silver_hit(e):
    blob=" ".join(str(x) for x in [e.get("name"),e.get("name_cn"),e.get("desc_cn"),e.get("description"),str(e.get("tag_l1")),str(e.get("tag_l2"))])
    return [k for k in SILVER_KW if k in blob]
ev=[]
for s in serials:
    e=by[s]
    ev.append({"serial":s,"name":e.get("name"),"name_cn":e.get("name_cn"),
      "funding_latest":(e.get("funding_latest") if isinstance(e.get("funding_latest"),dict) else {}),
      "payor_model":e.get("payor_model"),"highlights":e.get("highlights"),
      "tag_l1":e.get("tag_l1"),"tag_l2":e.get("tag_l2"),
      "info_score":e.get("info_score"),"diff_score":e.get("diff_score"),"copy_score":e.get("copy_score"),
      "signal_strength":e.get("signal_strength"),"research_value":e.get("research_value"),
      "silver_hit":silver_hit(e)})
json.dump(ev,open("scores_draft/rec25_evidence.json","w"),ensure_ascii=False,indent=1)
print("25家推荐理由证据包已建:", len(ev))
