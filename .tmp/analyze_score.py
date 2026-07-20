import json, re
data=json.load(open("data/enterprise/all_enterprises.json",encoding="utf-8"))
by={e["serial"]:e for e in data}

# ---- 把 signal_strength.py 的逻辑移植到"企业"字段 ----
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
    disp=(fl.get("display") or fl.get("amount") or "")
    rnd=(fl.get("round") or "")
    stage=(e.get("stage") or "")
    blob=f"{disp} {rnd} {stage}".lower()
    score=0.3  # 小基线
    # IPO / 上市
    is_ipo = ("ipo" in blob) or ("上市" in blob) or ("纳斯达克" in blob) or ("敲钟" in blob) or ("挂牌" in blob)
    if is_ipo: score+=6
    # 融资
    is_fund = any(k in blob for k in ["融资","轮","raises","series"])
    if is_fund:
        val,cur=parse_amount(str(disp))
        if val>0:
            tbl=FUND_OVER if cur=="USD" else FUND_DOM
            for low,sc in tbl:
                if val>=low: score+=sc; break
    # 收购
    is_ma = any(k in blob for k in ["收购","并购","merger","acquir"])
    if is_ma:
        val,cur=parse_amount(str(disp))
        if val>0:
            for low,sc in MA_TIERS:
                if val>=low: score+=sc; break
    # 时效
    d=fl.get("date") or ""
    days=9999
    if d:
        try:
            from datetime import datetime,timezone
            dd=datetime.strptime(str(d)[:10],"%Y-%m-%d").replace(tzinfo=timezone.utc)
            days=(datetime.now(timezone.utc)-dd).days
        except: days=9999
    if days<=7: score+=2.5
    elif days<=30: score+=2.0
    elif days<=60: score+=1.5
    elif days<=180: score+=1.0
    elif days<=365: score+=0.5
    else: score+=0.25
    # 新闻覆盖加成
    nc=e.get("news_coverage")
    if isinstance(nc,dict):
        cnt=nc.get("news_count",0) or 0
        if cnt>=20: score+=1.0
        elif cnt>=10: score+=0.5
    return round(min(10.0,score),2)

# ---- 银发相关性粗筛 ----
SILVER_KW=["养老","老年","银发","适老","康养","长者","退休","老龄","老人","养护","助老","长辈","照护","护理","陪诊","慢病","护工","长护险","康复","营养","听力","认知","失能","痴呆","健管","养老","居家养老","机构养老","养老社区","助听器","养老平台","养老服"]
EXCLUDE_KW=["综合电商","Web3","通用AI","泛再生","泛医疗VC","泛融媒体","品牌PR","活动传播"]
def silver_verdict(e):
    blob=" ".join(str(x) for x in [e.get("name"),e.get("name_cn"),e.get("desc_cn"),e.get("description"),str(e.get("tag_l1")),str(e.get("tag_l2")),str(e.get("business_tags"))])
    if any(k in blob for k in EXCLUDE_KW): return "排除(非银发)"
    hit=[k for k in SILVER_KW if k in blob]
    return ("银发" if hit else "待核(无关键词)"), hit

serials=json.load(open("scores_draft/pilot25_serials.json",encoding="utf-8"))
print("=== 25家：旧信号(我近似) vs 正确企业信号 vs 重算综合分 ===")
for s in serials:
    e=by[s]
    old=e.get("signal_strength")
    new=ent_signal(e)
    info=e.get("info_score"); diff=e.get("diff_score"); copy=e.get("copy_score")
    rv_old=e.get("research_value")
    rv_new=round((new*0.3+(info or 0)*0.3+(diff or 0)*0.2+(copy or 0)*0.2)*10,1) if all(x is not None for x in [info,diff,copy]) else None
    sv, hit = silver_verdict(e)
    name=e.get("name_cn") or e.get("name")
    print(f"{s} {name[:14]:14} 旧sig={old} 新sig={new} | 旧RV={rv_old} 新RV={rv_new} | 银发={sv} {hit if isinstance(sv,tuple) else ''}")

# ---- 全量重排 + 选下一批30 ----
print("\n=== 全量企业信号重排，筛选[有融资/IPO/上市]且银发，排除已做25家，取前30 ===")
cands=[]
for e in data:
    s=e["serial"]
    if s in serials: continue
    fl=e.get("funding_latest") or {}
    if not isinstance(fl,dict): fl={}
    disp=(fl.get("display") or fl.get("amount") or "")
    rnd=(fl.get("round") or ""); stage=(e.get("stage") or "")
    has_fin = bool(disp.strip()) or ("上市" in stage) or ("IPO" in str(rnd).upper())
    if not has_fin: continue
    sv,hit=silver_verdict(e)
    if sv=="排除(非银发)": continue
    sig=ent_signal(e)
    cands.append((sig,s,e.get("name_cn") or e.get("name"),disp,rnd,stage,sv))
cands.sort(key=lambda x:-x[0])
top30=[c[1] for c in cands[:30]]
print(f"候选(有融资且银发)共 {len(cands)} 家，取前30:")
for i,c in enumerate(cands[:30],1):
    print(f"{i:2d}. {c[1]} {str(c[2])[:16]:16} sig={c[0]} fund={str(c[3])[:20]!r} rnd={c[4]} 银发={c[6]}")
json.dump(top30,open("scores_draft/new30_serials.json","w"),ensure_ascii=False)
print("\n已存 new30_serials.json")
